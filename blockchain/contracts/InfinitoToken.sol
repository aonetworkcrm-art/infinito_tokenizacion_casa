// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title InfinitoToken (TI)
 * @notice ERC-20 token del Proyecto Infinito en Polygon Amoy Testnet
 * @dev Implementa AccessControl para roles granulares, ERC20Permit para
 *      transacciones sin gas (gasless), y un tax de 2% en transfers que
 *      alimenta la tesoreria de la DAO.
 *
 * Distribucion Inicial (1,000,000 TI):
 *   51% -> Padres (Multisig) - Soberania vitalicia
 *   35% -> Joker (Arquitecto) - Gobernanza (65% en vesting)
 *   14% -> Pool de Herederos - Incentivos familiares
 *
 * Polygon Amoy Testnet:
 *   Chain ID: 80002
 *   RPC: https://rpc-amoy.polygon.technology
 *   Explorer: https://amoy.polygonscan.com
 *
 * @author Romny (El Joker) + Buffy (Codebuff AI)
 * @version 1.0.1
 */

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Pausable.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Permit.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

contract InfinitoToken is
    ERC20,
    ERC20Burnable,
    ERC20Pausable,
    ERC20Permit,
    AccessControl,
    ReentrancyGuard
{
    // ============================================
    // ROLES
    // ============================================
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");
    bytes32 public constant TAX_MANAGER_ROLE = keccak256("TAX_MANAGER_ROLE");
    bytes32 public constant TREASURY_ROLE = keccak256("TREASURY_ROLE");

    // ============================================
    // CONSTANTES
    // ============================================
    /// @notice Total supply fijo: 1,000,000 TI
    uint256 public constant TOTAL_SUPPLY = 1_000_000 * 10 ** 18; // 1,000,000 TI con 18 decimals

    /// @notice Tax de transferencia: 2% (200 = 2% con 4 decimales)
    uint256 public constant TAX_BPS = 200; // 200 basis points = 2%

    /// @notice Maximo tax permitido: 5%
    uint256 public constant MAX_TAX_BPS = 500;

    /// @notice Direccion por defecto de la tesoreria DAO
    address public treasuryAddress;

    /// @notice Porcentaje de tax actual (modificable solo por TAX_MANAGER_ROLE)
    uint256 public taxBps = TAX_BPS;

    /// @notice Si el tax esta activo o no
    bool public taxActive = true;

    /// @notice Lista de direcciones exentas de tax (ej. la tesoreria misma)
    mapping(address => bool) public isExemptFromTax;

    // ============================================
    // EVENTOS
    // ============================================
    event TreasuryUpdated(address indexed newTreasury);
    event TaxUpdated(uint256 newTaxBps);
    event TaxExemptionUpdated(address indexed account, bool exempt);
    event TaxCollected(address indexed from, uint256 amount, address indexed treasury);
    event TokensMinted(address indexed to, uint256 amount);
    event TokensBurned(address indexed from, uint256 amount);

    // ============================================
    // CONSTRUCTOR
    // ============================================
    /**
     * @notice Inicializa el token con distribucion inicial
     * @param _treasuryAddress Direccion de la tesoreria DAO que recibe el tax
     * @param _padresAddress Direccion Multisig de los padres (51%)
     * @param _jokerAddress Direccion del Joker/Arquitecto (35%)
     */
    constructor(
        address _treasuryAddress,
        address _padresAddress,
        address _jokerAddress
    ) ERC20("Infinito Token", "TI") ERC20Permit("Infinito Token") {
        require(_treasuryAddress != address(0), "Treasury cannot be zero");
        require(_padresAddress != address(0), "Padres cannot be zero");
        require(_jokerAddress != address(0), "Joker cannot be zero");

        // Configurar roles
        _grantRole(DEFAULT_ADMIN_ROLE, _jokerAddress);
        _grantRole(MINTER_ROLE, _jokerAddress);
        _grantRole(PAUSER_ROLE, _jokerAddress);
        _grantRole(TAX_MANAGER_ROLE, _jokerAddress);
        _grantRole(TREASURY_ROLE, _treasuryAddress);

        treasuryAddress = _treasuryAddress;

        // Eximir la tesoreria del tax
        isExemptFromTax[_treasuryAddress] = true;
        isExemptFromTax[_jokerAddress] = true;

        // Distribucion inicial:
        // 51% -> Padres (510,000 TI)
        _mint(_padresAddress, (TOTAL_SUPPLY * 51) / 100);
        emit TokensMinted(_padresAddress, (TOTAL_SUPPLY * 51) / 100);

        // 35% -> Joker (350,000 TI - con vesting fuera del contrato)
        _mint(_jokerAddress, (TOTAL_SUPPLY * 35) / 100);
        emit TokensMinted(_jokerAddress, (TOTAL_SUPPLY * 35) / 100);

        // 14% queda en poder del MINTER para distribuir desde el pool
        // No se mintea automaticamente para evitar dilucion no deseada

        // Pausar el contrato inicialmente hasta que se verifique
        _pause();
    }

    // ============================================
    // FUNCIONES DEL TOKEN
    // ============================================

    /**
     * @notice Mintea nuevos tokens (solo MINTER_ROLE)
     * @param to Direccion receptora
     * @param amount Cantidad de tokens (en wei, 18 decimals)
     */
    function mintTokens(
        address to,
        uint256 amount
    ) external onlyRole(MINTER_ROLE) whenNotPaused {
        require(to != address(0), "Cannot mint to zero address");
        require(amount > 0, "Amount must be greater than 0");
        require(
            totalSupply() + amount <= TOTAL_SUPPLY,
            "Exceeds max supply"
        );

        _mint(to, amount);
        emit TokensMinted(to, amount);
    }

    /**
     * @notice Quema tokens del pool de herederos (solo TREASURY_ROLE)
     * @param amount Cantidad a quemar
     */
    function burnFromPool(
        uint256 amount
    ) external onlyRole(TREASURY_ROLE) whenNotPaused {
        require(amount > 0, "Amount must be greater than 0");
        _burn(msg.sender, amount);
        emit TokensBurned(msg.sender, amount);
    }

    // ============================================
    // FUNCIONES DE ADMINISTRACION
    // ============================================

    /**
     * @notice Actualiza la direccion de la tesoreria (solo TREASURY_ROLE)
     */
    function updateTreasury(
        address _newTreasury
    ) external onlyRole(TREASURY_ROLE) {
        require(_newTreasury != address(0), "Treasury cannot be zero");
        treasuryAddress = _newTreasury;
        emit TreasuryUpdated(_newTreasury);
    }

    /**
     * @notice Actualiza el porcentaje de tax (solo TAX_MANAGER_ROLE)
     * @param _newTaxBps Nuevo tax en basis points (max 500 = 5%)
     */
    function updateTax(uint256 _newTaxBps) external onlyRole(TAX_MANAGER_ROLE) {
        require(_newTaxBps <= MAX_TAX_BPS, "Tax exceeds maximum");
        taxBps = _newTaxBps;
        emit TaxUpdated(_newTaxBps);
    }

    /**
     * @notice Activa/desactiva el tax de transferencia
     */
    function toggleTax() external onlyRole(TAX_MANAGER_ROLE) {
        taxActive = !taxActive;
    }

    /**
     * @notice Exime o revoca la exencion de tax a una direccion
     */
    function setTaxExemption(
        address account,
        bool exempt
    ) external onlyRole(TAX_MANAGER_ROLE) {
        isExemptFromTax[account] = exempt;
        emit TaxExemptionUpdated(account, exempt);
    }

    /**
     * @notice Pausa el contrato (solo PAUSER_ROLE)
     */
    function pause() external onlyRole(PAUSER_ROLE) {
        _pause();
    }

    /**
     * @notice Reanuda el contrato (solo PAUSER_ROLE)
     */
    function unpause() external onlyRole(PAUSER_ROLE) {
        _unpause();
    }

    // ============================================
    // HOOKS: TRANSFERENCIA CON TAX
    // ============================================

    /**
     * @notice Hook de transferencia que aplica el tax del 2%
     * @dev El tax se descuenta del monto transferido y se envia a la tesoreria
     */
    function _update(
        address from,
        address to,
        uint256 value
    ) internal override(ERC20, ERC20Pausable) whenNotPaused {
        // Si el tax esta activo, y ninguna de las partes esta exenta,
        // y no es mint/burn, aplicar tax
        if (
            taxActive &&
            from != address(0) && // No aplicar tax en mints
            to != address(0) &&   // No aplicar tax en burns
            !isExemptFromTax[from] &&
            !isExemptFromTax[to]
        ) {
            uint256 taxAmount = (value * taxBps) / 10000;
            uint256 transferAmount = value - taxAmount;

            if (taxAmount > 0) {
                // Enviar tax a la tesoreria
                super._update(from, treasuryAddress, taxAmount);
                emit TaxCollected(from, taxAmount, treasuryAddress);
            }

            // Enviar el resto al destinatario
            super._update(from, to, transferAmount);
        } else {
            super._update(from, to, value);
        }
    }

    // ============================================
    // OVERRIDES NECESARIOS POR HERENCIA MULTIPLE
    // ============================================

    /// @notice ERC20 en OZ v5 ya devuelve 18 decimals por defecto, lo mantenemos explícito
    function decimals()
        public
        view
        virtual
        override
        returns (uint8)
    {
        return 18;
    }

    /// @notice ERC20Permit nonces override necesario por herencia múltiple
    function nonces(
        address owner
    ) public view virtual override(ERC20Permit) returns (uint256) {
        return super.nonces(owner);
    }

    // ============================================
    // FUNCIONES PUBLICAS DE UTILIDAD
    // ============================================

    /// @notice Retorna el domain separator para ERC20Permit (gasless approvals)
    function domainSeparator() external view returns (bytes32) {
        return _domainSeparatorV4();
    }
}

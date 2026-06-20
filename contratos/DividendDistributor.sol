// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title DividendDistributor
 * @notice Distribucion automatica de dividendos en MATIC/USDC a holders
 *         del InfinitoToken (TI). Usa el patron Pull-based: los holders
 *         reclaman sus dividendos llamando a claim().
 *
 * Mecanica:
 *   1. El backend (TreasuryFlow) deposita ganancias en el contrato
 *   2. Cada deposito actualiza el dividendo acumulado por accion (cumulativeDividendPerShare)
 *   3. Los holders reclaman sus dividendos proporcionales a sus tokens TI
 *
 * Caracteristicas:
 *   - Pull-based (no Push): evita gas explosion en loops
 *   - Usa los balances reales del token TI (se consultan on-chain)
 *   - Depositos en MATIC nativo (Polygon) o ERC-20 (USDC)
 *   - Snapshot-based para evitar manipulacion
 *   - Distribucion: 70% tesoreria, 10% airdrops familia, 20% gas/ops
 *
 * Polygon Amoy Testnet:
 *   Chain ID: 80002
 *
 * @author Romny (El Joker) + Buffy (Codebuff AI)
 * @version 1.0.0
 */

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Pausable.sol";

interface IInfinitoToken {
    function balanceOf(address account) external view returns (uint256);
    function totalSupply() external view returns (uint256);
}

contract DividendDistributor is AccessControl, ReentrancyGuard, Pausable {
    using SafeERC20 for IERC20;

    // ============================================
    // ROLES
    // ============================================
    bytes32 public constant DEPOSITOR_ROLE = keccak256("DEPOSITOR_ROLE");
    bytes32 public constant TREASURY_ROLE = keccak256("TREASURY_ROLE");
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");

    // ============================================
    // CONSTANTES DE DISTRIBUCION
    // ============================================
    /// @notice 70% del deposito va a la tesoreria DAO
    uint256 public constant TREASURY_SHARE_BPS = 7000; // 70%

    /// @notice 10% del deposito va a airdrops familiares
    uint256 public constant FAMILY_AIRDROP_BPS = 1000; // 10%

    /// @notice Restante 20% para gas y operaciones
    ///         (se queda en el contrato para ser usado por el ADMIN)

    /// @notice Maximo que puede distribuirse por ciclo (evita manipulacion)
    uint256 public constant MAX_DISTRIBUTION_BPS = 5000; // 50% del profit depositado

    // ============================================
    // ESTADO
    // ============================================

    /// @notice El token TI
    IInfinitoToken public immutable infinitoToken;

    /// @notice Token usado para dividendos (address(0) = MATIC nativo)
    address public immutable dividendToken;

    /// @notice Si dividendToken es address(0), usamos MATIC nativo
    bool public immutable isNativeDividend;

    /// @notice Direccion de la tesoreria DAO
    address public treasuryAddress;

    /// @notice Total de dividendos acumulados y NO reclamados
    uint256 public totalUnclaimedDividends;

    /// @notice Total de dividendos distribuidos historicamente
    uint256 public totalDividendsDistributed;

    /// @notice Dividendo acumulado por accion (en wei, escalado x1e12)
    uint256 public cumulativeDividendPerShare;

    /// @notice Correccion por precision (escala el dividendo por accion)
    uint256 private constant PRECISION_FACTOR = 1e12;

    /// @notice Ultimo dividendo por accion reclamado por cada holder
    mapping(address => uint256) public lastClaimedDividendPerShare;

    /// @notice Dividendos reclamables actualmente (antes del claim)
    mapping(address => uint256) public pendingDividends;

    // ============================================
    // EVENTOS
    // ============================================
    event DividendsDeposited(
        address indexed depositor,
        uint256 amount,
        uint256 treasuryShare,
        uint256 airdropShare
    );
    event DividendsClaimed(
        address indexed claimant,
        uint256 amount,
        uint256 tokenBalance
    );
    event TreasuryUpdated(address indexed newTreasury);
    event EmergencyWithdraw(address indexed token, uint256 amount);
    event MinDistributionUpdated(uint256 newMinAmount);

    // ============================================
    // CONSTRUCTOR
    // ============================================

    /**
     * @notice Inicializa el distribuidor de dividendos
     * @param _infinitoToken Direccion del contrato InfinitoToken (TI)
     * @param _treasuryAddress Direccion de la tesoreria DAO
     * @param _dividendToken Direccion del token de dividendos (address(0) = MATIC)
     */
    constructor(
        address _infinitoToken,
        address _treasuryAddress,
        address _dividendToken
    ) {
        require(_infinitoToken != address(0), "Invalid token address");
        require(_treasuryAddress != address(0), "Invalid treasury address");

        infinitoToken = IInfinitoToken(_infinitoToken);
        treasuryAddress = _treasuryAddress;
        dividendToken = _dividendToken;
        isNativeDividend = (_dividendToken == address(0));

        // Roles
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(DEPOSITOR_ROLE, msg.sender);
        _grantRole(TREASURY_ROLE, _treasuryAddress);
        _grantRole(ADMIN_ROLE, msg.sender);
    }

    // ============================================
    // DEPOSITOS (solo DEPOSITOR_ROLE)
    // ============================================

    /**
     * @notice Deposita MATIC nativo como dividendos
     * @dev Los fondos se dividen: 70% tesoreria, 10% airdrops, 20% operaciones
     */
    function depositNative()
        external
        payable
        onlyRole(DEPOSITOR_ROLE)
        whenNotPaused
        nonReentrant
    {
        require(isNativeDividend, "This contract uses ERC-20 dividends");
        require(msg.value > 0, "No MATIC sent");
        _processDeposit(msg.value);
    }

    /**
     * @notice Deposita tokens ERC-20 (USDC, etc.) como dividendos
     * @param token Direccion del token a depositar (debe coincidir con dividendToken)
     * @param amount Cantidad de tokens a depositar
     */
    function depositERC20(
        address token,
        uint256 amount
    ) external onlyRole(DEPOSITOR_ROLE) whenNotPaused nonReentrant {
        require(!isNativeDividend, "This contract uses native MATIC");
        require(token == dividendToken, "Invalid token");
        require(amount > 0, "No tokens sent");

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);
        _processDeposit(amount);
    }

    /**
     * @notice Procesa un deposito: distribuye entre tesoreria, airdrops y acumulado
     */
    function _processDeposit(uint256 totalAmount) internal {
        // 70% -> Tesoreria DAO
        uint256 treasuryShare = (totalAmount * TREASURY_SHARE_BPS) / 10000;

        // 10% -> Airdrops familiares (se queda en el contrato para claim)
        uint256 airdropShare = (totalAmount * FAMILY_AIRDROP_BPS) / 10000;

        // 20% -> Operaciones (se queda en el contrato, accesible por ADMIN_ROLE)
        uint256 opsShare = totalAmount - treasuryShare - airdropShare;

        // Enviar la parte de la tesoreria
        if (isNativeDividend) {
            (bool sent, ) = payable(treasuryAddress).call{value: treasuryShare}("");
            require(sent, "Failed to send MATIC to treasury");
        } else {
            IERC20(dividendToken).safeTransfer(treasuryAddress, treasuryShare);
        }

        // Actualizar el dividendo acumulado por accion
        uint256 totalSupply = infinitoToken.totalSupply();
        if (totalSupply > 0 && airdropShare > 0) {
            uint256 dividendPerShare = (airdropShare * PRECISION_FACTOR) / totalSupply;
            cumulativeDividendPerShare += dividendPerShare;
            totalUnclaimedDividends += airdropShare;
        }

        totalDividendsDistributed += totalAmount;

        emit DividendsDeposited(msg.sender, totalAmount, treasuryShare, airdropShare);
    }

    // ============================================
    // RECLAMO DE DIVIDENDOS (Pull-based)
    // ============================================

    /**
     * @notice Reclama los dividendos acumulados para un holder
     * @dev Cualquiera puede llamar por cualquier holder (gas-abstracted)
     * @param holder Direccion del holder cuyos dividendos se reclaman
     */
    function claimDividends(
        address holder
    ) external whenNotPaused nonReentrant returns (uint256) {
        uint256 claimable = _calculateClaimable(holder);
        require(claimable > 0, "No dividends to claim");

        // Actualizar el estado antes de la transferencia (proteccion contra reentrancia)
        lastClaimedDividendPerShare[holder] = cumulativeDividendPerShare;
        pendingDividends[holder] = 0;
        totalUnclaimedDividends -= claimable;

        // Transferir los dividendos
        if (isNativeDividend) {
            (bool sent, ) = payable(holder).call{value: claimable}("");
            require(sent, "Failed to send MATIC dividend");
        } else {
            IERC20(dividendToken).safeTransfer(holder, claimable);
        }

        uint256 balance = infinitoToken.balanceOf(holder);
        emit DividendsClaimed(holder, claimable, balance);

        return claimable;
    }

    /**
     * @notice Reclama TODOS los dividendos pendientes para multiples holders
     *         (solo ADMIN - para optimizar gas)
     */
    function claimForMultiple(
        address[] calldata holders
    ) external onlyRole(ADMIN_ROLE) whenNotPaused {
        for (uint256 i = 0; i < holders.length; i++) {
            uint256 claimable = _calculateClaimable(holders[i]);
            if (claimable > 0) {
                lastClaimedDividendPerShare[holders[i]] = cumulativeDividendPerShare;
                pendingDividends[holders[i]] = 0;
                totalUnclaimedDividends -= claimable;

                if (isNativeDividend) {
                    (bool sent, ) = payable(holders[i]).call{value: claimable}("");
                    require(sent, "Failed to send MATIC dividend");
                } else {
                    IERC20(dividendToken).safeTransfer(holders[i], claimable);
                }

                emit DividendsClaimed(holders[i], claimable, infinitoToken.balanceOf(holders[i]));
            }
        }
    }

    // ============================================
    // CONSULTAS
    // ============================================

    /**
     * @notice Calcula los dividendos reclamables para un holder
     * @param holder Direccion del holder
     * @return Cantidad de dividendos reclamables
     */
    function getClaimableDividends(
        address holder
    ) external view returns (uint256) {
        return _calculateClaimable(holder);
    }

    /**
     * @notice Calcula interno los dividendos reclamables
     */
    function _calculateClaimable(address holder) internal view returns (uint256) {
        uint256 holderBalance = infinitoToken.balanceOf(holder);
        if (holderBalance == 0) return 0;

        uint256 unpaidDividendPerShare = cumulativeDividendPerShare -
            lastClaimedDividendPerShare[holder];

        if (unpaidDividendPerShare == 0) return 0;

        return (holderBalance * unpaidDividendPerShare) / PRECISION_FACTOR;
    }

    /**
     * @notice Obtiene el balance de MATIC nativo del contrato (disponible para dividendos)
     */
    function getContractNativeBalance() external view returns (uint256) {
        return address(this).balance;
    }

    /**
     * @notice Obtiene toda la info de dividendos para un holder
     */
    function getHolderInfo(
        address holder
    )
        external
        view
        returns (
            uint256 balance,
            uint256 claimable,
            uint256 lastClaimed,
            uint256 cumulative
        )
    {
        balance = infinitoToken.balanceOf(holder);
        claimable = _calculateClaimable(holder);
        lastClaimed = lastClaimedDividendPerShare[holder];
        cumulative = cumulativeDividendPerShare;
    }

    // ============================================
    // ADMINISTRACION
    // ============================================

    /**
     * @notice Actualiza la direccion de la tesoreria (solo TREASURY_ROLE)
     */
    function updateTreasury(
        address _newTreasury
    ) external onlyRole(TREASURY_ROLE) {
        require(_newTreasury != address(0), "Invalid treasury");
        treasuryAddress = _newTreasury;
        emit TreasuryUpdated(_newTreasury);
    }

    /**
     * @notice Retira fondos de operaciones (20% del deposito)
     *         Solo para costos de gas, VPS, herramientas
     */
    function withdrawOperations(
        uint256 amount
    ) external onlyRole(ADMIN_ROLE) nonReentrant {
        require(amount > 0, "Amount must be > 0");
        uint256 maxWithdraw = isNativeDividend
            ? address(this).balance - totalUnclaimedDividends
            : IERC20(dividendToken).balanceOf(address(this)) - totalUnclaimedDividends;

        require(amount <= maxWithdraw, "Insufficient ops funds");

        if (isNativeDividend) {
            (bool sent, ) = payable(treasuryAddress).call{value: amount}("");
            require(sent, "Failed to send");
        } else {
            IERC20(dividendToken).safeTransfer(treasuryAddress, amount);
        }
    }

    // ============================================
    // EMERGENCIA
    // ============================================

    /**
     * @notice Retiro de emergencia de tokens atascados en el contrato
     * @param token Direccion del token (address(0) = MATIC)
     * @param amount Cantidad a retirar
     */
    function emergencyWithdraw(
        address token,
        uint256 amount
    ) external onlyRole(DEFAULT_ADMIN_ROLE) nonReentrant {
        if (token == address(0)) {
            // MATIC nativo
            uint256 maxWithdraw = address(this).balance - totalUnclaimedDividends;
            require(amount <= maxWithdraw, "Cannot withdraw unclaimed dividends");
            (bool sent, ) = payable(treasuryAddress).call{value: amount}("");
            require(sent, "Failed to send");
        } else {
            IERC20(token).safeTransfer(treasuryAddress, amount);
        }
        emit EmergencyWithdraw(token, amount);
    }

    /**
     * @notice Pausa el contrato (solo DEFAULT_ADMIN_ROLE)
     */
    function pause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _pause();
    }

    /**
     * @notice Reanuda el contrato (solo DEFAULT_ADMIN_ROLE)
     */
    function unpause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _unpause();
    }

    /**
     * @notice Recibir MATIC (para depositNative)
     */
    receive() external payable {
        // Solo aceptar MATIC si no es un deposito de dividendos
        // Los depositos deben hacerse via depositNative()
    }
}

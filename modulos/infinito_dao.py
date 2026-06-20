"""
INFINITO DAO — Core Tokenomics Engine
======================================
Precisión decimal absoluta para cálculos de herencia y distribución.
Núcleo del Proyecto Infinito.

Autor: Romny (El Joker) + Buffy (Codebuff AI)
Versión: 1.0.0
"""

from decimal import Decimal, getcontext, ROUND_HALF_DOWN
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import time

# Configurar precisión financiera: 28 decimales
getcontext().prec = 28
getcontext().rounding = ROUND_HALF_DOWN


class BeneficiaryRole(Enum):
    """Roles dentro del ecosistema Infinito DAO."""
    PADRES = "padres_vitalicio"
    JOKER = "joker_arquitecto"
    HEREDERO = "heredero"
    INVERSOR = "inversor"
    MIEMBRO = "miembro"


@dataclass
class Beneficiary:
    """Representa un beneficiario dentro del DAO."""
    address: str
    name: str
    role: BeneficiaryRole
    tokens: Decimal = Decimal('0')
    locked_tokens: Decimal = Decimal('0')
    contributions: List[Dict] = field(default_factory=list)
    stake_amount: Decimal = Decimal('0')
    last_dividend_claim: float = 0.0

    def total_balance(self) -> Decimal:
        """Balance total (liberados + locked)."""
        return self.tokens + self.locked_tokens

    def voting_power(self) -> Decimal:
        """Poder de voto basado en tokens no locked."""
        return self.tokens


class InfinitoDAO:
    """
    Clase principal del DAO Infinito.
    Gestiona la tokenización, distribución, aportes y dividendos.
    """

    # Constantes de la DAO
    TOTAL_SUPPLY = Decimal('1000000')  # 1,000,000 TI
    PRECISION = Decimal('0.00000001')

    # Distribución inicial
    PADRES_PCT = Decimal('0.51')    # 51%
    JOKER_PCT = Decimal('0.35')     # 35%
    POOL_PCT = Decimal('0.14')      # 14%

    # Vesting
    JOKER_VESTING_CLIFF = 180       # 6 meses en días
    JOKER_VESTING_TOTAL = 730       # 2 años en días

    # Treasury
    TREASURY_SPLIT = {
        'tesoreria_dao': Decimal('0.70'),   # 70% a tesorería
        'gas_operations': Decimal('0.20'),  # 20% para gas y ops
        'airdrops': Decimal('0.10'),        # 10% airdrops a stakers
    }

    # Porcentaje de profit esperado en caza de ballenas (0.5%-5%)
    WHALE_PROFIT_PCT = Decimal('0.02')  # 2% por defecto (conservador)

    def __init__(self, property_value_usd: Decimal = Decimal('103000'), owner_address: str = "0xJOKER_MAIN"):
        """
        Inicializa la DAO con la propiedad valorada.

        Args:
            property_value_usd: Valor de mercado de la propiedad en USD.
                               Default: $103,000 (casa en Villa Faro)
            owner_address: Dirección del Joker/Arquitecto con permisos de administración.
        """
        self.owner_address = owner_address
        self.property_value = property_value_usd
        self.ledger: Dict[str, Beneficiary] = {}
        self.pool_herederos = self.TOTAL_SUPPLY * self.POOL_PCT
        self.gas_treasury = Decimal('0')
        self.dao_treasury = Decimal('0')
        self.total_distributed = Decimal('0')
        self.creation_timestamp = time.time()
        self.last_vesting_claim_timestamp = self.creation_timestamp
        self.contribution_log: List[Dict] = []

        # Inicializar beneficiarios principales
        self._init_default_beneficiaries()

    def _init_default_beneficiaries(self):
        """Configura los beneficiarios iniciales con su distribución base."""
        padres_tokens = (self.TOTAL_SUPPLY * self.PADRES_PCT).quantize(
            Decimal('0.00000001')
        )
        joker_tokens = (self.TOTAL_SUPPLY * self.JOKER_PCT).quantize(
            Decimal('0.00000001')
        )

        self.add_beneficiary(
            address="0xPADRES_MULTISIG",
            name="Ramón & Nicolasa",
            role=BeneficiaryRole.PADRES,
            tokens=padres_tokens,
            locked_tokens=Decimal('0')
        )

        self.add_beneficiary(
            address="0xJOKER_MAIN",
            name="Romny (Joker)",
            role=BeneficiaryRole.JOKER,
            tokens=joker_tokens * Decimal('0.35'),  # 35% inmediato
            locked_tokens=joker_tokens * Decimal('0.65')  # 65% en vesting
        )

        # El pool de herederos se mantiene en reserva
        self.total_distributed = padres_tokens + joker_tokens

    def add_beneficiary(
        self,
        address: str,
        name: str,
        role: BeneficiaryRole,
        tokens: Decimal = Decimal('0'),
        locked_tokens: Decimal = Decimal('0')
    ) -> bool:
        """Agrega un nuevo beneficiario al ledger."""
        if address in self.ledger:
            return False

        self.ledger[address] = Beneficiary(
            address=address,
            name=name,
            role=role,
            tokens=tokens,
            locked_tokens=locked_tokens
        )
        return True

    def distribute_from_pool(
        self,
        beneficiary_address: str,
        amount_tokens: Decimal,
        reason: str,
        caller_address: Optional[str] = None
    ) -> Dict:
        """
        Distribuye tokens del Pool de Herederos a un beneficiario.
        Solo el Joker (owner_address) puede ejecutar esta función.

        Args:
            beneficiary_address: Dirección del beneficiario
            amount_tokens: Cantidad de tokens a distribuir
            reason: Razón de la distribución
            caller_address: Dirección del que llama (para verificación de permisos)

        Returns:
            Dict con el resultado de la operación
        """
        # Verificación de permisos: solo el Joker puede distribuir del pool
        if caller_address and caller_address != self.owner_address:
            return {
                'success': False,
                'error': f'Unauthorized: Only owner ({self.owner_address}) can distribute from pool'
            }

        if amount_tokens <= 0:
            return {'success': False, 'error': 'Amount must be positive'}

        if amount_tokens > self.pool_herederos:
            return {
                'success': False,
                'error': f'Insufficient pool. Available: {self.pool_herederos} TI'
            }

        if beneficiary_address not in self.ledger:
            return {'success': False, 'error': 'Beneficiary not found'}

        self.pool_herederos -= amount_tokens
        self.ledger[beneficiary_address].tokens += amount_tokens

        entry = {
            'timestamp': time.time(),
            'type': 'pool_distribution',
            'beneficiary': beneficiary_address,
            'amount': str(amount_tokens),
            'reason': reason,
            'pool_remaining': str(self.pool_herederos)
        }
        self.contribution_log.append(entry)

        return {
            'success': True,
            'amount_distributed': str(amount_tokens),
            'pool_remaining': str(self.pool_herederos),
            'new_balance': str(self.ledger[beneficiary_address].tokens)
        }

    def apply_contribution(
        self,
        beneficiary_address: str,
        contribution_usd: Decimal,
        dilution_factor: Decimal = Decimal('1.0'),
        description: str = ""
    ) -> Dict:
        """
        Aplica una contribución (monetaria o valorizada) al sistema.

        Usa la fórmula:
        NewShare = CurrentShare + (Contribution / TotalAssetValue) × DilutionFactor

        Args:
            beneficiary_address: Dirección del beneficiario
            contribution_usd: Valor de la contribución en USD
            dilution_factor: Factor de dilución (0.5 - 2.0, default 1.0)
            description: Descripción de la contribución

        Returns:
            Dict con el resultado del cálculo
        """
        if contribution_usd <= 0:
            return {'success': False, 'error': 'Contribution must be positive'}

        if beneficiary_address not in self.ledger:
            return {'success': False, 'error': 'Beneficiary not found'}

        if dilution_factor < Decimal('0.5') or dilution_factor > Decimal('2.0'):
            return {
                'success': False,
                'error': 'Dilution factor must be between 0.5 and 2.0'
            }

        # Actualizar valor de la propiedad con la contribución
        self.property_value += contribution_usd

        # Calcular nuevos tokens
        tokens_earned = (
            (contribution_usd / self.property_value)
            * self.TOTAL_SUPPLY
            * dilution_factor
        ).quantize(Decimal('0.00000001'))

        self.ledger[beneficiary_address].tokens += tokens_earned
        self.ledger[beneficiary_address].contributions.append({
            'timestamp': time.time(),
            'amount_usd': str(contribution_usd),
            'tokens_earned': str(tokens_earned),
            'description': description
        })
        self.total_distributed += tokens_earned

        entry = {
            'timestamp': time.time(),
            'type': 'contribution',
            'beneficiary': beneficiary_address,
            'contribution_usd': str(contribution_usd),
            'tokens_earned': str(tokens_earned),
            'dilution_factor': str(dilution_factor)
        }
        self.contribution_log.append(entry)

        return {
            'success': True,
            'tokens_earned': str(tokens_earned),
            'new_total_supply': str(self.total_distributed),
            'new_property_value': str(self.property_value),
            'percentage': str(
                (self.ledger[beneficiary_address].tokens / self.total_distributed * 100)
                if self.total_distributed > 0 else Decimal('0')
            )
        }

    def claim_vested_tokens(self, address: str) -> Dict:
        """
        Reclama tokens liberados por vesting (aplica al Joker).
        Trackea el último reclamo para evitar double-claiming.

        Returns:
            Dict con los tokens liberados
        """
        if address not in self.ledger:
            return {'success': False, 'error': 'Beneficiary not found'}

        beneficiary = self.ledger[address]
        if beneficiary.role != BeneficiaryRole.JOKER:
            return {'success': False, 'error': 'Only Joker has vesting schedule'}

        now = time.time()
        elapsed_days = (now - self.creation_timestamp) / 86400

        if elapsed_days < self.JOKER_VESTING_CLIFF:
            return {
                'success': False,
                'error': f'Cliff not met. {self.JOKER_VESTING_CLIFF - elapsed_days:.0f} days remaining'
            }

        if beneficiary.locked_tokens <= 0:
            return {'success': False, 'error': 'No locked tokens to claim'}

        # Calcular días desde el último reclamo (o desde el cliff)
        last_claim = max(self.last_vesting_claim_timestamp, self.creation_timestamp + self.JOKER_VESTING_CLIFF * 86400)
        days_since_last_claim = (now - last_claim) / 86400

        if days_since_last_claim < 1:
            return {
                'success': False,
                'error': f'Must wait at least 1 day between claims. {days_since_last_claim:.1f} days since last claim'
            }

        # Proporción: días desde último reclamo / total período vesting post-cliff
        total_vesting_days = self.JOKER_VESTING_TOTAL - self.JOKER_VESTING_CLIFF
        claimable_pct = min(
            Decimal('1.0'),
            Decimal(str(days_since_last_claim)) / Decimal(str(total_vesting_days))
        )

        # Lo que se reclama ahora es el proportion de locked_tokens
        claimable = (beneficiary.locked_tokens * claimable_pct).quantize(
            Decimal('0.00000001')
        )

        # Actualizar timestamp
        self.last_vesting_claim_timestamp = now

        if claimable > 0:
            beneficiary.tokens += claimable
            beneficiary.locked_tokens -= claimable
            self.total_distributed += claimable  # track as distributed

        return {
            'success': True,
            'claimed': str(claimable),
            'remaining_locked': str(beneficiary.locked_tokens),
            'claimable_pct': str(claimable_pct * 100) + '%'
        }

    def distribute_dividends(
        self,
        total_profit_usd: Decimal,
        source: str = "seo_content"
    ) -> Dict:
        """
        Distribuye ganancias entre los tenedores de tokens según la
        estructura de treasury split.

        Args:
            total_profit_usd: Ganancia total a distribuir en USD
            source: Fuente de la ganancia (seo, mev, etc.)

        Returns:
            Dict con la distribución
        """
        to_treasury = (total_profit_usd * self.TREASURY_SPLIT['tesoreria_dao']).quantize(
            Decimal('0.01')
        )
        to_gas = (total_profit_usd * self.TREASURY_SPLIT['gas_operations']).quantize(
            Decimal('0.01')
        )
        to_airdrops = (total_profit_usd * self.TREASURY_SPLIT['airdrops']).quantize(
            Decimal('0.01')
        )

        self.dao_treasury += to_treasury
        self.gas_treasury += to_gas

        entry = {
            'timestamp': time.time(),
            'type': 'dividend_distribution',
            'source': source,
            'total': str(total_profit_usd),
            'to_treasury': str(to_treasury),
            'to_gas': str(to_gas),
            'to_airdrops': str(to_airdrops)
        }
        self.contribution_log.append(entry)

        return {
            'success': True,
            'dao_treasury': str(self.dao_treasury),
            'gas_treasury': str(self.gas_treasury),
            'airdrops_pool': str(to_airdrops)
        }

    def calculate_whale_share(
        self,
        whale_value_usd: Decimal,
        stake_percentage: Decimal,
        profit_pct: Optional[Decimal] = None
    ) -> Dict:
        """
        Calcula la participación de un staker en una caza de ballena.
        El profit_pct ahora es configurable y usa WHALE_PROFIT_PCT por defecto
        para mantener consistencia con whale_watcher.py.

        Args:
            whale_value_usd: Valor de la ballena capturada en USD
            stake_percentage: Porcentaje del staker en el pool total (0-1)
            profit_pct: Porcentaje de profit sobre el valor (default: 2%)

        Returns:
            Dict con el desglose de la ganancia
        """
        if profit_pct is None:
            profit_pct = self.WHALE_PROFIT_PCT

        if profit_pct < Decimal('0.001') or profit_pct > Decimal('0.10'):
            return {'success': False, 'error': 'Profit % must be between 0.1% and 10%'}

        gross_profit = (whale_value_usd * profit_pct).quantize(
            Decimal('0.01')
        )

        # Costos: gas (~0.5%) + bribes (~1%) + flash loan fee (~0.09%)
        costs_pct = Decimal('0.0159')  # 1.59%
        costs = (whale_value_usd * costs_pct).quantize(Decimal('0.01'))

        net_profit = gross_profit - costs

        # Distribución: 70% tesorería, 20% ops, 10% airdrops
        staker_share = (
            net_profit * self.TREASURY_SPLIT['airdrops'] * stake_percentage
        ).quantize(Decimal('0.01'))

        return {
            'whale_value': str(whale_value_usd),
            'profit_pct': str(profit_pct * 100) + '%',
            'gross_profit': str(gross_profit),
            'costs': str(costs),
            'net_profit': str(net_profit),
            'stake_percentage': str(stake_percentage * 100) + '%',
            'staker_payout': str(staker_share)
        }

    def get_portfolio(self, address: str) -> Optional[Dict]:
        """Obtiene el portafolio completo de un beneficiario."""
        if address not in self.ledger:
            return None

        b = self.ledger[address]
        total_dist = self.total_distributed if self.total_distributed > 0 else Decimal('1')

        return {
            'address': b.address,
            'name': b.name,
            'role': b.role.value,
            'tokens': str(b.tokens),
            'locked_tokens': str(b.locked_tokens),
            'total_balance': str(b.total_balance()),
            'percentage': str(
                (b.tokens / total_dist * 100).quantize(Decimal('0.0001'))
            ),
            'voting_power': str(b.voting_power()),
            'stake_amount': str(b.stake_amount),
            'contributions_count': len(b.contributions)
        }

    def get_summary(self) -> Dict:
        """Obtiene un resumen completo del estado de la DAO."""
        return {
            'property_value_usd': str(self.property_value),
            'total_supply': str(self.TOTAL_SUPPLY),
            'total_distributed': str(self.total_distributed),
            'pool_herederos_remaining': str(self.pool_herederos),
            'dao_treasury_usd': str(self.dao_treasury),
            'gas_treasury_usd': str(self.gas_treasury),
            'beneficiary_count': len(self.ledger),
            'contributions_count': len(self.contribution_log),
            'owner_address': self.owner_address,
            'vesting_status': {
                'cliff_days': self.JOKER_VESTING_CLIFF,
                'total_vesting_days': self.JOKER_VESTING_TOTAL,
                'last_claim_timestamp': self.last_vesting_claim_timestamp,
                'creation_timestamp': self.creation_timestamp
            },
            'timestamp': time.time()
        }

    def export_ledger(self, filepath: str = "dao_ledger.json"):
        """Exporta el ledger completo a un archivo JSON."""
        data = {
            'property_value': str(self.property_value),
            'pool_herederos': str(self.pool_herederos),
            'total_distributed': str(self.total_distributed),
            'dao_treasury': str(self.dao_treasury),
            'gas_treasury': str(self.gas_treasury),
            'beneficiaries': {
                addr: {
                    'name': b.name,
                    'role': b.role.value,
                    'tokens': str(b.tokens),
                    'locked_tokens': str(b.locked_tokens),
                    'stake_amount': str(b.stake_amount),
                    'contributions': b.contributions
                }
                for addr, b in self.ledger.items()
            },
            'contribution_log': self.contribution_log[-100:],  # Últimas 100
            'exported_at': time.time()
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return {'success': True, 'filepath': filepath}


# =============================================
# DEMO / EJEMPLO DE USO
# =============================================
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 INFINITO DAO — Demonstration")
    print("=" * 60)

    # Inicializar DAO
    dao = InfinitoDAO(property_value_usd=Decimal('103000'))

    # Mostrar resumen inicial
    summary = dao.get_summary()
    print(f"\n📊 Estado Inicial de la DAO:")
    print(f"   Propiedad valorada en: ${summary['property_value_usd']} USD")
    print(f"   Total Supply: {summary['total_supply']} TI")
    print(f"   Pool de Herederos: {summary['pool_herederos_remaining']} TI")

    # Agregar a Reymond como heredero
    dao.add_beneficiary(
        address="0xREYMOND_WALLET",
        name="Reymond",
        role=BeneficiaryRole.HEREDERO
    )

    # Distribuir tokens del pool a Reymond por méritos
    result = dao.distribute_from_pool(
        "0xREYMOND_WALLET",
        Decimal('50000'),  # 50,000 TI
        "Aporte en gestión y cuidado de la propiedad"
    )
    print(f"\n📤 Distribución a Reymond:")
    print(f"   {result.get('amount_distributed', 'N/A')} TI distribuidos")
    print(f"   Pool restante: {result.get('pool_remaining', 'N/A')} TI")

    # Simular una contribución de Reymond (inversión en construcción)
    result = dao.apply_contribution(
        "0xREYMOND_WALLET",
        Decimal('50000'),  # $50,000 USD en construcción
        dilution_factor=Decimal('1.2'),  # Factor premium por ser pronto
        description="Inversión en construcción de segundo nivel"
    )
    print(f"\n🏗️ Contribución de Reymond:")
    print(f"   Tokens ganados: {result.get('tokens_earned', 'N/A')} TI")
    print(f"   Nuevo valor propiedad: ${result.get('new_property_value', 'N/A')}")

    # Mostrar portafolios
    for addr in ['0xJOKER_MAIN', '0xREYMOND_WALLET']:
        portfolio = dao.get_portfolio(addr)
        if portfolio:
            print(f"\n👤 {portfolio['name']} ({portfolio['role']}):")
            print(f"   Tokens: {portfolio['tokens']} TI")
            print(f"   Porcentaje: {portfolio['percentage']}%")

    # Simular una caza de ballena
    whale_share = dao.calculate_whale_share(
        whale_value_usd=Decimal('500000'),  # Ballena de $500K
        stake_percentage=Decimal('0.05')     # Staker tiene 5% del pool
    )
    print(f"\n🐋 Caza de Ballena ($500,000 USD):")
    print(f"   Profit bruto: ${whale_share['gross_profit']}")
    print(f"   Pago al staker: ${whale_share['staker_payout']}")

    print("\n" + "=" * 60)
    print("✅ DAO Operational — Sistema Listo")
    print("=" * 60)

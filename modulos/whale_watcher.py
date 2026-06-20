"""
WHALE WATCHER — MEV Detection & Flash Loan Analysis Engine
============================================================
Sistema de detección de ballenas en el mempool de Polygon,
análisis de oportunidades de arbitraje con flash loans,
y cálculo de profitability para el Proyecto Infinito.

Autor: Romny (El Joker) + Buffy (Codebuff AI)
Versión: 1.0.0
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from decimal import Decimal, getcontext, ROUND_HALF_DOWN
from enum import Enum
import json
import time
import random

getcontext().prec = 28
getcontext().rounding = ROUND_HALF_DOWN


class WhaleCategory(Enum):
    """Clasificación de ballenas según el tamaño de transacción."""
    JUVENIL = "juvenil"        # $5k - $50k
    AZUL = "azul"              # $50k - $250k
    DORADA = "dorada"          # $250k - $1M
    MITICA = "mitica"          # $1M+


@dataclass
class WhaleTransaction:
    """Representa una transacción de ballena detectada en el mempool."""
    tx_hash: str
    from_address: str
    to_address: str
    value_usd: Decimal
    gas_price_gwei: Decimal
    gas_limit: int
    category: WhaleCategory
    timestamp: float
    token_address: Optional[str] = None
    contract_interaction: Optional[str] = None
    is_flash_loan_opportunity: bool = False
    estimated_flash_loan_profit: Optional[Decimal] = None
    confidence_score: float = 0.0  # 0.0 - 1.0

    @property
    def category_emoji(self) -> str:
        return {
            WhaleCategory.JUVENIL: "🐟",
            WhaleCategory.AZUL: "🐋",
            WhaleCategory.DORADA: "🐋✨",
            WhaleCategory.MITICA: "🐋💎",
        }.get(self.category, "🐟")

    @property
    def value_formatted(self) -> str:
        if self.value_usd >= Decimal('1000000'):
            return f"${float(self.value_usd) / 1_000_000:.2f}M"
        elif self.value_usd >= Decimal('1000'):
            return f"${float(self.value_usd) / 1_000:.1f}K"
        return f"${float(self.value_usd):.2f}"


@dataclass
class FlashLoanOpportunity:
    """Oportunidad de arbitraje con flash loan."""
    whale_tx: WhaleTransaction
    dex_path: List[str]
    expected_profit_usd: Decimal
    gas_cost_usd: Decimal
    bribe_amount_usd: Decimal
    net_profit_usd: Decimal
    execution_time_estimate: float  # segundos
    risk_score: float  # 0.0 - 1.0 (mayor = más riesgoso)
    confidence: float  # 0.0 - 1.0

    @property
    def is_profitable(self) -> bool:
        return self.net_profit_usd > Decimal('0')

    @property
    def roi_percent(self) -> Decimal:
        if self.gas_cost_usd + self.bribe_amount_usd > 0:
            return (self.net_profit_usd / (self.gas_cost_usd + self.bribe_amount_usd) * 100)
        return Decimal('0')


class WhaleWatcher:
    """
    Motor de detección y análisis de ballenas en el mempool.

    Actualmente en modo simulación (testnet Polygon Amoy).
    La conexión real al mempool se activará en mainnet.
    """

    # Configuración de detección
    MIN_TRANSACTION_VALUE = Decimal('5000')  # $5,000 mínimo
    FLASH_LOAN_FEE_PCT = Decimal('0.0009')  # 0.09% fee de flash loan (Aave/Uniswap)
    BRIBES_PCT_OF_PROFIT = Decimal('0.20')  # 20% del profit va a bribes
    GAS_BUFFER = Decimal('1.2')  # 20% de buffer en gas

    # Umbrales de categoría
    JUVENIL_MIN = Decimal('5000')
    JUVENIL_MAX = Decimal('50000')
    AZUL_MIN = Decimal('50000')
    AZUL_MAX = Decimal('250000')
    DORADA_MIN = Decimal('250000')
    DORADA_MAX = Decimal('1000000')
    MITICA_MIN = Decimal('1000000')

    def __init__(self, network: str = "polygon_amoy_testnet"):
        self.network = network
        self.detected_whales: List[WhaleTransaction] = []
        self.opportunities: List[FlashLoanOpportunity] = []
        self.total_profits = Decimal('0')
        self.total_whales_detected = 0
        self.total_whales_hunted = 0
        self.is_connected = False

        # DEX paths simulados para Polygon
        self.dex_pools = {
            'quickSwap': {'fee': Decimal('0.003'), 'liquidity_score': 0.9},
            'sushiSwap': {'fee': Decimal('0.0025'), 'liquidity_score': 0.8},
            'balancer': {'fee': Decimal('0.002'), 'liquidity_score': 0.7},
            'curve': {'fee': Decimal('0.0004'), 'liquidity_score': 0.85},
        }

    def classify_whale(self, value_usd: Decimal) -> WhaleCategory:
        """Clasifica una ballena por su tamaño."""
        if value_usd >= self.MITICA_MIN:
            return WhaleCategory.MITICA
        elif value_usd >= self.DORADA_MIN:
            return WhaleCategory.DORADA
        elif value_usd >= self.AZUL_MIN:
            return WhaleCategory.AZUL
        else:
            return WhaleCategory.JUVENIL

    def detect_whale(
        self,
        tx_hash: str,
        from_addr: str,
        to_addr: str,
        value_usd: Decimal,
        gas_price_gwei: Decimal,
        gas_limit: int,
        token_address: Optional[str] = None
    ) -> Optional[WhaleTransaction]:
        """
        Analiza una transacción y la clasifica si es una ballena.

        Args:
            tx_hash: Hash de la transacción
            from_addr: Dirección de origen
            to_addr: Dirección de destino
            value_usd: Valor en USD
            gas_price_gwei: Precio del gas en Gwei
            gas_limit: Límite de gas
            token_address: Dirección del token (si aplica)

        Returns:
            WhaleTransaction si es ballena, None si no
        """
        if value_usd < self.MIN_TRANSACTION_VALUE:
            return None

        category = self.classify_whale(value_usd)
        is_flash_loan_opp = self._is_flash_loan_opportunity(
            from_addr, to_addr, value_usd
        )

        whale = WhaleTransaction(
            tx_hash=tx_hash,
            from_address=from_addr,
            to_address=to_addr,
            value_usd=value_usd.quantize(Decimal('0.01')),
            gas_price_gwei=gas_price_gwei.quantize(Decimal('0.000000001')),
            gas_limit=gas_limit,
            category=category,
            timestamp=time.time(),
            token_address=token_address,
            is_flash_loan_opportunity=is_flash_loan_opp,
            confidence_score=self._calculate_confidence(value_usd, category)
        )

        self.detected_whales.append(whale)
        self.total_whales_detected += 1

        return whale

    def _is_flash_loan_opportunity(
        self, from_addr: str, to_addr: str, value_usd: Decimal
    ) -> bool:
        """
        Determina si una transacción es oportunidad de flash loan.
        En producción, esto analiza el contrato y el mempool.
        """
        # Simulación: ~30% de las transacciones grandes son oportunidades
        return value_usd >= self.AZUL_MIN and random.random() < 0.3

    def _calculate_confidence(
        self, value_usd: Decimal, category: WhaleCategory
    ) -> float:
        """Calcula nivel de confianza en la detección."""
        base = 0.7
        if category == WhaleCategory.MITICA:
            base += 0.2
        elif category == WhaleCategory.DORADA:
            base += 0.15
        elif category == WhaleCategory.AZUL:
            base += 0.1

        # A mayor valor, mayor confianza
        value_factor = min(0.1, float(value_usd / Decimal('1000000')))
        return min(1.0, base + value_factor)

    def analyze_flash_loan_opportunity(
        self, whale: WhaleTransaction
    ) -> Optional[FlashLoanOpportunity]:
        """
        Analiza una ballena como oportunidad de flash loan.

        Calcula:
        - Profit esperado del arbitraje
        - Costo de gas
        - Bribe a validadores (Flashbots)
        - Profit neto

        Args:
            whale: Transacción de ballena detectada

        Returns:
            FlashLoanOpportunity o None si no es rentable
        """
        if not whale.is_flash_loan_opportunity:
            return None

        # Simular ruta DEX (en producción sería consulta a oráculos)
        dex_path = self._simulate_dex_path(whale)
        if not dex_path:
            return None

        # Profit esperado: ~0.5-3% del valor de la ballena
        profit_pct = Decimal(str(random.uniform(0.005, 0.03)))
        expected_profit = (whale.value_usd * profit_pct).quantize(Decimal('0.01'))

        # Costos
        gas_cost = self._estimate_gas_cost(whale)
        flash_loan_fee = (whale.value_usd * self.FLASH_LOAN_FEE_PCT).quantize(
            Decimal('0.01')
        )
        total_gas = gas_cost + flash_loan_fee

        # Bribe a validadores (20% del profit estimado)
        bribe = (expected_profit * self.BRIBES_PCT_OF_PROFIT).quantize(
            Decimal('0.01')
        )

        # Profit neto
        net_profit = (expected_profit - total_gas - bribe).quantize(
            Decimal('0.01')
        )

        # Risk score
        risk = self._calculate_risk_score(whale, expected_profit)

        opportunity = FlashLoanOpportunity(
            whale_tx=whale,
            dex_path=dex_path,
            expected_profit_usd=expected_profit,
            gas_cost_usd=total_gas,
            bribe_amount_usd=bribe,
            net_profit_usd=net_profit,
            execution_time_estimate=random.uniform(0.5, 3.0),
            risk_score=risk,
            confidence=self._calculate_opportunity_confidence(risk, net_profit)
        )

        self.opportunities.append(opportunity)

        if net_profit > 0:
            self.total_whales_hunted += 1
            self.total_profits += net_profit

        return opportunity

    def _simulate_dex_path(self, whale: WhaleTransaction) -> List[str]:
        """
        Simula una ruta de arbitraje entre DEXs.
        En producción, consulta precios en tiempo real.
        """
        # Simular si hay oportunidad de arbitraje (30% de probabilidad)
        if random.random() < 0.3:
            dex_names = list(self.dex_pools.keys())
            # Ruta típica: Comprar en DEX A, vender en DEX B
            return random.sample(dex_names, 2)
        return []

    def _estimate_gas_cost(self, whale: WhaleTransaction) -> Decimal:
        """Estima el costo de gas de la transacción."""
        # ~300,000 gas para flash loan complejo
        estimated_gas = Decimal('300000')
        # Precio de gas en Polygon: ~30-100 Gwei
        gas_price_gwei = Decimal(str(random.uniform(30, 100)))
        # 1 Gwei = 1e-9 MATIC, 1 MATIC ~ $0.70 USD
        matic_price = Decimal('0.70')

        total_gas_cost = (
            estimated_gas
            * gas_price_gwei
            * Decimal('1e-9')
            * matic_price
            * self.GAS_BUFFER
        ).quantize(Decimal('0.01'))

        return total_gas_cost

    def _calculate_risk_score(
        self, whale: WhaleTransaction, expected_profit: Decimal
    ) -> float:
        """
        Calcula el nivel de riesgo de la operación.

        Factores:
        - Tamaño de la ballena (mayor ballena = menor riesgo relativo)
        - Profit esperado vs capital
        - Complejidad de la ruta DEX
        """
        risk = 0.3  # Base risk

        # Ballenas más grandes = menos riesgo (más liquidez)
        if whale.category == WhaleCategory.MITICA:
            risk -= 0.1
        elif whale.category == WhaleCategory.JUVENIL:
            risk += 0.1

        # Profit pequeño = más riesgo relativo
        profit_ratio = float(expected_profit / whale.value_usd)
        if profit_ratio < 0.01:
            risk += 0.2
        elif profit_ratio < 0.02:
            risk += 0.1

        return min(1.0, max(0.0, risk))

    def _calculate_opportunity_confidence(
        self, risk: float, net_profit: Decimal
    ) -> float:
        """Calcula confianza en la oportunidad."""
        base = 0.6
        if net_profit > 0:
            base += 0.2
        if risk < 0.4:
            base += 0.1
        return min(1.0, base)

    def simulate_mempool_scan(self, count: int = 50) -> List[WhaleTransaction]:
        """
        Simula el escaneo del mempool generando transacciones aleatorias.
        Útil para pruebas y demostraciones.

        Args:
            count: Número de transacciones a simular

        Returns:
            Lista de ballenas detectadas
        """
        detected = []
        addresses = [
            f"0x{''.join(random.choices('0123456789abcdef', k=40))}"
            for _ in range(20)
        ]

        for _ in range(count):
            value = Decimal(str(random.uniform(100, 500000)))
            tx = self.detect_whale(
                tx_hash=f"0x{''.join(random.choices('0123456789abcdef', k=64))}",
                from_addr=random.choice(addresses),
                to_addr=random.choice(addresses + [None]),
                value_usd=value,
                gas_price_gwei=Decimal(str(random.uniform(30, 150))),
                gas_limit=random.randint(50000, 500000),
                token_address=random.choice([
                    None,
                    "0x7ceb23fd6bc0add59e62ac25578270cff1b9f619",  # WETH on Polygon
                    "0x2791bca1f2de4661ed88a30c99a7a9449aa84174",  # USDC on Polygon
                    "0xc2132d05d31c914a87c6611c10748aeb04b58e8f",  # USDT on Polygon
                ])
            )
            if tx:
                detected.append(tx)

        return detected

    def get_whale_summary(self) -> Dict:
        """Resumen de todas las ballenas detectadas y oportunidades."""
        categories = {}
        for cat in WhaleCategory:
            cats = [w for w in self.detected_whales if w.category == cat]
            if cats:
                categories[cat.value] = {
                    'count': len(cats),
                    'total_value': float(sum(
                        w.value_usd for w in cats
                    )),
                    'avg_value': float(sum(
                        w.value_usd for w in cats
                    )) / len(cats),
                }

        profitable_opps = [
            o for o in self.opportunities if o.is_profitable
        ]

        return {
            'network': self.network,
            'total_whales_detected': self.total_whales_detected,
            'total_whales_hunted': self.total_whales_hunted,
            'total_profits_usd': float(self.total_profits),
            'total_opportunities': len(self.opportunities),
            'profitable_opportunities': len(profitable_opps),
            'categories': categories,
            'top_opportunities': [
                {
                    'value': float(o.whale_tx.value_usd),
                    'net_profit': float(o.net_profit_usd),
                    'roi': float(o.roi_percent),
                    'risk': o.risk_score,
                }
                for o in sorted(
                    self.opportunities,
                    key=lambda x: x.net_profit_usd,
                    reverse=True
                )[:5]
                if o.net_profit_usd > 0
            ]
        }

    def export_report(self, filepath: str = "whale_report.json"):
        """Exporta el reporte de ballenas a JSON."""
        data = {
            'summary': self.get_whale_summary(),
            'recent_whales': [
                {
                    'tx_hash': w.tx_hash,
                    'value': float(w.value_usd),
                    'category': w.category.value,
                    'is_opportunity': w.is_flash_loan_opportunity,
                    'timestamp': w.timestamp,
                }
                for w in self.detected_whales[-20:]
            ],
            'generated_at': time.time()
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return {'success': True, 'filepath': filepath}


# =============================================
# DEMO / EJEMPLO DE USO
# =============================================
if __name__ == "__main__":
    print("=" * 60)
    print("🐋 WHALE WATCHER — Mempool Scanner & MEV Engine")
    print("=" * 60)

    watcher = WhaleWatcher(network="polygon_amoy_testnet")

    # Simular escaneo de mempool
    print("\n🔍 Escaneando mempool...")
    whales = watcher.simulate_mempool_scan(count=100)
    print(f"Ballenas detectadas: {len(whales)}")

    # Mostrar ballenas por categoría
    for cat in WhaleCategory:
        count = len([w for w in whales if w.category == cat])
        if count > 0:
            total_val = sum(w.value_usd for w in whales if w.category == cat)
            print(f"  {cat.value}: {count} ballenas | Total: ${float(total_val):,.2f}")

    # Analizar oportunidades de flash loan
    print("\n💎 Analizando oportunidades de flash loan...")
    opportunities_found = 0
    for whale in whales:
        if whale.is_flash_loan_opportunity:
            opp = watcher.analyze_flash_loan_opportunity(whale)
            if opp and opp.is_profitable:
                opportunities_found += 1
                print(f"\n  🐋 {whale.category_emoji} {whale.value_formatted}")
                print(f"     Profit neto: ${float(opp.net_profit_usd):,.2f}")
                print(f"     ROI: {float(opp.roi_percent):.1f}%")
                print(f"     Riesgo: {opp.risk_score:.2f}")

    # Resumen
    summary = watcher.get_whale_summary()
    print(f"\n📊 Resumen de Caza:")
    print(f"   Ballenas detectadas: {summary['total_whales_detected']}")
    print(f"   Oportunidades rentables: {summary['profitable_opportunities']}")
    print(f"   Profit total simulado: ${summary['total_profits_usd']:,.2f}")

    print("\n" + "=" * 60)
    print("✅ Whale Watcher — Sistema Listo")
    print("=" * 60)

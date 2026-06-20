"""
TREASURY FLOW — Gestión de Flujo de Tesorería
===============================================
Sistema centralizado de contabilidad que registra todos los ingresos,
distribuye dividendos, maneja el gas treasury, y genera reportes
de flujo de caja para el Proyecto Infinito.

Autor: Romny (El Joker) + Buffy (Codebuff AI)
Versión: 1.0.0
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from decimal import Decimal, getcontext, ROUND_HALF_DOWN
from enum import Enum
import json
import time

getcontext().prec = 28
getcontext().rounding = ROUND_HALF_DOWN


class IncomeSource(Enum):
    """Fuentes de ingreso del sistema."""
    SEO_CONTENT = "seo_content"
    MEV_WHALE = "mev_whale"
    FLASH_LOAN = "flash_loan"
    AIRDROP = "airdrop"
    CONTRIBUTION = "contribution"
    STAKING_REWARD = "staking_reward"
    OTHER = "other"


class ExpenseCategory(Enum):
    """Categorías de gastos del sistema."""
    GAS_FEE = "gas_fee"
    BRIBES = "bribes"
    VPS_HOSTING = "vps_hosting"
    TOOLS = "tools"
    DEVELOPMENT = "development"
    MARKETING = "marketing"
    TAXES = "taxes"
    OTHER = "other"


@dataclass
class Transaction:
    """Registro de una transacción financiera del sistema."""
    id: str
    timestamp: float
    amount_usd: Decimal
    source: Optional[IncomeSource] = None
    expense_category: Optional[ExpenseCategory] = None
    description: str = ""
    from_address: Optional[str] = None
    to_address: Optional[str] = None
    tx_hash: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


@dataclass
class WeeklyReport:
    """Reporte semanal de flujo de caja."""
    week_number: int
    start_date: float
    end_date: float
    total_income: Decimal
    total_expenses: Decimal
    net_profit: Decimal
    income_by_source: Dict[str, Decimal]
    expenses_by_category: Dict[str, Decimal]
    dao_treasury_balance: Decimal
    gas_treasury_balance: Decimal
    distribution_to_family: Decimal


class TreasuryFlow:
    """
    Sistema de contabilidad y gestión de flujo de tesorería.
    """

    # Distribución de ingresos
    DAO_TREASURY_PCT = Decimal('0.70')       # 70%
    GAS_OPS_PCT = Decimal('0.20')             # 20%
    FAMILY_AIRDROP_PCT = Decimal('0.10')      # 10%

    # Fondos de emergencia (del treasury DAO)
    EMERGENCY_FUND_PCT = Decimal('0.20')      # 20% del treasury
    REINVESTMENT_PCT = Decimal('0.50')        # 50% para reinversión
    DISTRIBUTABLE_PCT = Decimal('0.30')       # 30% distribuible

    def __init__(self, initial_treasury: Decimal = Decimal('0')):
        self.transactions: List[Transaction] = []
        self.dao_treasury = initial_treasury
        self.gas_treasury = Decimal('0')
        self.emergency_fund = Decimal('0')
        self.total_income = Decimal('0')
        self.total_expenses = Decimal('0')
        self.total_distributed = Decimal('0')
        self.last_week_number = 0
        self.week_start_time = time.time()

    def record_income(
        self,
        amount_usd: Decimal,
        source: IncomeSource,
        description: str = "",
        **metadata
    ) -> Transaction:
        """
        Registra un ingreso al sistema.

        Args:
            amount_usd: Monto en USD
            source: Fuente del ingreso
            description: Descripción opcional
            metadata: Metadatos adicionales

        Returns:
            Transaction registrada
        """
        tx = Transaction(
            id=f"INC-{len(self.transactions) + 1}-{int(time.time())}",
            timestamp=time.time(),
            amount_usd=amount_usd.quantize(Decimal('0.01')),
            source=source,
            description=description,
            metadata=metadata
        )
        self.transactions.append(tx)
        self.total_income += amount_usd

        # Aplicar distribución automática
        self._auto_distribute(tx)

        return tx

    def record_expense(
        self,
        amount_usd: Decimal,
        category: ExpenseCategory,
        description: str = "",
        **metadata
    ) -> Transaction:
        """
        Registra un gasto del sistema.

        Args:
            amount_usd: Monto en USD
            category: Categoría del gasto
            description: Descripción opcional
            metadata: Metadatos adicionales

        Returns:
            Transaction registrada
        """
        tx = Transaction(
            id=f"EXP-{len(self.transactions) + 1}-{int(time.time())}",
            timestamp=time.time(),
            amount_usd=amount_usd.quantize(Decimal('0.01')),
            expense_category=category,
            description=description,
            metadata=metadata
        )
        self.transactions.append(tx)
        self.total_expenses += amount_usd

        # Si es gasto de gas, usar gas treasury primero
        if category in (ExpenseCategory.GAS_FEE, ExpenseCategory.BRIBES):
            if self.gas_treasury >= amount_usd:
                self.gas_treasury -= amount_usd
            else:
                # Si no hay suficiente gas, usar DAO treasury
                self.dao_treasury -= amount_usd

        return tx

    def _auto_distribute(self, income_tx: Transaction):
        """
        Distribuye automáticamente un ingreso según las proporciones definidas.
        """
        amount = income_tx.amount_usd

        to_dao = (amount * self.DAO_TREASURY_PCT).quantize(Decimal('0.01'))
        to_gas = (amount * self.GAS_OPS_PCT).quantize(Decimal('0.01'))
        to_family = (amount * self.FAMILY_AIRDROP_PCT).quantize(Decimal('0.01'))

        # Redondear para evitar pérdidas
        total_distributed = to_dao + to_gas + to_family
        if total_distributed > amount:
            diff = total_distributed - amount
            to_dao -= diff
        elif total_distributed < amount:
            diff = amount - total_distributed
            to_dao += diff

        # Actualizar treasuries
        self.dao_treasury += to_dao
        self.gas_treasury += to_gas
        self.total_distributed += to_family + to_gas

        # Del treasury DAO, reservar para emergencias
        emergency = (to_dao * self.EMERGENCY_FUND_PCT).quantize(Decimal('0.01'))
        self.emergency_fund += emergency

    def distribute_to_family(
        self,
        member_address: str,
        percentage: Decimal,  # 0-1
        reason: str = "airdop_distribution"
    ) -> Dict:
        """
        Distribuye ganancias a un miembro de la familia según su % de tokens.

        Args:
            member_address: Dirección del miembro
            percentage: Porcentaje del pool familiar que le corresponde (0-1)
            reason: Razón de la distribución

        Returns:
            Dict con los detalles de la distribución
        """
        # El pool familiar es el 10% de los ingresos
        available = self.total_income * self.FAMILY_AIRDROP_PCT

        # Menos lo ya distribuido
        already_distributed = Decimal('0')
        for tx in self.transactions:
            if tx.metadata.get('type') == 'family_distribution':
                already_distributed += tx.amount_usd

        remaining = available - already_distributed

        if remaining <= 0:
            return {
                'success': False,
                'error': 'No remaining distributable funds this period'
            }

        amount = (remaining * percentage).quantize(Decimal('0.01'))

        tx = Transaction(
            id=f"DIV-{len(self.transactions) + 1}-{int(time.time())}",
            timestamp=time.time(),
            amount_usd=amount,
            source=IncomeSource.STAKING_REWARD,
            description=f"Family distribution to {member_address}: {reason}",
            to_address=member_address,
            metadata={'type': 'family_distribution', 'reason': reason}
        )
        self.transactions.append(tx)
        self.total_distributed += amount

        return {
            'success': True,
            'amount': str(amount),
            'member': member_address,
            'percentage': str(percentage * 100) + '%',
            'remaining_pool': str(remaining - amount)
        }

    def get_balance_sheet(self) -> Dict:
        """Genera un balance general del sistema."""
        return {
            'total_income': float(self.total_income),
            'total_expenses': float(self.total_expenses),
            'net_profit': float(self.total_income - self.total_expenses),
            'dao_treasury': float(self.dao_treasury),
            'gas_treasury': float(self.gas_treasury),
            'emergency_fund': float(self.emergency_fund),
            'total_distributed': float(self.total_distributed),
            'transaction_count': len(self.transactions),
        }

    def get_weekly_report(self) -> WeeklyReport:
        """Genera un reporte semanal de flujo de caja."""
        now = time.time()
        week_seconds = 7 * 24 * 60 * 60

        # Filtrar transacciones de esta semana
        week_txs = [
            t for t in self.transactions
            if t.timestamp >= self.week_start_time
            and t.timestamp <= now
        ]

        income_by_source: Dict[str, Decimal] = {}
        expenses_by_category: Dict[str, Decimal] = {}
        total_income = Decimal('0')
        total_expenses = Decimal('0')

        for tx in week_txs:
            if tx.source:
                key = tx.source.value
                income_by_source[key] = income_by_source.get(key, Decimal('0')) + tx.amount_usd
                total_income += tx.amount_usd
            elif tx.expense_category:
                key = tx.expense_category.value
                expenses_by_category[key] = expenses_by_category.get(key, Decimal('0')) + tx.amount_usd
                total_expenses += tx.amount_usd

        self.last_week_number += 1
        report = WeeklyReport(
            week_number=self.last_week_number,
            start_date=self.week_start_time,
            end_date=now,
            total_income=total_income,
            total_expenses=total_expenses,
            net_profit=total_income - total_expenses,
            income_by_source={k: float(v) for k, v in income_by_source.items()},
            expenses_by_category={k: float(v) for k, v in expenses_by_category.items()},
            dao_treasury_balance=self.dao_treasury,
            gas_treasury_balance=self.gas_treasury,
            distribution_to_family=self.total_distributed
        )

        # Reset para próxima semana
        self.week_start_time = now

        return report

    def get_profitability_metrics(self, days: int = 30) -> Dict:
        """Calcula métricas de rentabilidad para un período."""
        cutoff = time.time() - (days * 86400)
        period_txs = [t for t in self.transactions if t.timestamp >= cutoff]

        income = sum(t.amount_usd for t in period_txs if t.source)
        expenses = sum(t.amount_usd for t in period_txs if t.expense_category)

        return {
            'period_days': days,
            'total_income': float(income),
            'total_expenses': float(expenses),
            'net_profit': float(income - expenses),
            'daily_avg_income': float(income / max(1, days)),
            'daily_avg_expenses': float(expenses / max(1, days)),
            'profit_margin': float(
                ((income - expenses) / income * 100) if income > 0 else 0
            ),
        }

    def project_growth(
        self,
        monthly_seo_revenue: Decimal,
        monthly_mev_revenue: Decimal,
        months: int = 12
    ) -> List[Dict]:
        """
        Proyecta el crecimiento del tesoro mensual por mes.

        Args:
            monthly_seo_revenue: Ingreso mensual esperado de SEO
            monthly_mev_revenue: Ingreso mensual esperado de MEV
            months: Número de meses a proyectar

        Returns:
            Lista de proyecciones mes a mes
        """
        projections = []
        current_treasury = self.dao_treasury
        total_monthly = monthly_seo_revenue + monthly_mev_revenue

        for month in range(1, months + 1):
            # Asumir crecimiento mensual del 10% en SEO
            seo_growth = Decimal('1.10') ** Decimal(str(month))
            monthly_income = (
                monthly_seo_revenue * seo_growth + monthly_mev_revenue
            )

            # 20% del ingreso va a gastos operativos
            expenses = monthly_income * Decimal('0.20')

            # 70% a treasury
            to_treasury = (monthly_income - expenses) * Decimal('0.70')

            current_treasury += to_treasury

            projections.append({
                'month': month,
                'income': float(monthly_income),
                'expenses': float(expenses),
                'to_treasury': float(to_treasury),
                'cumulative_treasury': float(current_treasury),
            })

        return projections

    def export_report(self, filepath: str = "treasury_report.json"):
        """Exporta el reporte completo a JSON."""
        data = {
            'balance_sheet': self.get_balance_sheet(),
            'profitability': self.get_profitability_metrics(),
            'recent_transactions': [
                {
                    'id': t.id,
                    'timestamp': t.timestamp,
                    'amount': float(t.amount_usd),
                    'source': t.source.value if t.source else None,
                    'expense_category': t.expense_category.value if t.expense_category else None,
                    'description': t.description,
                }
                for t in self.transactions[-50:]  # Últimas 50 transacciones
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
    print("💰 TREASURY FLOW — Cash Flow Management System")
    print("=" * 60)

    treasury = TreasuryFlow()

    # Simular ingresos semanales
    print("\n📥 Registrando ingresos (simulación 1 semana)...")

    # SEO Content
    treasury.record_income(
        Decimal('15000'),
        IncomeSource.SEO_CONTENT,
        "Revenue from 10 SEO content nodes - Week 1",
    )

    treasury.record_income(
        Decimal('35000'),
        IncomeSource.MEV_WHALE,
        "Whale capture - 1 Dorada ($500K tx)",
    )

    treasury.record_income(
        Decimal('8000'),
        IncomeSource.SEO_CONTENT,
        "Revenue from 5 new content nodes - Week 1",
    )

    # Gastos
    treasury.record_expense(
        Decimal('1200'),
        ExpenseCategory.VPS_HOSTING,
        "AlexHost VPS - Monthly",
    )

    treasury.record_expense(
        Decimal('800'),
        ExpenseCategory.GAS_FEE,
        "Polygon gas fees - contract interactions",
    )

    treasury.record_expense(
        Decimal('500'),
        ExpenseCategory.TOOLS,
        "SEO tools and APIs",
    )

    # Balance
    balance = treasury.get_balance_sheet()
    print(f"\n📊 Balance General:")
    print(f"   Ingresos totales: ${balance['total_income']:,.2f}")
    print(f"   Gastos totales: ${balance['total_expenses']:,.2f}")
    print(f"   Profit neto: ${balance['net_profit']:,.2f}")
    print(f"   Tesorería DAO: ${balance['dao_treasury']:,.2f}")
    print(f"   Fondo de Gas: ${balance['gas_treasury']:,.2f}")
    print(f"   Fondo de Emergencia: ${balance['emergency_fund']:,.2f}")

    # Proyección a 12 meses
    print(f"\n📈 Proyección de Crecimiento (12 meses):")
    projections = treasury.project_growth(
        monthly_seo_revenue=Decimal('65000'),
        monthly_mev_revenue=Decimal('80000'),
        months=12
    )
    for proj in projections:
        print(f"   Mes {proj['month']:2d}: ${proj['income']:>8,.2f} ingreso → "
              f"Tesorería acumulada: ${proj['cumulative_treasury']:>10,.2f}")

    print("\n" + "=" * 60)
    print("✅ Treasury Flow — Sistema Listo")
    print("=" * 60)

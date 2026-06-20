"""Tests for TreasuryFlow — Cash Flow Management & Accounting Engine."""

import sys
import os
from decimal import Decimal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from modulos.treasury_flow import TreasuryFlow, IncomeSource, ExpenseCategory


# ================================================================
# FIXTURES
# ================================================================

@pytest.fixture
def treasury():
    return TreasuryFlow()


@pytest.fixture
def seeded_treasury(treasury):
    """Treasury with 3 income and 2 expense records."""
    treasury.record_income(Decimal("15000"), IncomeSource.SEO_CONTENT, "SEO Week 1")
    treasury.record_income(Decimal("35000"), IncomeSource.MEV_WHALE, "Whale capture Dorada")
    treasury.record_income(Decimal("8000"), IncomeSource.SEO_CONTENT, "SEO Week 2")
    treasury.record_expense(Decimal("1200"), ExpenseCategory.VPS_HOSTING, "VPS hosting")
    treasury.record_expense(Decimal("800"), ExpenseCategory.GAS_FEE, "Gas fees")
    return treasury


# ================================================================
# INITIALIZATION TESTS
# ================================================================

class TestInitialization:
    def test_default_initial_state(self, treasury):
        """Fresh treasury should have all zeros."""
        b = treasury.get_balance_sheet()
        assert b["total_income"] == 0.0
        assert b["total_expenses"] == 0.0
        assert b["net_profit"] == 0.0
        assert b["dao_treasury"] == 0.0
        assert b["gas_treasury"] == 0.0
        assert b["emergency_fund"] == 0.0
        assert b["total_distributed"] == 0.0
        assert b["transaction_count"] == 0

    def test_custom_initial_treasury(self):
        t = TreasuryFlow(initial_treasury=Decimal("50000"))
        b = t.get_balance_sheet()
        assert b["dao_treasury"] == 50000.0

    def test_distribution_constants(self, treasury):
        assert treasury.DAO_TREASURY_PCT == Decimal("0.70")
        assert treasury.GAS_OPS_PCT == Decimal("0.20")
        assert treasury.FAMILY_AIRDROP_PCT == Decimal("0.10")
        assert treasury.EMERGENCY_FUND_PCT == Decimal("0.20")


# ================================================================
# INCOME RECORDING TESTS
# ================================================================

class TestIncomeRecording:
    def test_record_income_single(self, treasury):
        tx = treasury.record_income(
            Decimal("10000"), IncomeSource.SEO_CONTENT, "Test income"
        )
        assert tx.id.startswith("INC-")
        assert tx.source == IncomeSource.SEO_CONTENT
        assert tx.amount_usd == Decimal("10000")

    def test_record_income_updates_total(self, treasury):
        treasury.record_income(Decimal("15000"), IncomeSource.SEO_CONTENT)
        b = treasury.get_balance_sheet()
        assert b["total_income"] == 15000.0

    def test_record_income_accumulates(self, treasury):
        treasury.record_income(Decimal("10000"), IncomeSource.SEO_CONTENT)
        treasury.record_income(Decimal("20000"), IncomeSource.MEV_WHALE)
        b = treasury.get_balance_sheet()
        assert b["total_income"] == 30000.0

    def test_record_income_all_sources(self, treasury):
        for source in IncomeSource:
            treasury.record_income(Decimal("1000"), source, f"Test {source.value}")
        b = treasury.get_balance_sheet()
        assert b["total_income"] == float(Decimal("1000") * len(IncomeSource))

    def test_record_income_with_metadata(self, treasury):
        tx = treasury.record_income(
            Decimal("5000"), IncomeSource.FLASH_LOAN,
            "Flash loan arb", tx_hash="0xabc123"
        )
        assert tx.metadata["tx_hash"] == "0xabc123"


# ================================================================
# EXPENSE RECORDING TESTS
# ================================================================

class TestExpenseRecording:
    def test_record_expense_single(self, treasury):
        tx = treasury.record_expense(
            Decimal("500"), ExpenseCategory.GAS_FEE, "Gas test"
        )
        assert tx.id.startswith("EXP-")
        assert tx.expense_category == ExpenseCategory.GAS_FEE

    def test_record_expense_updates_total(self, treasury):
        treasury.record_expense(Decimal("1000"), ExpenseCategory.VPS_HOSTING)
        b = treasury.get_balance_sheet()
        assert b["total_expenses"] == 1000.0

    def test_record_expense_all_categories(self, treasury):
        for cat in ExpenseCategory:
            treasury.record_expense(Decimal("100"), cat)
        b = treasury.get_balance_sheet()
        assert b["total_expenses"] == float(Decimal("100") * len(ExpenseCategory))

    def test_record_expense_gas_fee_reduces_gas_treasury(self, treasury):
        """Gas treasury should be charged for gas fees first."""
        treasury.record_income(Decimal("10000"), IncomeSource.SEO_CONTENT)
        # Gas treasury should have 20% = 2000
        b_before = treasury.get_balance_sheet()
        assert b_before["gas_treasury"] > 0

        treasury.record_expense(Decimal("300"), ExpenseCategory.GAS_FEE)
        b_after = treasury.get_balance_sheet()
        assert b_after["gas_treasury"] == b_before["gas_treasury"] - 300.0


# ================================================================
# AUTO DISTRIBUTION TESTS
# ================================================================

class TestAutoDistribution:
    def test_income_auto_distributes_70_20_10(self, treasury):
        """Income of $10,000 → $7,000 DAO, $2,000 gas, $1,000 family."""
        treasury.record_income(Decimal("10000"), IncomeSource.SEO_CONTENT)
        b = treasury.get_balance_sheet()
        # Dao: 7000, minus 20% emergency = 5600
        assert b["dao_treasury"] == 7000.0
        assert b["gas_treasury"] == 2000.0

    def test_emergency_fund_20pct_of_dao_share(self, treasury):
        treasury.record_income(Decimal("10000"), IncomeSource.SEO_CONTENT)
        b = treasury.get_balance_sheet()
        # 20% of 7000 = 1400
        assert b["emergency_fund"] == 1400.0

    def test_multiple_incomes_compound_treasuries(self, seeded_treasury):
        b = seeded_treasury.get_balance_sheet()
        total_income = Decimal("15000") + Decimal("35000") + Decimal("8000")  # 58000
        expected_dao = float(total_income * Decimal("0.70"))
        # Gas treasury: 58000 * 0.20 = 11600, minus 800 GAS_FEE expense = 10800
        expected_gas = float(total_income * Decimal("0.20")) - 800.0
        assert b["dao_treasury"] == expected_dao
        assert b["gas_treasury"] == expected_gas


# ================================================================
# BALANCE SHEET TESTS
# ================================================================

class TestBalanceSheet:
    def test_balance_sheet_all_keys(self, seeded_treasury):
        b = seeded_treasury.get_balance_sheet()
        assert "total_income" in b
        assert "total_expenses" in b
        assert "net_profit" in b
        assert "dao_treasury" in b
        assert "gas_treasury" in b
        assert "emergency_fund" in b
        assert "total_distributed" in b
        assert "transaction_count" in b

    def test_net_profit_correct(self, seeded_treasury):
        b = seeded_treasury.get_balance_sheet()
        # Income: 58000, Expenses: 2000 → Net: 56000
        assert b["net_profit"] == 56000.0
        assert b["transaction_count"] == 5

    def test_negative_net_profit(self, treasury):
        treasury.record_income(Decimal("1000"), IncomeSource.OTHER)
        treasury.record_expense(Decimal("5000"), ExpenseCategory.DEVELOPMENT)
        b = treasury.get_balance_sheet()
        assert b["net_profit"] == -4000.0


# ================================================================
# FAMILY DISTRIBUTION TESTS
# ================================================================

class TestFamilyDistribution:
    def test_distribute_to_family_valid(self, seeded_treasury):
        r = seeded_treasury.distribute_to_family(
            "0xFAMILY_WALLET", Decimal("0.50"), "Quarterly dividend"
        )
        assert r["success"]
        assert r["member"] == "0xFAMILY_WALLET"

    def test_no_remaining_funds(self, treasury):
        r = treasury.distribute_to_family(
            "0xFAMILY_WALLET", Decimal("0.50")
        )
        assert not r["success"]
        assert "No remaining" in r["error"]

    def test_exhaust_family_pool(self, seeded_treasury):
        r1 = seeded_treasury.distribute_to_family(
            "0xFAMILY_WALLET", Decimal("1.0"), "Full pool"
        )
        assert r1["success"]
        r2 = seeded_treasury.distribute_to_family(
            "0xFAMILY_WALLET", Decimal("1.0"), "No more"
        )
        assert not r2["success"]


# ================================================================
# WEEKLY REPORT TESTS
# ================================================================

class TestWeeklyReport:
    def test_weekly_report_fields(self, seeded_treasury):
        r = seeded_treasury.get_weekly_report()
        assert r.week_number == 1
        assert r.total_income > 0
        assert r.total_expenses > 0
        assert "seo_content" in r.income_by_source
        assert "vps_hosting" in r.expenses_by_category

    def test_weekly_report_income_by_source(self, seeded_treasury):
        r = seeded_treasury.get_weekly_report()
        # 15000 + 8000 = 23000 in SEO, 35000 in MEV
        assert r.income_by_source["seo_content"] == 23000.0
        assert r.income_by_source["mev_whale"] == 35000.0

    def test_weekly_report_increments_number(self, seeded_treasury):
        r1 = seeded_treasury.get_weekly_report()
        r2 = seeded_treasury.get_weekly_report()
        assert r2.week_number == r1.week_number + 1

    def test_weekly_increments_number(self, seeded_treasury):
        r1 = seeded_treasury.get_weekly_report()
        r2 = seeded_treasury.get_weekly_report()
        # Each call increments the week number
        assert r2.week_number == r1.week_number + 1
        # Verify report structure
        assert hasattr(r2, "total_income")
        assert hasattr(r2, "total_expenses")
        assert hasattr(r2, "net_profit")
        assert hasattr(r2, "income_by_source")
        assert hasattr(r2, "expenses_by_category")
        assert hasattr(r2, "dao_treasury_balance")


# ================================================================
# PROFITABILITY METRICS TESTS
# ================================================================

class TestProfitability:
    def test_profitability_metrics_fields(self, seeded_treasury):
        m = seeded_treasury.get_profitability_metrics(days=30)
        assert "period_days" in m
        assert "total_income" in m
        assert "total_expenses" in m
        assert "net_profit" in m
        assert "daily_avg_income" in m
        assert "profit_margin" in m

    def test_profit_margin_calculation(self, seeded_treasury):
        m = seeded_treasury.get_profitability_metrics(days=30)
        # Profit: 56000, Income: 58000 → margin: ~96.55%
        expected_margin = ((58000.0 - 2000.0) / 58000.0) * 100
        assert abs(m["profit_margin"] - expected_margin) < 0.01

    def test_zero_income_profit_margin(self, treasury):
        m = treasury.get_profitability_metrics(days=30)
        assert m["profit_margin"] == 0.0

    def test_daily_averages(self, seeded_treasury):
        m = seeded_treasury.get_profitability_metrics(days=30)
        assert m["daily_avg_income"] > 0
        assert m["daily_avg_expenses"] > 0


# ================================================================
# GROWTH PROJECTION TESTS
# ================================================================

class TestProjection:
    def test_project_growth_12_months(self, seeded_treasury):
        proj = seeded_treasury.project_growth(
            monthly_seo_revenue=Decimal("65000"),
            monthly_mev_revenue=Decimal("80000"),
            months=12
        )
        assert len(proj) == 12

    def test_projection_monthly_increasing(self, seeded_treasury):
        proj = seeded_treasury.project_growth(
            monthly_seo_revenue=Decimal("50000"),
            monthly_mev_revenue=Decimal("50000"),
            months=6
        )
        for i in range(1, len(proj)):
            assert proj[i]["cumulative_treasury"] >= proj[i - 1]["cumulative_treasury"]

    def test_projection_fields(self, seeded_treasury):
        proj = seeded_treasury.project_growth(
            monthly_seo_revenue=Decimal("100000"),
            monthly_mev_revenue=Decimal("50000"),
            months=1
        )
        m = proj[0]
        assert "month" in m
        assert "income" in m
        assert "expenses" in m
        assert "to_treasury" in m
        assert "cumulative_treasury" in m

    def test_projection_zero_revenue(self, seeded_treasury):
        proj = seeded_treasury.project_growth(
            monthly_seo_revenue=Decimal("0"),
            monthly_mev_revenue=Decimal("0"),
            months=3
        )
        # No revenue means expenses will drain the treasury
        for m in proj:
            assert m["income"] >= 0


# ================================================================
# EXPORT TESTS
# ================================================================

class TestExport:
    def test_export_report(self, seeded_treasury, tmp_path):
        fp = str(tmp_path / "treasury_report.json")
        r = seeded_treasury.export_report(fp)
        assert r["success"]
        assert os.path.exists(fp)

    def test_export_has_balance_sheet(self, seeded_treasury, tmp_path):
        fp = str(tmp_path / "treasury_report.json")
        seeded_treasury.export_report(fp)
        import json
        with open(fp) as f:
            data = json.load(f)
        assert "balance_sheet" in data
        assert "profitability" in data
        assert "recent_transactions" in data

    def test_export_recent_txs_limit_50(self, seeded_treasury, tmp_path):
        fp = str(tmp_path / "treasury_report.json")
        seeded_treasury.export_report(fp)
        import json
        with open(fp) as f:
            data = json.load(f)
        assert len(data["recent_transactions"]) == 5  # Our 5 seeded txs


# ================================================================
# EDGE CASE & STRESS TESTS
# ================================================================

class TestEdgeCases:
    def test_large_numbers(self, treasury):
        treasury.record_income(
            Decimal("9999999.99"), IncomeSource.SEO_CONTENT
        )
        b = treasury.get_balance_sheet()
        assert b["total_income"] == 9999999.99

    def test_small_numbers(self, treasury):
        treasury.record_income(
            Decimal("0.01"), IncomeSource.OTHER
        )
        b = treasury.get_balance_sheet()
        assert b["total_income"] == 0.01

    def test_many_transactions(self, treasury):
        for i in range(100):
            treasury.record_income(
                Decimal("100"), IncomeSource.SEO_CONTENT, f"TX {i}"
            )
        b = treasury.get_balance_sheet()
        assert b["total_income"] == 10000.0
        assert b["transaction_count"] == 100

    def test_record_then_expense_then_balance(self, treasury):
        treasury.record_income(Decimal("10000"), IncomeSource.SEO_CONTENT)
        treasury.record_expense(Decimal("1500"), ExpenseCategory.TOOLS)
        b = treasury.get_balance_sheet()
        assert b["net_profit"] == 8500.0
        assert b["transaction_count"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

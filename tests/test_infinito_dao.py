"""Tests for InfinitoDAO — Core Tokenomics Engine."""

import sys
import os
import time
from decimal import Decimal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from modulos.infinito_dao import InfinitoDAO, BeneficiaryRole


# ================================================================
# FIXTURES
# ================================================================

@pytest.fixture
def dao():
    """DAO with default property value ($103,000)."""
    return InfinitoDAO(property_value_usd=Decimal("103000"))


@pytest.fixture
def dao_with_members(dao):
    """DAO with Reymond and Joohan added as members."""
    dao.add_beneficiary("0xREYMOND_WALLET", "Reymond", BeneficiaryRole.HEREDERO)
    dao.add_beneficiary("0xJOHAN_WALLET", "Joohan", BeneficiaryRole.HEREDERO)
    return dao


# ================================================================
# INITIALIZATION TESTS
# ================================================================

class TestInitialization:
    def test_default_property_value(self, dao):
        """Default property should be $103,000."""
        s = dao.get_summary()
        assert s["property_value_usd"] == "103000"

    def test_total_supply(self, dao):
        s = dao.get_summary()
        assert s["total_supply"] == "1000000"

    def test_initial_distribution_pool(self, dao):
        """Pool should be 14% of 1M = 140,000 TI."""
        s = dao.get_summary()
        assert s["pool_herederos_remaining"] == "140000.00"

    def test_initial_beneficiaries(self, dao):
        """Should have 2 default beneficiaries (padres + joker)."""
        s = dao.get_summary()
        assert s["beneficiary_count"] == 2

    def test_owners_set(self, dao):
        s = dao.get_summary()
        assert s["owner_address"] == "0xJOKER_MAIN"

    def test_custom_property_value(self):
        dao2 = InfinitoDAO(property_value_usd=Decimal("200000"))
        s = dao2.get_summary()
        assert s["property_value_usd"] == "200000"

    def test_custom_owner_address(self):
        dao2 = InfinitoDAO(owner_address="0xCUSTOM_OWNER")
        s = dao2.get_summary()
        assert s["owner_address"] == "0xCUSTOM_OWNER"


# ================================================================
# BENEFICIARY TESTS
# ================================================================

class TestBeneficiaries:
    def test_add_new_member(self, dao):
        assert dao.add_beneficiary("0xNEW", "New Member", BeneficiaryRole.HEREDERO)
        s = dao.get_summary()
        assert s["beneficiary_count"] == 3

    def test_add_duplicate_member(self, dao):
        assert not dao.add_beneficiary("0xPADRES_MULTISIG", "Dupe", BeneficiaryRole.HEREDERO)

    def test_add_all_roles(self, dao):
        for role in BeneficiaryRole:
            addr = f"0x{role.value}_WALLET"
            assert dao.add_beneficiary(addr, role.value, role)
        s = dao.get_summary()
        assert s["beneficiary_count"] == 2 + len(BeneficiaryRole)

    def test_get_portfolio_existing(self, dao):
        p = dao.get_portfolio("0xJOKER_MAIN")
        assert p is not None
        assert p["name"] == "Romny (Joker)"
        assert p["role"] == "joker_arquitecto"

    def test_get_portfolio_nonexistent(self, dao):
        assert dao.get_portfolio("0xGHOST") is None

    def test_get_portfolio_fields(self, dao):
        p = dao.get_portfolio("0xPADRES_MULTISIG")
        assert "tokens" in p
        assert "locked_tokens" in p
        assert "total_balance" in p
        assert "percentage" in p
        assert "voting_power" in p
        assert "contributions_count" in p


# ================================================================
# DISTRIBUTION TESTS
# ================================================================

class TestDistribution:
    def test_distribute_valid(self, dao_with_members):
        r = dao_with_members.distribute_from_pool(
            "0xREYMOND_WALLET", Decimal("50000"),
            "Merit", caller_address="0xJOKER_MAIN"
        )
        assert r["success"]
        assert r["amount_distributed"] == "50000"

    def test_distribute_reduces_pool(self, dao_with_members):
        dao_with_members.distribute_from_pool(
            "0xREYMOND_WALLET", Decimal("30000"),
            "Test", caller_address="0xJOKER_MAIN"
        )
        s = dao_with_members.get_summary()
        assert s["pool_herederos_remaining"] == "110000.00"

    def test_distribute_insufficient_pool(self, dao_with_members):
        r = dao_with_members.distribute_from_pool(
            "0xREYMOND_WALLET", Decimal("999999"),
            "Too much", caller_address="0xJOKER_MAIN"
        )
        assert not r["success"]
        assert "Insufficient" in r["error"]

    def test_distribute_invalid_amount(self, dao_with_members):
        r = dao_with_members.distribute_from_pool(
            "0xREYMOND_WALLET", Decimal("-100"),
            "Negative", caller_address="0xJOKER_MAIN"
        )
        assert not r["success"]

    def test_distribute_unauthorized(self, dao_with_members):
        r = dao_with_members.distribute_from_pool(
            "0xREYMOND_WALLET", Decimal("1000"),
            "Hack attempt", caller_address="0xEVIL"
        )
        assert not r["success"]

    def test_distribute_nonexistent_member(self, dao_with_members):
        r = dao_with_members.distribute_from_pool(
            "0xGHOST", Decimal("1000"),
            "Ghost", caller_address="0xJOKER_MAIN"
        )
        assert not r["success"]

    def test_distribute_multiple_beneficiaries(self, dao_with_members):
        dao_with_members.distribute_from_pool(
            "0xREYMOND_WALLET", Decimal("25000"),
            "First", caller_address="0xJOKER_MAIN"
        )
        dao_with_members.distribute_from_pool(
            "0xJOHAN_WALLET", Decimal("15000"),
            "Second", caller_address="0xJOKER_MAIN"
        )
        r = dao_with_members.get_portfolio("0xREYMOND_WALLET")
        j = dao_with_members.get_portfolio("0xJOHAN_WALLET")
        assert r["tokens"] == "25000"
        assert j["tokens"] == "15000"


# ================================================================
# CONTRIBUTION TESTS
# ================================================================

class TestContributions:
    def test_apply_contribution_valid(self, dao_with_members):
        r = dao_with_members.apply_contribution(
            "0xREYMOND_WALLET", Decimal("50000"),
            dilution_factor=Decimal("1.0"),
            description="Construction"
        )
        assert r["success"]
        assert Decimal(r["tokens_earned"]) > 0

    def test_contribution_increases_property_value(self, dao_with_members):
        r = dao_with_members.apply_contribution(
            "0xREYMOND_WALLET", Decimal("50000"),
            dilution_factor=Decimal("1.0")
        )
        assert r["new_property_value"] == "153000"

    def test_contribution_dilution_factor_zero(self, dao_with_members):
        r = dao_with_members.apply_contribution(
            "0xREYMOND_WALLET", Decimal("1000"),
            dilution_factor=Decimal("0.3")
        )
        assert not r["success"]

    def test_contribution_dilution_factor_over_limit(self, dao_with_members):
        r = dao_with_members.apply_contribution(
            "0xREYMOND_WALLET", Decimal("1000"),
            dilution_factor=Decimal("3.0")
        )
        assert not r["success"]

    def test_contribution_negative(self, dao_with_members):
        r = dao_with_members.apply_contribution(
            "0xREYMOND_WALLET", Decimal("-500"),
            dilution_factor=Decimal("1.0")
        )
        assert not r["success"]

    def test_contribution_nonexistent_member(self, dao_with_members):
        r = dao_with_members.apply_contribution(
            "0xGHOST", Decimal("5000"),
            dilution_factor=Decimal("1.0")
        )
        assert not r["success"]

    def test_contribution_logs(self, dao_with_members):
        dao_with_members.apply_contribution(
            "0xREYMOND_WALLET", Decimal("25000"),
            dilution_factor=Decimal("1.0")
        )
        s = dao_with_members.get_summary()
        assert s["contributions_count"] >= 1

    def test_contribution_tokens_earned_formula(self, dao_with_members):
        """Verify: tokens = (contribution / new_value) * supply * dilution"""
        r = dao_with_members.apply_contribution(
            "0xREYMOND_WALLET", Decimal("50000"),
            dilution_factor=Decimal("1.2")
        )
        expected = (Decimal("50000") / Decimal("153000")) * Decimal("1000000") * Decimal("1.2")
        assert abs(Decimal(r["tokens_earned"]) - expected) < Decimal("0.01")


# ================================================================
# VESTING TESTS
# ================================================================

class TestVesting:
    def test_vesting_cliff_not_met(self, dao):
        """Should fail because cliff is 180 days."""
        r = dao.claim_vested_tokens("0xJOKER_MAIN")
        assert not r["success"]
        assert "Cliff" in r["error"]

    def test_vesting_only_joker(self, dao_with_members):
        r = dao_with_members.claim_vested_tokens("0xREYMOND_WALLET")
        assert not r["success"]
        assert "Only Joker" in r["error"]

    def test_vesting_nonexistent(self, dao):
        r = dao.claim_vested_tokens("0xGHOST")
        assert not r["success"]

    def test_joker_has_locked_tokens(self, dao):
        p = dao.get_portfolio("0xJOKER_MAIN")
        locked = Decimal(p["locked_tokens"])
        expected = Decimal("350000") * Decimal("0.65")  # 35% de 1M * 65% locked
        assert locked == expected


# ================================================================
# DIVIDEND TESTS
# ================================================================

class TestDividends:
    def test_distribute_dividends_valid(self, dao):
        r = dao.distribute_dividends(Decimal("50000"), source="seo_content")
        assert r["success"]
        assert Decimal(r["dao_treasury"]) > 0
        assert Decimal(r["gas_treasury"]) > 0

    def test_dividends_split_70_20_10(self, dao):
        r = dao.distribute_dividends(Decimal("100000"))
        # 70% to treasury = 70000
        assert Decimal(r["dao_treasury"]) == Decimal("70000")
        # 20% to gas = 20000
        assert Decimal(r["gas_treasury"]) == Decimal("20000")
        # 10% airdrops = 10000
        assert Decimal(r["airdrops_pool"]) == Decimal("10000")

    def test_dividends_multiple_distributions(self, dao):
        dao.distribute_dividends(Decimal("10000"))
        dao.distribute_dividends(Decimal("20000"))
        s = dao.get_summary()
        # dao_treasury should be 7000 + 14000 = 21000
        assert Decimal(s["dao_treasury_usd"]) == Decimal("21000")

    def test_dividends_tracks_log(self, dao):
        dao.distribute_dividends(Decimal("5000"))
        s = dao.get_summary()
        assert s["contributions_count"] >= 1


# ================================================================
# WHALE SHARE TESTS
# ================================================================

class TestWhaleShare:
    def test_calculate_whale_share_valid(self, dao):
        r = dao.calculate_whale_share(
            whale_value_usd=Decimal("500000"),
            stake_percentage=Decimal("0.05")
        )
        assert r["gross_profit"] is not None
        assert r["net_profit"] is not None
        assert r["staker_payout"] is not None

    def test_whale_share_default_profit(self, dao):
        """Default profit should be 2%."""
        r = dao.calculate_whale_share(
            whale_value_usd=Decimal("100000"),
            stake_percentage=Decimal("0.10")
        )
        gross = Decimal(r["gross_profit"])
        assert gross == Decimal("2000")  # 2% of 100K

    def test_whale_share_custom_profit(self, dao):
        r = dao.calculate_whale_share(
            whale_value_usd=Decimal("100000"),
            stake_percentage=Decimal("0.10"),
            profit_pct=Decimal("0.05")
        )
        gross = Decimal(r["gross_profit"])
        assert gross == Decimal("5000")  # 5% of 100K

    def test_whale_share_invalid_profit(self, dao):
        r = dao.calculate_whale_share(
            whale_value_usd=Decimal("100000"),
            stake_percentage=Decimal("0.10"),
            profit_pct=Decimal("0.20")  # 20% > max 10%
        )
        assert not r["success"]

    def test_whale_share_too_small_profit(self, dao):
        r = dao.calculate_whale_share(
            whale_value_usd=Decimal("100000"),
            stake_percentage=Decimal("0.10"),
            profit_pct=Decimal("0.0005")  # 0.05% < min 0.1%
        )
        assert not r["success"]


# ================================================================
# SUMMARY & EDGE CASE TESTS
# ================================================================

class TestSummary:
    def test_summary_all_fields(self, dao):
        s = dao.get_summary()
        assert "property_value_usd" in s
        assert "total_supply" in s
        assert "pool_herederos_remaining" in s
        assert "dao_treasury_usd" in s
        assert "gas_treasury_usd" in s
        assert "beneficiary_count" in s
        assert "vesting_status" in s
        assert "owner_address" in s
        assert "timestamp" in s

    def test_summary_vesting_info(self, dao):
        s = dao.get_summary()
        v = s["vesting_status"]
        assert v["cliff_days"] == 180
        assert v["total_vesting_days"] == 730

    def test_export_ledger_file(self, dao, tmp_path):
        fp = str(tmp_path / "test_ledger.json")
        r = dao.export_ledger(fp)
        assert r["success"]
        assert os.path.exists(fp)


# ================================================================
# RUN
# ================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

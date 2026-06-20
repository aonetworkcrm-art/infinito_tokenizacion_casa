"""Integration tests for API REST — tests all endpoints via FastAPI TestClient."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi.testclient import TestClient
from api_server import app, state, AppState


# ================================================================
# FIXTURES
# ================================================================

@pytest.fixture(autouse=True)
def reset_state():
    """Reset all modules to clean state before each test."""
    global state
    # We import the module-level state and replace it
    import api_server
    api_server.state = AppState()
    yield
    # Don't need cleanup since each test gets fresh state


@pytest.fixture
def client():
    return TestClient(app)


# ================================================================
# SYSTEM ENDPOINTS
# ================================================================

class TestSystem:
    def test_root(self, client):
        r = client.get("/")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "operational"
        assert data["project"] == "PROYECTO INFINITO"
        assert "dao" in data["modules"]
        assert "whales" in data["modules"]
        assert "seo" in data["modules"]
        assert "treasury" in data["modules"]

    def test_reset(self, client):
        # Record some data first
        client.post("/api/treasury/income", json={
            "amount_usd": 5000, "source": "seo_content"
        })
        r = client.get("/api/treasury/balance")
        assert r.json()["total_income"] == 5000.0

        # Reset
        r = client.get("/api/reset")
        assert r.status_code == 200
        assert r.json()["success"]

        # Verify reset
        r = client.get("/api/treasury/balance")
        assert r.json()["total_income"] == 0.0


# ================================================================
# DAO ENDPOINTS
# ================================================================

class TestDAOSummary:
    def test_summary_default(self, client):
        r = client.get("/api/dao/summary")
        assert r.status_code == 200
        s = r.json()
        assert s["total_supply"] == "1000000"
        assert s["beneficiary_count"] == 2
        assert "property_value_usd" in s
        assert "dao_treasury_usd" in s
        assert "vesting_status" in s

    def test_summary_fields(self, client):
        r = client.get("/api/dao/summary")
        assert r.status_code == 200
        keys = r.json().keys()
        assert "property_value_usd" in keys
        assert "total_supply" in keys
        assert "pool_herederos_remaining" in keys
        assert "beneficiary_count" in keys
        assert "vesting_status" in keys


class TestDAOMembers:
    def test_list_members_default(self, client):
        r = client.get("/api/dao/members")
        assert r.status_code == 200
        data = r.json()
        assert data["count"] == 2
        assert len(data["members"]) == 2

    def test_add_member_valid(self, client):
        r = client.post("/api/dao/members", json={
            "address": "0xNEW_FAMILY",
            "name": "Test Member",
            "role": "heredero",
        })
        assert r.status_code == 200
        assert r.json()["success"]

        # Verify member was added
        r = client.get("/api/dao/members")
        assert r.json()["count"] == 3

    def test_add_member_invalid_role(self, client):
        r = client.post("/api/dao/members", json={
            "address": "0xBAD_ROLE",
            "name": "Bad Role",
            "role": "invalid_role",
        })
        assert r.status_code == 422  # Pydantic validation

    def test_add_duplicate_member(self, client):
        r = client.post("/api/dao/members", json={
            "address": "0xPADRES_MULTISIG",
            "name": "Dupe",
            "role": "heredero",
        })
        assert r.status_code == 400
        assert "ya existe" in r.json()["detail"]


class TestDAOPortfolio:
    def test_portfolio_existing_joker(self, client):
        r = client.get("/api/dao/portfolio/0xJOKER_MAIN")
        assert r.status_code == 200
        p = r.json()
        assert p["name"] == "Romny (Joker)"
        assert p["role"] == "joker_arquitecto"
        assert "tokens" in p
        assert "locked_tokens" in p
        assert "voting_power" in p

    def test_portfolio_existing_padres(self, client):
        r = client.get("/api/dao/portfolio/0xPADRES_MULTISIG")
        assert r.status_code == 200
        p = r.json()
        assert p["name"] == "Ramón & Nicolasa"

    def test_portfolio_nonexistent(self, client):
        r = client.get("/api/dao/portfolio/0xGHOST_WALLET")
        assert r.status_code == 404


class TestDAODistribute:
    def test_distribute_success(self, client):
        # Add a member first
        client.post("/api/dao/members", json={
            "address": "0xHEREDERO_1",
            "name": "Heredero 1",
            "role": "heredero",
        })
        r = client.post("/api/dao/distribute", json={
            "beneficiary_address": "0xHEREDERO_1",
            "amount_tokens": 50000,
            "reason": "Merit distribution"
        })
        assert r.status_code == 200
        assert r.json()["success"]
        assert r.json()["amount_distributed"] == "50000.0"

    def test_distribute_insufficient_pool(self, client):
        client.post("/api/dao/members", json={
            "address": "0xHEREDERO_1", "name": "H1", "role": "heredero",
        })
        r = client.post("/api/dao/distribute", json={
            "beneficiary_address": "0xHEREDERO_1",
            "amount_tokens": 99999999,
            "reason": "Too much"
        })
        assert r.status_code == 400

    def test_distribute_nonexistent_member(self, client):
        r = client.post("/api/dao/distribute", json={
            "beneficiary_address": "0xGHOST",
            "amount_tokens": 1000,
        })
        assert r.status_code == 400

    def test_distribute_unauthorized(self, client):
        client.post("/api/dao/members", json={
            "address": "0xHEREDERO_1", "name": "H1", "role": "heredero",
        })
        r = client.post("/api/dao/distribute", json={
            "beneficiary_address": "0xHEREDERO_1",
            "amount_tokens": 1000,
            "caller_address": "0xEVIL"
        })
        assert r.status_code == 400


class TestDAOContribute:
    def test_contribute_success(self, client):
        client.post("/api/dao/members", json={
            "address": "0xHEREDERO_1", "name": "H1", "role": "heredero",
        })
        r = client.post("/api/dao/contribute", json={
            "beneficiary_address": "0xHEREDERO_1",
            "contribution_usd": 50000,
            "dilution_factor": 1.0,
        })
        assert r.status_code == 200
        assert r.json()["success"]
        assert "tokens_earned" in r.json()

    def test_contribute_nonexistent_member(self, client):
        r = client.post("/api/dao/contribute", json={
            "beneficiary_address": "0xGHOST",
            "contribution_usd": 1000,
        })
        assert r.status_code == 400

    def test_contribute_negative(self, client):
        client.post("/api/dao/members", json={
            "address": "0xHEREDERO_1", "name": "H1", "role": "heredero",
        })
        r = client.post("/api/dao/contribute", json={
            "beneficiary_address": "0xHEREDERO_1",
            "contribution_usd": -500,
        })
        assert r.status_code == 422  # Pydantic: gt=0


class TestDAODividends:
    def test_dividends_success(self, client):
        r = client.post("/api/dao/dividends", json={
            "total_profit_usd": 50000,
            "source": "seo_content"
        })
        assert r.status_code == 200
        data = r.json()
        assert data["success"]
        assert "dao_treasury" in data
        assert "gas_treasury" in data
        assert "airdrops_pool" in data

    def test_dividends_70_20_10(self, client):
        r = client.post("/api/dao/dividends", json={
            "total_profit_usd": 100000,
        })
        data = r.json()
        assert data["dao_treasury"] == "70000.00"
        assert data["gas_treasury"] == "20000.00"
        assert data["airdrops_pool"] == "10000.00"


class TestDAOVesting:
    def test_vesting_cliff_not_met(self, client):
        r = client.post("/api/dao/claim-vesting", json={
            "address": "0xJOKER_MAIN"
        })
        assert r.status_code == 400
        assert "Cliff" in r.json()["detail"]

    def test_vesting_nonexistent(self, client):
        r = client.post("/api/dao/claim-vesting", json={
            "address": "0xGHOST"
        })
        assert r.status_code == 400


class TestDAOWhaleShare:
    def test_whale_share_valid(self, client):
        r = client.get(
            "/api/dao/whale-share",
            params={"whale_value_usd": 500000, "stake_pct": 0.05, "profit_pct": 0.02}
        )
        assert r.status_code == 200
        data = r.json()
        assert "gross_profit" in data
        assert "net_profit" in data
        assert "staker_payout" in data

    def test_whale_share_invalid_profit(self, client):
        r = client.get(
            "/api/dao/whale-share",
            params={"whale_value_usd": 100000, "stake_pct": 0.05, "profit_pct": 0.20}
        )
        assert r.status_code == 400

    def test_whale_share_missing_param(self, client):
        r = client.get("/api/dao/whale-share", params={"whale_value_usd": 500000})
        assert r.status_code == 200  # stake_pct and profit_pct have defaults


# ================================================================
# WHALE WATCHER ENDPOINTS
# ================================================================

class TestWhaleScan:
    def test_scan_default(self, client):
        r = client.post("/api/whales/scan", json={})
        assert r.status_code == 200
        data = r.json()
        assert data["count"] > 0
        assert data["network"] == "polygon_amoy_testnet (simulado)"
        assert len(data["whales"]) > 0
        # Check whale structure
        w = data["whales"][0]
        assert "tx_hash" in w
        assert "value_usd" in w
        assert "category" in w
        assert "value_formatted" in w

    def test_scan_custom_count(self, client):
        r = client.post("/api/whales/scan", json={"count": 200})
        assert r.status_code == 200
        assert len(r.json()["whales"]) > 0

    def test_scan_invalid_count(self, client):
        r = client.post("/api/whales/scan", json={"count": 0})
        assert r.status_code == 422  # Pydantic: ge=1


class TestWhaleSummary:
    def test_summary_empty(self, client):
        r = client.get("/api/whales/summary")
        assert r.status_code == 200
        s = r.json()
        assert s["total_whales_detected"] == 0
        assert s["total_profits_usd"] == 0.0

    def test_summary_after_scan(self, client):
        client.post("/api/whales/scan", json={"count": 50})
        r = client.get("/api/whales/summary")
        assert r.status_code == 200
        assert r.json()["total_whales_detected"] > 0

    def test_summary_fields(self, client):
        r = client.get("/api/whales/summary")
        assert "network" in r.json()
        assert "total_whales_detected" in r.json()
        assert "categories" in r.json()


class TestWhaleOpportunities:
    def test_opportunities_empty_initially(self, client):
        r = client.get("/api/whales/opportunities")
        assert r.status_code == 200
        assert r.json()["count"] == 0

    def test_opportunities_after_scan(self, client):
        client.post("/api/whales/scan", json={"count": 200})
        r = client.get("/api/whales/opportunities")
        assert r.status_code == 200
        data = r.json()
        assert "opportunities" in data
        if data["count"] > 0:
            opp = data["opportunities"][0]
            assert "whale_value" in opp
            assert "net_profit" in opp
            assert "dex_path" in opp

    def test_opportunities_min_profit_filter(self, client):
        client.post("/api/whales/scan", json={"count": 200})
        r = client.get("/api/whales/opportunities", params={"min_profit": 1000})
        assert r.status_code == 200


# ================================================================
# SEO ORACLE ENDPOINTS
# ================================================================

class TestSEONiches:
    def test_niches_default_filter(self, client):
        r = client.get("/api/seo/niches")
        assert r.status_code == 200
        data = r.json()
        assert data["count"] > 0
        n = data["niches"][0]
        assert "id" in n
        assert "name" in n
        assert "cpc_avg" in n
        assert "difficulty" in n
        assert "keywords" in n

    def test_niches_low_cpc(self, client):
        r = client.get("/api/seo/niches", params={"min_cpc": 50})
        assert r.status_code == 200
        # Lower CPC threshold should include more niches
        r_high = client.get("/api/seo/niches", params={"min_cpc": 200})
        assert r.json()["count"] >= r_high.json()["count"]

    def test_niches_high_cpc(self, client):
        r = client.get("/api/seo/niches", params={"min_cpc": 500})
        assert r.status_code == 200


class TestSEORanking:
    def test_ranking_sorted(self, client):
        r = client.get("/api/seo/ranking")
        assert r.status_code == 200
        ranking = r.json()["ranking"]
        scores = [n["profitability_score"] for n in ranking]
        assert scores == sorted(scores, reverse=True)

    def test_ranking_top_is_personal_injury(self, client):
        r = client.get("/api/seo/ranking")
        top = r.json()["ranking"][0]
        assert top["id"] == "personal-injury-law"
        assert top["cpc_avg"] >= 200

    def test_ranking_fields(self, client):
        r = client.get("/api/seo/ranking")
        for n in r.json()["ranking"]:
            assert "id" in n
            assert "name" in n
            assert "cpc_avg" in n
            assert "difficulty" in n
            assert "evergreen" in n


class TestSEOProjection:
    def test_projection_valid(self, client):
        r = client.post("/api/seo/projection", json={
            "niche_id": "personal-injury-law",
            "monthly_visitors": 5000,
            "ctr_pct": 2.0,
            "nodes_count": 3,
        })
        assert r.status_code == 200
        data = r.json()
        assert data["clicks_monthly"] == 300
        assert data["monthly_revenue"]["avg"] > 0

    def test_projection_invalid_niche(self, client):
        r = client.post("/api/seo/projection", json={
            "niche_id": "invalid-niche",
            "monthly_visitors": 5000,
        })
        assert r.status_code == 404

    def test_projection_zero_visitors_rejected(self, client):
        r = client.post("/api/seo/projection", json={
            "niche_id": "personal-injury-law",
            "monthly_visitors": 0,  # ge=100 in Pydantic
            "ctr_pct": 2.0,
        })
        assert r.status_code == 422

    def test_projection_high_gt_low(self, client):
        r = client.post("/api/seo/projection", json={
            "niche_id": "asset-recovery",
            "monthly_visitors": 3000,
            "ctr_pct": 2.0,
            "nodes_count": 2,
        })
        data = r.json()
        rev = data["monthly_revenue"]
        assert rev["high"] >= rev["avg"]
        assert rev["avg"] >= rev["low"]


class TestSEOContentPlan:
    def test_content_plan_single(self, client):
        r = client.post("/api/seo/content-plan", json={
            "selected_niches": ["personal-injury-law"]
        })
        assert r.status_code == 200
        data = r.json()
        assert len(data["nodes"]) == 1
        assert data["total_monthly_visitors"] > 0

    def test_content_plan_multiple(self, client):
        r = client.post("/api/seo/content-plan", json={
            "selected_niches": [
                "personal-injury-law",
                "asset-recovery",
                "cybersecurity-compliance"
            ]
        })
        assert r.status_code == 200
        assert len(r.json()["nodes"]) == 3

    def test_content_plan_invalid_niche(self, client):
        r = client.post("/api/seo/content-plan", json={
            "selected_niches": ["invalid-niche"]
        })
        assert r.status_code == 200
        assert len(r.json()["nodes"]) == 0  # Invalid niches are silently ignored


class TestSEOEvergreen:
    def test_evergreen_year_1(self, client):
        r = client.get("/api/seo/evergreen-multiplier/1")
        assert r.status_code == 200
        assert r.json()["multiplier"] == 1.0

    def test_evergreen_year_5(self, client):
        r = client.get("/api/seo/evergreen-multiplier/5")
        assert r.status_code == 200
        assert r.json()["multiplier"] > 1.0

    def test_evergreen_year_0_invalid(self, client):
        r = client.get("/api/seo/evergreen-multiplier/0")
        assert r.status_code == 400

    def test_evergreen_year_100_invalid(self, client):
        r = client.get("/api/seo/evergreen-multiplier/100")
        assert r.status_code == 400


# ================================================================
# TREASURY ENDPOINTS
# ================================================================

class TestTreasuryBalance:
    def test_balance_empty(self, client):
        r = client.get("/api/treasury/balance")
        assert r.status_code == 200
        assert r.json()["total_income"] == 0.0
        assert r.json()["total_expenses"] == 0.0
        assert r.json()["transaction_count"] == 0


class TestTreasuryIncome:
    def test_record_income(self, client):
        r = client.post("/api/treasury/income", json={
            "amount_usd": 15000,
            "source": "seo_content",
            "description": "Test SEO income"
        })
        assert r.status_code == 200
        data = r.json()
        assert data["success"]
        assert data["transaction_id"].startswith("INC-")
        assert data["amount_usd"] == 15000.0

    def test_income_updates_balance(self, client):
        client.post("/api/treasury/income", json={
            "amount_usd": 10000, "source": "seo_content"
        })
        r = client.get("/api/treasury/balance")
        assert r.json()["total_income"] == 10000.0

    def test_income_invalid_source(self, client):
        r = client.post("/api/treasury/income", json={
            "amount_usd": 1000,
            "source": "invalid_source",
        })
        assert r.status_code == 422  # Pydantic pattern validation

    def test_income_negative_rejected(self, client):
        r = client.post("/api/treasury/income", json={
            "amount_usd": -100,
            "source": "seo_content",
        })
        assert r.status_code == 422


class TestTreasuryExpense:
    def test_record_expense(self, client):
        # First add income to have gas treasury
        client.post("/api/treasury/income", json={
            "amount_usd": 10000, "source": "seo_content"
        })
        r = client.post("/api/treasury/expense", json={
            "amount_usd": 500,
            "category": "vps_hosting",
            "description": "VPS monthly"
        })
        assert r.status_code == 200
        data = r.json()
        assert data["success"]
        assert data["transaction_id"].startswith("EXP-")

    def test_expense_invalid_category(self, client):
        r = client.post("/api/treasury/expense", json={
            "amount_usd": 100,
            "category": "invalid_category",
        })
        assert r.status_code == 422

    def test_expense_deducts_from_gas_treasury(self, client):
        client.post("/api/treasury/income", json={
            "amount_usd": 10000, "source": "seo_content"
        })
        b_before = client.get("/api/treasury/balance").json()
        client.post("/api/treasury/expense", json={
            "amount_usd": 300,
            "category": "gas_fee",
        })
        b_after = client.get("/api/treasury/balance").json()
        assert b_after["gas_treasury"] == b_before["gas_treasury"] - 300.0


class TestTreasuryProjection:
    def test_projection_12_months(self, client):
        r = client.get(
            "/api/treasury/projection",
            params={"monthly_seo": 65000, "monthly_mev": 80000, "months": 12}
        )
        assert r.status_code == 200
        data = r.json()
        assert len(data["projections"]) == 12
        assert data["total_months"] == 12

    def test_projection_increasing(self, client):
        r = client.get(
            "/api/treasury/projection",
            params={"monthly_seo": 50000, "monthly_mev": 50000, "months": 6}
        )
        projs = r.json()["projections"]
        for i in range(1, len(projs)):
            assert projs[i]["cumulative_treasury"] >= projs[i - 1]["cumulative_treasury"]

    def test_projection_fields(self, client):
        r = client.get(
            "/api/treasury/projection",
            params={"monthly_seo": 100000, "monthly_mev": 50000, "months": 3}
        )
        m = r.json()["projections"][0]
        assert "month" in m
        assert "income" in m
        assert "expenses" in m
        assert "to_treasury" in m
        assert "cumulative_treasury" in m


class TestTreasuryWeekly:
    def test_weekly_first_report(self, client):
        client.post("/api/treasury/income", json={
            "amount_usd": 15000, "source": "seo_content"
        })
        r = client.get("/api/treasury/weekly")
        assert r.status_code == 200
        data = r.json()
        assert data["week_number"] >= 1
        assert "total_income" in data
        assert "total_expenses" in data
        assert "income_by_source" in data

    def test_weekly_empty(self, client):
        r = client.get("/api/treasury/weekly")
        assert r.status_code == 200
        assert r.json()["total_income"] == 0.0


class TestTreasuryProfitability:
    def test_profitability_empty(self, client):
        r = client.get("/api/treasury/profitability", params={"days": 30})
        assert r.status_code == 200
        m = r.json()
        assert m["total_income"] == 0.0
        assert m["profit_margin"] == 0.0

    def test_profitability_after_income(self, client):
        client.post("/api/treasury/income", json={
            "amount_usd": 10000, "source": "seo_content"
        })
        r = client.get("/api/treasury/profitability", params={"days": 30})
        assert r.status_code == 200
        assert r.json()["total_income"] == 10000.0

    def test_profitability_invalid_days(self, client):
        r = client.get("/api/treasury/profitability", params={"days": 0})
        assert r.status_code == 422  # ge=1


class TestTreasuryDistributeFamily:
    def test_distribute_family_no_funds(self, client):
        r = client.post("/api/treasury/distribute-family", json={
            "member_address": "0xFAMILY",
            "percentage": 0.5,
        })
        assert r.status_code == 400
        assert "No remaining" in r.json()["detail"]

    def test_distribute_family_success(self, client):
        # Add income first so there's a family pool
        client.post("/api/treasury/income", json={
            "amount_usd": 50000, "source": "seo_content"
        })
        r = client.post("/api/treasury/distribute-family", json={
            "member_address": "0xFAMILY_WALLET",
            "percentage": 0.5,
            "reason": "Quarterly dividend"
        })
        assert r.status_code == 200
        data = r.json()
        assert data["success"]
        assert "amount" in data
        assert data["member"] == "0xFAMILY_WALLET"

    def test_distribute_family_exhausted(self, client):
        client.post("/api/treasury/income", json={
            "amount_usd": 10000, "source": "seo_content"
        })
        # Take all the family pool
        client.post("/api/treasury/distribute-family", json={
            "member_address": "0xFAMILY",
            "percentage": 1.0,
        })
        r = client.post("/api/treasury/distribute-family", json={
            "member_address": "0xFAMILY",
            "percentage": 1.0,
        })
        assert r.status_code == 400


# ================================================================
# ERROR HANDLING & EDGE CASES
# ================================================================

class TestErrorHandling:
    def test_nonexistent_route(self, client):
        r = client.get("/api/nonexistent")
        assert r.status_code == 404

    def test_invalid_json_body(self, client):
        r = client.post(
            "/api/dao/distribute",
            data="not-json",
            headers={"Content-Type": "application/json"}
        )
        assert r.status_code == 422  # FastAPI returns 422 for invalid JSON

    def test_empty_body_to_post(self, client):
        r = client.post("/api/dao/dividends", json={})
        assert r.status_code == 422  # total_profit_usd is required

    def test_missing_required_query_param(self, client):
        r = client.get("/api/dao/whale-share")
        assert r.status_code == 422  # whale_value_usd is required

    def test_negative_amount_rejected(self, client):
        r = client.post("/api/treasury/income", json={
            "amount_usd": -100,
            "source": "seo_content",
        })
        assert r.status_code == 422

    def test_zero_amount_rejected(self, client):
        r = client.post("/api/treasury/income", json={
            "amount_usd": 0,
            "source": "seo_content",
        })
        assert r.status_code == 422  # gt=0

    def test_string_instead_of_number(self, client):
        r = client.post("/api/treasury/income", json={
            "amount_usd": "not-a-number",
            "source": "seo_content",
        })
        assert r.status_code == 422


# ================================================================
# FULL WORKFLOW TEST
# ================================================================

class TestFullWorkflow:
    """Simulates a complete business day: SEO → MEV → Treasury → DAO."""

    def test_complete_business_day(self, client):
        # 1. Start fresh after reset
        client.get("/api/reset")

        # 2. Check system status
        r = client.get("/")
        assert r.json()["status"] == "operational"

        # 3. SEO: Get ranking and projection
        r = client.get("/api/seo/ranking")
        top_niche = r.json()["ranking"][0]["id"]
        assert top_niche == "personal-injury-law"

        r = client.post("/api/seo/projection", json={
            "niche_id": top_niche,
            "monthly_visitors": 5000,
            "ctr_pct": 2.0,
            "nodes_count": 3,
        })
        monthly_rev = r.json()["monthly_revenue"]["avg"]
        assert monthly_rev > 0

        # 4. Whale Watcher: Scan mempool
        r = client.post("/api/whales/scan", json={"count": 100})
        assert r.json()["count"] > 0

        r = client.get("/api/whales/summary")
        assert r.json()["total_whales_detected"] > 0

        # 5. Treasury: Record income from SEO and MEV
        client.post("/api/treasury/income", json={
            "amount_usd": 15000, "source": "seo_content",
            "description": f"SEO revenue from {top_niche}",
        })
        client.post("/api/treasury/income", json={
            "amount_usd": 35000, "source": "mev_whale",
            "description": "Whale capture - Dorada",
        })
        r = client.get("/api/treasury/balance")
        assert r.json()["total_income"] == 50000.0
        assert r.json()["dao_treasury"] == 35000.0  # 70% of 50000

        # 6. Treasury: Record expenses
        client.post("/api/treasury/expense", json={
            "amount_usd": 1200, "category": "vps_hosting",
        })
        client.post("/api/treasury/expense", json={
            "amount_usd": 500, "category": "tools",
        })
        r = client.get("/api/treasury/balance")
        assert r.json()["total_expenses"] == 1700.0

        # 7. DAO: Distribute dividends
        r = client.post("/api/dao/dividends", json={
            "total_profit_usd": 48300,  # 50000 - 1700
            "source": "combined",
        })
        assert r.json()["success"]

        # 8. Treasury: Check projection
        r = client.get(
            "/api/treasury/projection",
            params={"monthly_seo": 65000, "monthly_mev": 80000, "months": 3}
        )
        assert len(r.json()["projections"]) == 3

        # 9. Verify final balance (TreasuryFlow has 2 incomes + 2 expenses = 4 transactions)
        r = client.get("/api/treasury/balance")
        assert r.json()["transaction_count"] == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

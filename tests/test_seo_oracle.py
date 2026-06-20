"""Tests for SEOOracle — High-CPC Niche Research & Yield Projection Engine."""

import sys
import os
from decimal import Decimal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from modulos.seo_oracle import SEOOracle, TrafficDifficulty


# ================================================================
# FIXTURES
# ================================================================

@pytest.fixture
def oracle():
    return SEOOracle()


# ================================================================
# NICHE DATA TESTS
# ================================================================

class TestNicheData:
    def test_niches_populated(self, oracle):
        """Should have pre-loaded niches."""
        assert len(oracle.NICHES_DB) > 0

    def test_niches_have_all_fields(self, oracle):
        for n in oracle.NICHES_DB:
            assert n.id
            assert n.name
            assert n.category
            assert len(n.keywords) > 0
            assert n.cpc_min > 0
            assert n.cpc_max >= n.cpc_min
            assert n.cpc_avg > 0
            assert n.search_volume in ("bajo", "medio", "alto", "muy_alto")
            assert isinstance(n.difficulty, TrafficDifficulty)
            assert 1 <= n.evergreen_score <= 10
            assert n.language in ("es", "en", "ambos")

    def test_cpc_range_string_format(self, oracle):
        n = oracle.NICHES_DB[0]
        assert "$" in n.cpc_range_str
        assert "-" in n.cpc_range_str

    def test_profitability_score_positive(self, oracle):
        for n in oracle.NICHES_DB:
            assert n.profitability_score > 0

    def test_best_niche_is_personal_injury(self, oracle):
        """Highest CPC niche should be personal-injury-law."""
        ranked = oracle.rank_niches_by_profitability()
        assert ranked[0]["id"] == "personal-injury-law"
        assert ranked[0]["cpc_avg"] >= 200


# ================================================================
# FILTER TESTS
# ================================================================

class TestFilters:
    def test_get_top_niches_min_cpc(self, oracle):
        niches = oracle.get_top_niches(min_cpc=Decimal("150"))
        for n in niches:
            assert n.cpc_avg >= 150

    def test_get_top_niches_default(self, oracle):
        niches = oracle.get_top_niches()
        assert len(niches) >= 5  # Most should be above $80

    def test_get_top_niches_includes_low_cpc(self, oracle):
        niches = oracle.get_top_niches(min_cpc=Decimal("50"))
        assert len(niches) == len(oracle.NICHES_DB)

    def test_get_niches_by_category_legal(self, oracle):
        legal = oracle.get_niches_by_category("Servicios Legales")
        for n in legal:
            assert n.category == "Servicios Legales"
        assert len(legal) >= 2  # At least asset-recovery + personal-injury

    def test_get_niches_by_category_tech(self, oracle):
        tech = oracle.get_niches_by_category("Tecnología B2B")
        assert len(tech) >= 1

    def test_get_niches_by_category_empty(self, oracle):
        empty = oracle.get_niches_by_category("NoExiste")
        assert len(empty) == 0


# ================================================================
# RANKING TESTS
# ================================================================

class TestRanking:
    def test_ranking_sorted_descending(self, oracle):
        ranked = oracle.rank_niches_by_profitability()
        scores = [n["profitability_score"] for n in ranked]
        assert scores == sorted(scores, reverse=True)

    def test_ranking_has_all_fields(self, oracle):
        ranked = oracle.rank_niches_by_profitability()
        for n in ranked:
            assert "id" in n
            assert "name" in n
            assert "cpc_avg" in n
            assert "profitability_score" in n
            assert "difficulty" in n
            assert "evergreen" in n
            assert "language" in n

    def test_ranking_all_niches_present(self, oracle):
        ranked = oracle.rank_niches_by_profitability()
        assert len(ranked) == len(oracle.NICHES_DB)

    def test_ranking_top_3_evergreen(self, oracle):
        """Top niches should be high evergreen score."""
        ranked = oracle.rank_niches_by_profitability()
        for n in ranked[:3]:
            assert n["evergreen"] >= 8


# ================================================================
# YIELD PROJECTION TESTS
# ================================================================

class TestYieldProjection:
    def test_projection_valid_niche(self, oracle):
        p = oracle.calculate_yield_projection(
            niche_id="personal-injury-law",
            monthly_visitors=5000,
            ctr_pct=Decimal("2.0"),
            nodes_count=3
        )
        assert p is not None
        assert p["niche"] == "Abogados de Accidentes (Personal Injury)"
        assert p["monthly_visitors_total"] == 15000

    def test_projection_invalid_niche(self, oracle):
        p = oracle.calculate_yield_projection(
            niche_id="invalid-niche",
            monthly_visitors=5000,
            ctr_pct=Decimal("2.0")
        )
        assert p is None

    def test_projection_revenue_positive(self, oracle):
        p = oracle.calculate_yield_projection(
            niche_id="asset-recovery",
            monthly_visitors=3000,
            ctr_pct=Decimal("2.0"),
            nodes_count=2
        )
        assert p["monthly_revenue"]["low"] > 0
        assert p["monthly_revenue"]["avg"] > 0
        assert p["monthly_revenue"]["high"] > 0

    def test_projection_high_gt_low(self, oracle):
        p = oracle.calculate_yield_projection(
            niche_id="cybersecurity-compliance",
            monthly_visitors=4000,
            ctr_pct=Decimal("2.5"),
            nodes_count=3
        )
        assert p["monthly_revenue"]["high"] >= p["monthly_revenue"]["avg"]
        assert p["monthly_revenue"]["avg"] >= p["monthly_revenue"]["low"]

    def test_projection_yearly_12x_monthly(self, oracle):
        p = oracle.calculate_yield_projection(
            niche_id="personal-injury-law",
            monthly_visitors=5000,
            ctr_pct=Decimal("2.0"),
            nodes_count=1
        )
        assert abs(p["yearly_revenue"]["avg"] - p["monthly_revenue"]["avg"] * 12) < 0.01

    def test_projection_clicks_calculation(self, oracle):
        p = oracle.calculate_yield_projection(
            niche_id="personal-injury-law",
            monthly_visitors=10000,
            ctr_pct=Decimal("3.0"),
            nodes_count=2
        )
        # CTR = 3%, so clicks = 20000 * 0.03 = 600
        assert p["clicks_monthly"] == 600

    def test_projection_confidence_levels(self, oracle):
        p1 = oracle.calculate_yield_projection("personal-injury-law", 5000, Decimal("2.0"))
        p2 = oracle.calculate_yield_projection("mesothelioma", 500, Decimal("1.0"))
        assert p1["confidence"] is not None
        assert p2["confidence"] is not None


# ================================================================
# CONTENT PLAN TESTS
# ================================================================

class TestContentPlan:
    def test_content_plan_single_niche(self, oracle):
        plan = oracle.create_content_plan(["personal-injury-law"])
        assert len(plan["nodes"]) == 1
        assert plan["total_monthly_visitors"] > 0
        assert plan["total_monthly_revenue"]["avg"] > 0

    def test_content_plan_multiple_niches(self, oracle):
        plan = oracle.create_content_plan([
            "personal-injury-law",
            "asset-recovery",
            "cybersecurity-compliance"
        ])
        assert len(plan["nodes"]) == 3
        assert plan["total_monthly_visitors"] > 0

    def test_content_plan_invalid_niche(self, oracle):
        plan = oracle.create_content_plan(["invalid-niche"])
        assert len(plan["nodes"]) == 0

    def test_content_plan_revenue_accumulation(self, oracle):
        plan = oracle.create_content_plan([
            "personal-injury-law",
            "asset-recovery"
        ])
        total_avg = sum(n["monthly_revenue"]["avg"] for n in plan["nodes"])
        assert abs(plan["total_monthly_revenue"]["avg"] - total_avg) < 0.01

    def test_content_plan_all_totals(self, oracle):
        plan = oracle.create_content_plan(["personal-injury-law"])
        assert "total_monthly_revenue" in plan
        assert "total_yearly_revenue" in plan
        assert "total_monthly_visitors" in plan
        assert "total_clicks" in plan


# ================================================================
# EVERGREEN TESTS
# ================================================================

class TestEvergreen:
    def test_evergreen_year_1(self, oracle):
        m = oracle.get_evergreen_multiplier(1)
        assert m == Decimal("1.00")

    def test_evergreen_year_3(self, oracle):
        m = oracle.get_evergreen_multiplier(3)
        # Should have some decay but still > 2x
        assert m > Decimal("1.50")

    def test_evergreen_year_10(self, oracle):
        m = oracle.get_evergreen_multiplier(10)
        assert m > Decimal("1.00")

    def test_evergreen_increasing_with_years(self, oracle):
        m1 = oracle.get_evergreen_multiplier(2)
        m5 = oracle.get_evergreen_multiplier(5)
        # Multiplier should be higher for more years
        assert m5 > m1


# ================================================================
# EXPORT TESTS
# ================================================================

class TestExport:
    def test_export_report(self, oracle, tmp_path):
        fp = str(tmp_path / "seo_report.json")
        r = oracle.export_report(fp)
        assert r["success"]
        assert os.path.exists(fp)

    def test_export_report_has_ranking(self, oracle, tmp_path):
        fp = str(tmp_path / "seo_report.json")
        oracle.export_report(fp)
        import json
        with open(fp) as f:
            data = json.load(f)
        assert "ranking" in data
        assert "niches" in data


# ================================================================
# EDGE CASE TESTS
# ================================================================

class TestEdgeCases:
    def test_oracle_reusable(self, oracle):
        """Oracle should produce consistent results on multiple calls."""
        r1 = oracle.rank_niches_by_profitability()
        r2 = oracle.rank_niches_by_profitability()
        assert r1 == r2

    def test_zero_visitors(self, oracle):
        p = oracle.calculate_yield_projection(
            niche_id="personal-injury-law",
            monthly_visitors=0,
            ctr_pct=Decimal("2.0")
        )
        assert p["clicks_monthly"] == 0
        assert p["monthly_revenue"]["avg"] == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

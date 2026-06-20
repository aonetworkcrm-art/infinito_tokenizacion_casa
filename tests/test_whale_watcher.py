"""Tests for WhaleWatcher — MEV Detection & Flash Loan Analysis Engine."""

import sys
import os
from decimal import Decimal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from modulos.whale_watcher import WhaleWatcher, WhaleCategory


# ================================================================
# FIXTURES
# ================================================================

@pytest.fixture
def watcher():
    return WhaleWatcher(network="polygon_amoy_testnet")


# ================================================================
# CLASSIFICATION TESTS
# ================================================================

class TestClassification:
    def test_classify_juvenil(self, watcher):
        """$5,000-$50,000 should be Juvenil."""
        assert watcher.classify_whale(Decimal("5000")) == WhaleCategory.JUVENIL
        assert watcher.classify_whale(Decimal("25000")) == WhaleCategory.JUVENIL
        assert watcher.classify_whale(Decimal("49999")) == WhaleCategory.JUVENIL

    def test_classify_azul(self, watcher):
        """$50,000-$250,000 should be Azul."""
        assert watcher.classify_whale(Decimal("50000")) == WhaleCategory.AZUL
        assert watcher.classify_whale(Decimal("150000")) == WhaleCategory.AZUL
        assert watcher.classify_whale(Decimal("249999")) == WhaleCategory.AZUL

    def test_classify_dorada(self, watcher):
        """$250,000-$1,000,000 should be Dorada."""
        assert watcher.classify_whale(Decimal("250000")) == WhaleCategory.DORADA
        assert watcher.classify_whale(Decimal("500000")) == WhaleCategory.DORADA
        assert watcher.classify_whale(Decimal("999999")) == WhaleCategory.DORADA

    def test_classify_mitica(self, watcher):
        """$1,000,000+ should be Mítica."""
        assert watcher.classify_whale(Decimal("1000000")) == WhaleCategory.MITICA
        assert watcher.classify_whale(Decimal("5000000")) == WhaleCategory.MITICA
        assert watcher.classify_whale(Decimal("10000000")) == WhaleCategory.MITICA

    def test_classify_boundary_just_below(self, watcher):
        """$4,999 should be below minimum (returns Juvenil but won't be detected)."""
        assert watcher.classify_whale(Decimal("4999")) == WhaleCategory.JUVENIL


# ================================================================
# DETECTION TESTS
# ================================================================

class TestDetection:
    def test_detect_valid_whale(self, watcher):
        w = watcher.detect_whale(
            tx_hash="0xtest123",
            from_addr="0xfrom",
            to_addr="0xto",
            value_usd=Decimal("100000"),
            gas_price_gwei=Decimal("50"),
            gas_limit=200000
        )
        assert w is not None
        assert w.category == WhaleCategory.AZUL
        assert w.value_usd == Decimal("100000")

    def test_detect_below_minimum(self, watcher):
        w = watcher.detect_whale(
            tx_hash="0xtest",
            from_addr="0xfrom",
            to_addr="0xto",
            value_usd=Decimal("100"),  # Below $5,000 minimum
            gas_price_gwei=Decimal("50"),
            gas_limit=200000
        )
        assert w is None

    def test_detect_exactly_minimum(self, watcher):
        w = watcher.detect_whale(
            tx_hash="0xtest",
            from_addr="0xfrom",
            to_addr="0xto",
            value_usd=Decimal("5000"),
            gas_price_gwei=Decimal("50"),
            gas_limit=200000
        )
        assert w is not None

    def test_detect_sets_category_emoji(self, watcher):
        w = watcher.detect_whale(
            tx_hash="0xtest",
            from_addr="0xfrom",
            to_addr="0xto",
            value_usd=Decimal("500000"),
            gas_price_gwei=Decimal("50"),
            gas_limit=200000
        )
        assert w.category_emoji is not None
        assert w.category == WhaleCategory.DORADA

    def test_detect_value_formatted(self, watcher):
        w = watcher.detect_whale(
            tx_hash="0xtest",
            from_addr="0xfrom",
            to_addr="0xto",
            value_usd=Decimal("1500000"),
            gas_price_gwei=Decimal("50"),
            gas_limit=200000
        )
        assert "M" in w.value_formatted  # Should show as 1.50M

    def test_detect_ranges(self, watcher):
        """Test detection across all value ranges."""
        cases = [
            (Decimal("5000"), WhaleCategory.JUVENIL),
            (Decimal("50000"), WhaleCategory.AZUL),
            (Decimal("250000"), WhaleCategory.DORADA),
            (Decimal("1000000"), WhaleCategory.MITICA),
        ]
        for value, expected_cat in cases:
            w = watcher.detect_whale(
                tx_hash="0xtest",
                from_addr="0xfrom",
                to_addr="0xto",
                value_usd=value,
                gas_price_gwei=Decimal("50"),
                gas_limit=200000
            )
            assert w is not None
            assert w.category == expected_cat


# ================================================================
# FLASH LOAN TESTS
# ================================================================

class TestFlashLoan:
    def test_flash_loan_only_on_opportunity(self, watcher):
        """Non-opportunity whales should return None."""
        for _ in range(100):
            w = watcher.detect_whale(
                tx_hash="0xtest",
                from_addr="0xfrom",
                to_addr="0xto",
                value_usd=Decimal("100000"),
                gas_price_gwei=Decimal("50"),
                gas_limit=200000
            )
            opp = watcher.analyze_flash_loan_opportunity(w)
            if not w.is_flash_loan_opportunity:
                assert opp is None

    def test_flash_loan_profitable(self, watcher):
        """Flash loan should have positive expected profit."""
        found = False
        for _ in range(200):
            w = watcher.detect_whale(
                tx_hash="0xtest",
                from_addr="0xfrom",
                to_addr="0xto",
                value_usd=Decimal("200000"),
                gas_price_gwei=Decimal("50"),
                gas_limit=200000,
                token_address="0x7ceb23fd6bc0add59e62ac25578270cff1b9f619"
            )
            if w.is_flash_loan_opportunity:
                opp = watcher.analyze_flash_loan_opportunity(w)
                if opp:
                    found = True
                    assert opp.net_profit_usd >= Decimal("0")
                    assert opp.roi_percent >= Decimal("0")
                    break
        assert found, "No profitable flash loan opportunity found in 200 attempts"

    def test_flash_loan_has_dex_path(self, watcher):
        """Flash loan should have at least 2 DEXes in path."""
        for _ in range(200):
            w = watcher.detect_whale(
                tx_hash="0xtest",
                from_addr="0xfrom",
                to_addr="0xto",
                value_usd=Decimal("250000"),
                gas_price_gwei=Decimal("50"),
                gas_limit=200000
            )
            if w.is_flash_loan_opportunity:
                opp = watcher.analyze_flash_loan_opportunity(w)
                if opp:
                    assert len(opp.dex_path) >= 2
                    break


# ================================================================
# SIMULATION TESTS
# ================================================================

class TestSimulation:
    def test_simulate_mempool_scan_count(self, watcher):
        whales = watcher.simulate_mempool_scan(count=50)
        assert len(whales) > 0
        assert len(whales) <= 50

    def test_simulate_all_categories_present(self, watcher):
        """Large scan should produce all categories."""
        whales = watcher.simulate_mempool_scan(count=200)
        categories = set(w.category for w in whales)
        assert WhaleCategory.JUVENIL in categories
        assert WhaleCategory.AZUL in categories
        assert WhaleCategory.DORADA in categories

    def test_simulate_increases_counters(self, watcher):
        watcher.simulate_mempool_scan(count=50)
        s = watcher.get_whale_summary()
        assert s["total_whales_detected"] > 0


# ================================================================
# SUMMARY TESTS
# ================================================================

class TestSummary:
    def test_summary_fields(self, watcher):
        s = watcher.get_whale_summary()
        assert "network" in s
        assert "total_whales_detected" in s
        assert "total_whales_hunted" in s
        assert "total_profits_usd" in s
        assert "profitable_opportunities" in s
        assert "categories" in s

    def test_summary_categories(self, watcher):
        watcher.simulate_mempool_scan(count=100)
        s = watcher.get_whale_summary()
        cats = s["categories"]
        assert len(cats) > 0

    def test_export_report(self, watcher, tmp_path):
        watcher.simulate_mempool_scan(count=10)
        fp = str(tmp_path / "whale_report.json")
        r = watcher.export_report(fp)
        assert r["success"]
        assert os.path.exists(fp)

    def test_empty_state(self, watcher):
        """Summary on fresh watcher should have zeros."""
        s = watcher.get_whale_summary()
        assert s["total_whales_detected"] == 0
        assert s["total_profits_usd"] == 0.0


# ================================================================
# DEX POOLS TESTS
# ================================================================

class TestDEXPools:
    def test_known_dex_pools(self, watcher):
        assert "quickSwap" in watcher.dex_pools
        assert "sushiSwap" in watcher.dex_pools
        assert len(watcher.dex_pools) == 4

    def test_dex_pool_fees(self, watcher):
        for name, pool in watcher.dex_pools.items():
            assert pool["fee"] > 0
            assert 0 <= pool["liquidity_score"] <= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

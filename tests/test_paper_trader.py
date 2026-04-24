import pytest
import os
from src.paper_trader import PaperTrader, PaperTrade

@pytest.fixture
def temp_trader(tmp_path):
    data_file = tmp_path / "test_trades.json"
    return PaperTrader(str(data_file))

def test_calculate_stats_no_trades(temp_trader):
    stats = temp_trader.calculate_stats()
    # Expected final keys after unification
    expected_keys = {
        "total_trades", "wins", "losses", "win_rate",
        "avg_profit_pct", "total_profit_pct", "best_trade", "worst_trade"
    }
    assert set(stats.keys()) == expected_keys
    assert stats["total_trades"] == 0
    assert stats["win_rate"] == 0
    assert stats["avg_profit_pct"] == 0
    assert stats["total_profit_pct"] == 0
    assert stats["wins"] == 0
    assert stats["losses"] == 0
    assert stats["best_trade"] == 0
    assert stats["worst_trade"] == 0

def test_calculate_stats_single_win(temp_trader):
    # Add a trade and manually close it as WON
    trade = temp_trader.add_trade(
        symbol="AAPL", action="BUY", entry_price=100,
        stop_loss=90, take_profit=110, confidence=80,
        pattern="TEST", signals=[]
    )
    temp_trader.close_trade_manually(trade.id, 110, reason="WON")

    stats = temp_trader.calculate_stats()
    assert stats["total_trades"] == 1
    assert stats["wins"] == 1
    assert stats["losses"] == 0
    assert stats["win_rate"] == 100.0
    assert stats["avg_profit_pct"] == 10.0
    assert stats["total_profit_pct"] == 10.0
    assert stats["best_trade"] == 10.0
    assert stats["worst_trade"] == 10.0

def test_calculate_stats_single_loss(temp_trader):
    # Add a trade and manually close it as STOPPED
    trade = temp_trader.add_trade(
        symbol="AAPL", action="BUY", entry_price=100,
        stop_loss=90, take_profit=110, confidence=80,
        pattern="TEST", signals=[]
    )
    temp_trader.close_trade_manually(trade.id, 90, reason="STOPPED")

    stats = temp_trader.calculate_stats()
    assert stats["total_trades"] == 1
    assert stats["wins"] == 0
    assert stats["losses"] == 1
    assert stats["win_rate"] == 0.0
    assert stats["avg_profit_pct"] == -10.0
    assert stats["total_profit_pct"] == -10.0
    assert stats["best_trade"] == -10.0
    assert stats["worst_trade"] == -10.0

def test_calculate_stats_mixed(temp_trader):
    # Win: +10%
    t1 = temp_trader.add_trade("T1", "BUY", 100, 90, 110, 80, "P1", [])
    temp_trader.close_trade_manually(t1.id, 110, "WON")

    # Loss (STOPPED): -5%
    t2 = temp_trader.add_trade("T2", "BUY", 100, 95, 110, 80, "P2", [])
    temp_trader.close_trade_manually(t2.id, 95, "STOPPED")

    # Loss (LOST): -20%
    t3 = temp_trader.add_trade("T3", "BUY", 100, 80, 120, 80, "P3", [])
    temp_trader.close_trade_manually(t3.id, 80, "LOST")

    stats = temp_trader.calculate_stats()
    assert stats["total_trades"] == 3
    assert stats["wins"] == 1
    assert stats["losses"] == 2
    assert pytest.approx(stats["win_rate"]) == 33.33333333333333
    assert pytest.approx(stats["avg_profit_pct"]) == (10 - 5 - 20) / 3
    assert stats["total_profit_pct"] == (10 - 5 - 20)
    assert stats["best_trade"] == 10.0
    assert stats["worst_trade"] == -20.0

import pytest
from src.pattern_detector import PatternDetector, DetectionResult

@pytest.fixture
def detector():
    return PatternDetector()

def test_detect_pump_and_dump(detector):
    # Case 1: Volume spike + Rapid movement (triggered)
    analysis = {
        "volume_profile": {"is_spike": True, "volume_ratio": 3.5},
        "price_velocity": {"is_rapid_movement": True, "avg_pct_change": 5.5, "direction": "up"},
        "social_sentiment": {"mention_count": 25}
    }
    result = detector.detect_pump_and_dump(analysis)
    assert result is not None
    assert result.pattern_type == "PUMP_AND_DUMP"
    assert result.recommendation == "AVOID"

    # Case 2: Only one signal (not triggered)
    analysis = {
        "volume_profile": {"is_spike": True, "volume_ratio": 3.5},
        "price_velocity": {"is_rapid_movement": False},
        "social_sentiment": {"mention_count": 5}
    }
    result = detector.detect_pump_and_dump(analysis)
    assert result is None

def test_detect_whale_accumulation(detector):
    # Case 1: Steady volume + Price stability + Gradual uptrend (triggered)
    candles = [{"close": 100}] * 11
    candles[-1] = {"close": 102}
    analysis = {
        "volume_profile": {"volume_ratio": 1.5},
        "price_velocity": {"avg_pct_change": 0.5},
        "candles": candles
    }
    result = detector.detect_whale_accumulation(analysis)
    assert result is not None
    assert result.pattern_type == "WHALE_ACCUMULATION"
    assert result.recommendation == "BUY"

    # Case 2: Insufficient data
    analysis = {"candles": [{"close": 100}] * 5}
    result = detector.detect_whale_accumulation(analysis)
    assert result is None

def test_detect_unusual_activity(detector):
    analysis = {
        "volume_profile": {"volume_ratio": 2.0},
        "price_velocity": {"avg_pct_change": 2.0},
        "social_sentiment": {"mention_count": 15}
    }
    result = detector.detect_unusual_activity(analysis)
    assert result is not None
    assert result.pattern_type == "UNUSUAL_ACTIVITY"
    assert result.recommendation == "WATCH"

def test_analyze_pattern_priority(detector):
    # Both Pump and Unusual match, Pump should win (higher confidence)
    analysis = {
        "symbol": "TEST",
        "volume_profile": {"is_spike": True, "volume_ratio": 4.0},
        "price_velocity": {"is_rapid_movement": True, "avg_pct_change": 10.0, "direction": "up"},
        "social_sentiment": {"mention_count": 50},
        "candles": [{"close": 100}] * 11
    }
    result = detector.analyze_pattern(analysis)
    assert result.pattern_type == "PUMP_AND_DUMP"
    assert len(detector.get_history()) == 1

def test_analyze_pattern_normal(detector):
    analysis = {
        "volume_profile": {"volume_ratio": 1.0},
        "price_velocity": {"avg_pct_change": 0.1},
        "social_sentiment": {"mention_count": 0}
    }
    result = detector.analyze_pattern(analysis)
    assert result.pattern_type == "NORMAL"
    assert result.recommendation == "HOLD"

def test_calculate_trade_signal(detector):
    # BUY
    res_buy = DetectionResult("WHALE", 80, [], "BUY", "MEDIUM")
    sig_buy = detector.calculate_trade_signal(res_buy, 100.0)
    assert sig_buy["action"] == "BUY"
    assert sig_buy["entry"] == pytest.approx(101.0)

    # SHORT
    res_short = DetectionResult("PUMP", 80, [], "SHORT", "HIGH")
    sig_short = detector.calculate_trade_signal(res_short, 100.0)
    assert sig_short["action"] == "SHORT"
    assert sig_short["entry"] == pytest.approx(98.0)

    # AVOID
    res_avoid = DetectionResult("PUMP", 90, [], "AVOID", "CRITICAL")
    sig_avoid = detector.calculate_trade_signal(res_avoid, 100.0)
    assert sig_avoid["action"] == "AVOID"

    # WATCH
    res_watch = DetectionResult("UNUSUAL", 50, ["Signal"], "WATCH", "MEDIUM", "1h")
    sig_watch = detector.calculate_trade_signal(res_watch, 100.0)
    assert sig_watch["action"] == "WATCH"

def test_get_history(detector):
    analysis = {
        "symbol": "AAPL",
        "volume_profile": {"volume_ratio": 1.0},
        "price_velocity": {"avg_pct_change": 0.1}
    }
    detector.analyze_pattern(analysis)

    assert len(detector.get_history()) == 0 # NORMAL is not added to history based on code

    # Trigger a pattern
    analysis_pump = {
        "symbol": "GME",
        "volume_profile": {"is_spike": True, "volume_ratio": 5.0},
        "price_velocity": {"is_rapid_movement": True, "avg_pct_change": 10.0, "direction": "up"},
        "social_sentiment": {"mention_count": 100}
    }
    detector.analyze_pattern(analysis_pump)
    assert len(detector.get_history()) == 1
    assert detector.get_history("GME")[0]["symbol"] == "GME"
    assert len(detector.get_history("AAPL")) == 0

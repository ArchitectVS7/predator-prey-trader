import pytest
from src.pattern_detector import PatternDetector, DetectionResult

@pytest.fixture
def detector():
    return PatternDetector()

def test_detect_pump_and_dump_no_signals(detector):
    analysis = {
        "volume_profile": {},
        "price_velocity": {},
        "social_sentiment": {}
    }
    result = detector.detect_pump_and_dump(analysis)
    assert result is None

def test_detect_pump_and_dump_volume_spike_only(detector):
    analysis = {
        "volume_profile": {"is_spike": True, "volume_ratio": 3.5},
        "price_velocity": {},
        "social_sentiment": {}
    }
    # confidence = 30, len(signals) = 1
    result = detector.detect_pump_and_dump(analysis)
    assert result is None

def test_detect_pump_and_dump_volume_and_social(detector):
    analysis = {
        "volume_profile": {"is_spike": True, "volume_ratio": 3.5},
        "price_velocity": {},
        "social_sentiment": {"mention_count": 25}
    }
    # confidence = 30 + 20 = 50, len(signals) = 2
    result = detector.detect_pump_and_dump(analysis)
    assert result is not None
    assert result.pattern_type == "PUMP_AND_DUMP"
    assert result.confidence == 50
    assert "Volume spike: 3.5x average" in result.signals
    assert "High social activity: 25 mentions" in result.signals

def test_detect_pump_and_dump_price_and_social_below_threshold(detector):
    analysis = {
        "volume_profile": {},
        "price_velocity": {"is_rapid_movement": True, "avg_pct_change": 6.0},
        "social_sentiment": {"mention_count": 25}
    }
    # confidence = 25 + 20 = 45, len(signals) = 2.
    # Threshold is confidence >= 50.
    result = detector.detect_pump_and_dump(analysis)
    assert result is None

def test_detect_pump_and_dump_volume_and_price(detector):
    analysis = {
        "volume_profile": {"is_spike": True, "volume_ratio": 4.0},
        "price_velocity": {"is_rapid_movement": True, "avg_pct_change": 7.0, "direction": "up"},
        "social_sentiment": {}
    }
    # confidence = 30 + 25 = 55, len(signals) = 2
    result = detector.detect_pump_and_dump(analysis)
    assert result is not None
    assert result.confidence == 55
    assert result.recommendation == "AVOID"

def test_detect_pump_and_dump_all_signals(detector):
    analysis = {
        "volume_profile": {"is_spike": True, "volume_ratio": 5.0},
        "price_velocity": {"is_rapid_movement": True, "avg_pct_change": 8.0, "direction": "up"},
        "social_sentiment": {"mention_count": 50}
    }
    # confidence = 30 + 25 + 20 = 75, len(signals) = 3
    result = detector.detect_pump_and_dump(analysis)
    assert result is not None
    assert result.confidence == 75
    assert len(result.signals) == 3

def test_detect_pump_and_dump_short_recommendation(detector):
    analysis = {
        "volume_profile": {"is_spike": True, "volume_ratio": 4.0},
        "price_velocity": {"is_rapid_movement": True, "avg_pct_change": -7.0, "direction": "down"},
        "social_sentiment": {"mention_count": 25}
    }
    # confidence = 30 + 25 + 20 = 75
    result = detector.detect_pump_and_dump(analysis)
    assert result is not None
    assert result.recommendation == "SHORT"

def test_detect_pump_and_dump_social_sentiment_error(detector):
    # Test that it handles "error" in social_sentiment
    analysis = {
        "volume_profile": {"is_spike": True, "volume_ratio": 3.5},
        "price_velocity": {"is_rapid_movement": True, "avg_pct_change": 6.0},
        "social_sentiment": {"error": "API down", "mention_count": 100} # should ignore mention_count
    }
    # confidence = 30 + 25 = 55
    result = detector.detect_pump_and_dump(analysis)
    assert result is not None
    assert result.confidence == 55
    assert len(result.signals) == 2

import pytest
from src.pattern_detector import PatternDetector, DetectionResult

@pytest.fixture
def detector():
    return PatternDetector()

def test_calculate_trade_signal_avoid(detector):
    detection = DetectionResult(
        pattern_type="PUMP_AND_DUMP",
        confidence=90.0,
        signals=["Signal 1", "Signal 2"],
        recommendation="AVOID",
        risk_level="CRITICAL"
    )
    current_price = 100.0
    signal = detector.calculate_trade_signal(detection, current_price)

    assert signal["action"] == "AVOID"
    assert signal["entry"] is None
    assert signal["stop_loss"] is None
    assert signal["take_profit"] is None
    assert "reason" in signal

def test_calculate_trade_signal_short(detector):
    detection = DetectionResult(
        pattern_type="PUMP_AND_DUMP",
        confidence=80.0,
        signals=["Signal 1", "Signal 2"],
        recommendation="SHORT",
        risk_level="HIGH"
    )
    current_price = 100.0
    signal = detector.calculate_trade_signal(detection, current_price)

    assert signal["action"] == "SHORT"
    assert signal["entry"] == pytest.approx(98.0)
    assert signal["stop_loss"] == pytest.approx(105.0)
    assert signal["take_profit"] == pytest.approx(85.0)
    assert signal["confidence"] == 80.0
    # risk_reward = abs((85 - 98) / (105 - 98)) = 13 / 7 approx 1.857
    assert signal["risk_reward"] == pytest.approx(13/7)

def test_calculate_trade_signal_buy(detector):
    detection = DetectionResult(
        pattern_type="WHALE_ACCUMULATION",
        confidence=75.0,
        signals=["Signal 1", "Signal 2"],
        recommendation="BUY",
        risk_level="MEDIUM"
    )
    current_price = 100.0
    signal = detector.calculate_trade_signal(detection, current_price)

    assert signal["action"] == "BUY"
    assert signal["entry"] == pytest.approx(101.0)
    assert signal["stop_loss"] == pytest.approx(95.0)
    assert signal["take_profit"] == pytest.approx(115.0)
    assert signal["confidence"] == 75.0
    # risk_reward = abs((115 - 101) / (101 - 95)) = 14 / 6 approx 2.333
    assert signal["risk_reward"] == pytest.approx(14/6)

def test_calculate_trade_signal_watch(detector):
    detection = DetectionResult(
        pattern_type="UNUSUAL_ACTIVITY",
        confidence=50.0,
        signals=["Signal 1", "Signal 2"],
        recommendation="WATCH",
        risk_level="MEDIUM",
        timeframe="1-2 hours"
    )
    current_price = 100.0
    signal = detector.calculate_trade_signal(detection, current_price)

    assert signal["action"] == "WATCH"
    assert signal["entry"] is None
    assert signal["reason"] == ["Signal 1", "Signal 2"]
    assert signal["timeframe"] == "1-2 hours"

def test_calculate_trade_signal_hold(detector):
    detection = DetectionResult(
        pattern_type="NORMAL",
        confidence=70.0,
        signals=["No manipulation patterns detected"],
        recommendation="HOLD",
        risk_level="LOW"
    )
    current_price = 100.0
    signal = detector.calculate_trade_signal(detection, current_price)

    assert signal["action"] == "HOLD"
    assert signal["entry"] is None
    assert "reason" in signal

def test_calculate_trade_signal_default(detector):
    # Testing unknown recommendation
    detection = DetectionResult(
        pattern_type="UNKNOWN",
        confidence=0.0,
        signals=[],
        recommendation="UNKNOWN",
        risk_level="LOW"
    )
    current_price = 100.0
    signal = detector.calculate_trade_signal(detection, current_price)

    assert signal["action"] == "HOLD"
    assert signal["entry"] is None

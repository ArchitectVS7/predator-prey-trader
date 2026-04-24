#!/usr/bin/env python3
"""
Pattern Detector for Predator-Prey Trade Analyzer
Detects manipulation patterns: pumps, whale accumulation, coordinated behavior
"""

from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class DetectionResult:
    """Pattern detection result"""
    pattern_type: str  # pump, whale_accumulation, insider, normal
    confidence: float  # 0-100
    signals: List[str]  # What triggered detection
    recommendation: str  # BUY, SELL, HOLD, AVOID
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    timeframe: Optional[str] = None  # When to act
    
    def to_dict(self) -> Dict:
        return {
            "pattern": self.pattern_type,
            "confidence": self.confidence,
            "signals": self.signals,
            "recommendation": self.recommendation,
            "risk": self.risk_level,
            "timeframe": self.timeframe
        }


class PatternDetector:
    """Detect market manipulation patterns"""
    
    def __init__(self):
        self.detection_history = []
    
    def detect_pump_and_dump(self, analysis: Dict) -> Optional[DetectionResult]:
        """
        Detect coordinated pump & dump pattern
        
        Signals:
        - Sudden volume spike (>3x average)
        - Rapid price increase (>5% in short time)
        - High social media activity
        - No fundamental news catalyst
        """
        signals = []
        confidence = 0
        
        vol = analysis.get("volume_profile", {})
        vel = analysis.get("price_velocity", {})
        sent = analysis.get("social_sentiment", {})
        
        # Check volume spike
        if vol.get("is_spike", False):
            volume_ratio = vol.get("volume_ratio", 0)
            signals.append(f"Volume spike: {volume_ratio:.1f}x average")
            confidence += 30
        
        # Check rapid price movement
        if vel.get("is_rapid_movement", False):
            avg_change = vel.get("avg_pct_change", 0)
            signals.append(f"Rapid price movement: {avg_change:+.1f}%")
            confidence += 25
        
        # Check social activity
        mention_count = sent.get("mention_count", 0) if "error" not in sent else 0
        if mention_count > 20:  # High mention count
            signals.append(f"High social activity: {mention_count} mentions")
            confidence += 20
        
        # Pump requires multiple signals
        if len(signals) >= 2 and confidence >= 50:
            return DetectionResult(
                pattern_type="PUMP_AND_DUMP",
                confidence=min(confidence, 95),  # Cap at 95%
                signals=signals,
                recommendation="AVOID" if vel.get("direction") == "up" else "SHORT",
                risk_level="CRITICAL",
                timeframe="30-60 minutes until dump"
            )
        
        return None
    
    def detect_whale_accumulation(self, analysis: Dict) -> Optional[DetectionResult]:
        """
        Detect whale quietly accumulating
        
        Signals:
        - Steady volume above average
        - Price stable or slowly rising
        - No major price volatility
        - Pattern over multiple hours/days
        """
        signals = []
        confidence = 0
        
        vol = analysis.get("volume_profile", {})
        vel = analysis.get("price_velocity", {})
        candles = analysis.get("candles", [])
        
        if not candles or len(candles) < 10:
            return None
        
        # Check for steady volume
        volume_ratio = vol.get("volume_ratio", 0)
        if 1.2 <= volume_ratio <= 2.0:  # Above average but not spiking
            signals.append(f"Steady elevated volume: {volume_ratio:.1f}x")
            confidence += 25
        
        # Check for price stability
        avg_change = abs(vel.get("avg_pct_change", 0))
        if avg_change < 1.0:  # Stable price
            signals.append(f"Price stable: {avg_change:.2f}% avg change")
            confidence += 20
        
        # Check for gradual upward trend
        recent_prices = [c["close"] for c in candles[-10:] if c.get("close")]
        if len(recent_prices) >= 5:
            trend = (recent_prices[-1] - recent_prices[0]) / recent_prices[0] * 100
            if 0.5 <= trend <= 3.0:  # Slow steady rise
                signals.append(f"Gradual uptrend: {trend:.1f}%")
                confidence += 25
        
        if len(signals) >= 2 and confidence >= 50:
            return DetectionResult(
                pattern_type="WHALE_ACCUMULATION",
                confidence=min(confidence, 85),
                signals=signals,
                recommendation="BUY",
                risk_level="MEDIUM",
                timeframe="Entry within 24 hours"
            )
        
        return None
    
    def detect_unusual_activity(self, analysis: Dict) -> Optional[DetectionResult]:
        """
        Detect unusual activity that doesn't fit clear patterns
        
        Signals:
        - Any combination of anomalous metrics
        - Requires investigation
        """
        signals = []
        confidence = 0
        
        vol = analysis.get("volume_profile", {})
        vel = analysis.get("price_velocity", {})
        sent = analysis.get("social_sentiment", {})
        
        # Volume anomaly (but not extreme spike)
        volume_ratio = vol.get("volume_ratio", 0)
        if 1.5 <= volume_ratio < 3.0:
            signals.append(f"Elevated volume: {volume_ratio:.1f}x")
            confidence += 15
        
        # Price movement (but not rapid)
        avg_change = abs(vel.get("avg_pct_change", 0))
        if 1.0 <= avg_change < 3.0:
            signals.append(f"Notable price movement: {avg_change:.1f}%")
            confidence += 15
        
        # Social activity
        mention_count = sent.get("mention_count", 0) if "error" not in sent else 0
        if 10 <= mention_count < 20:
            signals.append(f"Moderate social activity: {mention_count} mentions")
            confidence += 10
        
        if len(signals) >= 2 and confidence >= 30:
            return DetectionResult(
                pattern_type="UNUSUAL_ACTIVITY",
                confidence=min(confidence, 60),
                signals=signals,
                recommendation="WATCH",
                risk_level="MEDIUM",
                timeframe="Monitor for 1-2 hours"
            )
        
        return None
    
    def analyze_pattern(self, analysis: Dict) -> DetectionResult:
        """
        Main pattern analysis function
        Returns the highest-confidence detection or NORMAL
        """
        detections = []
        
        # Try each pattern detector
        pump = self.detect_pump_and_dump(analysis)
        if pump:
            detections.append(pump)
        
        whale = self.detect_whale_accumulation(analysis)
        if whale:
            detections.append(whale)
        
        unusual = self.detect_unusual_activity(analysis)
        if unusual:
            detections.append(unusual)
        
        # Return highest confidence detection
        if detections:
            best = max(detections, key=lambda d: d.confidence)
            self.detection_history.append({
                "timestamp": datetime.now().isoformat(),
                "symbol": analysis.get("symbol"),
                "detection": best.to_dict()
            })
            return best
        
        # No patterns detected - normal market behavior
        return DetectionResult(
            pattern_type="NORMAL",
            confidence=70.0,
            signals=["No manipulation patterns detected"],
            recommendation="HOLD",
            risk_level="LOW",
            timeframe=None
        )
    
    def calculate_trade_signal(self, detection: DetectionResult, 
                              current_price: float) -> Dict:
        """
        Convert detection into actionable trade signal
        
        Returns:
            entry_price, stop_loss, take_profit, position_size, risk_reward
        """
        if detection.recommendation == "AVOID":
            return {
                "action": "AVOID",
                "reason": "Pump & dump detected - high risk",
                "entry": None,
                "stop_loss": None,
                "take_profit": None
            }
        
        elif detection.recommendation == "SHORT":
            # Short play on pump collapse
            entry = current_price * 0.98  # Enter slightly below current
            stop_loss = current_price * 1.05  # 5% stop loss
            take_profit = current_price * 0.85  # 15% profit target
            
            return {
                "action": "SHORT",
                "entry": entry,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "risk_reward": abs((take_profit - entry) / (stop_loss - entry)),
                "confidence": detection.confidence
            }
        
        elif detection.recommendation == "BUY":
            # Long play on whale accumulation
            entry = current_price * 1.01  # Enter slightly above to confirm
            stop_loss = current_price * 0.95  # 5% stop loss
            take_profit = current_price * 1.15  # 15% profit target
            
            return {
                "action": "BUY",
                "entry": entry,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "risk_reward": abs((take_profit - entry) / (entry - stop_loss)),
                "confidence": detection.confidence
            }
        
        elif detection.recommendation == "WATCH":
            return {
                "action": "WATCH",
                "reason": detection.signals,
                "entry": None,
                "timeframe": detection.timeframe
            }
        
        else:  # HOLD
            return {
                "action": "HOLD",
                "reason": "Normal market conditions",
                "entry": None
            }
    
    def get_history(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get detection history"""
        if symbol:
            return [h for h in self.detection_history if h.get("symbol") == symbol]
        return self.detection_history


if __name__ == "__main__":
    # Test pattern detector
    from data_fetcher import DataFetcher
    
    fetcher = DataFetcher()
    detector = PatternDetector()
    
    # Test with AAPL
    print("Analyzing AAPL...")
    analysis = fetcher.fetch_and_analyze("AAPL")
    
    if "error" not in analysis:
        detection = detector.analyze_pattern(analysis)
        
        print(f"\n🔍 DETECTION RESULT")
        print(f"Pattern: {detection.pattern_type}")
        print(f"Confidence: {detection.confidence:.1f}%")
        print(f"Risk: {detection.risk_level}")
        print(f"Recommendation: {detection.recommendation}")
        print(f"\nSignals:")
        for signal in detection.signals:
            print(f"  • {signal}")
        
        if detection.timeframe:
            print(f"\nTimeframe: {detection.timeframe}")
        
        # Generate trade signal
        current_price = analysis.get("current_price", 0)
        trade_signal = detector.calculate_trade_signal(detection, current_price)
        
        print(f"\n📊 TRADE SIGNAL")
        print(f"Action: {trade_signal['action']}")
        
        if trade_signal.get("entry"):
            print(f"Entry: ${trade_signal['entry']:.2f}")
            print(f"Stop Loss: ${trade_signal['stop_loss']:.2f}")
            print(f"Take Profit: ${trade_signal['take_profit']:.2f}")
            print(f"Risk/Reward: {trade_signal['risk_reward']:.2f}")

#!/usr/bin/env python3
"""
CLI Dashboard for Predator-Prey Trade Analyzer
Shows real-time analysis, detections, and paper trading results
"""

import sys
import time
from datetime import datetime
from typing import List

from data_fetcher import DataFetcher, CryptoDataFetcher
from pattern_detector import PatternDetector
from paper_trader import PaperTrader


class Dashboard:
    """CLI Dashboard for trade analysis"""
    
    def __init__(self):
        self.fetcher = DataFetcher()
        self.crypto_fetcher = CryptoDataFetcher()
        self.detector = PatternDetector()
        self.trader = PaperTrader("data/paper_trades.json")
        self.watchlist = []
    
    def print_header(self):
        """Print dashboard header"""
        print("\n" + "="*70)
        print("  🦅 PREDATOR-PREY TRADE ANALYZER")
        print("  Phase 1: Pattern Detection & Paper Trading")
        print("="*70 + "\n")
    
    def analyze_symbol(self, symbol: str, auto_trade: bool = False):
        """Analyze a symbol and optionally create paper trade"""
        print(f"\n{'─'*70}")
        print(f"📊 Analyzing {symbol}...")
        print(f"{'─'*70}\n")
        
        # Fetch and analyze
        analysis = self.fetcher.fetch_and_analyze(symbol)
        
        if "error" in analysis:
            print(f"❌ Error: {analysis['error']}")
            return None
        
        # Detect patterns
        detection = self.detector.analyze_pattern(analysis)
        current_price = analysis.get("current_price", 0)
        
        # Display current price
        print(f"💰 Current Price: ${current_price:.2f}")
        print(f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Display volume profile
        vol = analysis.get("volume_profile", {})
        print(f"\n📈 Volume Profile:")
        print(f"  Average: {vol.get('avg_volume', 0):,.0f}")
        print(f"  Recent: {vol.get('recent_volume', 0):,.0f}")
        print(f"  Ratio: {vol.get('volume_ratio', 0):.2f}x")
        if vol.get('is_spike'):
            print(f"  ⚠️  VOLUME SPIKE DETECTED")
        
        # Display price velocity
        vel = analysis.get("price_velocity", {})
        print(f"\n🚀 Price Velocity:")
        print(f"  Avg Change: {vel.get('avg_pct_change', 0):+.2f}%")
        print(f"  Direction: {vel.get('direction', 'unknown').upper()}")
        if vel.get('is_rapid_movement'):
            print(f"  ⚠️  RAPID MOVEMENT DETECTED")
        
        # Display social sentiment
        sent = analysis.get("social_sentiment", {})
        if "error" not in sent:
            print(f"\n💬 Social Sentiment (Reddit r/wallstreetbets):")
            print(f"  Mentions: {sent.get('mention_count', 0)}")
            print(f"  Total Score: {sent.get('total_score', 0)}")
            print(f"  Avg Upvote Ratio: {sent.get('avg_upvote_ratio', 0):.2f}")
        
        # Display detection
        self.print_detection(detection)
        
        # Generate trade signal
        trade_signal = self.detector.calculate_trade_signal(detection, current_price)
        self.print_trade_signal(trade_signal)
        
        # Auto-create paper trade if enabled
        if auto_trade and trade_signal["action"] in ["BUY", "SHORT"]:
            self.create_paper_trade(symbol, detection, trade_signal, current_price)
        
        return {
            "analysis": analysis,
            "detection": detection,
            "trade_signal": trade_signal
        }
    
    def print_detection(self, detection):
        """Print detection result"""
        print(f"\n🔍 PATTERN DETECTION")
        print(f"{'─'*70}")
        
        # Color code based on pattern
        pattern_emoji = {
            "PUMP_AND_DUMP": "🚨",
            "WHALE_ACCUMULATION": "🐋",
            "UNUSUAL_ACTIVITY": "👀",
            "NORMAL": "✅"
        }
        
        emoji = pattern_emoji.get(detection.pattern_type, "❓")
        print(f"{emoji} Pattern: {detection.pattern_type}")
        print(f"📊 Confidence: {detection.confidence:.1f}%")
        print(f"⚠️  Risk Level: {detection.risk_level}")
        print(f"💡 Recommendation: {detection.recommendation}")
        
        if detection.timeframe:
            print(f"⏰ Timeframe: {detection.timeframe}")
        
        print(f"\n📋 Signals Detected:")
        for signal in detection.signals:
            print(f"  • {signal}")
    
    def print_trade_signal(self, signal):
        """Print trade signal"""
        print(f"\n🎯 TRADE SIGNAL")
        print(f"{'─'*70}")
        
        action = signal["action"]
        
        if action == "AVOID":
            print(f"⛔ Action: AVOID")
            print(f"   Reason: {signal.get('reason', 'High risk detected')}")
        
        elif action in ["BUY", "SHORT"]:
            print(f"📈 Action: {action}")
            print(f"   Entry: ${signal['entry']:.2f}")
            print(f"   Stop Loss: ${signal['stop_loss']:.2f}")
            print(f"   Take Profit: ${signal['take_profit']:.2f}")
            print(f"   Risk/Reward: {signal['risk_reward']:.2f}")
            print(f"   Confidence: {signal['confidence']:.1f}%")
        
        elif action == "WATCH":
            print(f"👀 Action: WATCH")
            print(f"   Monitor: {signal.get('timeframe', 'Next 1-2 hours')}")
        
        else:  # HOLD
            print(f"🤚 Action: HOLD")
            print(f"   Reason: Normal market conditions")
    
    def create_paper_trade(self, symbol, detection, signal, current_price):
        """Create paper trade from signal"""
        trade = self.trader.add_trade(
            symbol=symbol,
            action=signal["action"],
            entry_price=signal.get("entry", current_price),
            stop_loss=signal.get("stop_loss"),
            take_profit=signal.get("take_profit"),
            confidence=detection.confidence,
            pattern=detection.pattern_type,
            signals=detection.signals
        )
        
        print(f"\n📝 Paper Trade Created: {trade.id}")
        print(f"   Status: OPEN")
    
    def show_portfolio(self):
        """Show paper trading portfolio"""
        print(f"\n{'='*70}")
        print(f"📊 PAPER TRADING PORTFOLIO")
        print(f"{'='*70}\n")
        
        # Show stats
        stats = self.trader.calculate_stats()
        
        print(f"📈 Statistics:")
        print(f"  Total Trades: {stats['total_trades']}")
        print(f"  Wins: {stats['wins']} | Losses: {stats['losses']}")
        print(f"  Win Rate: {stats['win_rate']:.1f}%")
        print(f"  Avg Profit: {stats['avg_profit_pct']:+.2f}%")
        print(f"  Total Profit: {stats['total_profit_pct']:+.2f}%")
        
        if stats['best_trade'] != 0:
            print(f"  Best Trade: {stats['best_trade']:+.2f}%")
            print(f"  Worst Trade: {stats['worst_trade']:+.2f}%")
        
        # Show open trades
        open_trades = self.trader.get_open_trades()
        if open_trades:
            print(f"\n🟢 Open Trades ({len(open_trades)}):")
            for trade in open_trades[-5:]:  # Last 5
                print(f"  {trade.symbol} | {trade.action} @ ${trade.entry_price:.2f}")
                print(f"    Entry: {trade.timestamp[:19]}")
                print(f"    Pattern: {trade.pattern_detected}")
        
        # Show recent closed trades
        closed = self.trader.get_closed_trades()
        if closed:
            print(f"\n⚪ Recent Closed Trades ({len(closed)}):")
            for trade in closed[-5:]:  # Last 5
                status_emoji = "✅" if trade.status == "WON" else "❌"
                print(f"  {status_emoji} {trade.symbol} | {trade.action} | {trade.profit_loss_pct:+.2f}%")
    
    def update_open_trades(self):
        """Update all open trades with current prices"""
        open_trades = self.trader.get_open_trades()
        
        if not open_trades:
            print("No open trades to update.")
            return
        
        print(f"\nUpdating {len(open_trades)} open trades...")
        
        for trade in open_trades:
            # Fetch current price
            analysis = self.fetcher.fetch_and_analyze(trade.symbol)
            
            if "error" in analysis:
                continue
            
            current_price = analysis.get("current_price", 0)
            updated = self.trader.update_trade(trade.id, current_price)
            
            if updated and updated.status != "OPEN":
                status_emoji = "✅" if updated.status == "WON" else "❌"
                print(f"{status_emoji} {updated.symbol} closed: {updated.profit_loss_pct:+.2f}%")
    
    def run_watchlist(self, symbols: List[str], interval: int = 300):
        """Monitor watchlist continuously"""
        self.watchlist = symbols
        
        print(f"\n🔍 Monitoring Watchlist:")
        for symbol in symbols:
            print(f"  • {symbol}")
        print(f"\nInterval: {interval} seconds")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                print(f"\n{'='*70}")
                print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"{'='*70}")
                
                for symbol in symbols:
                    try:
                        self.analyze_symbol(symbol, auto_trade=True)
                    except Exception as e:
                        print(f"Error analyzing {symbol}: {e}")
                
                # Update open trades
                self.update_open_trades()
                
                print(f"\n⏳ Next check in {interval} seconds...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\nStopping watchlist monitor.")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Predator-Prey Trade Analyzer")
    parser.add_argument('symbol', nargs='?', help='Stock symbol to analyze')
    parser.add_argument('--portfolio', action='store_true', help='Show portfolio')
    parser.add_argument('--watch', nargs='+', help='Monitor symbols')
    parser.add_argument('--interval', type=int, default=300, help='Watch interval (seconds)')
    parser.add_argument('--update', action='store_true', help='Update open trades')
    
    args = parser.parse_args()
    
    dashboard = Dashboard()
    dashboard.print_header()
    
    if args.portfolio:
        dashboard.show_portfolio()
    
    elif args.update:
        dashboard.update_open_trades()
        dashboard.show_portfolio()
    
    elif args.watch:
        dashboard.run_watchlist(args.watch, interval=args.interval)
    
    elif args.symbol:
        dashboard.analyze_symbol(args.symbol, auto_trade=False)
        print("\n" + "="*70)
        print("Tip: Use --watch to monitor continuously")
        print("="*70)
    
    else:
        print("Usage:")
        print("  python dashboard.py AAPL           # Analyze single symbol")
        print("  python dashboard.py --portfolio    # View portfolio")
        print("  python dashboard.py --watch AAPL GME  # Monitor symbols")
        print("  python dashboard.py --update       # Update open trades")


if __name__ == "__main__":
    main()

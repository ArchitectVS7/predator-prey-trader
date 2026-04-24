#!/usr/bin/env python3
"""
Paper Trading System - Track predictions without real money
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class PaperTrade:
    """Represents a paper trade"""
    id: str
    symbol: str
    action: str  # BUY, SHORT, AVOID, WATCH
    entry_price: float
    stop_loss: Optional[float]
    take_profit: Optional[float]
    confidence: float
    pattern_detected: str
    signals: List[str]
    timestamp: str
    status: str = "OPEN"  # OPEN, WON, LOST, STOPPED
    exit_price: Optional[float] = None
    exit_timestamp: Optional[str] = None
    profit_loss: Optional[float] = None
    profit_loss_pct: Optional[float] = None
    
    def close(self, exit_price: float, status: str) -> None:
        """Close the trade and calculate profit/loss"""
        self.status = status
        self.exit_price = exit_price
        self.exit_timestamp = datetime.now().isoformat()

        if self.action == "BUY":
            self.profit_loss = exit_price - self.entry_price
        elif self.action == "SHORT":
            self.profit_loss = self.entry_price - exit_price

        if self.entry_price > 0 and self.profit_loss is not None:
            self.profit_loss_pct = (self.profit_loss / self.entry_price) * 100

    def to_dict(self) -> Dict:
        return asdict(self)


class PaperTrader:
    """Manages paper trading portfolio"""
    
    def __init__(self, data_file: str = "paper_trades.json"):
        self.data_file = Path(data_file)
        self.trades: List[PaperTrade] = []
        self.load_trades()
    
    def load_trades(self):
        """Load trades from file"""
        if self.data_file.exists():
            with open(self.data_file) as f:
                data = json.load(f)
                self.trades = [PaperTrade(**t) for t in data]
    
    def save_trades(self):
        """Save trades to file"""
        with open(self.data_file, 'w') as f:
            json.dump([t.to_dict() for t in self.trades], f, indent=2)
    
    def add_trade(self, symbol: str, action: str, entry_price: float,
                  stop_loss: Optional[float], take_profit: Optional[float],
                  confidence: float, pattern: str, signals: List[str]) -> PaperTrade:
        """Add new paper trade"""
        trade_id = f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        trade = PaperTrade(
            id=trade_id,
            symbol=symbol,
            action=action,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            confidence=confidence,
            pattern_detected=pattern,
            signals=signals,
            timestamp=datetime.now().isoformat()
        )
        
        self.trades.append(trade)
        self.save_trades()
        
        return trade
    
    def update_trade(self, trade_id: str, current_price: float):
        """Update trade based on current price"""
        trade = next((t for t in self.trades if t.id == trade_id), None)
        
        if not trade or trade.status != "OPEN":
            return None
        
        # Check if stop loss or take profit hit
        if trade.action == "BUY":
            if trade.stop_loss and current_price <= trade.stop_loss:
                trade.close(trade.stop_loss, "STOPPED")
            elif trade.take_profit and current_price >= trade.take_profit:
                trade.close(trade.take_profit, "WON")
        
        elif trade.action == "SHORT":
            if trade.stop_loss and current_price >= trade.stop_loss:
                trade.close(trade.stop_loss, "STOPPED")
            elif trade.take_profit and current_price <= trade.take_profit:
                trade.close(trade.take_profit, "WON")
        
        self.save_trades()
        return trade
    
    def get_open_trades(self) -> List[PaperTrade]:
        """Get all open trades"""
        return [t for t in self.trades if t.status == "OPEN"]
    
    def get_closed_trades(self) -> List[PaperTrade]:
        """Get all closed trades"""
        return [t for t in self.trades if t.status != "OPEN"]
    
    def calculate_stats(self) -> Dict:
        """Calculate trading statistics"""
        closed = self.get_closed_trades()
        
        if not closed:
            return {
                "total_trades": 0,
                "win_rate": 0,
                "avg_profit": 0,
                "total_profit": 0
            }
        
        wins = [t for t in closed if t.status == "WON"]
        losses = [t for t in closed if t.status in ["LOST", "STOPPED"]]
        
        total_profit = sum(t.profit_loss_pct or 0 for t in closed)
        avg_profit = total_profit / len(closed)
        
        win_rate = (len(wins) / len(closed)) * 100 if closed else 0
        
        return {
            "total_trades": len(closed),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": win_rate,
            "avg_profit_pct": avg_profit,
            "total_profit_pct": total_profit,
            "best_trade": max((t.profit_loss_pct or 0 for t in closed), default=0),
            "worst_trade": min((t.profit_loss_pct or 0 for t in closed), default=0)
        }
    
    def get_trades_by_pattern(self, pattern: str) -> List[PaperTrade]:
        """Get trades filtered by pattern type"""
        return [t for t in self.trades if t.pattern_detected == pattern]
    
    def close_trade_manually(self, trade_id: str, exit_price: float, reason: str = "MANUAL"):
        """Manually close a trade"""
        trade = next((t for t in self.trades if t.id == trade_id), None)
        
        if not trade or trade.status != "OPEN":
            return None

        trade.close(exit_price, reason)
        
        self.save_trades()
        return trade


if __name__ == "__main__":
    # Test paper trader
    trader = PaperTrader("test_trades.json")
    
    # Add test trade
    trade = trader.add_trade(
        symbol="AAPL",
        action="BUY",
        entry_price=150.00,
        stop_loss=142.50,
        take_profit=172.50,
        confidence=75.0,
        pattern="WHALE_ACCUMULATION",
        signals=["Steady volume", "Gradual uptrend"]
    )
    
    print(f"Created trade: {trade.id}")
    print(f"Entry: ${trade.entry_price:.2f}")
    print(f"Stop: ${trade.stop_loss:.2f}")
    print(f"Target: ${trade.take_profit:.2f}")
    
    # Simulate price update
    print("\nSimulating price movement...")
    trader.update_trade(trade.id, 175.00)  # Hit take profit
    
    # Show stats
    stats = trader.calculate_stats()
    print(f"\n📊 STATS")
    print(f"Total Trades: {stats['total_trades']}")
    print(f"Win Rate: {stats['win_rate']:.1f}%")
    print(f"Avg Profit: {stats['avg_profit_pct']:.2f}%")

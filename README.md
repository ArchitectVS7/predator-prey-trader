# Predator-Prey Trade Analyzer 🦅

**AI-Powered Market Manipulation Detection**

Phase 1: Pattern detection, paper trading, and backtesting before going live.

---

## 🎯 What Is This?

A trading tool that detects market manipulation patterns (pump & dumps, whale accumulation, coordinated behavior) and generates trade signals. 

**Phase 1 Goal:** Test predictions with paper trading until we hit 60%+ accuracy, THEN consider real money.

---

## 🚀 Quick Start

### Analyze a Stock

```bash
cd src
python3 dashboard.py AAPL
```

### Monitor Watchlist

```bash
python3 dashboard.py --watch AAPL GME TSLA
```

### View Portfolio

```bash
python3 dashboard.py --portfolio
```

### Update Open Trades

```bash
python3 dashboard.py --update
```

---

## 📊 Features

### Pattern Detection

**1. Pump & Dump**
- Sudden volume spike (>3x average)
- Rapid price movement (>5%)
- High social media activity
- No news catalyst
- **Signal:** AVOID or SHORT

**2. Whale Accumulation**
- Steady elevated volume
- Price stable or slow rise
- Gradual accumulation pattern
- **Signal:** BUY (early entry)

**3. Unusual Activity**
- Moderate anomalies
- Requires monitoring
- **Signal:** WATCH

### Data Sources (All Free/Public)

- **Market Data:** Yahoo Finance API (OHLCV, volume)
- **Social Sentiment:** Reddit r/wallstreetbets (mentions, scores)
- **Crypto:** CoinGecko API

### Paper Trading

- Track predictions without real money
- Automatic entry/exit simulation
- Win rate tracking
- Performance metrics

---

## 📈 Example Output

```
======================================================================
  🦅 PREDATOR-PREY TRADE ANALYZER
  Phase 1: Pattern Detection & Paper Trading
======================================================================

──────────────────────────────────────────────────────────────────────
📊 Analyzing AAPL...
──────────────────────────────────────────────────────────────────────

💰 Current Price: $182.45
📅 Time: 2026-02-20 22:30:15

📈 Volume Profile:
  Average: 45,234,567
  Recent: 98,543,210
  Ratio: 2.18x
  ⚠️  VOLUME SPIKE DETECTED

🚀 Price Velocity:
  Avg Change: +3.45%
  Direction: UP
  ⚠️  RAPID MOVEMENT DETECTED

💬 Social Sentiment (Reddit r/wallstreetbets):
  Mentions: 45
  Total Score: 1,234
  Avg Upvote Ratio: 0.87

🔍 PATTERN DETECTION
──────────────────────────────────────────────────────────────────────
🚨 Pattern: PUMP_AND_DUMP
📊 Confidence: 82.0%
⚠️  Risk Level: CRITICAL
💡 Recommendation: AVOID
⏰ Timeframe: 30-60 minutes until dump

📋 Signals Detected:
  • Volume spike: 2.2x average
  • Rapid price movement: +3.5%
  • High social activity: 45 mentions

🎯 TRADE SIGNAL
──────────────────────────────────────────────────────────────────────
⛔ Action: AVOID
   Reason: Pump & dump detected - high risk
```

---

## 🛠️ How It Works

### 1. Data Collection

```python
from data_fetcher import DataFetcher

fetcher = DataFetcher()
analysis = fetcher.fetch_and_analyze("AAPL")
```

Fetches:
- OHLCV data (5-minute candles, last 24 hours)
- Volume profile
- Price velocity
- Social sentiment

### 2. Pattern Detection

```python
from pattern_detector import PatternDetector

detector = PatternDetector()
detection = detector.analyze_pattern(analysis)
```

Detects:
- Coordinated pumps
- Whale accumulation
- Unusual activity

Returns:
- Pattern type
- Confidence score (0-100%)
- Risk level
- Trade recommendation

### 3. Trade Signal Generation

```python
trade_signal = detector.calculate_trade_signal(detection, current_price)
```

Generates:
- Entry price
- Stop loss
- Take profit
- Risk/reward ratio

### 4. Paper Trading

```python
from paper_trader import PaperTrader

trader = PaperTrader()
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
```

Tracks:
- Entry/exit prices
- Win/loss status
- Profit/loss percentage
- Pattern accuracy

---

## 📊 Strategy

### Phase 1: Paper Trading (Current)

**Goal:** Achieve 60%+ win rate

**Actions:**
1. Monitor watchlist continuously
2. Log all predictions
3. Track which patterns work best
4. Iterate on detection algorithms
5. Analyze false positives/negatives

**Duration:** 1-2 weeks minimum

### Phase 2: Small Real Money (Future)

**Prerequisites:**
- 60%+ win rate over 100+ paper trades
- Understand why predictions succeed/fail
- Risk management rules defined

**Actions:**
- Start with $100-500 positions
- Strict stop losses
- Track real-world slippage
- Compare to paper trading results

### Phase 3: Scale (Future)

**Prerequisites:**
- Profitable over 3+ months
- Risk management working
- Emotional control proven

---

## 🎯 Detection Strategies

### Strategy 1: Fade the Pump

**When:** Pump & dump detected  
**Action:** Wait for dump, buy the dip  
**Risk/Reward:** 2:1 to 3:1  
**Win Rate Target:** 55-65%

### Strategy 2: Follow the Whale

**When:** Whale accumulation detected  
**Action:** Buy alongside whale, exit when distribution starts  
**Risk/Reward:** 2:1 to 4:1  
**Win Rate Target:** 60-70%

### Strategy 3: Avoid the Trap

**When:** High-risk patterns detected  
**Action:** Stay out (prevention = profit)  
**Value:** Saves capital for better opportunities

---

## 📂 Project Structure

```
predator-prey-trader/
├── src/
│   ├── data_fetcher.py      # Market data collection
│   ├── pattern_detector.py  # Manipulation detection
│   ├── paper_trader.py      # Paper trading system
│   └── dashboard.py         # CLI interface
├── data/
│   └── paper_trades.json    # Paper trading history
├── tests/                   # Unit tests
├── docs/                    # Documentation
└── README.md
```

---

## 🔧 Technical Details

### Detection Thresholds

**Pump & Dump:**
- Volume spike: >3x average
- Price velocity: >5% in <1 hour
- Social mentions: >20 in last 24h
- Confidence: Need 2+ signals, 50%+ confidence

**Whale Accumulation:**
- Volume: 1.2-2.0x average (elevated but not spiking)
- Price stability: <1% average change
- Gradual trend: 0.5-3% upward over period
- Confidence: Need 2+ signals, 50%+ confidence

### Data Refresh Rates

- **Stock data:** Every 5 minutes
- **Social sentiment:** Every 30 minutes (to avoid rate limits)
- **Trade updates:** Real-time on each watchlist check

### Paper Trading Rules

- **Entry:** Confirmed at specified price
- **Stop loss:** Automatic exit if price hits
- **Take profit:** Automatic exit if price hits
- **Time limit:** 7 days (close any open trades)

---

## 📈 Performance Metrics

Track:
- **Win rate:** % of trades that hit take profit
- **Avg profit:** Average % gain per trade
- **Risk/reward:** Average R:R ratio
- **Pattern accuracy:** Which patterns work best
- **False positives:** Detections that don't play out
- **Missed opportunities:** Real patterns we didn't catch

---

## ⚠️ Risk Management

**Phase 1 (Paper Trading):**
- No real money at risk
- Test aggressive and conservative strategies
- Learn from mistakes without cost

**Phase 2 (Real Trading - Future):**
- Max 1-2% of capital per trade
- Always use stop losses
- Never revenge trade
- Track emotional state

**Legal:**
- Using public data = legal
- Pattern detection = legal
- Trading on your analysis = legal
- This is NOT insider trading
- This is NOT market manipulation

---

## 🎯 Success Criteria

**To move to Phase 2 (Real Money):**

✅ 100+ paper trades logged  
✅ 60%+ overall win rate  
✅ Positive total profit %  
✅ Understand why trades win/lose  
✅ Risk management rules defined  
✅ Emotional control demonstrated  

**Current Status:** Phase 1 - Paper Trading

---

## 🚧 Roadmap

### Week 1: Data Collection
- [x] Stock data fetcher
- [x] Social sentiment scraper
- [x] Volume/price analyzers
- [ ] More data sources (Twitter, news)

### Week 2: Pattern Detection
- [x] Pump & dump detector
- [x] Whale accumulation detector
- [x] Unusual activity detector
- [ ] Insider trading patterns
- [ ] Coordinated buying detection

### Week 3: Paper Trading
- [x] Trade tracking system
- [x] Entry/exit simulation
- [x] Performance metrics
- [ ] Backtesting historical data

### Week 4: Visualization
- [x] CLI dashboard
- [ ] Charts (price, volume, patterns)
- [ ] Web dashboard (optional)
- [ ] Mobile alerts (Telegram)

### Phase 2: Real Trading (2+ weeks out)
- [ ] Broker API integration (Robinhood, etc.)
- [ ] Real-time order execution
- [ ] Slippage tracking
- [ ] Tax reporting

---

## 🤝 Contributing

This is a **personal trading tool**. Phase 1 is about learning and iteration.

**Not financial advice.** Trade at your own risk.

---

## 📄 License

MIT License

---

## 🎉 Credits

**Concept:** VS7  
**Implementation:** LG2 (OpenClaw agent)  
**Inspired by:** Predator-prey dynamics, whale watching, and avoiding getting rekt

---

**Ready to hunt?** 🦅

Run: `python3 src/dashboard.py AAPL`

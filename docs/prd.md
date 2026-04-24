# Product Requirements Document

> **Status:** Draft

## Overview
The Predator-Prey Trade Analyzer is an AI-powered market manipulation detection tool. The system actively monitors real-time market data to identify unusual patterns—such as pump and dumps or whale accumulation—and generates trade signals to instantly capitalize on these trends. Before risking actual capital, the system operates in a continuous "training phase" using paper trading. During this phase, it logs simulated buys and sells, allowing users to evaluate the accuracy and success rate of its predictions over extended periods.

## Goals
- **Pattern Detection:** Continuously monitor market data (e.g., OHLCV, volume spikes, price velocity) and social sentiment to detect market manipulation and emerging trends in real time.
- **Immediate Execution (Simulated):** Generate and instantly simulate trades based on detected patterns to capitalize on market movements.
- **Continuous Training & Evaluation:** Operate in a paper trading mode (the "training phase") that continuously logs simulated trades. Track and analyze the success of these predictions over days or weeks without financial risk.
- **Performance Metrics:** Provide comprehensive analytics on win rates, profit/loss, and pattern accuracy to evaluate and improve the detection algorithms.
- **Seamless Transition to Live Trading:** Ensure the architecture supports a future transition from paper trading to live order execution with broker APIs once a target confidence threshold (e.g., 60%+ win rate) is reached.

## Non-Goals
- **Immediate Live Trading:** Integrating with real brokerages for live execution is not part of the initial phase; the focus is exclusively on the paper trading training phase.
- **Manual Trading Interface:** The system is primarily an automated signal generator and paper trading engine, rather than a fully-featured UI for discretionary day trading.
- **Complex Financial Modeling:** Focus is on specific short-term manipulation patterns rather than long-term fundamental analysis.

## Requirements
1. **Data Ingestion System:**
   - Fetch real-time market data (price, volume, OHLCV) using free/public APIs (e.g., Yahoo Finance).
   - Gather social sentiment data (e.g., Reddit r/wallstreetbets mentions and scores).
   - Support interval-based polling (e.g., 5-minute candles).

2. **Pattern Detection Engine:**
   - Implement algorithms to identify "Pump & Dump" scenarios (volume spikes, rapid price changes, high social activity).
   - Implement algorithms to identify "Whale Accumulation" (steady elevated volume, stable price).
   - Calculate confidence scores and risk levels for each detected pattern.

3. **Trade Signal Generation:**
   - Automatically determine trade actions (BUY, SHORT, AVOID, WATCH) based on pattern detection.
   - Calculate entry prices, stop losses, and take profit targets based on current market conditions.

4. **Paper Trading & Logging System ("Training Phase"):**
   - Automatically log simulated trades based on generated signals.
   - Continuously update open trades to simulate hitting stop losses or take profits based on real-time price updates.
   - Persist trade history (e.g., in a JSON file) for long-term evaluation over days or weeks.

5. **Dashboard & Reporting:**
   - Provide a Command Line Interface (CLI) for real-time monitoring of watchlists.
   - Display a portfolio summary detailing total trades, win rates, average profits, and performance broken down by pattern type.
   - Allow users to manually review the success of the system's predictions.
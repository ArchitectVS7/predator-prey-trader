#!/usr/bin/env python3
"""
Data Fetcher for Predator-Prey Trade Analyzer
Fetches market data from free APIs (no auth required for basic usage)
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time


class DataFetcher:
    """Fetch market data from free sources"""
    
    def __init__(self):
        self.session = requests.Session()
        # Use free tier APIs (no key required for basic usage)
        self.yahoo_base = "https://query1.finance.yahoo.com/v8/finance/chart/"
        self.reddit_base = "https://www.reddit.com/r/"
        
    def fetch_stock_data(self, symbol: str, interval: str = "1h", 
                        range_: str = "1d") -> Dict:
        """
        Fetch stock data from Yahoo Finance
        
        Args:
            symbol: Stock ticker (e.g. 'AAPL', 'GME')
            interval: 1m, 5m, 15m, 1h, 1d
            range_: 1d, 5d, 1mo, 3mo, 1y
        """
        url = f"{self.yahoo_base}{symbol}"
        params = {
            "interval": interval,
            "range": range_
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if "chart" not in data or "result" not in data["chart"]:
                return {"error": "Invalid response from API"}
            
            result = data["chart"]["result"][0]
            
            # Extract OHLCV data
            timestamps = result["timestamp"]
            quotes = result["indicators"]["quote"][0]
            
            candles = []
            for i in range(len(timestamps)):
                candles.append({
                    "timestamp": timestamps[i],
                    "datetime": datetime.fromtimestamp(timestamps[i]).isoformat(),
                    "open": quotes["open"][i],
                    "high": quotes["high"][i],
                    "low": quotes["low"][i],
                    "close": quotes["close"][i],
                    "volume": quotes["volume"][i]
                })
            
            return {
                "symbol": symbol,
                "interval": interval,
                "candles": candles,
                "meta": result.get("meta", {})
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def fetch_social_sentiment(self, symbol: str, subreddit: str = "wallstreetbets") -> Dict:
        """
        Fetch social sentiment from Reddit (public JSON feed)
        
        Args:
            symbol: Stock ticker
            subreddit: Reddit community name
        """
        url = f"{self.reddit_base}{subreddit}/search.json"
        params = {
            "q": symbol,
            "sort": "new",
            "limit": 100,
            "t": "day"
        }
        
        headers = {
            "User-Agent": "PredatorPreyTrader/1.0"
        }
        
        try:
            response = self.session.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if "data" not in data or "children" not in data["data"]:
                return {"error": "Invalid Reddit response"}
            
            posts = data["data"]["children"]
            
            mentions = []
            for post in posts:
                post_data = post["data"]
                mentions.append({
                    "title": post_data.get("title", ""),
                    "score": post_data.get("score", 0),
                    "num_comments": post_data.get("num_comments", 0),
                    "created_utc": post_data.get("created_utc", 0),
                    "upvote_ratio": post_data.get("upvote_ratio", 0),
                    "url": post_data.get("url", "")
                })
            
            # Calculate sentiment metrics
            total_score = sum(m["score"] for m in mentions)
            total_comments = sum(m["num_comments"] for m in mentions)
            avg_ratio = sum(m["upvote_ratio"] for m in mentions) / len(mentions) if mentions else 0
            
            return {
                "symbol": symbol,
                "subreddit": subreddit,
                "mention_count": len(mentions),
                "total_score": total_score,
                "total_comments": total_comments,
                "avg_upvote_ratio": avg_ratio,
                "mentions": mentions[:10]  # Top 10
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def calculate_volume_profile(self, candles: List[Dict]) -> Dict:
        """Calculate volume profile metrics"""
        if not candles:
            return {}
        
        volumes = [c["volume"] for c in candles if c["volume"]]
        
        if not volumes:
            return {}
        
        avg_volume = sum(volumes) / len(volumes)
        max_volume = max(volumes)
        recent_volume = volumes[-1] if volumes else 0
        
        # Volume spike detection
        volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 0
        
        return {
            "avg_volume": avg_volume,
            "max_volume": max_volume,
            "recent_volume": recent_volume,
            "volume_ratio": volume_ratio,
            "is_spike": volume_ratio > 2.0
        }
    
    def calculate_price_velocity(self, candles: List[Dict]) -> Dict:
        """Calculate price movement velocity"""
        if len(candles) < 2:
            return {}
        
        # Recent price changes
        recent_prices = [c["close"] for c in candles[-10:] if c["close"]]
        
        if len(recent_prices) < 2:
            return {}
        
        # Calculate percentage changes
        changes = []
        for i in range(1, len(recent_prices)):
            pct_change = ((recent_prices[i] - recent_prices[i-1]) / recent_prices[i-1]) * 100
            changes.append(pct_change)
        
        avg_change = sum(changes) / len(changes) if changes else 0
        max_change = max(changes) if changes else 0
        min_change = min(changes) if changes else 0
        
        # Detect rapid movement
        is_rapid = abs(avg_change) > 2.0  # >2% average change
        
        return {
            "avg_pct_change": avg_change,
            "max_pct_change": max_change,
            "min_pct_change": min_change,
            "is_rapid_movement": is_rapid,
            "direction": "up" if avg_change > 0 else "down"
        }
    
    def fetch_and_analyze(self, symbol: str) -> Dict:
        """Fetch all data and run basic analysis"""
        print(f"Fetching data for {symbol}...")
        
        # Get stock data
        stock_data = self.fetch_stock_data(symbol, interval="5m", range_="1d")
        
        if "error" in stock_data:
            return {"error": stock_data["error"]}
        
        # Get social sentiment
        sentiment = self.fetch_social_sentiment(symbol)
        
        # Analyze
        candles = stock_data.get("candles", [])
        volume_profile = self.calculate_volume_profile(candles)
        price_velocity = self.calculate_price_velocity(candles)
        
        # Get current price
        current_price = candles[-1]["close"] if candles else 0
        
        return {
            "symbol": symbol,
            "current_price": current_price,
            "timestamp": datetime.now().isoformat(),
            "candles": candles,
            "volume_profile": volume_profile,
            "price_velocity": price_velocity,
            "social_sentiment": sentiment,
            "data_points": len(candles)
        }


class CryptoDataFetcher:
    """Fetch crypto data (simpler for MVP)"""
    
    def __init__(self):
        self.session = requests.Session()
        # CoinGecko free API
        self.base_url = "https://api.coingecko.com/api/v3"
    
    def fetch_crypto_data(self, coin_id: str = "bitcoin", days: int = 1) -> Dict:
        """
        Fetch crypto price data
        
        Args:
            coin_id: Coin ID (bitcoin, ethereum, etc.)
            days: Number of days of history
        """
        url = f"{self.base_url}/coins/{coin_id}/market_chart"
        params = {
            "vs_currency": "usd",
            "days": days,
            "interval": "hourly" if days <= 7 else "daily"
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Convert to candle-like format
            prices = data.get("prices", [])
            volumes = data.get("total_volumes", [])
            
            candles = []
            for i in range(len(prices)):
                timestamp = prices[i][0] / 1000  # Convert ms to seconds
                candles.append({
                    "timestamp": timestamp,
                    "datetime": datetime.fromtimestamp(timestamp).isoformat(),
                    "price": prices[i][1],
                    "volume": volumes[i][1] if i < len(volumes) else 0
                })
            
            return {
                "coin_id": coin_id,
                "candles": candles,
                "current_price": candles[-1]["price"] if candles else 0
            }
            
        except Exception as e:
            return {"error": str(e)}


if __name__ == "__main__":
    # Test data fetcher
    fetcher = DataFetcher()
    
    print("Testing stock data fetch...")
    result = fetcher.fetch_and_analyze("AAPL")
    
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"\n✅ {result['symbol']}")
        print(f"Current Price: ${result['current_price']:.2f}")
        print(f"Data Points: {result['data_points']}")
        
        print(f"\nVolume Profile:")
        vol = result.get("volume_profile", {})
        print(f"  Average: {vol.get('avg_volume', 0):,.0f}")
        print(f"  Recent: {vol.get('recent_volume', 0):,.0f}")
        print(f"  Ratio: {vol.get('volume_ratio', 0):.2f}x")
        print(f"  Spike: {'YES' if vol.get('is_spike') else 'NO'}")
        
        print(f"\nPrice Velocity:")
        vel = result.get("price_velocity", {})
        print(f"  Avg Change: {vel.get('avg_pct_change', 0):.2f}%")
        print(f"  Direction: {vel.get('direction', 'unknown')}")
        print(f"  Rapid: {'YES' if vel.get('is_rapid_movement') else 'NO'}")
        
        print(f"\nSocial Sentiment:")
        sent = result.get("social_sentiment", {})
        if "error" not in sent:
            print(f"  Mentions: {sent.get('mention_count', 0)}")
            print(f"  Total Score: {sent.get('total_score', 0)}")
            print(f"  Avg Upvote Ratio: {sent.get('avg_upvote_ratio', 0):.2f}")
    
    print("\n" + "="*60)
    print("Testing crypto data fetch...")
    
    crypto = CryptoDataFetcher()
    btc_data = crypto.fetch_crypto_data("bitcoin", days=1)
    
    if "error" in btc_data:
        print(f"Error: {btc_data['error']}")
    else:
        print(f"\n✅ {btc_data['coin_id']}")
        print(f"Current Price: ${btc_data['current_price']:,.2f}")
        print(f"Data Points: {len(btc_data['candles'])}")

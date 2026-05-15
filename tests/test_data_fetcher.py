import sys
from unittest.mock import MagicMock

# Mock requests before importing src.data_fetcher
mock_requests = MagicMock()
sys.modules["requests"] = mock_requests

import pytest
from unittest.mock import patch
from src.data_fetcher import DataFetcher, CryptoDataFetcher

@pytest.fixture
def data_fetcher():
    return DataFetcher()

@pytest.fixture
def crypto_fetcher():
    return CryptoDataFetcher()

def test_fetch_stock_data_success(data_fetcher):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "chart": {
            "result": [{
                "timestamp": [1645392000],
                "indicators": {
                    "quote": [{
                        "open": [150.0],
                        "high": [155.0],
                        "low": [149.0],
                        "close": [152.0],
                        "volume": [1000000]
                    }]
                },
                "meta": {"currency": "USD"}
            }]
        }
    }
    mock_response.raise_for_status.return_value = None

    with patch.object(data_fetcher.session, 'get', return_value=mock_response):
        result = data_fetcher.fetch_stock_data("AAPL")

    assert "error" not in result
    assert result["symbol"] == "AAPL"
    assert len(result["candles"]) == 1
    assert result["candles"][0]["close"] == 152.0
    assert result["meta"]["currency"] == "USD"

def test_fetch_stock_data_error(data_fetcher):
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = Exception("API Error")

    with patch.object(data_fetcher.session, 'get', return_value=mock_response):
        result = data_fetcher.fetch_stock_data("AAPL")

    assert "error" in result
    assert "API Error" in result["error"]

def test_fetch_social_sentiment_success(data_fetcher):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": {
            "children": [
                {
                    "data": {
                        "title": "AAPL to the moon",
                        "score": 100,
                        "num_comments": 10,
                        "created_utc": 1645392000,
                        "upvote_ratio": 0.9,
                        "url": "http://example.com"
                    }
                }
            ]
        }
    }
    mock_response.raise_for_status.return_value = None

    with patch.object(data_fetcher.session, 'get', return_value=mock_response):
        result = data_fetcher.fetch_social_sentiment("AAPL")

    assert "error" not in result
    assert result["symbol"] == "AAPL"
    assert result["mention_count"] == 1
    assert result["total_score"] == 100
    assert result["avg_upvote_ratio"] == 0.9

def test_calculate_volume_profile(data_fetcher):
    # Case 1: No candles
    assert data_fetcher.calculate_volume_profile([]) == {}

    # Case 2: Normal volume
    candles = [
        {"volume": 100},
        {"volume": 100},
        {"volume": 100}
    ]
    result = data_fetcher.calculate_volume_profile(candles)
    assert result["volume_ratio"] == 1.0
    assert result["is_spike"] is False

    # Case 3: Volume spike
    candles = [
        {"volume": 100},
        {"volume": 100},
        {"volume": 700}
    ]
    result = data_fetcher.calculate_volume_profile(candles)
    assert result["volume_ratio"] > 2.0
    assert result["is_spike"] is True

def test_calculate_price_velocity(data_fetcher):
    # Case 1: Insufficient candles
    assert data_fetcher.calculate_price_velocity([{"close": 100}]) == {}

    # Case 2: Stable price
    candles = [{"close": 100}, {"close": 101}]
    result = data_fetcher.calculate_price_velocity(candles)
    assert result["avg_pct_change"] == 1.0
    assert result["is_rapid_movement"] is False

    # Case 3: Rapid movement
    candles = [{"close": 100}, {"close": 103}]
    result = data_fetcher.calculate_price_velocity(candles)
    assert result["avg_pct_change"] == 3.0
    assert result["is_rapid_movement"] is True

def test_fetch_crypto_data_success(crypto_fetcher):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "prices": [[1645392000000, 40000.0]],
        "total_volumes": [[1645392000000, 1000000000.0]]
    }
    mock_response.raise_for_status.return_value = None

    with patch.object(crypto_fetcher.session, 'get', return_value=mock_response):
        result = crypto_fetcher.fetch_crypto_data("bitcoin")

    assert "error" not in result
    assert result["coin_id"] == "bitcoin"
    assert result["current_price"] == 40000.0
    assert len(result["candles"]) == 1

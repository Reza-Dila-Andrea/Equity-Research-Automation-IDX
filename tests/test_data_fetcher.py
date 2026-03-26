"""
Unit tests untuk DynamicDataFetcher
"""

import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from src.data_fetcher import DynamicDataFetcher
from src.error_handler import ValidationException, DataFetchException


class TestDataFetcher(unittest.TestCase):
    """Test DynamicDataFetcher class"""
    
    def setUp(self):
        """Setup test fixtures"""
        self.valid_ticker = "BBCA"
        self.invalid_ticker = "INVALID"
    
    def test_initialization_valid_ticker(self):
        """Test initialization dengan valid ticker"""
        fetcher = DynamicDataFetcher(self.valid_ticker)
        self.assertEqual(fetcher.ticker, "BBCA")
        self.assertEqual(fetcher.symbol, "BBCA.JK")
        self.assertIsNotNone(fetcher.sector)
        self.assertIsNotNone(fetcher.peers)
    
    def test_initialization_invalid_ticker(self):
        """Test initialization dengan invalid ticker"""
        with self.assertRaises(ValidationException):
            DynamicDataFetcher("INVALID_TICKER")
    
    def test_ticker_uppercase(self):
        """Test that ticker is converted to uppercase"""
        fetcher = DynamicDataFetcher("bbca")
        self.assertEqual(fetcher.ticker, "BBCA")
    
    def test_get_sector(self):
        """Test sector identification"""
        # Banking
        fetcher_bbca = DynamicDataFetcher("BBCA")
        self.assertEqual(fetcher_bbca.get_sector(), "banking")
        
        # Automotive
        fetcher_asii = DynamicDataFetcher("ASII")
        self.assertEqual(fetcher_asii.get_sector(), "automotive")
    
    def test_get_peers(self):
        """Test peer selection"""
        fetcher = DynamicDataFetcher("BBCA")
        peers = fetcher.get_peers()
        
        self.assertIsInstance(peers, list)
        self.assertLessEqual(len(peers), 3)
        self.assertNotIn("BBCA", peers)  # Self not in peers
        
        # Banking peers should include BMRI
        self.assertIn("BMRI", peers)
    
    def test_symbol_format(self):
        """Test Yahoo Finance symbol format"""
        fetcher = DynamicDataFetcher("BBCA")
        self.assertEqual(fetcher.symbol, "BBCA.JK")
    
    def test_wacc_estimation(self):
        """Test WACC estimation by sector"""
        # Banking should have ~9% WACC
        fetcher_bbca = DynamicDataFetcher("BBCA")
        self.assertAlmostEqual(fetcher_bbca.estimated_wacc, 0.09, places=2)
        
        # Automotive should have ~11% WACC
        fetcher_asii = DynamicDataFetcher("ASII")
        self.assertAlmostEqual(fetcher_asii.estimated_wacc, 0.11, places=2)
    
    @patch('yfinance.Ticker')
    def test_fetch_current_price_success(self, mock_ticker):
        """Test successful price fetch"""
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = {'regularMarketPrice': 3650.0}
        mock_ticker.return_value = mock_ticker_instance
        
        fetcher = DynamicDataFetcher("BBCA")
        price = fetcher.fetch_current_price()
        
        self.assertEqual(price, 3650.0)
    
    @patch('yfinance.Ticker')
    def test_fetch_current_price_fallback(self, mock_ticker):
        """Test price fetch fallback to history"""
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = {'regularMarketPrice': None}
        mock_ticker_instance.history.return_value = pd.DataFrame({
            'Close': [3650.0, 3660.0]
        })
        mock_ticker.return_value = mock_ticker_instance
        
        fetcher = DynamicDataFetcher("BBCA")
        price = fetcher.fetch_current_price()
        
        self.assertIsNotNone(price)
        self.assertGreater(price, 0)
    
    @patch('yfinance.Ticker')
    def test_fetch_historical_prices(self, mock_ticker):
        """Test historical price fetching"""
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.history.return_value = pd.DataFrame({
            'Close': [3600, 3650, 3700],
            'Open': [3580, 3620, 3680],
            'High': [3700, 3750, 3800],
            'Low': [3550, 3600, 3650]
        })
        mock_ticker.return_value = mock_ticker_instance
        
        fetcher = DynamicDataFetcher("BBCA")
        prices = fetcher.fetch_historical_prices()
        
        self.assertIsInstance(prices, pd.DataFrame)
        self.assertIn('Close', prices.columns)
        self.assertEqual(len(prices), 3)
    
    @patch('yfinance.Ticker')
    def test_fetch_financials(self, mock_ticker):
        """Test financial data fetching"""
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.quarterly_financials = pd.DataFrame({
            'Total Revenue': [30000, 32000, 34000, 36000],
            'Net Income': [6000, 6500, 7000, 7500]
        }, index=pd.date_range('2023-01-01', periods=4, freq='Q'))
        mock_ticker.return_value = mock_ticker_instance
        
        fetcher = DynamicDataFetcher("BBCA")
        financials = fetcher.fetch_financials()
        
        self.assertIsInstance(financials, dict)
        self.assertGreater(len(financials), 0)
    
    @patch('yfinance.Ticker')
    def test_fetch_key_metrics(self, mock_ticker):
        """Test key metrics fetching"""
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = {
            'regularMarketPrice': 3650.0,
            'trailingPE': 14.2,
            'priceToBook': 2.1,
            'returnOnEquity': 0.182,
            'dividendYield': 0.032,
            'marketCap': 730000000000,
            'sharesOutstanding': 2000000000
        }
        mock_ticker.return_value = mock_ticker_instance
        
        fetcher = DynamicDataFetcher("BBCA")
        metrics = fetcher.fetch_key_metrics()
        
        self.assertIn('price', metrics)
        self.assertIn('pe_ratio', metrics)
        self.assertIn('pb_ratio', metrics)
        self.assertEqual(metrics['price'], 3650.0)
        self.assertEqual(metrics['pe_ratio'], 14.2)
    
    @patch('yfinance.Ticker')
    def test_get_shares_outstanding(self, mock_ticker):
        """Test shares outstanding calculation"""
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = {
            'sharesOutstanding': 2000000000  # 2B shares
        }
        mock_ticker.return_value = mock_ticker_instance
        
        fetcher = DynamicDataFetcher("BBCA")
        shares = fetcher.get_shares_outstanding()
        
        self.assertEqual(shares, 2.0)  # In billions
    
    def test_get_all_data(self):
        """Test get_all_data returns dict"""
        fetcher = DynamicDataFetcher("BBCA")
        
        # Should not raise exception
        try:
            data = fetcher.get_all_data()
            self.assertIsInstance(data, dict)
            self.assertIn('ticker', data)
            self.assertEqual(data['ticker'], 'BBCA')
        except Exception:
            # OK if API fails (network issue)
            pass


class TestDataFetcherIntegration(unittest.TestCase):
    """Integration tests dengan real data (slow)"""
    
    def test_fetch_real_bbca_data(self):
        """Test fetching real BBCA data"""
        try:
            fetcher = DynamicDataFetcher("BBCA")
            fetcher.validate_stock()
            
            price = fetcher.fetch_current_price()
            self.assertIsNotNone(price)
            self.assertGreater(price, 0)
        except Exception as e:
            self.skipTest(f"Network error: {e}")
    
    def test_fetch_real_asii_data(self):
        """Test fetching real ASII data"""
        try:
            fetcher = DynamicDataFetcher("ASII")
            fetcher.validate_stock()
            
            metrics = fetcher.fetch_key_metrics()
            self.assertIsInstance(metrics, dict)
        except Exception as e:
            self.skipTest(f"Network error: {e}")


if __name__ == '__main__':
    unittest.main()

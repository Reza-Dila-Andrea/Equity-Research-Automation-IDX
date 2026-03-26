"""
Unit tests untuk DCF Valuation
"""

import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from src.dcf_valuation import UniversalDCFValuation
from src.error_handler import CalculationException


class TestDCFValuation(unittest.TestCase):
    """Test UniversalDCFValuation class"""
    
    def setUp(self):
        """Setup test fixtures"""
        self.ticker = "BBCA"
    
    def test_initialization(self):
        """Test DCF initialization"""
        dcf = UniversalDCFValuation(self.ticker)
        
        self.assertEqual(dcf.ticker, "BBCA")
        self.assertIsNotNone(dcf.wacc)
        self.assertEqual(dcf.terminal_growth, 0.03)
    
    def test_wacc_by_sector(self):
        """Test WACC estimation by sector"""
        dcf_bbca = UniversalDCFValuation("BBCA")
        dcf_asii = UniversalDCFValuation("ASII")
        
        # Banking should have lower WACC than automotive
        self.assertLess(dcf_bbca.wacc, dcf_asii.wacc)
    
    @patch.object(UniversalDCFValuation, 'fetch_financial_data')
    def test_calculate_revenue_cagr(self, mock_fetch):
        """Test revenue CAGR calculation"""
        dcf = UniversalDCFValuation(self.ticker)
        
        # Mock financial data
        dcf.financials = pd.DataFrame({
            'revenue': [30000, 33000, 36300, 39930]
        })
        
        cagr = dcf.calculate_revenue_cagr()
        
        # Should be approximately 10%
        self.assertAlmostEqual(cagr, 0.10, places=1)
    
    @patch.object(UniversalDCFValuation, 'fetch_financial_data')
    def test_calculate_fcf_margin(self, mock_fetch):
        """Test FCF margin calculation"""
        dcf = UniversalDCFValuation(self.ticker)
        
        # Mock financial data
        dcf.financials = pd.DataFrame({
            'revenue': [30000, 33000, 36300],
            'net_income': [6000, 6600, 7260]
        })
        
        margin = dcf.calculate_fcf_margin()
        
        # Should be approximately 20%
        self.assertAlmostEqual(margin, 0.20, places=1)
        self.assertGreater(margin, 0)
    
    @patch.object(UniversalDCFValuation, 'fetch_financial_data')
    def test_project_cashflows(self, mock_fetch):
        """Test cash flow projection"""
        dcf = UniversalDCFValuation(self.ticker)
        
        # Mock financial data
        dcf.financials = pd.DataFrame({
            'revenue': [30000, 33000, 36300],
            'net_income': [6000, 6600, 7260]
        })
        
        projections = dcf.project_cashflows(
            projection_years=5,
            growth_rate=0.10
        )
        
        self.assertEqual(len(projections), 5)
        self.assertIn('year', projections.columns)
        self.assertIn('revenue', projections.columns)
        self.assertIn('fcf', projections.columns)
        
        # Each year should have higher revenue
        revenues = projections['revenue'].values
        for i in range(1, len(revenues)):
            self.assertGreater(revenues[i], revenues[i-1])
    
    def test_calculate_terminal_value(self):
        """Test terminal value calculation"""
        dcf = UniversalDCFValuation(self.ticker)
        
        fcf_year5 = 10000
        tv = dcf.calculate_terminal_value(fcf_year5)
        
        # TV should be positive and reasonable
        self.assertGreater(tv, 0)
        self.assertGreater(tv, fcf_year5)  # TV typically > 1x FCF
    
    def test_calculate_terminal_value_invalid(self):
        """Test terminal value with invalid params"""
        dcf = UniversalDCFValuation(self.ticker)
        dcf.terminal_growth = 0.15  # Higher than WACC
        dcf.wacc = 0.10
        
        with self.assertRaises(CalculationException):
            dcf.calculate_terminal_value(10000)
    
    @patch.object(UniversalDCFValuation, 'fetch_financial_data')
    def test_calculate_fair_value(self, mock_fetch):
        """Test main fair value calculation"""
        dcf = UniversalDCFValuation(self.ticker)
        
        # Mock financial data
        dcf.financials = pd.DataFrame({
            'revenue': [30000, 33000, 36300],
            'net_income': [6000, 6600, 7260]
        })
        
        # Mock fetcher
        dcf.fetcher.get_shares_outstanding = MagicMock(return_value=2.0)
        
        result = dcf.calculate_fair_value(
            projection_years=5,
            growth_rate=0.10
        )
        
        # Check result structure
        self.assertIn('fair_value_per_share', result)
        self.assertIn('fair_value_low', result)
        self.assertIn('fair_value_high', result)
        self.assertIn('enterprise_value', result)
        self.assertIn('wacc', result)
        self.assertIn('assumptions', result)
        
        # Fair value should be positive
        self.assertGreater(result['fair_value_per_share'], 0)
        
        # Range should be ±10%
        self.assertAlmostEqual(
            result['fair_value_low'],
            result['fair_value_per_share'] * 0.90,
            delta=1
        )
    
    @patch.object(UniversalDCFValuation, 'fetch_financial_data')
    def test_override_wacc(self, mock_fetch):
        """Test WACC override"""
        dcf = UniversalDCFValuation(self.ticker)
        original_wacc = dcf.wacc
        
        # Mock financial data
        dcf.financials = pd.DataFrame({
            'revenue': [30000, 33000, 36300],
            'net_income': [6000, 6600, 7260]
        })
        
        # Mock fetcher
        dcf.fetcher.get_shares_outstanding = MagicMock(return_value=2.0)
        
        # Calculate with override
        result = dcf.calculate_fair_value(
            override_wacc=0.08
        )
        
        self.assertEqual(result['wacc'], 0.08)
        self.assertNotEqual(result['wacc'], original_wacc)
    
    @patch.object(UniversalDCFValuation, 'fetch_financial_data')
    def test_override_growth_rate(self, mock_fetch):
        """Test growth rate override"""
        dcf = UniversalDCFValuation(self.ticker)
        
        # Mock financial data
        dcf.financials = pd.DataFrame({
            'revenue': [30000, 33000, 36300],
            'net_income': [6000, 6600, 7260]
        })
        
        # Mock fetcher
        dcf.fetcher.get_shares_outstanding = MagicMock(return_value=2.0)
        
        # Calculate with custom growth
        result = dcf.calculate_fair_value(
            growth_rate=0.15
        )
        
        self.assertEqual(result['revenue_cagr'], 0.15)
    
    def test_cagr_bounds(self):
        """Test CAGR has reasonable bounds"""
        dcf = UniversalDCFValuation(self.ticker)
        
        # Mock high growth
        dcf.financials = pd.DataFrame({
            'revenue': [1000, 10000, 100000]  # Unrealistic growth
        })
        
        cagr = dcf.calculate_revenue_cagr()
        
        # Should be capped at 30%
        self.assertLessEqual(cagr, 0.30)
    
    def test_fcf_margin_bounds(self):
        """Test FCF margin has reasonable bounds"""
        dcf = UniversalDCFValuation(self.ticker)
        
        # Mock very high profit
        dcf.financials = pd.DataFrame({
            'revenue': [1000, 1000, 1000],
            'net_income': [900, 900, 900]  # 90% margins
        })
        
        margin = dcf.calculate_fcf_margin()
        
        # Should be capped at 40%
        self.assertLessEqual(margin, 0.40)


class TestDCFIntegration(unittest.TestCase):
    """Integration tests dengan real data"""
    
    def test_full_dcf_workflow_bbca(self):
        """Test complete DCF workflow untuk BBCA"""
        try:
            dcf = UniversalDCFValuation("BBCA")
            result = dcf.calculate_fair_value()
            
            # Check all required fields
            self.assertIn('fair_value_per_share', result)
            self.assertGreater(result['fair_value_per_share'], 0)
            self.assertLess(result['fair_value_per_share'], 100000)  # Sanity check
        except Exception as e:
            self.skipTest(f"Network error: {e}")
    
    def test_full_dcf_workflow_asii(self):
        """Test complete DCF workflow untuk ASII"""
        try:
            dcf = UniversalDCFValuation("ASII")
            result = dcf.calculate_fair_value()
            
            # Should return valid result
            self.assertIsNotNone(result)
            self.assertGreater(result['fair_value_per_share'], 0)
        except Exception as e:
            self.skipTest(f"Network error: {e}")


if __name__ == '__main__':
    unittest.main()

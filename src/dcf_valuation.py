"""
DCF Valuation module
Universal DCF model untuk ANY stock
"""

from src.data_fetcher import DynamicDataFetcher
from src.error_handler import CalculationException, DataValidator
from src.utils import safe_divide, calculate_cagr, format_number
import pandas as pd
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class UniversalDCFValuation:
    """
    DCF valuation untuk ANY stock
    Flexible assumptions, robust error handling
    """
    
    def __init__(self, ticker: str):
        """
        Initialize DCF valuation
        
        Args:
            ticker: Stock ticker
        """
        self.ticker = ticker.upper()
        self.fetcher = DynamicDataFetcher(ticker)
        self.financials = None
        self.wacc = self.fetcher.estimated_wacc  # Auto-estimated by sector
        self.terminal_growth = 0.03  # Conservative 3%
        
        logger.info(f"Initialized DCF for {self.ticker} with WACC={self.wacc:.1%}")
    
    def fetch_financial_data(self) -> Optional[pd.DataFrame]:
        """
        Fetch dan prepare financial data
        
        Returns:
            DataFrame dengan historical financials, atau None jika error
        """
        try:
            financials_dict = self.fetcher.fetch_financials()
            
            if not financials_dict:
                logger.warning(f"No financial data available for {self.ticker}")
                return None
            
            # Convert dict to DataFrame
            df = pd.DataFrame.from_dict(financials_dict, orient='index')
            df = df.sort_index()
            
            # Validate
            if not DataValidator.validate_financials(financials_dict):
                logger.warning(f"Financial data validation failed for {self.ticker}")
                return None
            
            self.financials = df
            logger.info(f"✓ Loaded financial data for {self.ticker}")
            return df
        
        except Exception as e:
            logger.error(f"Error loading financial data: {e}")
            return None
    
    def calculate_revenue_cagr(self, years: int = None) -> float:
        """
        Calculate historical revenue CAGR
        
        Args:
            years: Number of years (default: all available)
        
        Returns:
            CAGR sebagai decimal (0-1 scale)
        """
        if self.financials is None or len(self.financials) < 2:
            # Default growth rate jika no historical data
            logger.info(f"Using default growth rate for {self.ticker}")
            return 0.07  # 7% default
        
        revenues = self.financials['revenue']
        num_years = len(revenues) - 1
        
        if num_years <= 0 or revenues.iloc[0] <= 0:
            return 0.07
        
        cagr = calculate_cagr(revenues.iloc[0], revenues.iloc[-1], num_years)
        
        # Sanity check: CAGR tidak boleh negatif atau terlalu tinggi
        cagr = max(cagr, 0.02)  # Min 2%
        cagr = min(cagr, 0.30)  # Max 30%
        
        logger.info(f"Revenue CAGR for {self.ticker}: {cagr:.1%}")
        return cagr
    
    def calculate_fcf_margin(self) -> float:
        """
        Calculate Free Cash Flow sebagai % of revenue
        
        Returns:
            FCF margin (0-1 scale)
        """
        if self.financials is None or len(self.financials) == 0:
            # Default FCF margin
            logger.info(f"Using default FCF margin for {self.ticker}")
            return 0.15  # 15% default
        
        # Simple FCF = Net Income (untuk IDX simplified model)
        avg_ni = self.financials['net_income'].mean()
        avg_rev = self.financials['revenue'].mean()
        
        if avg_rev <= 0:
            return 0.15
        
        margin = safe_divide(avg_ni, avg_rev, 0.15)
        
        # Sanity check
        margin = max(margin, 0.05)  # Min 5%
        margin = min(margin, 0.40)  # Max 40%
        
        logger.info(f"FCF margin for {self.ticker}: {margin:.1%}")
        return margin
    
    def project_cashflows(self, projection_years: int = 5,
                         growth_rate: float = None) -> pd.DataFrame:
        """
        Project future cash flows
        
        Args:
            projection_years: Years to project (default 5)
            growth_rate: Revenue growth rate (default auto-calculated)
        
        Returns:
            DataFrame dengan projected cashflows
        """
        if growth_rate is None:
            growth_rate = self.calculate_revenue_cagr()
        
        # Get starting revenue
        if self.financials is not None and len(self.financials) > 0:
            last_revenue = self.financials['revenue'].iloc[-1]
        else:
            # Fallback: estimate dari market cap
            metrics = self.fetcher.fetch_key_metrics()
            market_cap = metrics.get('market_cap')
            if market_cap:
                last_revenue = (market_cap / 1e9) * 0.2  # Assume 20% margin rough
            else:
                last_revenue = 10  # Minimum estimate
                logger.warning(f"Using minimum revenue estimate for {self.ticker}")
        
        fcf_margin = self.calculate_fcf_margin()
        
        projections = []
        for year in range(1, projection_years + 1):
            projected_revenue = last_revenue * ((1 + growth_rate) ** year)
            projected_fcf = projected_revenue * fcf_margin
            
            projections.append({
                'year': year,
                'revenue': projected_revenue,
                'fcf': projected_fcf
            })
        
        df = pd.DataFrame(projections)
        logger.info(f"✓ Projected {projection_years} years of cashflows for {self.ticker}")
        return df
    
    def calculate_terminal_value(self, fcf_year_last: float) -> float:
        """
        Calculate terminal value using Gordon Growth Model
        
        TV = FCF_last × (1 + g) / (WACC - g)
        
        Args:
            fcf_year_last: FCF di tahun terakhir projection
        
        Returns:
            Terminal value
        """
        if self.terminal_growth >= self.wacc:
            raise CalculationException(
                f"Terminal growth ({self.terminal_growth:.1%}) >= WACC ({self.wacc:.1%})"
            )
        
        denominator = self.wacc - self.terminal_growth
        if denominator <= 0:
            raise CalculationException("Invalid WACC/growth combination")
        
        tv = (fcf_year_last * (1 + self.terminal_growth)) / denominator
        
        logger.info(f"Terminal value: {tv:,.0f}B")
        return tv
    
    def discount_cashflows(self, cashflows: pd.DataFrame,
                          terminal_value: float) -> Dict:
        """
        Discount all cash flows to present value
        
        PV = CF / (1 + WACC)^year
        
        Args:
            cashflows: Projected cashflows
            terminal_value: Terminal value
        
        Returns:
            Dict dengan PV summary
        """
        pv_fcf_total = 0
        
        for _, row in cashflows.iterrows():
            pv_factor = 1 / ((1 + self.wacc) ** row['year'])
            pv_fcf = row['fcf'] * pv_factor
            pv_fcf_total += pv_fcf
        
        # Terminal value PV
        terminal_pv_factor = 1 / ((1 + self.wacc) ** len(cashflows))
        pv_terminal = terminal_value * terminal_pv_factor
        
        logger.info(f"PV of FCF: {pv_fcf_total:,.0f}B")
        logger.info(f"PV of Terminal Value: {pv_terminal:,.0f}B")
        
        return {
            'pv_fcf': pv_fcf_total,
            'pv_terminal': pv_terminal
        }
    
    def calculate_fair_value(self, projection_years: int = 5,
                            growth_rate: float = None,
                            override_wacc: float = None) -> Dict:
        """
        Main DCF calculation - Calculate fair value
        
        Args:
            projection_years: Years to project
            growth_rate: Revenue growth rate (optional override)
            override_wacc: WACC override (optional)
        
        Returns:
            Dict dengan valuation result dan assumptions
        """
        try:
            # Override if provided
            if override_wacc:
                self.wacc = override_wacc
                logger.info(f"WACC overridden to {self.wacc:.1%}")
            
            if growth_rate is None:
                growth_rate = self.calculate_revenue_cagr()
            
            # Fetch data if not already loaded
            if self.financials is None:
                self.fetch_financial_data()
            
            # Get shares outstanding
            shares = self.fetcher.get_shares_outstanding()
            if shares is None:
                shares = 1.0
                logger.warning(f"Using default shares estimate for {self.ticker}")
            
            # Project cash flows
            projections = self.project_cashflows(projection_years, growth_rate)
            
            # Terminal value
            fcf_year_last = projections['fcf'].iloc[-1]
            terminal_value = self.calculate_terminal_value(fcf_year_last)
            
            # Discount to PV
            pv_data = self.discount_cashflows(projections, terminal_value)
            
            # Enterprise value & equity value
            enterprise_value = pv_data['pv_fcf'] + pv_data['pv_terminal']
            equity_value = enterprise_value  # Simplified (assume net debt = 0)
            
            # Per share value (dalam Rp)
            fair_value_per_share = (equity_value / shares) * 1000
            
            # Valuation range (±10%)
            fair_value_low = fair_value_per_share * 0.90
            fair_value_high = fair_value_per_share * 1.10
            
            result = {
                'ticker': self.ticker,
                'fair_value_per_share': fair_value_per_share,
                'fair_value_low': fair_value_low,
                'fair_value_high': fair_value_high,
                'enterprise_value': enterprise_value,
                'equity_value': equity_value,
                'shares_outstanding': shares,
                'pv_fcf': pv_data['pv_fcf'],
                'pv_terminal': pv_data['pv_terminal'],
                'wacc': self.wacc,
                'revenue_cagr': growth_rate,
                'fcf_margin': self.calculate_fcf_margin(),
                'assumptions': {
                    'projection_years': projection_years,
                    'growth_rate': growth_rate,
                    'terminal_growth': self.terminal_growth,
                    'wacc': self.wacc
                }
            }
            
            # Validate result
            if not DataValidator.validate_dcf_result(result):
                logger.warning(f"DCF result validation failed for {self.ticker}")
            
            logger.info(f"✓ DCF valuation complete for {self.ticker}")
            logger.info(f"  Fair Value: Rp {fair_value_per_share:,.0f}")
            
            return result
        
        except Exception as e:
            logger.error(f"Error dalam DCF calculation: {e}")
            raise CalculationException(f"DCF calculation failed: {e}")


# Example usage
if __name__ == "__main__":
    stocks = ["BBCA", "ASII", "TLKM"]
    
    for ticker in stocks:
        print(f"\n{'='*50}")
        print(f"DCF Valuation: {ticker}")
        print(f"{'='*50}")
        
        try:
            dcf = UniversalDCFValuation(ticker)
            result = dcf.calculate_fair_value()
            
            print(f"Fair Value: Rp {result['fair_value_per_share']:,.0f}")
            print(f"Range: Rp {result['fair_value_low']:,.0f} - Rp {result['fair_value_high']:,.0f}")
            print(f"Growth Rate: {result['revenue_cagr']:.1%}")
            print(f"WACC: {result['wacc']:.1%}")
        
        except Exception as e:
            print(f"Error: {e}")

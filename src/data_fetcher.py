"""
Data Fetcher untuk equity research skill
Supports ANY IDX stock dengan universal architecture
"""

import yfinance as yf
import pandas as pd
from typing import Dict, Optional, List
import logging
from src.error_handler import (
    DataFetchException, ValidationException,
    validate_stock_ticker, retry_on_failure
)
from src.utils import (
    save_to_cache, load_from_cache, get_sector_for_stock,
    get_peers_for_stock, estimate_wacc_by_sector
)

logger = logging.getLogger(__name__)


class DynamicDataFetcher:
    """
    Universal data fetcher untuk ANY stock
    Supports 700+ IDX stocks
    """
    
    def __init__(self, ticker: str):
        """
        Initialize dengan any stock ticker
        
        Args:
            ticker: Stock ticker (BBCA, ASII, TLKM, etc)
        
        Raises:
            ValidationException: Jika ticker invalid
        """
        self.ticker = ticker.upper()
        
        # Validate ticker format
        if not validate_stock_ticker(self.ticker):
            raise ValidationException(f"Invalid ticker format: {self.ticker}")
        
        self.symbol = f"{self.ticker}.JK"  # Yahoo Finance format
        self.sector = self.get_sector()
        self.peers = self.get_peers()
        self.estimated_wacc = estimate_wacc_by_sector(self.sector)
        
        logger.info(f"Initialized DataFetcher for {self.ticker} (sector: {self.sector})")
    
    def get_sector(self) -> str:
        """Get sector untuk stock"""
        return get_sector_for_stock(self.ticker)
    
    def get_peers(self) -> List[str]:
        """Get peer stocks (same sector)"""
        return get_peers_for_stock(self.ticker, max_peers=3)
    
    @retry_on_failure(max_retries=2, delay=0.5)
    def validate_stock(self) -> bool:
        """
        Validate if stock exists dan tradeable
        
        Returns:
            True jika stock valid
        
        Raises:
            DataFetchException: Jika stock tidak valid
        """
        try:
            ticker_obj = yf.Ticker(self.symbol)
            info = ticker_obj.info
            
            # Check if data available
            if info.get('regularMarketPrice') is None:
                raise DataFetchException(f"No market data for {self.ticker}")
            
            logger.info(f"✓ Stock {self.ticker} validated")
            return True
        
        except Exception as e:
            logger.error(f"Stock validation failed for {self.ticker}: {str(e)}")
            raise DataFetchException(f"Could not validate {self.ticker}: {str(e)}")
    
    @retry_on_failure(max_retries=2, delay=0.5)
    def fetch_current_price(self) -> Optional[float]:
        """
        Get current stock price
        
        Returns:
            Current price dalam Rp, atau None jika tidak ada data
        """
        # Check cache first
        cached = load_from_cache(self.ticker, 'price')
        if cached:
            return cached.get('price')
        
        try:
            ticker = yf.Ticker(self.symbol)
            price = ticker.info.get('regularMarketPrice')
            
            if price is None:
                # Fallback: get latest close dari history
                hist = ticker.history(period="1d")
                if hist.empty:
                    logger.warning(f"No price data available for {self.ticker}")
                    return None
                price = hist['Close'].iloc[-1]
            
            # Cache result
            save_to_cache(self.ticker, 'price', {'price': float(price)})
            return float(price)
        
        except Exception as e:
            logger.warning(f"Could not fetch current price for {self.ticker}: {e}")
            return None
    
    @retry_on_failure(max_retries=2, delay=0.5)
    def fetch_historical_prices(self, period: str = "1y") -> pd.DataFrame:
        """
        Get historical price data
        
        Args:
            period: Time period (1y, 6mo, 3mo, 1mo, etc)
        
        Returns:
            DataFrame dengan Close prices
        """
        try:
            ticker = yf.Ticker(self.symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                logger.warning(f"No historical data for {self.ticker}")
                return pd.DataFrame()
            
            return hist[['Close']]
        
        except Exception as e:
            logger.warning(f"Could not fetch price history for {self.ticker}: {e}")
            return pd.DataFrame()
    
    @retry_on_failure(max_retries=2, delay=0.5)
    def fetch_financials(self) -> Dict:
        """
        Fetch financial data (revenue, net income, etc)
        
        Returns:
            Dict {year: {revenue, net_income, capex, depreciation}} dalam Rp billions
        """
        # Check cache
        cached = load_from_cache(self.ticker, 'financials')
        if cached:
            return cached
        
        try:
            ticker = yf.Ticker(self.symbol)
            quarterly_financials = ticker.quarterly_financials
            
            if quarterly_financials is None or quarterly_financials.empty:
                logger.warning(f"No financial data available for {self.ticker}")
                return {}
            
            financials = {}
            
            try:
                # Get revenue dan net income rows
                revenues = quarterly_financials.loc['Total Revenue']
                net_income = quarterly_financials.loc['Net Income']
            except KeyError:
                logger.warning(f"Missing key financial metrics for {self.ticker}")
                return {}
            
            # Group by year (convert quarterly to annual)
            for col in revenues.index[-8:]:  # Last 8 quarters = 2 years
                year = col.year
                
                if year not in financials:
                    financials[year] = {
                        'revenue': 0,
                        'net_income': 0,
                        'capex': 0,
                        'depreciation': 0
                    }
                
                # Add quarterly data
                if pd.notna(revenues[col]):
                    financials[year]['revenue'] += revenues[col]
                if pd.notna(net_income[col]):
                    financials[year]['net_income'] += net_income[col]
            
            # Convert to Rp billions
            for year in list(financials.keys()):
                for key in financials[year]:
                    financials[year][key] = financials[year][key] / 1e9
            
            # Cache result
            save_to_cache(self.ticker, 'financials', financials)
            
            logger.info(f"✓ Fetched financials for {self.ticker}")
            return financials
        
        except Exception as e:
            logger.warning(f"Error fetching financials for {self.ticker}: {e}")
            return {}
    
    @retry_on_failure(max_retries=2, delay=0.5)
    def fetch_key_metrics(self) -> Dict:
        """
        Fetch key valuation metrics (P/E, P/B, ROE, dividend yield, dll)
        
        Returns:
            Dict dengan metrics
        """
        # Check cache
        cached = load_from_cache(self.ticker, 'metrics')
        if cached:
            return cached
        
        try:
            ticker = yf.Ticker(self.symbol)
            info = ticker.info
            
            metrics = {
                'price': info.get('regularMarketPrice'),
                'pe_ratio': info.get('trailingPE'),
                'pb_ratio': info.get('priceToBook'),
                'roe': info.get('returnOnEquity'),
                'roa': None,
                'dividend_yield': info.get('dividendYield'),
                'market_cap': info.get('marketCap'),
                'shares_outstanding': info.get('sharesOutstanding'),
                'debt': info.get('totalDebt'),
            }
            
            # Filter out None values
            metrics = {k: v for k, v in metrics.items() if v is not None}
            
            # Cache result
            save_to_cache(self.ticker, 'metrics', metrics)
            
            logger.info(f"✓ Fetched metrics for {self.ticker}")
            return metrics
        
        except Exception as e:
            logger.warning(f"Error fetching metrics for {self.ticker}: {e}")
            return {}
    
    @retry_on_failure(max_retries=2, delay=0.5)
    def fetch_dividend_history(self, years: int = 5) -> pd.DataFrame:
        """
        Get historical dividend payments
        
        Args:
            years: Number of years to retrieve
        
        Returns:
            DataFrame dengan dividend history
        """
        # Check cache
        cached = load_from_cache(self.ticker, 'dividends')
        if cached is not None:
            return pd.DataFrame(cached)
        
        try:
            ticker = yf.Ticker(self.symbol)
            dividends = ticker.dividends
            
            if dividends.empty:
                logger.warning(f"No dividend history for {self.ticker}")
                return pd.DataFrame()
            
            # Filter to requested years
            cutoff_date = pd.Timestamp.now() - pd.Timedelta(days=365*years)
            recent_divs = dividends[dividends.index > cutoff_date]
            
            # Cache result
            dividend_dict = recent_divs.to_dict()
            save_to_cache(self.ticker, 'dividends', dividend_dict)
            
            logger.info(f"✓ Fetched dividends for {self.ticker}")
            return recent_divs.to_frame('dividend')
        
        except Exception as e:
            logger.warning(f"Error fetching dividends for {self.ticker}: {e}")
            return pd.DataFrame()
    
    def fetch_peer_metrics(self) -> pd.DataFrame:
        """
        Fetch metrics untuk stock + peers
        
        Returns:
            DataFrame dengan metrics untuk semua stocks
        """
        metrics_list = []
        
        # Get own metrics
        try:
            own_metrics = self.fetch_key_metrics()
            own_metrics['ticker'] = self.ticker
            metrics_list.append(own_metrics)
        except:
            logger.warning(f"Could not fetch own metrics for {self.ticker}")
        
        # Get peers metrics
        for peer_ticker in self.peers:
            try:
                peer_fetcher = DynamicDataFetcher(peer_ticker)
                peer_metrics = peer_fetcher.fetch_key_metrics()
                peer_metrics['ticker'] = peer_ticker
                metrics_list.append(peer_metrics)
            except:
                logger.warning(f"Could not fetch metrics for peer {peer_ticker}")
        
        if not metrics_list:
            return pd.DataFrame()
        
        return pd.DataFrame(metrics_list)
    
    def get_shares_outstanding(self) -> Optional[float]:
        """
        Get number of shares outstanding
        
        Returns:
            Shares dalam billions, atau None jika tidak ada data
        """
        try:
            ticker = yf.Ticker(self.symbol)
            shares = ticker.info.get('sharesOutstanding')
            
            if shares:
                return shares / 1e9  # Convert to billions
            else:
                # Fallback: estimate dari market cap / price
                price = self.fetch_current_price()
                if price:
                    market_cap = ticker.info.get('marketCap')
                    if market_cap:
                        return (market_cap / price) / 1e9
            
            return None
        
        except Exception as e:
            logger.warning(f"Could not get shares outstanding for {self.ticker}: {e}")
            return None
    
    def get_all_data(self) -> Dict:
        """
        Get semua data sekaligus
        
        Returns:
            Dict dengan semua data yang diperlukan
        """
        return {
            'ticker': self.ticker,
            'sector': self.sector,
            'peers': self.peers,
            'wacc': self.estimated_wacc,
            'current_price': self.fetch_current_price(),
            'financials': self.fetch_financials(),
            'metrics': self.fetch_key_metrics(),
            'dividends': self.fetch_dividend_history(),
            'shares_outstanding': self.get_shares_outstanding(),
        }


# Example usage
if __name__ == "__main__":
    # Test dengan berbagai stocks
    stocks = ["BBCA", "ASII", "TLKM"]
    
    for ticker in stocks:
        print(f"\n{'='*50}")
        print(f"Testing {ticker}")
        print(f"{'='*50}")
        
        try:
            fetcher = DynamicDataFetcher(ticker)
            
            # Validate
            fetcher.validate_stock()
            
            # Fetch data
            price = fetcher.fetch_current_price()
            sector = fetcher.get_sector()
            peers = fetcher.get_peers()
            metrics = fetcher.fetch_key_metrics()
            
            print(f"✓ Ticker: {ticker}")
            print(f"✓ Sector: {sector}")
            print(f"✓ Price: Rp {price:,.0f}" if price else "✗ No price data")
            print(f"✓ Peers: {', '.join(peers)}")
            print(f"✓ WACC: {fetcher.estimated_wacc:.1%}")
            if metrics:
                print(f"✓ P/E: {metrics.get('pe_ratio', 'N/A')}")
        
        except Exception as e:
            print(f"✗ Error: {e}")

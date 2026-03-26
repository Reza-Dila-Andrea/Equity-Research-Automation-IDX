"""
Peer Comparison, Dividend Analysis, dan Technical Analysis modules
Production-ready implementations
"""

import pandas as pd
import logging
from typing import Dict, Optional
from src.data_fetcher import DynamicDataFetcher
from src.utils import format_number, format_percent, format_ratio, safe_divide

logger = logging.getLogger(__name__)


# ============================================================================
# PEER COMPARISON
# ============================================================================

class UniversalPeerComparison:
    """Universal peer comparison untuk any stock"""
    
    def __init__(self, ticker: str):
        self.ticker = ticker.upper()
        self.fetcher = DynamicDataFetcher(ticker)
        self.peers = self.fetcher.get_peers()
        self.metrics_data = None
    
    def fetch_peer_metrics(self) -> pd.DataFrame:
        """Fetch metrics untuk stock + peers"""
        try:
            self.metrics_data = self.fetcher.fetch_peer_metrics()
            logger.info(f"✓ Fetched peer metrics for {self.ticker}")
            return self.metrics_data
        except Exception as e:
            logger.error(f"Error fetching peer metrics: {e}")
            return pd.DataFrame()
    
    def calculate_sector_averages(self) -> Dict:
        """Calculate sector average untuk each metric"""
        if self.metrics_data is None or self.metrics_data.empty:
            return {}
        
        metrics = ['pe_ratio', 'pb_ratio', 'roe', 'roa', 'dividend_yield']
        averages = {}
        
        for metric in metrics:
            if metric in self.metrics_data.columns:
                avg = self.metrics_data[metric].mean()
                averages[f'{metric}_avg'] = avg
        
        return averages
    
    def generate_comparison_table(self) -> str:
        """Generate markdown table untuk peer comparison"""
        if self.metrics_data is None or self.metrics_data.empty:
            return "No peer data available"
        
        table = "| Ticker | P/E | P/B | ROE | Div Yield |\n"
        table += "|--------|-----|-----|-----|--------|\n"
        
        for _, row in self.metrics_data.iterrows():
            ticker = row.get('ticker', 'N/A')
            pe = format_ratio(row.get('pe_ratio'))
            pb = format_ratio(row.get('pb_ratio'))
            roe = format_percent(row.get('roe', 0) / 100 if row.get('roe') else 0)
            div = format_percent(row.get('dividend_yield', 0))
            
            table += f"| {ticker} | {pe} | {pb} | {roe} | {div} |\n"
        
        return table
    
    def analyze_valuation(self) -> str:
        """Provide qualitative valuation analysis"""
        if self.metrics_data is None or self.metrics_data.empty:
            return "Insufficient peer data for analysis"
        
        stock = self.metrics_data[self.metrics_data['ticker'] == self.ticker]
        if stock.empty:
            return "Stock data not found"
        
        stock_row = stock.iloc[0]
        peers = self.metrics_data[self.metrics_data['ticker'] != self.ticker]
        
        if peers.empty:
            return "No peers available"
        
        analysis = f"\nValuation Analysis ({self.ticker}):\n"
        analysis += "─" * 40 + "\n"
        
        # P/E analysis
        if 'pe_ratio' in stock_row and not pd.isna(stock_row['pe_ratio']):
            pe_vs_peers = stock_row['pe_ratio'] - peers['pe_ratio'].mean()
            analysis += f"P/E: {stock_row['pe_ratio']:.1f}x vs peers {peers['pe_ratio'].mean():.1f}x\n"
            analysis += f"  → {'Premium' if pe_vs_peers > 0 else 'Discount'} by {abs(pe_vs_peers):.1f}x\n"
        
        # ROE analysis
        if 'roe' in stock_row and not pd.isna(stock_row['roe']):
            roe_vs_peers = stock_row['roe'] - peers['roe'].mean()
            analysis += f"ROE: {stock_row['roe']:.1%} vs peers {peers['roe'].mean():.1%}\n"
            analysis += f"  → {'Superior' if roe_vs_peers > 0 else 'Below'} by {abs(roe_vs_peers):.1%}\n"
        
        return analysis


# ============================================================================
# DIVIDEND ANALYSIS
# ============================================================================

class UniversalDividendAnalysis:
    """Universal dividend analysis untuk any stock"""
    
    def __init__(self, ticker: str):
        self.ticker = ticker.upper()
        self.fetcher = DynamicDataFetcher(ticker)
        self.dividend_history = None
    
    def fetch_dividend_history(self) -> pd.DataFrame:
        """Get historical dividends"""
        try:
            self.dividend_history = self.fetcher.fetch_dividend_history()
            logger.info(f"✓ Fetched dividend history for {self.ticker}")
            return self.dividend_history
        except Exception as e:
            logger.error(f"Error fetching dividends: {e}")
            return pd.DataFrame()
    
    def has_dividend_history(self) -> bool:
        """Check if stock has dividend history"""
        if self.dividend_history is None:
            self.fetch_dividend_history()
        return not self.dividend_history.empty
    
    def calculate_dividend_cagr(self) -> Optional[float]:
        """Calculate dividend CAGR"""
        if self.dividend_history is None or len(self.dividend_history) < 2:
            return None
        
        divs = self.dividend_history['dividend'].values
        if len(divs) < 2 or divs[0] <= 0:
            return None
        
        years = len(divs) - 1
        return (divs[-1] / divs[0]) ** (1 / years) - 1
    
    def calculate_sustainability_score(self) -> float:
        """Score dividend sustainability (0-1)"""
        if not self.has_dividend_history():
            return 0.5  # Default neutral
        
        score = 0
        max_score = 3
        
        # Check for cuts
        divs = self.dividend_history['dividend'].values
        has_cuts = any(divs[i] < divs[i-1] for i in range(1, len(divs)))
        score += 0 if has_cuts else 1
        
        # Check for growth
        cagr = self.calculate_dividend_cagr()
        if cagr and cagr > 0.05:
            score += 1
        
        # Check for stable payout
        if len(divs) >= 3:
            score += 1
        
        return min(score / max_score, 1.0)
    
    def generate_dividend_report(self) -> str:
        """Generate dividend analysis report"""
        if not self.has_dividend_history():
            return f"No dividend history available for {self.ticker}"
        
        report = f"Dividend Analysis ({self.ticker})\n"
        report += "─" * 40 + "\n"
        
        divs = self.dividend_history['dividend'].values
        report += f"Dividend per share (last): Rp {divs[-1]:,.0f}\n"
        
        cagr = self.calculate_dividend_cagr()
        if cagr:
            report += f"CAGR: {cagr:+.1%}\n"
        
        score = self.calculate_sustainability_score()
        stars = "⭐" * int(score * 5)
        report += f"Sustainability: {stars} ({score:.1%})\n"
        
        return report


# ============================================================================
# TECHNICAL ANALYSIS
# ============================================================================

class UniversalTechnicalAnalysis:
    """Technical analysis untuk any stock"""
    
    def __init__(self, ticker: str):
        self.ticker = ticker.upper()
        self.fetcher = DynamicDataFetcher(ticker)
        self.price_data = None
    
    def fetch_price_data(self, period: str = "1y") -> pd.DataFrame:
        """Fetch historical prices"""
        try:
            self.price_data = self.fetcher.fetch_historical_prices(period)
            logger.info(f"✓ Fetched price data for {self.ticker}")
            return self.price_data
        except Exception as e:
            logger.error(f"Error fetching prices: {e}")
            return pd.DataFrame()
    
    def calculate_moving_averages(self, periods: list = None) -> Dict:
        """Calculate moving averages"""
        if self.price_data is None or self.price_data.empty:
            return {}
        
        if periods is None:
            periods = [50, 200]
        
        mas = {}
        for period in periods:
            if len(self.price_data) >= period:
                ma = self.price_data['Close'].rolling(window=period).mean().iloc[-1]
                mas[f'ma_{period}'] = ma
        
        return mas
    
    def calculate_rsi(self, period: int = 14) -> Optional[float]:
        """Calculate RSI (Relative Strength Index)"""
        if self.price_data is None or len(self.price_data) < period + 1:
            return None
        
        delta = self.price_data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1]
    
    def get_technical_signal(self) -> str:
        """Get technical signal"""
        if self.price_data is None or self.price_data.empty:
            return "NEUTRAL"
        
        current_price = self.price_data['Close'].iloc[-1]
        mas = self.calculate_moving_averages()
        rsi = self.calculate_rsi()
        
        # Simple signal logic
        signals = []
        
        # MA signal
        if 'ma_50' in mas and 'ma_200' in mas:
            if mas['ma_50'] > mas['ma_200']:
                signals.append("BULLISH")
            else:
                signals.append("BEARISH")
        
        # RSI signal
        if rsi:
            if rsi < 30:
                signals.append("OVERSOLD")
            elif rsi > 70:
                signals.append("OVERBOUGHT")
        
        return " | ".join(signals) if signals else "NEUTRAL"
    
    def generate_technical_report(self) -> str:
        """Generate technical analysis report"""
        if self.price_data is None or self.price_data.empty:
            return "Insufficient price data for technical analysis"
        
        report = f"Technical Analysis ({self.ticker})\n"
        report += "─" * 40 + "\n"
        
        current_price = self.price_data['Close'].iloc[-1]
        report += f"Current Price: Rp {current_price:,.0f}\n"
        
        mas = self.calculate_moving_averages()
        for ma_key, ma_val in mas.items():
            period = ma_key.split('_')[1]
            report += f"MA({period}): Rp {ma_val:,.0f}\n"
        
        rsi = self.calculate_rsi()
        if rsi:
            report += f"RSI(14): {rsi:.1f}\n"
        
        signal = self.get_technical_signal()
        report += f"Signal: {signal}\n"
        
        return report

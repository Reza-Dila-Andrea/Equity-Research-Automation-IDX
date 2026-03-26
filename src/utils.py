"""
Utility functions untuk equity research skill
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import hashlib
import logging

logger = logging.getLogger(__name__)


# Cache management
CACHE_DIR = "data/cache"
CACHE_EXPIRY_HOURS = 6


def ensure_cache_dir():
    """Ensure cache directory exists"""
    os.makedirs(CACHE_DIR, exist_ok=True)


def get_cache_path(ticker: str, data_type: str) -> str:
    """
    Get cache file path untuk stock data
    
    Args:
        ticker: Stock ticker
        data_type: Type of data (price, financials, metrics, etc)
    
    Returns:
        File path
    """
    return os.path.join(CACHE_DIR, f"{ticker}_{data_type}.json")


def save_to_cache(ticker: str, data_type: str, data: Dict):
    """
    Save data ke cache file
    
    Args:
        ticker: Stock ticker
        data_type: Type of data
        data: Data to cache
    """
    ensure_cache_dir()
    
    cache_path = get_cache_path(ticker, data_type)
    cache_data = {
        'timestamp': datetime.now().isoformat(),
        'data': data
    }
    
    try:
        with open(cache_path, 'w') as f:
            json.dump(cache_data, f, indent=2, default=str)
        logger.info(f"Cached {data_type} for {ticker}")
    except Exception as e:
        logger.warning(f"Could not cache data: {e}")


def load_from_cache(ticker: str, data_type: str) -> Dict:
    """
    Load data dari cache file
    
    Args:
        ticker: Stock ticker
        data_type: Type of data
    
    Returns:
        Cached data atau None if expired/missing
    """
    cache_path = get_cache_path(ticker, data_type)
    
    if not os.path.exists(cache_path):
        return None
    
    try:
        with open(cache_path, 'r') as f:
            cache_data = json.load(f)
        
        # Check if cache expired
        cached_time = datetime.fromisoformat(cache_data['timestamp'])
        age_hours = (datetime.now() - cached_time).total_seconds() / 3600
        
        if age_hours > CACHE_EXPIRY_HOURS:
            logger.info(f"Cache expired for {ticker}_{data_type}")
            return None
        
        logger.info(f"Loaded {ticker}_{data_type} from cache")
        return cache_data['data']
    
    except Exception as e:
        logger.warning(f"Could not load from cache: {e}")
        return None


def clear_cache(ticker: str = None):
    """
    Clear cache files
    
    Args:
        ticker: Specific ticker to clear (None = clear all)
    """
    if ticker:
        for file in os.listdir(CACHE_DIR):
            if file.startswith(ticker):
                try:
                    os.remove(os.path.join(CACHE_DIR, file))
                    logger.info(f"Cleared cache for {ticker}")
                except:
                    pass
    else:
        try:
            for file in os.listdir(CACHE_DIR):
                os.remove(os.path.join(CACHE_DIR, file))
            logger.info("Cleared all cache")
        except:
            pass


# Number formatting
def format_number(value: float, decimals: int = 0, prefix: str = "Rp") -> str:
    """
    Format number dengan Indonesian thousands separator
    
    Args:
        value: Number to format
        decimals: Number of decimal places
        prefix: Currency prefix (default: Rp)
    
    Returns:
        Formatted string
    """
    if value is None:
        return "N/A"
    
    if decimals == 0:
        formatted = f"{value:,.0f}"
    else:
        formatted = f"{value:,.{decimals}f}"
    
    if prefix:
        return f"{prefix} {formatted}"
    return formatted


def format_percent(value: float, decimals: int = 1) -> str:
    """
    Format percentage
    
    Args:
        value: Value (0-1 scale)
        decimals: Decimal places
    
    Returns:
        Formatted percentage string
    """
    if value is None:
        return "N/A"
    
    return f"{value*100:.{decimals}f}%"


def format_ratio(value: float, decimals: int = 1) -> str:
    """
    Format ratio (P/E, P/B, etc)
    
    Args:
        value: Ratio value
        decimals: Decimal places
    
    Returns:
        Formatted ratio string
    """
    if value is None:
        return "N/A"
    
    return f"{value:.{decimals}f}x"


# Stock sector/peer data
def load_sector_config() -> Dict:
    """Load sector and peer configuration"""
    config_file = "config/sector_config.json"
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except:
            pass
    
    # Default configuration
    return {
        'banking': ['BBCA', 'BMRI', 'BBBR', 'BBNI', 'BBKP'],
        'automotive': ['ASII', 'UNTR', 'IMAS'],
        'telecom': ['TLKM', 'ISAT'],
        'energy': ['PGAS', 'EXCL'],
        'food-beverage': ['INDF', 'UNVR'],
        'retail': ['HMSP', 'MITRA'],
    }


def get_sector_for_stock(ticker: str) -> str:
    """Get sector untuk stock"""
    sector_config = load_sector_config()
    
    for sector, stocks in sector_config.items():
        if ticker in stocks:
            return sector
    
    return "other"


def get_peers_for_stock(ticker: str, max_peers: int = 3) -> List[str]:
    """Get peer stocks untuk comparison"""
    sector = get_sector_for_stock(ticker)
    sector_config = load_sector_config()
    
    if sector not in sector_config:
        return []
    
    peers = sector_config[sector]
    # Remove self
    peers = [p for p in peers if p != ticker]
    # Return top N
    return peers[:max_peers]


# WACC estimation
def estimate_wacc_by_sector(sector: str) -> float:
    """
    Estimate WACC based on sector
    
    Reasonable WACC ranges for Indonesian stocks:
    - Banking: 8-9% (large, stable)
    - Telecom: 9-10% (regulated)
    - Energy: 9-11% (commodity)
    - Automotive: 10-12% (cyclical)
    - Retail: 11-13% (competitive)
    - Food: 8-10% (stable)
    - Other: 10% (default)
    """
    wacc_by_sector = {
        'banking': 0.09,
        'telecom': 0.095,
        'energy': 0.10,
        'automotive': 0.11,
        'food-beverage': 0.09,
        'retail': 0.12,
    }
    
    return wacc_by_sector.get(sector, 0.10)


# Report generation
def generate_markdown_table(headers: List[str], rows: List[List[Any]]) -> str:
    """
    Generate markdown table
    
    Args:
        headers: Column headers
        rows: Data rows
    
    Returns:
        Markdown table string
    """
    # Header
    table = "| " + " | ".join(headers) + " |\n"
    table += "|" + "|".join(["-" * 8 for _ in headers]) + "|\n"
    
    # Rows
    for row in rows:
        table += "| " + " | ".join([str(cell) for cell in row]) + " |\n"
    
    return table


def generate_report_filename(ticker: str, report_type: str = "full") -> str:
    """
    Generate report filename
    
    Args:
        ticker: Stock ticker
        report_type: Type of report (full, summary, etc)
    
    Returns:
        Filename
    """
    timestamp = datetime.now().strftime("%Y%m%d")
    return f"{ticker}_{report_type}_{timestamp}.md"


# Data transformation
def billions_to_millions(value: float) -> float:
    """Convert billions to millions"""
    if value is None:
        return None
    return value * 1000


def millions_to_billions(value: float) -> float:
    """Convert millions to billions"""
    if value is None:
        return None
    return value / 1000


def calculate_cagr(start_value: float, end_value: float, periods: int) -> float:
    """
    Calculate CAGR (Compound Annual Growth Rate)
    
    Args:
        start_value: Starting value
        end_value: Ending value
        periods: Number of periods
    
    Returns:
        CAGR as decimal (0-1 scale)
    """
    if start_value <= 0 or periods <= 0:
        return 0
    
    return (end_value / start_value) ** (1 / periods) - 1


def calculate_ytd_performance(current_price: float, ytd_open: float) -> float:
    """
    Calculate YTD performance
    
    Args:
        current_price: Current stock price
        ytd_open: Opening price at start of year
    
    Returns:
        YTD return as decimal
    """
    if ytd_open <= 0:
        return 0
    
    return (current_price - ytd_open) / ytd_open


# Validation helpers
def is_valid_price(price: float) -> bool:
    """Check if price is valid"""
    return price is not None and price > 0


def is_valid_percentage(value: float) -> bool:
    """Check if value is valid percentage (0-1 range)"""
    return value is not None and 0 <= value <= 1


def is_valid_ratio(value: float) -> bool:
    """Check if value is valid ratio"""
    return value is not None and value >= 0


# Color/emoji helpers for console output
def get_rating_emoji(rating: str) -> str:
    """Get emoji untuk rating"""
    emoji_map = {
        'STRONG BUY': '🚀',
        'BUY': '✓',
        'HOLD': '⏸',
        'SELL': '✗',
    }
    return emoji_map.get(rating, '•')


def get_signal_color(upside: float) -> str:
    """Get color code untuk upside"""
    if upside > 0.20:
        return "🟢"  # Green
    elif upside > 0.10:
        return "🟡"  # Yellow
    elif upside > -0.05:
        return "⚪"  # Neutral
    else:
        return "🔴"  # Red


# File I/O
def save_report(content: str, filepath: str):
    """Save report ke file"""
    try:
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Report saved: {filepath}")
    except Exception as e:
        logger.error(f"Could not save report: {e}")


def load_report(filepath: str) -> str:
    """Load report dari file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Could not load report: {e}")
        return None

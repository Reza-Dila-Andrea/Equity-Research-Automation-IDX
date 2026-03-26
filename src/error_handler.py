"""
Error handling dan logging untuk equity research skill
"""

import logging
from typing import Optional, Any
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('equity_research.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class EquityResearchException(Exception):
    """Base exception untuk equity research skill"""
    pass


class DataFetchException(EquityResearchException):
    """Exception saat fetch data"""
    pass


class ValidationException(EquityResearchException):
    """Exception saat validasi"""
    pass


class CalculationException(EquityResearchException):
    """Exception saat calculation"""
    pass


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safe division dengan default value
    
    Args:
        numerator: Dividend
        denominator: Divisor
        default: Default value jika denominator = 0
    
    Returns:
        Result atau default
    """
    try:
        if denominator == 0:
            logger.warning(f"Division by zero: {numerator}/{denominator}, returning {default}")
            return default
        return numerator / denominator
    except Exception as e:
        logger.error(f"Error dalam division: {e}")
        return default


def safe_get(data: dict, key: str, default: Any = None) -> Any:
    """
    Safe dictionary access
    
    Args:
        data: Dictionary
        key: Key to access
        default: Default value jika key tidak ada
    
    Returns:
        Value atau default
    """
    try:
        return data.get(key, default)
    except Exception as e:
        logger.warning(f"Error accessing {key}: {e}")
        return default


def validate_stock_ticker(ticker: str) -> bool:
    """
    Validate stock ticker format
    
    Args:
        ticker: Stock ticker (e.g., "BBCA")
    
    Returns:
        True if valid, False otherwise
    """
    if not ticker:
        return False
    
    # IDX stocks are usually 4-5 uppercase letters
    if len(ticker) < 3 or len(ticker) > 5:
        return False
    
    if not ticker.isupper():
        return False
    
    if not ticker.isalpha():
        return False
    
    return True


def validate_float(value: Any, min_val: float = None, max_val: float = None) -> bool:
    """
    Validate float value dengan optional range
    
    Args:
        value: Value to validate
        min_val: Minimum value (optional)
        max_val: Maximum value (optional)
    
    Returns:
        True if valid
    """
    try:
        float_val = float(value)
        
        if min_val is not None and float_val < min_val:
            return False
        
        if max_val is not None and float_val > max_val:
            return False
        
        return True
    except:
        return False


def log_calculation(ticker: str, calc_type: str, result: Any, assumptions: dict = None):
    """
    Log calculation untuk audit trail
    
    Args:
        ticker: Stock ticker
        calc_type: Type of calculation (DCF, Peer, etc)
        result: Calculation result
        assumptions: Assumptions used
    """
    timestamp = datetime.now().isoformat()
    
    log_entry = {
        'timestamp': timestamp,
        'ticker': ticker,
        'calc_type': calc_type,
        'result': str(result),
        'assumptions': assumptions
    }
    
    logger.info(f"Calculation: {log_entry}")


def handle_api_error(error: Exception, context: str) -> Optional[Any]:
    """
    Handle API errors dengan graceful fallback
    
    Args:
        error: Exception yang terjadi
        context: Context dimana error terjadi (e.g., "fetch_price_BBCA")
    
    Returns:
        Suggested fallback atau None
    """
    error_msg = str(error)
    
    if "404" in error_msg or "not found" in error_msg.lower():
        logger.warning(f"Resource not found in {context}: {error}")
        return None
    
    elif "timeout" in error_msg.lower() or "connection" in error_msg.lower():
        logger.warning(f"Connection error in {context}, using cached data")
        return "CACHED"
    
    elif "rate limit" in error_msg.lower() or "429" in error_msg:
        logger.warning(f"Rate limited in {context}, please retry later")
        return "RETRY_LATER"
    
    else:
        logger.error(f"Unexpected error in {context}: {error}")
        return None


class DataValidator:
    """Validate financial data"""
    
    @staticmethod
    def validate_financials(financials: dict) -> bool:
        """Validate financial data structure"""
        required_fields = ['revenue', 'net_income']
        
        for year_data in financials.values():
            for field in required_fields:
                if field not in year_data:
                    return False
                
                if not isinstance(year_data[field], (int, float)):
                    return False
        
        return True
    
    @staticmethod
    def validate_metrics(metrics: dict) -> bool:
        """Validate key metrics"""
        if not metrics:
            return False
        
        # At least price atau market_cap should exist
        if 'price' not in metrics and 'market_cap' not in metrics:
            return False
        
        return True
    
    @staticmethod
    def validate_dcf_result(result: dict) -> bool:
        """Validate DCF calculation result"""
        required_keys = [
            'fair_value_per_share',
            'enterprise_value',
            'wacc',
            'assumptions'
        ]
        
        for key in required_keys:
            if key not in result:
                return False
        
        # Fair value should be positive
        if result['fair_value_per_share'] <= 0:
            return False
        
        # WACC should be reasonable (1% - 30%)
        if not 0.01 <= result['wacc'] <= 0.30:
            return False
        
        return True


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """
    Decorator untuk retry logic
    
    Args:
        max_retries: Maximum number of retries
        delay: Delay between retries in seconds
    """
    import time
    from functools import wraps
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}, retrying in {delay}s...")
                        time.sleep(delay)
                    else:
                        logger.error(f"All {max_retries} attempts failed for {func.__name__}")
                        raise
        
        return wrapper
    return decorator

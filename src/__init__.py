"""
Equity Research Reports AI - Universal stock analysis skill for OpenClaw
"""

__version__ = "1.0.0"
__author__ = "Reza"
__description__ = "Automated equity research for Indonesian stocks (IDX)"

from src.data_fetcher import DynamicDataFetcher
from src.dcf_valuation import UniversalDCFValuation
from src.analysis_modules import (
    UniversalPeerComparison,
    UniversalDividendAnalysis,
    UniversalTechnicalAnalysis
)
from src.report_generator import UniversalEquityReportGenerator

__all__ = [
    'DynamicDataFetcher',
    'UniversalDCFValuation',
    'UniversalPeerComparison',
    'UniversalDividendAnalysis',
    'UniversalTechnicalAnalysis',
    'UniversalEquityReportGenerator',
]

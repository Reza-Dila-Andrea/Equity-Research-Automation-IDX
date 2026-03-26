"""
Report Generator
Combines all analyses into professional equity research reports
"""

import logging
from datetime import datetime
from typing import Dict, Optional
from src.data_fetcher import DynamicDataFetcher
from src.dcf_valuation import UniversalDCFValuation
from src.analysis_modules import (
    UniversalPeerComparison,
    UniversalDividendAnalysis,
    UniversalTechnicalAnalysis
)
from src.utils import format_number, format_percent, format_ratio, save_report

logger = logging.getLogger(__name__)


class UniversalEquityReportGenerator:
    """Generate professional equity research reports untuk ANY stock"""
    
    def __init__(self, ticker: str):
        """
        Initialize report generator
        
        Args:
            ticker: Stock ticker
        """
        self.ticker = ticker.upper()
        self.fetcher = DynamicDataFetcher(self.ticker)
        self.current_price = self.fetcher.fetch_current_price()
        
        # Initialize all modules
        self.dcf = UniversalDCFValuation(self.ticker)
        self.peers = UniversalPeerComparison(self.ticker)
        self.dividend = UniversalDividendAnalysis(self.ticker)
        self.technical = UniversalTechnicalAnalysis(self.ticker)
        
        logger.info(f"Initialized ReportGenerator for {self.ticker}")
    
    def calculate_recommendation(self, dcf_result: Dict) -> Dict:
        """
        Calculate investment recommendation
        
        Args:
            dcf_result: DCF valuation result
        
        Returns:
            Dict dengan rating, target price, dan rationale
        """
        if not self.current_price:
            return {
                'rating': 'HOLD',
                'target_price': dcf_result['fair_value_per_share'],
                'upside_downside': 0,
                'thesis': 'Unable to determine price. Manual analysis recommended.'
            }
        
        upside = (dcf_result['fair_value_per_share'] - self.current_price) / self.current_price
        
        # Determine rating based on upside
        if upside > 0.20:
            rating = "STRONG BUY 🚀"
            thesis = f"Trading {abs(upside):.0%} below fair value with strong fundamentals"
        elif upside > 0.10:
            rating = "BUY ✓"
            thesis = f"Attractive valuation with {upside:.0%} upside potential"
        elif upside > -0.05:
            rating = "HOLD ⏸"
            thesis = "Fairly valued at current levels"
        else:
            rating = "SELL ✗"
            thesis = f"Trading at premium valuation. Wait for pullback."
        
        return {
            'rating': rating,
            'target_price': dcf_result['fair_value_per_share'],
            'upside_downside': upside,
            'thesis': thesis
        }
    
    def generate_executive_summary(self) -> str:
        """Generate 1-page executive summary"""
        dcf_result = self.dcf.calculate_fair_value()
        recommendation = self.calculate_recommendation(dcf_result)
        sector = self.fetcher.sector
        
        summary = f"""
# EQUITY RESEARCH REPORT: {self.ticker}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC
**Sector:** {sector.upper()}
**Analyst:** Equity Research AI

## RATING: {recommendation['rating']}

| Metric | Value |
|--------|-------|
| Current Price | Rp {self.current_price:,.0f} |
| Target Price (12mo) | Rp {recommendation['target_price']:,.0f} |
| Upside/Downside | {recommendation['upside_downside']:+.1%} |
| Fair Value Range | Rp {dcf_result['fair_value_low']:,.0f} - {dcf_result['fair_value_high']:,.0f} |

### Investment Thesis
{recommendation['thesis']}

---
"""
        return summary
    
    def generate_valuation_section(self) -> str:
        """Generate DCF valuation section"""
        dcf_result = self.dcf.calculate_fair_value()
        
        section = f"""
## DCF VALUATION ANALYSIS

### Fair Value Calculation
| Metric | Value |
|--------|-------|
| Fair Value | Rp {dcf_result['fair_value_per_share']:,.0f} |
| Valuation Range | Rp {dcf_result['fair_value_low']:,.0f} - {dcf_result['fair_value_high']:,.0f} |
| Enterprise Value | Rp {dcf_result['enterprise_value']:,.0f}B |
| Equity Value | Rp {dcf_result['equity_value']:,.0f}B |
| Shares Outstanding | {dcf_result['shares_outstanding']:.2f}B |

### Key Assumptions
| Assumption | Value |
|-----------|-------|
| Revenue Growth (CAGR) | {dcf_result['revenue_cagr']:.1%} |
| WACC | {dcf_result['wacc']:.1%} |
| Terminal Growth Rate | {dcf_result['assumptions']['terminal_growth']:.1%} |
| Projection Period | {dcf_result['assumptions']['projection_years']} years |
| FCF Margin | {dcf_result['fcf_margin']:.1%} |

### Valuation Breakdown
- PV of Projected Cash Flows (5 years): Rp {dcf_result['pv_fcf']:,.0f}B ({dcf_result['pv_fcf']/dcf_result['enterprise_value']:.0%} of EV)
- PV of Terminal Value: Rp {dcf_result['pv_terminal']:,.0f}B ({dcf_result['pv_terminal']/dcf_result['enterprise_value']:.0%} of EV)

---
"""
        return section
    
    def generate_peer_section(self) -> str:
        """Generate peer comparison section"""
        self.peers.fetch_peer_metrics()
        
        section = f"""
## PEER COMPARISON ANALYSIS

{self.peers.generate_comparison_table()}

### Valuation Assessment
{self.peers.analyze_valuation()}

---
"""
        return section
    
    def generate_dividend_section(self) -> str:
        """Generate dividend analysis section"""
        if not self.dividend.has_dividend_history():
            return "## DIVIDEND ANALYSIS\nNo dividend history available for this stock.\n\n---\n"
        
        section = f"""
## DIVIDEND ANALYSIS & INCOME

{self.dividend.generate_dividend_report()}

---
"""
        return section
    
    def generate_technical_section(self) -> str:
        """Generate technical analysis section"""
        self.technical.fetch_price_data()
        
        section = f"""
## TECHNICAL ANALYSIS

{self.technical.generate_technical_report()}

---
"""
        return section
    
    def generate_risks_section(self) -> str:
        """Generate risks and catalysts section"""
        sector = self.fetcher.sector
        
        # Generic risks by sector
        sector_risks = {
            'banking': [
                'Interest rate increases pressuring net interest margins',
                'Economic slowdown reducing credit demand',
                'Rising non-performing loans'
            ],
            'automotive': [
                'Cyclical slowdown in auto sales',
                'EV transition execution risks',
                'Raw material cost volatility'
            ],
            'telecom': [
                'Regulatory pressures and spectrum costs',
                'Competition in data segment',
                ' currency headwinds'
            ],
            'energy': [
                'Oil price volatility',
                'Regulatory/environmental risks',
                'Transition to renewables'
            ],
            'food-beverage': [
                'Raw material cost inflation',
                'Competitive pricing pressures',
                'Currency risks'
            ],
        }
        
        risks = sector_risks.get(sector, [
            'Market risks',
            'Regulatory changes',
            'Economic slowdown'
        ])
        
        section = f"""
## RISKS & CATALYSTS

### Key Downside Risks
"""
        for i, risk in enumerate(risks, 1):
            section += f"- {risk}\n"
        
        section += f"""
### Key Upside Catalysts
- Quarterly earnings beat
- Dividend announcement/increase
- Strategic announcement
- Sector rotation

---
"""
        return section
    
    def generate_disclaimer_section(self) -> str:
        """Generate disclaimer section"""
        return f"""
## DISCLAIMER

This report is for educational purposes only. It is NOT investment advice.

**Important Notes:**
- Data sources: Yahoo Finance, Investing.com, IDX official
- Valuations based on historical data and assumptions
- Past performance does not guarantee future results
- Consult with a professional financial advisor before investing

**Limitations:**
- Does not account for major M&A or restructuring
- Based on historical trends (may not predict crises)
- Simplified model (not accounting for all factors)

---

*Report generated by Equity Research AI*
*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC*
"""
    
    def generate_full_report(self) -> str:
        """Generate comprehensive 5+ page equity research report"""
        logger.info(f"Generating full report for {self.ticker}")
        
        report = self.generate_executive_summary()
        report += self.generate_valuation_section()
        report += self.generate_peer_section()
        report += self.generate_dividend_section()
        report += self.generate_technical_section()
        report += self.generate_risks_section()
        report += self.generate_disclaimer_section()
        
        logger.info(f"✓ Report generation complete for {self.ticker}")
        return report
    
    def generate_quick_summary(self) -> str:
        """Generate quick 1-page summary"""
        dcf_result = self.dcf.calculate_fair_value()
        recommendation = self.calculate_recommendation(dcf_result)
        
        summary = f"""
# {self.ticker} - QUICK ANALYSIS

**Rating:** {recommendation['rating']}
**Current Price:** Rp {self.current_price:,.0f}
**Fair Value:** Rp {dcf_result['fair_value_per_share']:,.0f}
**Upside/Downside:** {recommendation['upside_downside']:+.1%}

**Key Metrics:**
- Revenue Growth: {dcf_result['revenue_cagr']:.1%}
- WACC: {dcf_result['wacc']:.1%}

**Investment Thesis:**
{recommendation['thesis']}
"""
        return summary
    
    def save_report(self, report_type: str = "full") -> str:
        """
        Save report to file
        
        Args:
            report_type: "full" atau "summary"
        
        Returns:
            Filepath where report was saved
        """
        if report_type == "full":
            content = self.generate_full_report()
            filename = f"reports/{self.ticker}_full_report.md"
        else:
            content = self.generate_quick_summary()
            filename = f"reports/{self.ticker}_summary.md"
        
        save_report(content, filename)
        return filename


# Example usage
if __name__ == "__main__":
    stocks = ["BBCA", "ASII", "TLKM"]
    
    for ticker in stocks:
        print(f"\n{'='*60}")
        print(f"Generating report for {ticker}")
        print(f"{'='*60}")
        
        try:
            gen = UniversalEquityReportGenerator(ticker)
            
            # Generate full report
            report = gen.generate_full_report()
            
            # Save to file
            filepath = gen.save_report("full")
            print(f"✓ Report saved: {filepath}")
            
            # Also print summary
            print("\n" + gen.generate_quick_summary())
        
        except Exception as e:
            print(f"✗ Error generating report: {e}")

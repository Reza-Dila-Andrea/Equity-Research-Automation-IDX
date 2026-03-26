"""
Quick Start Example
Simple example untuk mulai menggunakan equity research skill
"""

import sys
sys.path.insert(0, '.')

from src.report_generator import UniversalEquityReportGenerator


def example_1_quick_analysis():
    """Generate quick summary untuk satu stock"""
    print("="*60)
    print("Example 1: Quick Analysis")
    print("="*60)
    
    ticker = "BBCA"
    gen = UniversalEquityReportGenerator(ticker)
    summary = gen.generate_quick_summary()
    print(summary)


def example_2_full_report():
    """Generate full report untuk satu stock"""
    print("\n" + "="*60)
    print("Example 2: Full Report (1st page)")
    print("="*60)
    
    ticker = "ASII"
    gen = UniversalEquityReportGenerator(ticker)
    report = gen.generate_full_report()
    
    # Print first 2000 chars
    print(report[:2000] + "\n\n[...report continues...]")
    
    # Save to file
    filepath = gen.save_report("full")
    print(f"\n✓ Full report saved to: {filepath}")


def example_3_batch_analysis():
    """Generate reports untuk multiple stocks"""
    print("\n" + "="*60)
    print("Example 3: Batch Analysis")
    print("="*60)
    
    stocks = ["BBCA", "BMRI", "ASII", "TLKM"]
    
    for ticker in stocks:
        try:
            print(f"\nAnalyzing {ticker}...")
            gen = UniversalEquityReportGenerator(ticker)
            
            # Generate quick summary
            summary = gen.generate_quick_summary()
            rating_line = [line for line in summary.split('\n') if 'Rating' in line]
            if rating_line:
                print(f"  {rating_line[0].strip()}")
            
            # Save full report
            filepath = gen.save_report("full")
            print(f"  ✓ Report saved: {filepath}")
        
        except Exception as e:
            print(f"  ✗ Error: {e}")


def example_4_custom_assumptions():
    """Generate report dengan custom assumptions"""
    print("\n" + "="*60)
    print("Example 4: Custom Assumptions")
    print("="*60)
    
    from src.dcf_valuation import UniversalDCFValuation
    
    ticker = "INDF"
    dcf = UniversalDCFValuation(ticker)
    
    print(f"\nGenerating valuation untuk {ticker}...")
    print("Default assumptions:")
    result_default = dcf.calculate_fair_value()
    print(f"  Fair Value: Rp {result_default['fair_value_per_share']:,.0f}")
    print(f"  Growth: {result_default['revenue_cagr']:.1%}")
    print(f"  WACC: {result_default['wacc']:.1%}")
    
    print("\nWith custom assumptions (15% growth, 8% WACC):")
    result_custom = dcf.calculate_fair_value(
        growth_rate=0.15,
        override_wacc=0.08
    )
    print(f"  Fair Value: Rp {result_custom['fair_value_per_share']:,.0f}")
    print(f"  Growth: {result_custom['revenue_cagr']:.1%}")
    print(f"  WACC: {result_custom['wacc']:.1%}")


def example_5_peer_comparison():
    """Compare stock dengan peers"""
    print("\n" + "="*60)
    print("Example 5: Peer Comparison")
    print("="*60)
    
    from src.analysis_modules import UniversalPeerComparison
    
    stocks = ["BBCA", "BMRI", "BBBR"]
    
    for ticker in stocks:
        print(f"\n{ticker} Peer Analysis:")
        peers = UniversalPeerComparison(ticker)
        peers.fetch_peer_metrics()
        print(peers.generate_comparison_table())
        print(peers.analyze_valuation())


def example_6_dividend_analysis():
    """Analyze dividend sustainability"""
    print("\n" + "="*60)
    print("Example 6: Dividend Analysis")
    print("="*60)
    
    from src.analysis_modules import UniversalDividendAnalysis
    
    stocks = ["BBCA", "INDF"]
    
    for ticker in stocks:
        print(f"\n{ticker}:")
        div = UniversalDividendAnalysis(ticker)
        print(div.generate_dividend_report())


if __name__ == "__main__":
    print("\n" + "█"*60)
    print("█ Equity Research Reports AI - Quick Start Examples")
    print("█"*60)
    
    # Run examples
    example_1_quick_analysis()
    example_2_full_report()
    example_3_batch_analysis()
    example_4_custom_assumptions()
    example_5_peer_comparison()
    example_6_dividend_analysis()
    
    print("\n" + "█"*60)
    print("█ All examples completed!")
    print("█ Check 'reports/' folder for generated reports")
    print("█"*60 + "\n")

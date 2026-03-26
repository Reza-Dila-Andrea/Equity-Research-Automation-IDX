#!/usr/bin/env python3
"""
Quick start script for Equity Research Skill
Run this to test the skill immediately
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.report_generator import UniversalEquityReportGenerator

def main():
    """Run quick analysis"""
    print("=" * 60)
    print("Equity Research AI - Quick Start")
    print("=" * 60)
    
    stocks = ["BBCA", "ASII", "TLKM"]
    
    for ticker in stocks:
        try:
            print(f"\nAnalyzing {ticker}...")
            gen = UniversalEquityReportGenerator(ticker)
            summary = gen.generate_quick_summary()
            print(summary)
            print("-" * 60)
        except Exception as e:
            print(f"Error analyzing {ticker}: {e}")
    
    print("\n✓ Quick start complete!")
    print("For full reports, run: gen.save_report('full')")

if __name__ == "__main__":
    main()

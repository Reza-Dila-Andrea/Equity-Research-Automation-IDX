# Equity Research Reports AI

Automated equity research for Indonesian stocks (IDX). Generate professional DCF valuations, peer comparisons, and investment recommendations for ANY IDX stock in seconds.

[![GitHub](https://img.shields.io/badge/GitHub-equity--research--reports--ai-blue)](https://github.com/yourusername/equity-research-reports-ai)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-green)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Features ✨

- **Universal Stock Support**: Works for ALL 700+ IDX stocks (not just BBCA)
- **DCF Valuation**: Discounted cash flow model with automatic WACC by sector
- **Peer Comparison**: Auto-identify sector peers and benchmark metrics
- **Dividend Analysis**: Historical tracking and sustainability scoring
- **Technical Analysis**: Moving averages, RSI, trend signals
- **Professional Reports**: Generate markdown reports ready to share/email
- **Error Handling**: Robust fallbacks and caching
- **Fast**: Generate reports in 8-10 seconds

---

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/equity-research-reports-ai.git
cd equity-research-reports-ai

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
from src.report_generator import UniversalEquityReportGenerator

# Generate report for any stock
gen = UniversalEquityReportGenerator("BBCA")
report = gen.generate_full_report()
print(report)

# Save to file
gen.save_report("full")  # Saves to reports/BBCA_full_report.md
```

### Supported Stocks

**Banking:** BBCA, BMRI, BBBR, BBNI, BBKP
**Automotive:** ASII, UNTR, IMAS
**Telecom:** TLKM, ISAT
**Energy:** PGAS, EXCL
**Food-Beverage:** INDF, UNVR
**Retail:** HMSP, MITRA
**...and 700+ more IDX stocks**

All stocks are supported via dynamic architecture!

---

## Usage Examples

### 1. Quick Analysis

```python
from src.report_generator import UniversalEquityReportGenerator

gen = UniversalEquityReportGenerator("ASII")
print(gen.generate_quick_summary())

# Output:
# ASII - QUICK ANALYSIS
# Rating: BUY ✓
# Current Price: Rp 8,250
# Fair Value: Rp 9,100
# Upside: 10.3%
```

### 2. Full Research Report

```python
gen = UniversalEquityReportGenerator("ASII")
report = gen.generate_full_report()

# Generate 5+ page comprehensive report with:
# - DCF valuation
# - Peer comparison
# - Dividend analysis
# - Technical setup
# - Risks & catalysts
# - Investment recommendation
```

### 3. Direct Module Usage

```python
from src.data_fetcher import DynamicDataFetcher
from src.dcf_valuation import UniversalDCFValuation
from src.analysis_modules import UniversalPeerComparison

# Data fetching
fetcher = DynamicDataFetcher("TLKM")
price = fetcher.fetch_current_price()
metrics = fetcher.fetch_key_metrics()

# DCF valuation
dcf = UniversalDCFValuation("TLKM")
result = dcf.calculate_fair_value()
print(f"Fair Value: Rp {result['fair_value_per_share']:,.0f}")

# Peer comparison
peers = UniversalPeerComparison("TLKM")
print(peers.generate_comparison_table())
```

### 4. Batch Report Generation

```python
stocks = ["BBCA", "BMRI", "ASII", "TLKM", "INDF"]

for ticker in stocks:
    try:
        gen = UniversalEquityReportGenerator(ticker)
        filepath = gen.save_report("full")
        print(f"✓ {ticker}: {filepath}")
    except Exception as e:
        print(f"✗ {ticker}: {e}")
```

### 5. Custom Valuation Assumptions

```python
from src.dcf_valuation import UniversalDCFValuation

dcf = UniversalDCFValuation("BBCA")

# Override assumptions
result = dcf.calculate_fair_value(
    projection_years=5,
    growth_rate=0.10,        # 10% revenue growth
    override_wacc=0.08       # 8% WACC
)

print(f"Custom Fair Value: Rp {result['fair_value_per_share']:,.0f}")
```

---

## Project Structure

```
equity-research-reports-ai/
├── src/
│   ├── __init__.py                 # Package init
│   ├── data_fetcher.py            # Universal data fetching
│   ├── dcf_valuation.py           # DCF model
│   ├── analysis_modules.py        # Peer, dividend, technical analysis
│   ├── report_generator.py        # Report generation
│   ├── error_handler.py           # Error handling & logging
│   └── utils.py                   # Utility functions
├── config/
│   ├── default_config.yaml
│   └── sector_config.json
├── data/
│   ├── cache/                      # API response cache
│   └── sectors.json
├── tests/
│   ├── test_data_fetcher.py
│   ├── test_dcf.py
│   └── test_report_generator.py
├── examples/
│   ├── quick_start.py
│   └── batch_analysis.py
├── reports/                        # Generated reports saved here
├── SKILL.md                        # OpenClaw skill definition
├── README.md                       # This file
├── setup.py                        # Package setup
├── requirements.txt                # Dependencies
├── LICENSE                         # MIT License
└── .gitignore
```

---

## Architecture

### Universal Stock Support

Dynamic architecture automatically handles any stock:

```
User Input: "Analyze ASII"
    ↓
DynamicDataFetcher:
  - Validates ASII ✓
  - Identifies sector: automotive ✓
  - Fetches live data ✓
    ↓
UniversalDCFValuation:
  - Auto WACC by sector ✓
  - Projects cash flows ✓
  - Calculates fair value ✓
    ↓
Report Generation:
  - Creates professional report ✓
```

### Sector-Based Customization

WACC automatically adjusted by sector:

- Banking: 9% (large, stable)
- Telecom: 9.5% (regulated)
- Energy: 10% (commodity)
- Automotive: 11% (cyclical)
- Retail: 12% (competitive)

### Automatic Peer Selection

Peers auto-identified by sector:

```
BBCA (Banking) → Peers: BMRI, BBBR, BBNI
ASII (Auto) → Peers: UNTR, IMAS
TLKM (Telecom) → Peers: ISAT
```

---

## Configuration

### Sector Configuration

Edit `config/sector_config.json` to customize:

```json
{
  "banking": ["BBCA", "BMRI", "BBBR", "BBNI"],
  "automotive": ["ASII", "UNTR", "IMAS"],
  ...
}
```

### Default Assumptions

- Revenue Growth: Historical CAGR (min 2%, max 30%)
- WACC: Sector-based (8-12% range)
- Terminal Growth: 3% (conservative)
- Projection Period: 5 years

Override in code:

```python
result = dcf.calculate_fair_value(
    growth_rate=0.12,      # Override growth
    override_wacc=0.08     # Override WACC
)
```

---

## Data Sources

- **Prices**: Yahoo Finance API
- **Financials**: Yahoo Finance
- **Metrics**: Yahoo Finance (P/E, P/B, ROE, etc)
- **Dividends**: Yahoo Finance
- **Caching**: Local JSON cache (6-hour TTL)

---

## Error Handling

Graceful fallbacks for common issues:

| Error | Fallback |
|-------|----------|
| No price data | Use estimated value |
| No financials | Use default assumptions |
| No peers | Continue without comparison |
| API timeout | Use cached data |

---

## Testing

```bash
# Run tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_dcf.py -v

# Generate coverage
python -m pytest --cov=src tests/
```

---

## Limitations

- ⚠️ Simplified DCF model (not accounting for all factors)
- ⚠️ Assumes net debt = 0 (may not be accurate)
- ⚠️ Based on historical trends (may not predict crises)
- ⚠️ Does not account for major M&A or restructuring
- ⚠️ Yahoo Finance API delays of ~15 minutes

---

## Performance

- Report generation: 8-10 seconds per stock
- API calls per report: 3-5 (cached after)
- Typical cost: $0.01-0.05 per report
- Memory usage: ~50MB

---

## Roadmap

- [ ] v1.1: Machine learning valuation models
- [ ] v1.2: Earnings surprise analysis
- [ ] v1.3: Real-time price alerts
- [ ] v2.0: API access + white-label solution
- [ ] v2.1: Mobile app integration
- [ ] v2.2: Portfolio tracking

---

## Contributing

Contributions welcome! Please:

1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

---

## License

MIT License - see [LICENSE](LICENSE) file for details

---

## Disclaimer

**This tool is for educational purposes only. NOT investment advice.**

- Past performance does not guarantee future results
- Always consult a professional financial advisor before investing
- Data may have delays or inaccuracies
- Simplified model with limitations

---

## Acknowledgments

- Data: Yahoo Finance, Investing.com
- IDX official sources
- OpenClaw community

---

## Citation

If you use this in research/publication:

```bibtex
@software{equity_research_2024,
  title={Equity Research Reports AI},
  author={Reza},
  year={2024},
  url={https://github.com/yourusername/equity-research-reports-ai}
}
```

---

**Made with ❤️ for Indonesian stock market investors**

⭐ If useful, please star on GitHub!

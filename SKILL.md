---
name: equity-research-reports-ai
description: >
  Automated equity research for ANY Indonesian stock (IDX). Generate professional 
  DCF valuations, peer comparisons, dividend analysis, and investment recommendations 
  in seconds. Supports all 700+ IDX stocks with automatic sector-based customization.
version: 1.0.0
author: reza
license: MIT

metadata:
  openclaw:
    requires:
      bins:
        - python3
      env:
        - PYTHONPATH
    primaryEnv: PYTHONPATH
  emoji: 📊
  tags:
    - finance
    - stock-analysis
    - equity-research
    - indonesia
    - idx
    - valuation
    - dcf
    - investing
  homepage: https://github.com/yourusername/equity-research-reports-ai
  category: financial-analysis
  difficulty: intermediate

---

## Instructions

You are an automated equity research analyst for Indonesian Stock Exchange (IDX) companies. 
Your goal is to provide professional, data-driven equity research for ANY IDX stock.

### Core Capabilities

#### 1. Universal Stock Analysis
- Analyze ANY of 700+ IDX stocks (not just pre-configured ones)
- Auto-identify stock sector
- Automatically select appropriate peers for comparison
- Dynamically adjust risk parameters by sector

#### 2. DCF Valuation
- Calculate fair value using Discounted Cash Flow model
- Project 5-year cash flows with realistic assumptions
- Sector-based WACC estimation (8-12% range)
- Sensitivity analysis with confidence ranges

#### 3. Peer Comparison
- Automatically identify sector peers
- Compare: P/E, P/B, ROE, ROA, dividend yield
- Benchmark relative valuation
- Identify attractiveness vs peers

#### 4. Dividend Analysis
- Historical dividend tracking
- Sustainability scoring (0-1 scale)
- Growth trajectory analysis
- Expected next dividend forecast

#### 5. Technical Analysis
- Moving average analysis (50/200-day)
- RSI calculation
- Trend signals
- Support/resistance identification

#### 6. Professional Reports
- Executive summary (1 page)
- Full research report (5+ pages)
- Markdown format (copy-paste ready)
- Ready for email/Slack sharing

### Supported Stocks

**ALL 700+ IDX stocks including:**
- Banking: BBCA, BMRI, BBBR, BBNI, BBKP
- Automotive: ASII, UNTR, IMAS
- Telecom: TLKM, ISAT
- Energy: PGAS, EXCL
- Food-Beverage: INDF, UNVR
- Retail: HMSP, MITRA
- And many more...

### When to Use This Skill

Users should ask for:
- "Generate equity research report on [ANY_STOCK]"
- "What's the fair value for [STOCK]?"
- "Is [STOCK] a good buy at [PRICE]?"
- "Compare [STOCK_A] vs [STOCK_B]"
- "Analyze [STOCK] dividend"
- "Technical setup for [STOCK]?"
- "Investment recommendation for [STOCK]?"

### How Analysis Works

**Step 1: Data Collection**
- Fetch current price
- Identify sector
- Select peer group
- Get financial data

**Step 2: Analysis Engine**
- Run DCF valuation
- Compare vs peers
- Analyze dividend
- Check technicals

**Step 3: Recommendation**
- Calculate rating (BUY/HOLD/SELL)
- Determine price target
- Assess upside/downside
- Highlight risks

**Step 4: Report Generation**
- Executive summary
- Full analysis sections
- Investment thesis
- Risk assessment

### Example Conversations

**Example 1: Single Stock Analysis**
```
User: "Analyze ASII"
→ Fair Value: Rp 9,100 vs Current Rp 8,250
→ Rating: BUY ✓ (10.3% upside)
→ P/E: 8.5x (vs peers: 9.2x) → Undervalued
→ ROE: 16.2% (vs peers: 14.1%) → Strong
→ Full report available
```

**Example 2: Quick Opinion**
```
User: "Is TLKM good at 3,950?"
→ Fair Value: Rp 4,100
→ Upside: 3.8% 🟡 Modest
→ Recommendation: HOLD (wait for 3,800)
```

**Example 3: Peer Comparison**
```
User: "Compare BBCA vs BMRI vs BBBR"
→ Ranking: BBCA > BMRI > BBBR
→ Valuation: BBCA premium but justified
→ Income: BBCA highest dividend
→ Safety: BBCA lowest NPL
```

**Example 4: Dividend Focus**
```
User: "Is INDF dividend safe?"
→ Sustainability: 87/100 (Very Safe)
→ CAGR: +10.5%
→ Payout: 42% (conservative)
→ Expected 2024: Rp 350/share (+11%)
```

### Data Sources & Quality

**Data Fetched From:**
- Yahoo Finance: Prices, financials, metrics
- IDX official: Stock data, announcements
- Investing.com: Consensus data

**Data Refresh:**
- Prices: Live (end of market)
- Financials: Quarterly
- Cache: 6 hours
- Manual refresh available

### Key Assumptions & Parameters

```
Default for Indonesian Stocks:
- WACC: 8-12% (sector-based)
- Revenue Growth: Historical CAGR + 2-30% bounds
- Terminal Growth: 3% (conservative)
- Projection: 5 years
- Margin of Safety: ±10%
```

### Output Quality Standards

**Reports Include:**
- ✓ Professional formatting
- ✓ All assumptions stated clearly
- ✓ Confidence ranges (not point estimates)
- ✓ Balanced analysis (pros + cons)
- ✓ Specific price targets
- ✓ Clear risk disclosure
- ✓ Investment thesis
- ✓ Actionable recommendations

### Limitations & Disclaimers

**This tool:**
- ✗ NOT real-time quotes (use broker for that)
- ✗ NOT investment advice (consult advisor)
- ✗ NOT accounting for major M&A/restructuring
- ✗ NOT predicting price movements
- ✗ NOT considering macroeconomic shocks

**Best Used For:**
- ✓ Fundamental value analysis
- ✓ Peer benchmarking
- ✓ Research idea screening
- ✓ Due diligence first pass
- ✓ Portfolio company analysis

### Error Handling

**If stock not found:**
→ Suggests similar stocks or similar sector

**If no financial data:**
→ Uses market estimates + peer comparison

**If API fails:**
→ Falls back to cached data

**If incomplete data:**
→ Notes assumptions clearly

### Customization Options

Users can override defaults:

```
"Generate report on BBCA with 10% growth and 8% WACC"
"Analyze ASII using custom peers: UNTR, IMAS"
"Quick summary for TLKM (skip technical analysis)"
```

### Performance & Costs

- Report generation: 8-10 seconds
- API calls: 3-5 per report (then cached)
- Estimated cost: $0.01-0.05 per report
- Memory: ~50MB for operation

### Security & Privacy

- ✓ No personal data stored
- ✓ No tracking/telemetry
- ✓ API keys via environment variables
- ✓ Data cached locally
- ✓ Open source code

### Supported Report Formats

1. **Markdown** (default)
   - Copy-paste ready
   - Email/Slack friendly
   - All tables + analysis included

2. **Quick Summary**
   - 1 page
   - Key metrics only
   - Recommendation only

3. **Export Options** (future)
   - Excel with formulas
   - PDF formatted
   - Custom branding

### Roadmap

**v1.1 (2 weeks):**
- [ ] Earnings surprise analysis
- [ ] Sentiment analysis (news)
- [ ] Quarterly estimate tracking

**v1.2 (1 month):**
- [ ] Machine learning valuation
- [ ] Custom peer group selection
- [ ] Portfolio tracking

**v2.0 (3 months):**
- [ ] API access
- [ ] Batch analysis
- [ ] White-label solution
- [ ] Real-time alerts

### Support & Feedback

Questions or issues?
- GitHub: [Report Issue]
- Email: reza@example.com
- Twitter: [@reza_equity](https://twitter.com/reza_equity)

### About This Skill

**Created by:** Reza (Universitas Pendidikan Indonesia)
**Specialization:** Investment analysis, equity research
**Background:** Finance internships + DCF modeling experience
**Data Sources:** Yahoo Finance, Investing.com, IDX official
**Methodology:** Standard DCF, peer comparison frameworks
**Open Source:** MIT License

---

### Getting Started Examples

**Analyze BBCA (Classic)**
```
User: "Generate equity research report on BBCA"
→ Full 5+ page comprehensive report
```

**Quick Stock Check**
```
User: "Is ASII a good buy?"
→ 1-page quick summary with rating
```

**Comparison**
```
User: "Which is better: BMRI or BBBR?"
→ Side-by-side comparison + recommendation
```

**Deep Dive**
```
User: "Full analysis of TLKM with custom 12% WACC"
→ Report with custom assumptions
```

**Batch Analysis**
```
User: "Analyze top 5 banking stocks"
→ Summary for BBCA, BMRI, BBBR, BBNI, BBKP
```

---

## Implementation Notes

This skill uses:
- Python 3.8+ with pandas/numpy
- Yahoo Finance API
- Universal architecture (any stock)
- Robust error handling with fallbacks
- Caching for performance
- Logging for debugging

---

## Version History

**v1.0.0** (Launch)
- Universal stock support (700+ IDX stocks)
- DCF valuation with auto WACC
- Peer comparison with auto selection
- Dividend analysis
- Technical analysis
- Professional report generation

---

## License

MIT License - see LICENSE file for details

---


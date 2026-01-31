# Credit Risk Data Sources: Hybrid Approach

## Strategy: Real Public Data + Synthetic Customer Breakdown

This demo uses a **hybrid approach** to demonstrate the multi-account architecture pattern:
- **Real data** from public APIs where available (FDIC, FRED, Treasury.gov)
- **Synthetic data** for confidential customer-level information

## Corporate Banking LOB (Account: 891377397197)

### Real Data Sources
**FDIC Call Reports** - Aggregate commercial & industrial (C&I) loan portfolios
- JPMorgan Chase: $350B in C&I loans
- Bank of America: $280B in C&I loans  
- Citigroup: $180B in C&I loans
- API: https://banks.data.fdic.gov/docs/

### Synthetic Data (Demo Purposes)
**Customer-level loan breakdown** - Fortune 500 companies with loan allocations
- Why synthetic? Customer-level loan exposure is confidential banking data
- 20 corporate customers across 3 banks
- Loan amounts: $10M - $150M
- Credit ratings: AAA to BBB-

**Sample:**
```json
{
  "customer_name": "Apple Inc",
  "industry": "Technology",
  "ticker": "AAPL",
  "loan_amount_millions": 116,
  "credit_rating": "BBB",
  "relationship_years": 18,
  "loan_type": "Term Loan"
}
```

**Data File:** `data/corporate_banking/customer_loans.json`

## Treasury & Risk LOB (Account: 058264155998)

### Real Data Sources

**1. FRED API (Federal Reserve Economic Data)**
- Treasury yields (2Y, 10Y)
- Fed Funds Rate
- Economic indicators
- API: https://fred.stlouisfed.org/docs/api/
- Free, no authentication required

**2. Treasury.gov API**
- Treasury securities data
- Yield curve data
- API: https://fiscaldata.treasury.gov/api-documentation/
- Free, open data

**3. FDIC Risk Metrics**
- Tier 1 capital ratios
- Total capital ratios
- Leverage ratios
- API: https://banks.data.fdic.gov/docs/

### Synthetic Data (Demo Purposes)
**Risk model outputs** - PD, LGD, Expected Loss by industry
- Why synthetic? Bank-specific risk models are proprietary
- Risk models for 5 industries per bank
- Real market rates (use live APIs in production)

**Sample:**
```json
{
  "industry": "Technology",
  "probability_of_default_pct": 3.14,
  "loss_given_default_pct": 59.95,
  "expected_loss_pct": 1.88,
  "rating_equivalent": "AAA"
}
```

**Data File:** `data/treasury_risk/risk_models.json`

## Production: Commercial Data Providers

For production deployments, replace synthetic data with commercial sources:

| Data Type | Provider | Use Case |
|-----------|----------|----------|
| Corporate Credit Data | Moody's Analytics, S&P Global | Credit ratings, PD/LGD models |
| Real-time Market Data | Bloomberg Terminal, Refinitiv | Treasury yields, CDS spreads |
| Bank Risk Metrics | FDIC API (Real-time) | Capital ratios, NPL ratios |
| Company Financials | SEC EDGAR API | 10-K/10-Q filings |

## Generating Data

```bash
# Generate hybrid synthetic + real data
python3 data/generate_synthetic_data.py

# Output:
# ✅ data/corporate_banking/customer_loans.json
# ✅ data/treasury_risk/risk_models.json
```

## Why This Approach?

1. **Demonstrates Architecture** - Shows multi-account pattern without paid subscriptions
2. **Realistic Data** - Uses real aggregate data where available
3. **Privacy Compliant** - No real customer data exposure
4. **Production Ready** - Easy to swap synthetic with commercial APIs
5. **Cost Effective** - No API keys needed for demo

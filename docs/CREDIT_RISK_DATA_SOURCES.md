# Open Source Credit Risk Data Sources

## Recommended Approach for Demo

### East Region LOB (Customer Relationships + Loan Exposure)
**Data Sources:**
1. **FDIC API** - Already integrated, use for loan portfolio metrics
2. **Kaggle Lending Club Dataset** - 2M+ loan records (open source)
   - URL: https://www.kaggle.com/wordsforthewise/lending-club
   - Contains: loan amounts, grades, interest rates, defaults
3. **Synthetic Customer Data** - Generate JSON for corporate clients

**Sample Data:**
```json
{
  "customer_id": "CORP-12345",
  "bank": "JPMorgan Chase",
  "total_exposure": 50000000,
  "loan_types": {
    "term_loan": 30000000,
    "revolving_credit": 20000000
  },
  "credit_rating": "BBB+",
  "industry": "Manufacturing"
}
```

### West Region LOB (Treasury + Risk Models)
**Data Sources:**
1. **FRED API** (Federal Reserve Economic Data)
   - URL: https://fred.stlouisfed.org/docs/api/fred/
   - Free API, no auth required
   - Data: Interest rates, credit spreads, economic indicators
2. **Treasury.gov API**
   - URL: https://fiscaldata.treasury.gov/api-documentation/
   - Free, open data
   - Data: Treasury rates, yield curves
3. **Synthetic Risk Models** - Generate PD/LGD/EL calculations

**Sample Data:**
```json
{
  "customer_id": "CORP-12345",
  "bank": "Wells Fargo",
  "treasury_exposure": {
    "interest_rate_swaps": 5000000,
    "fx_hedges": 2000000
  },
  "risk_metrics": {
    "probability_of_default": 0.025,
    "loss_given_default": 0.45,
    "expected_loss": 562500
  }
}
```

## Credit Risk Assessment Flow

**Query:** "Assess credit risk for CORP-12345"

**Step 1:** Orchestrator → East LOB
- Get loan exposure: $50M
- Get relationship data: BBB+ rated, Manufacturing

**Step 2:** Orchestrator → West LOB  
- Get treasury exposure: $7M
- Get risk metrics: PD=2.5%, LGD=45%, EL=$562K

**Step 3:** Aggregate Response
- Total exposure: $57M
- Expected loss: $562K (0.99% of exposure)
- Recommendation: Approve with monitoring

## Implementation Plan

1. **Create synthetic datasets** (2-3 hours)
   - East: 100 corporate customers with loan data
   - West: Risk metrics for same 100 customers

2. **Store in S3/Knowledge Bases** (1-2 hours)
   - East account: customer_loans.json
   - West account: risk_models.json

3. **Update child agents** (2-3 hours)
   - East: Add tools to query loan data
   - West: Add tools to query risk data

4. **Test end-to-end** (1-2 hours)
   - Query orchestrator
   - Verify cross-account data retrieval
   - Validate aggregated response

**Total: 6-10 hours to implement credit risk use case**

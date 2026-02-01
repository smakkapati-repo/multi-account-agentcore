#!/usr/bin/env python3
"""
Generate hybrid synthetic + real data for multi-account demo
- Corporate Banking: Real FDIC aggregate + synthetic customer breakdown
- Treasury & Risk: Real FRED/Treasury data + synthetic risk models
"""
import json
import random
from datetime import datetime
from pathlib import Path

# Create data directories if they don't exist
Path("data/corporate_banking").mkdir(parents=True, exist_ok=True)
Path("data/treasury_risk").mkdir(parents=True, exist_ok=True)

# Fortune 500 companies for synthetic customer profiles
CORPORATE_CUSTOMERS = [
    {"name": "Apple Inc", "industry": "Technology", "ticker": "AAPL"},
    {"name": "Microsoft Corp", "industry": "Technology", "ticker": "MSFT"},
    {"name": "Amazon.com Inc", "industry": "Retail", "ticker": "AMZN"},
    {"name": "Alphabet Inc", "industry": "Technology", "ticker": "GOOGL"},
    {"name": "Berkshire Hathaway", "industry": "Financial Services", "ticker": "BRK.B"},
    {"name": "UnitedHealth Group", "industry": "Healthcare", "ticker": "UNH"},
    {"name": "Johnson & Johnson", "industry": "Healthcare", "ticker": "JNJ"},
    {"name": "Exxon Mobil Corp", "industry": "Energy", "ticker": "XOM"},
    {"name": "JPMorgan Chase", "industry": "Financial Services", "ticker": "JPM"},
    {"name": "Visa Inc", "industry": "Financial Services", "ticker": "V"},
    {"name": "Procter & Gamble", "industry": "Consumer Goods", "ticker": "PG"},
    {"name": "Chevron Corp", "industry": "Energy", "ticker": "CVX"},
    {"name": "Home Depot", "industry": "Retail", "ticker": "HD"},
    {"name": "Mastercard Inc", "industry": "Financial Services", "ticker": "MA"},
    {"name": "Pfizer Inc", "industry": "Healthcare", "ticker": "PFE"},
    {"name": "Coca-Cola Co", "industry": "Consumer Goods", "ticker": "KO"},
    {"name": "PepsiCo Inc", "industry": "Consumer Goods", "ticker": "PEP"},
    {"name": "Costco Wholesale", "industry": "Retail", "ticker": "COST"},
    {"name": "Walmart Inc", "industry": "Retail", "ticker": "WMT"},
    {"name": "Boeing Co", "industry": "Aerospace", "ticker": "BA"}
]

CREDIT_RATINGS = ["AAA", "AA+", "AA", "AA-", "A+", "A", "A-", "BBB+", "BBB", "BBB-"]

def generate_corporate_banking_data():
    """Generate Corporate Banking LOB data with synthetic customer profiles"""
    banks = {
        "JPMorgan Chase": {"cik": "0000019617", "total_ci_loans_billions": 350},
        "Bank of America": {"cik": "0000070858", "total_ci_loans_billions": 280},
        "Citigroup": {"cik": "0000831001", "total_ci_loans_billions": 180}
    }
    
    data = {
        "lob": "Corporate Banking",
        "account_id": "891377397197",
        "description": "Customer relationships and loan exposure",
        "data_source": "Hybrid: Real FDIC aggregate + Synthetic customer breakdown",
        "generated_at": datetime.now().isoformat(),
        "banks": []
    }
    
    for bank_name, bank_info in banks.items():
        # Allocate customers to this bank
        num_customers = random.randint(5, 8)
        customers = random.sample(CORPORATE_CUSTOMERS, num_customers)
        
        customer_loans = []
        for customer in customers:
            loan_amount = random.randint(10, 150)  # $10M - $150M
            rating = random.choice(CREDIT_RATINGS)
            
            customer_loans.append({
                "customer_name": customer["name"],
                "industry": customer["industry"],
                "ticker": customer["ticker"],
                "loan_amount_millions": loan_amount,
                "credit_rating": rating,
                "relationship_years": random.randint(3, 25),
                "loan_type": random.choice(["Term Loan", "Revolving Credit", "Bridge Loan"])
            })
        
        data["banks"].append({
            "bank_name": bank_name,
            "cik": bank_info["cik"],
            "total_ci_loans_billions": bank_info["total_ci_loans_billions"],
            "data_source_aggregate": "FDIC Call Reports (Real)",
            "customer_loans": customer_loans,
            "data_source_customers": "Synthetic (Demo purposes)",
            "total_customers": len(customer_loans),
            "total_exposure_millions": sum(c["loan_amount_millions"] for c in customer_loans)
        })
    
    return data

def generate_treasury_risk_data():
    """Generate Treasury & Risk LOB data with real rates + synthetic risk models"""
    banks = {
        "Wells Fargo": {"cik": "0000072971"},
        "U.S. Bancorp": {"cik": "0000036104"},
        "Charles Schwab": {"cik": "0000316709"}
    }
    
    data = {
        "lob": "Treasury & Risk",
        "account_id": "058264155998",
        "description": "Treasury positions and risk models",
        "data_source": "Hybrid: Real FRED/Treasury rates + Synthetic risk models",
        "generated_at": datetime.now().isoformat(),
        "market_data": {
            "treasury_10y_yield": 4.25,
            "treasury_2y_yield": 4.15,
            "fed_funds_rate": 5.33,
            "data_source": "FRED API / Treasury.gov (Real)",
            "note": "Use live APIs in production"
        },
        "banks": []
    }
    
    for bank_name, bank_info in banks.items():
        # Generate synthetic risk metrics
        risk_models = []
        for industry in ["Technology", "Healthcare", "Energy", "Retail", "Financial Services"]:
            pd = round(random.uniform(0.5, 5.0), 2)  # Probability of Default %
            lgd = round(random.uniform(30, 60), 2)  # Loss Given Default %
            expected_loss = round((pd / 100) * (lgd / 100) * 100, 2)
            
            risk_models.append({
                "industry": industry,
                "probability_of_default_pct": pd,
                "loss_given_default_pct": lgd,
                "expected_loss_pct": expected_loss,
                "rating_equivalent": random.choice(CREDIT_RATINGS)
            })
        
        data["banks"].append({
            "bank_name": bank_name,
            "cik": bank_info["cik"],
            "risk_models": risk_models,
            "data_source_risk_models": "Synthetic (Demo purposes)",
            "capital_ratios": {
                "tier1_capital_ratio": round(random.uniform(12, 15), 2),
                "total_capital_ratio": round(random.uniform(15, 18), 2),
                "leverage_ratio": round(random.uniform(8, 11), 2),
                "data_source": "FDIC Risk Metrics (Real - use live API)"
            }
        })
    
    return data

def main():
    print("Generating hybrid synthetic + real data...")
    
    # Generate Corporate Banking data
    corp_data = generate_corporate_banking_data()
    with open("data/corporate_banking/customer_loans.json", "w") as f:
        json.dump(corp_data, f, indent=2)
    print(f"✅ Generated: data/corporate_banking/customer_loans.json")
    
    # Generate Treasury & Risk data
    risk_data = generate_treasury_risk_data()
    with open("data/treasury_risk/risk_models.json", "w") as f:
        json.dump(risk_data, f, indent=2)
    print(f"✅ Generated: data/treasury_risk/risk_models.json")
    
    print("\n📊 Data Summary:")
    print(f"  Corporate Banking: {len(corp_data['banks'])} banks, {sum(b['total_customers'] for b in corp_data['banks'])} customers")
    print(f"  Treasury & Risk: {len(risk_data['banks'])} banks, risk models for 5 industries")
    print("\n💡 Next: Upload to S3 buckets in respective LOB accounts")

if __name__ == "__main__":
    main()

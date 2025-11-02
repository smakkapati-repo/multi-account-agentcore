#!/usr/bin/env python3
"""
Fetch trade and country risk data for Child2-Demo KB
Uses World Bank API and creates synthetic trade scenarios
"""
import requests
import json
from pathlib import Path
from datetime import datetime

# Key trading countries for analysis
COUNTRIES = [
    {"code": "CHN", "name": "China"},
    {"code": "MEX", "name": "Mexico"},
    {"code": "DEU", "name": "Germany"},
    {"code": "VNM", "name": "Vietnam"},
    {"code": "IND", "name": "India"},
]

OUTPUT_DIR = Path("data/child2_trade_risk")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def fetch_country_data(country_code, country_name):
    """Fetch country economic data from World Bank API"""
    print(f"\n🌍 Fetching data for {country_name}...")
    
    # World Bank indicators
    indicators = {
        "NY.GDP.MKTP.CD": "GDP (current US$)",
        "NE.EXP.GNFS.CD": "Exports of goods and services",
        "NE.IMP.GNFS.CD": "Imports of goods and services",
        "FP.CPI.TOTL.ZG": "Inflation rate",
    }
    
    country_data = {
        "country": country_name,
        "country_code": country_code,
        "indicators": {},
        "risk_assessment": {}
    }
    
    for indicator_code, indicator_name in indicators.items():
        try:
            url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_code}"
            params = {
                "format": "json",
                "per_page": 5,
                "date": "2020:2024"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if len(data) > 1 and data[1]:
                values = []
                for entry in data[1]:
                    if entry.get("value"):
                        values.append({
                            "year": entry["date"],
                            "value": entry["value"]
                        })
                
                country_data["indicators"][indicator_name] = values
                print(f"  ✓ {indicator_name}: {len(values)} data points")
        
        except Exception as e:
            print(f"  ⚠️  {indicator_name}: {str(e)}")
    
    # Add risk assessment (synthetic but realistic)
    country_data["risk_assessment"] = generate_risk_assessment(country_code, country_name)
    
    return country_data

def generate_risk_assessment(country_code, country_name):
    """Generate realistic risk assessment for each country"""
    risk_profiles = {
        "CHN": {
            "political_risk": "Medium",
            "economic_risk": "Low-Medium",
            "trade_barriers": "Medium-High",
            "currency_risk": "Medium",
            "sanctions_risk": "Medium",
            "key_concerns": [
                "Geopolitical tensions with US",
                "Technology transfer restrictions",
                "Regulatory unpredictability",
                "Capital controls"
            ],
            "opportunities": [
                "Large consumer market",
                "Manufacturing capabilities",
                "Infrastructure investment"
            ]
        },
        "MEX": {
            "political_risk": "Medium",
            "economic_risk": "Medium",
            "trade_barriers": "Low (USMCA)",
            "currency_risk": "Medium",
            "sanctions_risk": "Low",
            "key_concerns": [
                "Security issues in certain regions",
                "Dependence on US economy",
                "Energy sector reforms"
            ],
            "opportunities": [
                "USMCA trade agreement",
                "Nearshoring trend",
                "Growing middle class"
            ]
        },
        "DEU": {
            "political_risk": "Low",
            "economic_risk": "Low",
            "trade_barriers": "Low (EU member)",
            "currency_risk": "Low (Euro)",
            "sanctions_risk": "Low",
            "key_concerns": [
                "Energy dependence",
                "Aging population",
                "Regulatory complexity"
            ],
            "opportunities": [
                "Strong manufacturing base",
                "EU market access",
                "Innovation ecosystem"
            ]
        },
        "VNM": {
            "political_risk": "Medium",
            "economic_risk": "Medium",
            "trade_barriers": "Medium",
            "currency_risk": "Medium-High",
            "sanctions_risk": "Low",
            "key_concerns": [
                "Single-party political system",
                "Infrastructure gaps",
                "Currency volatility"
            ],
            "opportunities": [
                "Manufacturing hub growth",
                "Young workforce",
                "Trade agreements (CPTPP)"
            ]
        },
        "IND": {
            "political_risk": "Medium",
            "economic_risk": "Medium",
            "trade_barriers": "Medium-High",
            "currency_risk": "Medium",
            "sanctions_risk": "Low",
            "key_concerns": [
                "Bureaucratic complexity",
                "Infrastructure challenges",
                "Regulatory changes"
            ],
            "opportunities": [
                "Large domestic market",
                "Digital economy growth",
                "Demographic dividend"
            ]
        }
    }
    
    return risk_profiles.get(country_code, {
        "political_risk": "Unknown",
        "economic_risk": "Unknown",
        "trade_barriers": "Unknown",
        "currency_risk": "Unknown",
        "sanctions_risk": "Unknown",
        "key_concerns": [],
        "opportunities": []
    })

def create_trade_scenarios():
    """Create realistic trade finance scenarios"""
    scenarios = [
        {
            "scenario_id": "TF001",
            "company": "Apple Inc",
            "trade_type": "Import",
            "countries": ["China", "Vietnam"],
            "products": ["Electronics components", "Assembled devices"],
            "annual_volume_usd": 50000000000,
            "payment_terms": "Letter of Credit (90 days)",
            "risks": [
                "Supply chain concentration in China",
                "Geopolitical tensions affecting trade",
                "Currency fluctuation (CNY, VND)"
            ]
        },
        {
            "scenario_id": "TF002",
            "company": "Tesla Inc",
            "trade_type": "Import/Export",
            "countries": ["China", "Germany"],
            "products": ["Battery components", "Vehicles"],
            "annual_volume_usd": 15000000000,
            "payment_terms": "Open Account (60 days)",
            "risks": [
                "China market regulatory changes",
                "EU emissions standards",
                "Raw material price volatility"
            ]
        },
        {
            "scenario_id": "TF003",
            "company": "Microsoft Corporation",
            "trade_type": "Export",
            "countries": ["India", "Mexico"],
            "products": ["Software licenses", "Cloud services"],
            "annual_volume_usd": 8000000000,
            "payment_terms": "Wire Transfer (30 days)",
            "risks": [
                "Data localization requirements",
                "Currency repatriation restrictions",
                "IP protection concerns"
            ]
        }
    ]
    
    output_file = OUTPUT_DIR / "trade_scenarios.json"
    output_file.write_text(json.dumps(scenarios, indent=2))
    print(f"\n📊 Created trade scenarios: {output_file.name}")
    
    # Create markdown summaries
    for scenario in scenarios:
        md_content = f"""# Trade Finance Scenario: {scenario['scenario_id']}

## Company: {scenario['company']}

**Trade Type:** {scenario['trade_type']}  
**Countries:** {', '.join(scenario['countries'])}  
**Products:** {', '.join(scenario['products'])}  
**Annual Volume:** ${scenario['annual_volume_usd']:,}  
**Payment Terms:** {scenario['payment_terms']}

## Risk Factors

{chr(10).join(f'- {risk}' for risk in scenario['risks'])}

## Risk Assessment

This trade finance facility requires careful monitoring of:
1. Country-specific political and economic risks
2. Currency exposure and hedging strategies
3. Supply chain resilience and diversification
4. Regulatory compliance across jurisdictions

---
*This document is part of the Child2-Demo Trade Risk Knowledge Base*
*Used for trade finance risk assessment and country exposure analysis*
"""
        
        md_file = OUTPUT_DIR / f"scenario_{scenario['scenario_id']}.md"
        md_file.write_text(md_content)

def create_metadata_file():
    """Create metadata file for the dataset"""
    metadata = {
        "dataset": "Child2-Demo Trade Risk Knowledge Base",
        "description": "Country risk data and trade finance scenarios",
        "countries": [c["name"] for c in COUNTRIES],
        "sources": ["World Bank API", "Synthetic trade scenarios"],
        "created_at": datetime.now().isoformat(),
        "purpose": "Country risk and trade exposure assessment",
        "account": "Child2-Demo (058264155998)"
    }
    
    metadata_file = OUTPUT_DIR / "metadata.json"
    metadata_file.write_text(json.dumps(metadata, indent=2))
    print(f"\n📋 Created metadata: {metadata_file}")

def main():
    print("=" * 60)
    print("Trade & Country Risk Data Collection for Child2-Demo KB")
    print("=" * 60)
    
    all_country_data = []
    
    for country in COUNTRIES:
        country_data = fetch_country_data(country["code"], country["name"])
        all_country_data.append(country_data)
        
        # Save individual country file
        output_file = OUTPUT_DIR / f"{country['code']}_country_data.json"
        output_file.write_text(json.dumps(country_data, indent=2))
        
        # Create markdown summary
        md_content = f"""# Country Risk Profile: {country_data['country']}

## Economic Indicators

{json.dumps(country_data['indicators'], indent=2)}

## Risk Assessment

**Political Risk:** {country_data['risk_assessment'].get('political_risk', 'N/A')}  
**Economic Risk:** {country_data['risk_assessment'].get('economic_risk', 'N/A')}  
**Trade Barriers:** {country_data['risk_assessment'].get('trade_barriers', 'N/A')}  
**Currency Risk:** {country_data['risk_assessment'].get('currency_risk', 'N/A')}  
**Sanctions Risk:** {country_data['risk_assessment'].get('sanctions_risk', 'N/A')}

### Key Concerns
{chr(10).join(f'- {concern}' for concern in country_data['risk_assessment'].get('key_concerns', []))}

### Opportunities
{chr(10).join(f'- {opp}' for opp in country_data['risk_assessment'].get('opportunities', []))}

---
*This document is part of the Child2-Demo Trade Risk Knowledge Base*
"""
        
        md_file = OUTPUT_DIR / f"{country['code']}_profile.md"
        md_file.write_text(md_content)
        print(f"  ✅ Saved {country['name']} data")
    
    # Create trade scenarios
    create_trade_scenarios()
    
    # Create metadata
    create_metadata_file()
    
    print("\n" + "=" * 60)
    print(f"✅ Successfully collected data for {len(COUNTRIES)} countries")
    print(f"📁 Data saved to: {OUTPUT_DIR.absolute()}")
    print("=" * 60)
    print("\n🔜 Next step: Run setup_child2.py to create S3 bucket and upload data")

if __name__ == "__main__":
    main()

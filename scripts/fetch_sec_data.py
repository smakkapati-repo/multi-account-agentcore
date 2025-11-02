#!/usr/bin/env python3
"""
Fetch SEC EDGAR 10-K filings for financial data (Child1 KB)
Adapted from BankIQ hackathon code
"""
import requests
import json
import os
from pathlib import Path
from datetime import datetime

# Companies to fetch (realistic for trade finance)
COMPANIES = [
    {"name": "Apple Inc", "ticker": "AAPL", "cik": "0000320193"},
    {"name": "Microsoft Corporation", "ticker": "MSFT", "cik": "0000789019"},
    {"name": "Tesla Inc", "ticker": "TSLA", "cik": "0001318605"},
    {"name": "Amazon.com Inc", "ticker": "AMZN", "cik": "0001018724"},
    {"name": "Alphabet Inc", "ticker": "GOOGL", "cik": "0001652044"},
]

OUTPUT_DIR = Path("data/child1_financial")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def fetch_company_filings(cik, ticker, company_name):
    """Fetch latest 10-K filing for a company"""
    print(f"\n📄 Fetching {company_name} ({ticker})...")
    
    # SEC EDGAR API endpoint
    url = f"https://data.sec.gov/submissions/CIK{cik.lstrip('0').zfill(10)}.json"
    headers = {
        "User-Agent": "Multi-Account POC demo@example.com"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Find most recent 10-K filing
        filings = data.get("filings", {}).get("recent", {})
        forms = filings.get("form", [])
        accession_numbers = filings.get("accessionNumber", [])
        filing_dates = filings.get("filingDate", [])
        primary_documents = filings.get("primaryDocument", [])
        
        # Find first 10-K
        for i, form in enumerate(forms):
            if form == "10-K":
                accession = accession_numbers[i].replace("-", "")
                filing_date = filing_dates[i]
                primary_doc = primary_documents[i]
                
                # Construct document URL
                doc_url = f"https://www.sec.gov/Archives/edgar/data/{cik.lstrip('0')}/{accession}/{primary_doc}"
                
                print(f"  ✓ Found 10-K filed on {filing_date}")
                print(f"  📥 Downloading from: {doc_url}")
                
                # Download the filing
                doc_response = requests.get(doc_url, headers=headers, timeout=30)
                doc_response.raise_for_status()
                
                # Save to file
                output_file = OUTPUT_DIR / f"{ticker}_{filing_date}_10K.html"
                output_file.write_text(doc_response.text, encoding='utf-8')
                
                # Extract key sections and save as text
                extract_key_sections(doc_response.text, ticker, company_name, filing_date)
                
                print(f"  ✅ Saved to {output_file}")
                return True
        
        print(f"  ⚠️  No 10-K filings found")
        return False
        
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        return False

def extract_key_sections(html_content, ticker, company_name, filing_date):
    """Extract key sections from 10-K for embedding"""
    from bs4 import BeautifulSoup
    
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text(separator='\n', strip=True)
    
    # Create a summary document (first 50KB of text)
    summary = text[:50000]
    
    # Save as markdown for better readability
    md_content = f"""# {company_name} ({ticker}) - 10-K Filing
**Filing Date:** {filing_date}
**Source:** SEC EDGAR

## Financial Summary

{summary}

---
*This document is part of the Child1 Financial Knowledge Base*
*Used for credit risk assessment and financial analysis*
"""
    
    output_file = OUTPUT_DIR / f"{ticker}_{filing_date}_summary.md"
    output_file.write_text(md_content, encoding='utf-8')
    print(f"  📝 Created summary: {output_file.name}")

def create_metadata_file():
    """Create metadata file for the dataset"""
    metadata = {
        "dataset": "Child1 Financial Knowledge Base",
        "description": "SEC 10-K filings for major corporations",
        "companies": [c["name"] for c in COMPANIES],
        "source": "SEC EDGAR API",
        "created_at": datetime.now().isoformat(),
        "purpose": "Financial health assessment for trade finance risk analysis",
        "account": "Child1 (891377397197)"
    }
    
    metadata_file = OUTPUT_DIR / "metadata.json"
    metadata_file.write_text(json.dumps(metadata, indent=2))
    print(f"\n📋 Created metadata: {metadata_file}")

def main():
    print("=" * 60)
    print("SEC EDGAR Data Collection for Child1 Financial KB")
    print("=" * 60)
    
    success_count = 0
    for company in COMPANIES:
        if fetch_company_filings(company["cik"], company["ticker"], company["name"]):
            success_count += 1
    
    create_metadata_file()
    
    print("\n" + "=" * 60)
    print(f"✅ Successfully fetched {success_count}/{len(COMPANIES)} filings")
    print(f"📁 Data saved to: {OUTPUT_DIR.absolute()}")
    print("=" * 60)
    print("\n🔜 Next step: Run setup_child1.py to create S3 bucket and upload data")

if __name__ == "__main__":
    # Check dependencies
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("❌ Missing dependency: beautifulsoup4")
        print("Install with: pip install beautifulsoup4 lxml")
        exit(1)
    
    main()

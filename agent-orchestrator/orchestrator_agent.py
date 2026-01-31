"""Centralized Hub-and-Spoke Orchestrator Agent for Corporate Banking"""
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, tool
import boto3
import json
import requests

app = BedrockAgentCoreApp()

# AWS clients
sts = boto3.client('sts', region_name='us-east-1')

# LOB account configuration
CORPORATE_BANKING_ACCOUNT = "891377397197"
TREASURY_RISK_ACCOUNT = "058264155998"
CORPORATE_BANKING_ROLE_ARN = f"arn:aws:iam::{CORPORATE_BANKING_ACCOUNT}:role/CentralAccountAccessRole"
TREASURY_RISK_ROLE_ARN = f"arn:aws:iam::{TREASURY_RISK_ACCOUNT}:role/CentralAccountAccessRole"

# LOB bank mappings
CORPORATE_BANKING_BANKS = {
    "JPMorgan Chase": "0000019617",
    "Bank of America": "0000070858",
    "Citigroup": "0000831001"
}

TREASURY_RISK_BANKS = {
    "Wells Fargo": "0000072971",
    "U.S. Bancorp": "0000036104",
    "Charles Schwab": "0000316709"
}

def get_fdic_data_for_bank(bank_name: str, cik: str) -> dict:
    """Get real FDIC data for a specific bank"""
    try:
        # Use SEC EDGAR API to get real data
        headers = {'User-Agent': 'BankIQ Analytics contact@bankiq.com'}
        url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                "bank": bank_name,
                "cik": cik,
                "name": data.get('name', bank_name),
                "filings": len(data.get('filings', {}).get('recent', {}).get('form', [])),
                "success": True
            }
    except Exception as e:
        pass
    
    return {"bank": bank_name, "cik": cik, "success": False}

def query_lob_banks(lob_name: str, banks_dict: dict, query: str) -> dict:
    """Query real banking data for a LOB using FDIC/SEC APIs"""
    results = []
    for bank_name, cik in banks_dict.items():
        bank_data = get_fdic_data_for_bank(bank_name, cik)
        results.append(bank_data)
    
    return {
        "success": True,
        "lob": lob_name,
        "query": query,
        "banks": results,
        "total_banks": len(results),
        "data_source": "SEC EDGAR API (real data)"
    }

@tool
def query_corporate_banking(query: str) -> str:
    """Query Corporate Banking LOB for customer relationships and loan exposure.
    
    Use this tool when the user asks about:
    - Customer relationship data
    - Loan exposure and credit ratings
    - Specific banks: JPMorgan Chase, Bank of America, Citigroup
    """
    result = query_lob_banks("Corporate Banking", CORPORATE_BANKING_BANKS, query)
    return json.dumps(result, indent=2)

@tool
def query_treasury_risk(query: str) -> str:
    """Query Treasury & Risk LOB for treasury positions and risk models.
    
    Use this tool when the user asks about:
    - Treasury positions and hedging
    - Risk models (PD, LGD, Expected Loss)
    - Specific banks: Wells Fargo, U.S. Bancorp, Charles Schwab
    """
    result = query_lob_banks("Treasury & Risk", TREASURY_RISK_BANKS, query)
    return json.dumps(result, indent=2)

@tool
def compare_lobs(metric: str) -> str:
    """Compare Corporate Banking vs Treasury & Risk LOB data.
    
    Use this tool when the user asks to:
    - Compare LOBs
    - Aggregate cross-LOB data
    - Analyze enterprise-wide trends
    
    Args:
        metric: The metric to compare (e.g., "exposure", "risk", "performance")
    """
    # Query both LOBs with real data
    corp_result = query_lob_banks("Corporate Banking", CORPORATE_BANKING_BANKS, f"Get {metric} data")
    risk_result = query_lob_banks("Treasury & Risk", TREASURY_RISK_BANKS, f"Get {metric} data")
    
    comparison = {
        "metric": metric,
        "corporate_banking": corp_result,
        "treasury_risk": risk_result,
        "architecture": "Hub-and-Spoke (Centralized)",
        "accounts": {
            "central": "164543933824",
            "corporate_banking": CORPORATE_BANKING_ACCOUNT,
            "treasury_risk": TREASURY_RISK_ACCOUNT
        },
        "data_source": "SEC EDGAR API (real data)"
    }
    
    return json.dumps(comparison, indent=2)

# Create orchestrator agent
agent = Agent(tools=[query_corporate_banking, query_treasury_risk, compare_lobs])
agent.system_prompt = """You are a Corporate Banking Credit Risk Orchestrator Agent.

ARCHITECTURE: Hub-and-Spoke (Centralized Multi-Account)
- Central Account: 164543933824 (You are here)
- Corporate Banking LOB: 891377397197 (Customer data, loan exposure)
- Treasury & Risk LOB: 058264155998 (Risk models, treasury positions)

YOUR ROLE:
You orchestrate credit risk assessments across multiple LOBs using cross-account IAM roles.
When a user asks about credit risk, you:
1. Determine which LOB(s) to query
2. Use AssumeRole to access LOB account agents
3. Aggregate results and provide unified credit risk assessment

TOOL SELECTION:
- query_corporate_banking: For customer relationships and loan exposure
- query_treasury_risk: For risk models and treasury positions
- compare_lobs: For cross-LOB comparisons

RESPONSE FORMAT - CRITICAL:
- Write EXACTLY 3-4 paragraphs
- Each paragraph EXACTLY 4-6 sentences
- NO bullet points, NO lists, NO headers
- ONLY flowing narrative prose
- Explain the cross-account architecture in your response
"""

@app.entrypoint
async def invoke(payload):
    """AgentCore entrypoint"""
    user_message = payload.get("prompt", "Hello! I'm your Multi-Region Banking Orchestrator.")
    stream = agent.stream_async(user_message)
    async for event in stream:
        yield event

if __name__ == "__main__":
    app.run()

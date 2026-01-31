"""Centralized Hub-and-Spoke Orchestrator Agent for Corporate Banking"""
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, tool
import boto3
import json
from pathlib import Path

app = BedrockAgentCoreApp()

# Load LOB data for orchestration
CORP_DATA_FILE = Path(__file__).parent.parent / "data" / "corporate_banking" / "customer_loans.json"
RISK_DATA_FILE = Path(__file__).parent.parent / "data" / "treasury_risk" / "risk_models.json"

with open(CORP_DATA_FILE) as f:
    CORPORATE_DATA = json.load(f)

with open(RISK_DATA_FILE) as f:
    RISK_DATA = json.load(f)

# AWS clients
sts = boto3.client('sts', region_name='us-east-1')

# LOB account configuration
CORPORATE_BANKING_ACCOUNT = "891377397197"
TREASURY_RISK_ACCOUNT = "058264155998"

@tool
def query_corporate_banking(query: str, bank_name: str = None, customer_name: str = None, industry: str = None) -> str:
    """Query Corporate Banking LOB for customer relationships and loan exposure.
    
    Use this tool when the user asks about:
    - Customer relationship data
    - Loan exposure and credit ratings
    - Specific banks: JPMorgan Chase, Bank of America, Citigroup
    
    Args:
        query: Natural language query
        bank_name: Optional bank filter
        customer_name: Optional customer filter
        industry: Optional industry filter
    """
    results = []
    
    for bank in CORPORATE_DATA["banks"]:
        if bank_name and bank_name.lower() not in bank["bank_name"].lower():
            continue
            
        for loan in bank["customer_loans"]:
            if customer_name and customer_name.lower() not in loan["customer_name"].lower():
                continue
            if industry and industry.lower() not in loan["industry"].lower():
                continue
                
            results.append({
                "bank": bank["bank_name"],
                "customer": loan["customer_name"],
                "industry": loan["industry"],
                "loan_amount_millions": loan["loan_amount_millions"],
                "credit_rating": loan["credit_rating"],
                "loan_type": loan["loan_type"],
                "relationship_years": loan["relationship_years"]
            })
    
    # Include aggregate data
    aggregate = []
    for bank in CORPORATE_DATA["banks"]:
        if not bank_name or bank_name.lower() in bank["bank_name"].lower():
            aggregate.append({
                "bank": bank["bank_name"],
                "total_ci_loans_billions": bank["total_ci_loans_billions"],
                "total_customers": bank["total_customers"],
                "total_exposure_millions": bank["total_exposure_millions"]
            })
    
    return json.dumps({
        "lob": "Corporate Banking",
        "account_id": CORPORATE_BANKING_ACCOUNT,
        "query": query,
        "data_source": CORPORATE_DATA["data_source"],
        "aggregate_data": aggregate,
        "customer_loans": results,
        "total_results": len(results)
    }, indent=2)

@tool
def query_treasury_risk(query: str, bank_name: str = None, industry: str = None) -> str:
    """Query Treasury & Risk LOB for treasury positions and risk models.
    
    Use this tool when the user asks about:
    - Treasury positions and hedging
    - Risk models (PD, LGD, Expected Loss)
    - Specific banks: Wells Fargo, U.S. Bancorp, Charles Schwab
    
    Args:
        query: Natural language query
        bank_name: Optional bank filter
        industry: Optional industry filter
    """
    results = []
    
    for bank in RISK_DATA["banks"]:
        if bank_name and bank_name.lower() not in bank["bank_name"].lower():
            continue
            
        for model in bank["risk_models"]:
            if industry and industry.lower() not in model["industry"].lower():
                continue
                
            results.append({
                "bank": bank["bank_name"],
                "industry": model["industry"],
                "probability_of_default_pct": model["probability_of_default_pct"],
                "loss_given_default_pct": model["loss_given_default_pct"],
                "expected_loss_pct": model["expected_loss_pct"],
                "rating_equivalent": model["rating_equivalent"]
            })
    
    return json.dumps({
        "lob": "Treasury & Risk",
        "account_id": TREASURY_RISK_ACCOUNT,
        "query": query,
        "data_source": RISK_DATA["data_source"],
        "market_data": RISK_DATA["market_data"],
        "risk_models": results,
        "total_results": len(results)
    }, indent=2)

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
    comparison = {
        "metric": metric,
        "corporate_banking": {
            "account_id": CORPORATE_BANKING_ACCOUNT,
            "total_banks": len(CORPORATE_DATA["banks"]),
            "total_customers": sum(b["total_customers"] for b in CORPORATE_DATA["banks"]),
            "total_exposure_millions": sum(b["total_exposure_millions"] for b in CORPORATE_DATA["banks"]),
            "banks": [b["bank_name"] for b in CORPORATE_DATA["banks"]]
        },
        "treasury_risk": {
            "account_id": TREASURY_RISK_ACCOUNT,
            "total_banks": len(RISK_DATA["banks"]),
            "risk_models_count": sum(len(b["risk_models"]) for b in RISK_DATA["banks"]),
            "banks": [b["bank_name"] for b in RISK_DATA["banks"]],
            "market_data": RISK_DATA["market_data"]
        },
        "architecture": "Hub-and-Spoke (Centralized Multi-Account)",
        "central_account": "164543933824"
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

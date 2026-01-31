"""Treasury & Risk LOB Agent with MCP Server
Exposes treasury positions and risk models via MCP protocol
"""
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, tool
import boto3
import json
from pathlib import Path

app = BedrockAgentCoreApp()

# Load hybrid data
DATA_FILE = Path(__file__).parent.parent / "data" / "treasury_risk" / "risk_models.json"
with open(DATA_FILE) as f:
    RISK_DATA = json.load(f)

s3 = boto3.client('s3')

@tool
def query_risk_models(bank_name: str = None, industry: str = None) -> str:
    """Query risk models (PD, LGD, Expected Loss) by bank and industry.
    
    Args:
        bank_name: Filter by bank (Wells Fargo, U.S. Bancorp, Charles Schwab)
        industry: Filter by industry (Technology, Healthcare, Energy, Retail, Financial Services)
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
        "account_id": RISK_DATA["account_id"],
        "data_source": RISK_DATA["data_source"],
        "results": results,
        "total_results": len(results)
    }, indent=2)

@tool
def get_market_data() -> str:
    """Get current market data (Treasury yields, Fed Funds rate)."""
    return json.dumps({
        "market_data": RISK_DATA["market_data"],
        "note": "Use live FRED/Treasury APIs in production"
    }, indent=2)

@tool
def get_bank_capital_ratios(bank_name: str) -> str:
    """Get capital ratios for a bank (Tier 1, Total Capital, Leverage).
    
    Args:
        bank_name: Bank name (Wells Fargo, U.S. Bancorp, Charles Schwab)
    """
    for bank in RISK_DATA["banks"]:
        if bank_name.lower() in bank["bank_name"].lower():
            return json.dumps({
                "bank_name": bank["bank_name"],
                "capital_ratios": bank["capital_ratios"],
                "note": "Use live FDIC API in production"
            }, indent=2)
    
    return json.dumps({"error": f"Bank {bank_name} not found"})

@tool
def calculate_expected_loss(industry: str, exposure_millions: float) -> str:
    """Calculate expected loss for a given industry and exposure amount.
    
    Args:
        industry: Industry name
        exposure_millions: Loan exposure in millions
    """
    # Average risk metrics across all banks for the industry
    industry_models = []
    
    for bank in RISK_DATA["banks"]:
        for model in bank["risk_models"]:
            if industry.lower() in model["industry"].lower():
                industry_models.append(model)
    
    if not industry_models:
        return json.dumps({"error": f"No risk models found for industry: {industry}"})
    
    avg_pd = sum(m["probability_of_default_pct"] for m in industry_models) / len(industry_models)
    avg_lgd = sum(m["loss_given_default_pct"] for m in industry_models) / len(industry_models)
    avg_el = sum(m["expected_loss_pct"] for m in industry_models) / len(industry_models)
    
    expected_loss_amount = exposure_millions * (avg_el / 100)
    
    return json.dumps({
        "industry": industry,
        "exposure_millions": exposure_millions,
        "average_pd_pct": round(avg_pd, 2),
        "average_lgd_pct": round(avg_lgd, 2),
        "average_el_pct": round(avg_el, 2),
        "expected_loss_millions": round(expected_loss_amount, 2),
        "models_used": len(industry_models)
    }, indent=2)

# Create agent with MCP tools
agent = Agent(tools=[query_risk_models, get_market_data, get_bank_capital_ratios, calculate_expected_loss])
agent.system_prompt = """You are the Treasury & Risk LOB Agent.

You provide risk models and treasury positions for:
- Wells Fargo
- U.S. Bancorp
- Charles Schwab

Data Sources:
- Real market data (Treasury yields, Fed Funds rate from FRED/Treasury.gov)
- Real capital ratios (FDIC risk metrics)
- Synthetic risk models (PD, LGD, Expected Loss by industry)

Your tools are exposed via MCP protocol for cross-account access from the central orchestrator.
"""

@app.entrypoint
async def invoke(payload):
    """AgentCore entrypoint with MCP support"""
    user_message = payload.get("prompt", "Hello from Treasury & Risk LOB!")
    stream = agent.stream_async(user_message)
    async for event in stream:
        yield event

if __name__ == "__main__":
    app.run()

"""Corporate Banking LOB Agent with MCP Server
Exposes customer relationships and loan exposure via MCP protocol
"""
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, tool
import boto3
import json
import os

app = BedrockAgentCoreApp()

# Load hybrid data from S3
s3 = boto3.client('s3')
S3_BUCKET = os.getenv('DATA_BUCKET', 'corporate-banking-891377397197')
S3_KEY = 'data/customer_loans.json'

def load_data_from_s3():
    """Load customer loans data from S3"""
    try:
        response = s3.get_object(Bucket=S3_BUCKET, Key=S3_KEY)
        return json.loads(response['Body'].read().decode('utf-8'))
    except Exception as e:
        print(f"Error loading data from S3: {e}")
        return {"banks": []}

CORPORATE_DATA = load_data_from_s3()

@tool
def query_customer_loans(bank_name: str = None, customer_name: str = None, industry: str = None) -> str:
    """Query customer relationships and loan exposure.
    
    Args:
        bank_name: Filter by bank (JPMorgan Chase, Bank of America, Citigroup)
        customer_name: Filter by customer name
        industry: Filter by industry
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
    
    return json.dumps({
        "lob": "Corporate Banking",
        "account_id": CORPORATE_DATA["account_id"],
        "data_source": CORPORATE_DATA["data_source"],
        "results": results,
        "total_results": len(results)
    }, indent=2)

@tool
def get_bank_aggregate_data(bank_name: str) -> str:
    """Get aggregate loan portfolio data for a bank.
    
    Args:
        bank_name: Bank name (JPMorgan Chase, Bank of America, Citigroup)
    """
    for bank in CORPORATE_DATA["banks"]:
        if bank_name.lower() in bank["bank_name"].lower():
            return json.dumps({
                "bank_name": bank["bank_name"],
                "total_ci_loans_billions": bank["total_ci_loans_billions"],
                "data_source_aggregate": bank["data_source_aggregate"],
                "total_customers": bank["total_customers"],
                "total_exposure_millions": bank["total_exposure_millions"],
                "customer_breakdown_available": True
            }, indent=2)
    
    return json.dumps({"error": f"Bank {bank_name} not found"})

@tool
def get_industry_exposure(industry: str) -> str:
    """Get total loan exposure by industry across all banks.
    
    Args:
        industry: Industry name (Technology, Healthcare, Energy, etc.)
    """
    exposure_by_bank = {}
    
    for bank in CORPORATE_DATA["banks"]:
        bank_exposure = 0
        customers = []
        
        for loan in bank["customer_loans"]:
            if industry.lower() in loan["industry"].lower():
                bank_exposure += loan["loan_amount_millions"]
                customers.append(loan["customer_name"])
        
        if bank_exposure > 0:
            exposure_by_bank[bank["bank_name"]] = {
                "exposure_millions": bank_exposure,
                "customers": customers
            }
    
    return json.dumps({
        "industry": industry,
        "exposure_by_bank": exposure_by_bank,
        "total_exposure_millions": sum(b["exposure_millions"] for b in exposure_by_bank.values())
    }, indent=2)

# Create agent with MCP tools
agent = Agent(tools=[query_customer_loans, get_bank_aggregate_data, get_industry_exposure])
agent.system_prompt = """You are the Corporate Banking LOB Agent.

You provide customer relationship data and loan exposure for:
- JPMorgan Chase
- Bank of America
- Citigroup

Data Sources:
- Real FDIC aggregate loan data (C&I loans in billions)
- Synthetic customer breakdown (Fortune 500 companies)

Your tools are exposed via MCP protocol for cross-account access from the central orchestrator.
"""

@app.entrypoint
async def invoke(payload):
    """AgentCore entrypoint with MCP support"""
    user_message = payload.get("prompt", "Hello from Corporate Banking LOB!")
    stream = agent.stream_async(user_message)
    async for event in stream:
        yield event

if __name__ == "__main__":
    app.run()

"""East Region Banking Agent with MCP Server
Exposes regional banking data via MCP protocol
"""
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, tool
import boto3
import json
import requests

app = BedrockAgentCoreApp()

# East Region Banks
EAST_BANKS = {
    "JPMorgan Chase": "0000019617",
    "Bank of America": "0000070858",
    "Citigroup": "0000831001",
    "PNC Financial": "0000713676",
    "TD Bank": "0000133058"
}

s3 = boto3.client('s3')

@tool
def mcp_query_east_kb(query: str) -> str:
    """MCP Tool: Query East Region Knowledge Base
    
    This tool is exposed via MCP protocol for cross-account access.
    Returns banking data for East region banks.
    """
    results = []
    for bank_name, cik in EAST_BANKS.items():
        try:
            headers = {'User-Agent': 'BankIQ Analytics contact@bankiq.com'}
            url = f"https://data.sec.gov/submissions/CIK{cik}.json"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results.append({
                    "bank": bank_name,
                    "cik": cik,
                    "name": data.get('name', bank_name),
                    "filings_count": len(data.get('filings', {}).get('recent', {}).get('form', []))
                })
        except:
            pass
    
    return json.dumps({
        "region": "East",
        "query": query,
        "banks": results,
        "mcp_enabled": True,
        "data_source": "SEC EDGAR API"
    }, indent=2)

@tool
def mcp_get_east_s3_document(document_key: str) -> str:
    """MCP Tool: Get document from East Region S3
    
    This tool is exposed via MCP protocol for cross-account access.
    Retrieves banking documents from regional S3 bucket.
    """
    try:
        bucket_name = "east-region-banking-891377397197"
        response = s3.get_object(Bucket=bucket_name, Key=document_key)
        content = response['Body'].read().decode('utf-8')
        
        return json.dumps({
            "success": True,
            "region": "East",
            "document_key": document_key,
            "content_preview": content[:500],
            "mcp_enabled": True
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "region": "East"
        })

@tool
def mcp_list_east_documents() -> str:
    """MCP Tool: List available documents in East Region S3
    
    This tool is exposed via MCP protocol for cross-account access.
    """
    try:
        bucket_name = "east-region-banking-891377397197"
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix="documents/")
        
        documents = [obj['Key'] for obj in response.get('Contents', [])]
        
        return json.dumps({
            "success": True,
            "region": "East",
            "documents": documents,
            "count": len(documents),
            "mcp_enabled": True
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "region": "East"
        })

# Create agent with MCP tools
agent = Agent(tools=[mcp_query_east_kb, mcp_get_east_s3_document, mcp_list_east_documents])
agent.system_prompt = """You are the East Region Banking Agent.

You provide banking data for East region banks via MCP protocol.
Your tools are exposed as MCP endpoints for cross-account access.

East Region Banks:
- JPMorgan Chase
- Bank of America
- Citigroup
- PNC Financial
- TD Bank

When responding, provide clear, concise information about East region banking data.
"""

@app.entrypoint
async def invoke(payload):
    """AgentCore entrypoint with MCP support"""
    user_message = payload.get("prompt", "Hello from East Region!")
    stream = agent.stream_async(user_message)
    async for event in stream:
        yield event

if __name__ == "__main__":
    app.run()

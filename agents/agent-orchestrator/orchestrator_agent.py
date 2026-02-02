"""Centralized Hub-and-Spoke Orchestrator Agent"""
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, tool
import json
import requests

app = BedrockAgentCoreApp()

# Gateway URLs
CORPORATE_BANKING_GATEWAY = "https://corporate-banking-gateway-noauth-vd51qkmqqy.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp"
TREASURY_RISK_GATEWAY = "https://treasury-risk-gateway-noauth-w7wh7wboyx.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp"

@tool
def query_customer_loans(bank_name: str = None, customer_name: str = None, industry: str = None) -> str:
    """Query customer loans from Corporate Banking LOB."""
    try:
        response = requests.post(
            CORPORATE_BANKING_GATEWAY,
            json={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "corporate-banking-tools___query_customer_loans",
                    "arguments": {k: v for k, v in {"bank_name": bank_name, "customer_name": customer_name, "industry": industry}.items() if v}
                },
                "id": 1
            }
        )
        if response.status_code == 200:
            result = response.json()
            return json.dumps(result.get('result', result))
        return json.dumps({"error": f"Gateway returned {response.status_code}"})
    except Exception as e:
        return json.dumps({"error": str(e)})

@tool
def query_risk_models(bank_name: str = None, industry: str = None) -> str:
    """Query risk models from Treasury & Risk LOB."""
    try:
        response = requests.post(
            TREASURY_RISK_GATEWAY,
            json={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "treasury-risk-tools___query_risk_models",
                    "arguments": {k: v for k, v in {"bank_name": bank_name, "industry": industry}.items() if v}
                },
                "id": 1
            }
        )
        if response.status_code == 200:
            result = response.json()
            return json.dumps(result.get('result', result))
        return json.dumps({"error": f"Gateway returned {response.status_code}"})
    except Exception as e:
        return json.dumps({"error": str(e)})

agent = Agent(tools=[query_customer_loans, query_risk_models])
agent.system_prompt = """You are a Corporate Banking Credit Risk Orchestrator Agent.

ARCHITECTURE: Hub-and-Spoke with AgentCore MCP Gateways
- Central Account: 164543933824 (You are here)
- Corporate Banking LOB: 891377397197 (MCP Gateway → Lambda → S3 customer data)
- Treasury & Risk LOB: 058264155998 (MCP Gateway → Lambda → S3 risk models)

You have tools that call LOB gateways to access distributed data.

RESPONSE FORMAT:
- Write 3-4 paragraphs, 4-6 sentences each
- NO bullet points, NO lists
- Flowing narrative prose
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

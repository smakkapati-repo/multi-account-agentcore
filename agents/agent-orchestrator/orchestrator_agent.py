"""Centralized Hub-and-Spoke Orchestrator Agent with MCP Client"""
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, tool
import boto3
import json
import os

app = BedrockAgentCoreApp()

# AWS clients
sts = boto3.client('sts', region_name='us-east-1')
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name='us-east-1')

# LOB account configuration
CORPORATE_BANKING_ACCOUNT = "891377397197"
TREASURY_RISK_ACCOUNT = "058264155998"
CORPORATE_BANKING_AGENT_ARN = os.getenv('CORPORATE_BANKING_AGENT_ARN', '')
TREASURY_RISK_AGENT_ARN = os.getenv('TREASURY_RISK_AGENT_ARN', '')

def assume_role_and_invoke_mcp(role_arn: str, agent_arn: str, tool_name: str, parameters: dict) -> dict:
    """Assume role in LOB account and invoke MCP tool"""
    try:
        # Assume role in LOB account
        assumed_role = sts.assume_role(
            RoleArn=role_arn,
            RoleSessionName='OrchestratorMCPClient'
        )
        
        credentials = assumed_role['Credentials']
        
        # Create bedrock client with assumed credentials
        lob_bedrock = boto3.client(
            'bedrock-agent-runtime',
            region_name='us-east-1',
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken']
        )
        
        # Invoke MCP tool via Bedrock Agent Runtime
        response = lob_bedrock.invoke_agent(
            agentId=agent_arn.split('/')[-1],
            agentAliasId='TSTALIASID',
            sessionId='mcp-session',
            inputText=json.dumps({
                'tool': tool_name,
                'parameters': parameters
            })
        )
        
        # Parse streaming response
        result = ''
        for event in response['completion']:
            if 'chunk' in event:
                result += event['chunk']['bytes'].decode('utf-8')
        
        return json.loads(result)
    
    except Exception as e:
        return {'error': str(e), 'mcp_call_failed': True}

@tool
def query_corporate_banking(query: str, bank_name: str = None, customer_name: str = None, industry: str = None) -> str:
    """Query Corporate Banking LOB via MCP for customer relationships and loan exposure.
    
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
    if not CORPORATE_BANKING_AGENT_ARN:
        return json.dumps({
            'error': 'Corporate Banking Agent ARN not configured',
            'note': 'Set CORPORATE_BANKING_AGENT_ARN environment variable'
        })
    
    role_arn = f"arn:aws:iam::{CORPORATE_BANKING_ACCOUNT}:role/CentralAccountAccessRole"
    
    result = assume_role_and_invoke_mcp(
        role_arn=role_arn,
        agent_arn=CORPORATE_BANKING_AGENT_ARN,
        tool_name='query_customer_loans',
        parameters={
            'bank_name': bank_name,
            'customer_name': customer_name,
            'industry': industry
        }
    )
    
    result['mcp_enabled'] = True
    result['cross_account'] = True
    result['query'] = query
    
    return json.dumps(result, indent=2)

@tool
def query_treasury_risk(query: str, bank_name: str = None, industry: str = None) -> str:
    """Query Treasury & Risk LOB via MCP for treasury positions and risk models.
    
    Use this tool when the user asks about:
    - Treasury positions and hedging
    - Risk models (PD, LGD, Expected Loss)
    - Specific banks: Wells Fargo, U.S. Bancorp, Charles Schwab
    
    Args:
        query: Natural language query
        bank_name: Optional bank filter
        industry: Optional industry filter
    """
    if not TREASURY_RISK_AGENT_ARN:
        return json.dumps({
            'error': 'Treasury & Risk Agent ARN not configured',
            'note': 'Set TREASURY_RISK_AGENT_ARN environment variable'
        })
    
    role_arn = f"arn:aws:iam::{TREASURY_RISK_ACCOUNT}:role/CentralAccountAccessRole"
    
    result = assume_role_and_invoke_mcp(
        role_arn=role_arn,
        agent_arn=TREASURY_RISK_AGENT_ARN,
        tool_name='query_risk_models',
        parameters={
            'bank_name': bank_name,
            'industry': industry
        }
    )
    
    result['mcp_enabled'] = True
    result['cross_account'] = True
    result['query'] = query
    
    return json.dumps(result, indent=2)

@tool
def compare_lobs(metric: str) -> str:
    """Compare Corporate Banking vs Treasury & Risk LOB data via MCP.
    
    Use this tool when the user asks to:
    - Compare LOBs
    - Aggregate cross-LOB data
    - Analyze enterprise-wide trends
    
    Args:
        metric: The metric to compare (e.g., "exposure", "risk", "performance")
    """
    # Query both LOBs via MCP
    corp_result = query_corporate_banking(f"Get {metric} data")
    risk_result = query_treasury_risk(f"Get {metric} data")
    
    comparison = {
        "metric": metric,
        "corporate_banking": json.loads(corp_result),
        "treasury_risk": json.loads(risk_result),
        "architecture": "Hub-and-Spoke with MCP",
        "central_account": "164543933824",
        "mcp_enabled": True
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

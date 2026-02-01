# MCP + AgentCore Gateway Implementation

## Architecture

```
Frontend → Gateway → Orchestrator (MCP Client) → LOB Agents (MCP Servers)
```

## Components

### 1. LOB Agents (MCP Servers)
**Corporate Banking** (`agent-corporate-banking/`)
- MCP Server enabled
- Exposes tools: `query_customer_loans`, `get_bank_aggregate_data`, `get_industry_exposure`
- Deployed to account: 891377397197

**Treasury & Risk** (`agent-treasury-risk/`)
- MCP Server enabled
- Exposes tools: `query_risk_models`, `get_market_data`, `get_bank_capital_ratios`, `calculate_expected_loss`
- Deployed to account: 058264155998

### 2. Orchestrator (MCP Client)
**Orchestrator** (`agent-orchestrator/`)
- MCP Client enabled
- Calls LOB agents via MCP protocol
- Cross-account IAM role assumption
- Gateway enabled for HTTP API
- Deployed to account: 164543933824

### 3. AgentCore Gateway
- HTTP/WebSocket endpoint
- Deployed with orchestrator
- Enables frontend integration
- Authentication & throttling

## Deployment

```bash
# 1. Deploy LOB agents with MCP servers
cd agent-corporate-banking
AWS_PROFILE=child1 agentcore deploy --enable-mcp
CORPORATE_BANKING_AGENT_ARN=$(AWS_PROFILE=child1 agentcore status | grep agent_arn | cut -d'"' -f4)

cd ../agent-treasury-risk
AWS_PROFILE=child2-demo agentcore deploy --enable-mcp
TREASURY_RISK_AGENT_ARN=$(AWS_PROFILE=child2-demo agentcore status | grep agent_arn | cut -d'"' -f4)

# 2. Deploy orchestrator with MCP client + gateway
cd ../agent-orchestrator
export CORPORATE_BANKING_AGENT_ARN=$CORPORATE_BANKING_AGENT_ARN
export TREASURY_RISK_AGENT_ARN=$TREASURY_RISK_AGENT_ARN
agentcore deploy

# 3. Deploy gateway
agentcore gateway deploy
GATEWAY_URL=$(agentcore gateway status | grep api_endpoint | cut -d'"' -f4)
echo "Gateway URL: $GATEWAY_URL"
```

## MCP Communication Flow

1. **Frontend** → HTTP POST to Gateway URL
2. **Gateway** → Invokes Orchestrator Agent
3. **Orchestrator** → Assumes role in LOB account
4. **Orchestrator** → Calls LOB agent via MCP (Bedrock Agent Runtime)
5. **LOB Agent** → Executes tool, returns result
6. **Orchestrator** → Aggregates results
7. **Gateway** → Streams response to frontend

## Configuration Files

**agent-corporate-banking/agentcore.yaml**
```yaml
mcp_server:
  enabled: true
  tools:
    - query_customer_loans
    - get_bank_aggregate_data
    - get_industry_exposure
```

**agent-treasury-risk/agentcore.yaml**
```yaml
mcp_server:
  enabled: true
  tools:
    - query_risk_models
    - get_market_data
    - get_bank_capital_ratios
    - calculate_expected_loss
```

**agent-orchestrator/agentcore.yaml**
```yaml
mcp_client:
  enabled: true
  servers:
    - name: corporate-banking
      account_id: "891377397197"
      role_arn: arn:aws:iam::891377397197:role/CentralAccountAccessRole
      agent_arn: ${CORPORATE_BANKING_AGENT_ARN}
    - name: treasury-risk
      account_id: "058264155998"
      role_arn: arn:aws:iam::058264155998:role/CentralAccountAccessRole
      agent_arn: ${TREASURY_RISK_AGENT_ARN}
gateway:
  enabled: true
```

## Testing

```bash
# Test gateway endpoint
curl -X POST $GATEWAY_URL \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Show me Technology loans from Corporate Banking"}'
```

## Value Added

1. **MCP Protocol**: Standardized agent-to-agent communication
2. **Cross-Account**: True multi-account orchestration with IAM roles
3. **Gateway**: HTTP API for frontend integration
4. **Streaming**: Real-time response streaming
5. **Scalability**: Independent LOB agent scaling

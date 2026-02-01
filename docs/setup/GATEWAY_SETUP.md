# LoanIQ Frontend - Gateway Configuration

## Setup

1. **Deploy AgentCore Gateway** (in orchestrator agent directory):
```bash
cd agent-orchestrator
agentcore gateway deploy
```

2. **Get Gateway URL**:
```bash
agentcore gateway status
# Look for: "api_endpoint": "https://xxx.execute-api.us-east-1.amazonaws.com/prod/invoke"
```

3. **Configure Frontend**:
```bash
cd frontend
echo "REACT_APP_GATEWAY_URL=https://xxx.execute-api.us-east-1.amazonaws.com/prod/invoke" > .env
```

4. **Start Frontend**:
```bash
npm start
```

## Gateway Architecture

```
Frontend (React)
  ↓ HTTPS POST
AgentCore Gateway (API Gateway)
  ↓ Invoke
Orchestrator Agent (Bedrock AgentCore)
  ↓ MCP Client
  ├→ Corporate Banking Agent (MCP Server)
  └→ Treasury & Risk Agent (MCP Server)
```

## Request Format

```javascript
POST https://xxx.execute-api.us-east-1.amazonaws.com/prod/invoke
Content-Type: application/json

{
  "prompt": "Show me Technology loans from Corporate Banking"
}
```

## Response Format

```javascript
{
  "response": "Agent response text...",
  "sessionId": "xxx",
  "metadata": {...}
}
```

## Troubleshooting

**Error: Gateway URL not configured**
- Create `.env` file with `REACT_APP_GATEWAY_URL`
- Restart React app

**Error: 403 Forbidden**
- Check Gateway authentication settings
- Verify IAM permissions

**Error: 504 Gateway Timeout**
- Agent taking too long (>30s)
- Check agent logs in CloudWatch

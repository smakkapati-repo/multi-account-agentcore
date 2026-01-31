# AgentCore Gateway Guide

## What is AgentCore Gateway?

AgentCore Gateway is an **API Gateway integration** that exposes your AgentCore agent as a REST API endpoint with:
- ✅ Direct HTTPS access (no backend proxy needed)
- ✅ Built-in authentication (API keys, IAM, Cognito)
- ✅ Rate limiting and throttling
- ✅ Request/response caching
- ✅ CloudWatch metrics and logging
- ✅ Serverless architecture

## Architecture Comparison

### Without Gateway (Current Tab 2 & Tab 3)
```
Frontend → Backend (ECS) → AgentCore Agent
```
- Backend acts as proxy
- Backend handles auth, logging, error handling
- 30-second timeout on ALB

### With Gateway (Tab 3 Enhanced)
```
Frontend → API Gateway → AgentCore Agent
```
- Direct API access
- Gateway handles auth, rate limiting, caching
- 29-second timeout on API Gateway

## Gateway Configuration

The gateway is configured in `.bedrock_agentcore.yaml`:

```yaml
gateway:
  enabled: true
  stage_name: prod
  throttle_rate_limit: 100    # requests per second
  throttle_burst_limit: 200   # burst capacity
```

## Deployment

Gateway is deployed automatically with the orchestrator agent:

```bash
cd agent-centralized
agentcore deploy              # Deploy agent
agentcore gateway deploy      # Deploy gateway
agentcore gateway status      # Get gateway URL
```

## Frontend Integration

Tab 3 includes a toggle to switch between:
1. **Backend Proxy** - Traditional pattern (Frontend → Backend → Agent)
2. **Gateway (Serverless)** - Direct API access (Frontend → Gateway → Agent)

The toggle is in `CentralizedAgentCore.js`:
```javascript
const endpoint = accessMode === 'gateway' 
  ? process.env.REACT_APP_GATEWAY_URL 
  : 'http://localhost:3001/api/chat-centralized';
```

## Environment Variables

Set the gateway URL in your frontend `.env`:
```bash
REACT_APP_GATEWAY_URL=https://abc123.execute-api.us-east-1.amazonaws.com/prod/invoke
```

## Gateway Commands

```bash
# Deploy gateway
agentcore gateway deploy

# Get gateway status and URL
agentcore gateway status

# Update gateway configuration
agentcore gateway update

# Delete gateway
agentcore gateway delete
```

## Benefits of Gateway

1. **Serverless** - No ECS/EC2 costs when idle
2. **Scalability** - Auto-scales to handle traffic spikes
3. **Security** - Built-in auth, rate limiting, API keys
4. **Caching** - Cache responses at edge locations
5. **Monitoring** - CloudWatch metrics out of the box
6. **Cost** - Pay per request (vs. always-on ECS)

## When to Use Gateway vs Backend

| Use Case | Recommendation |
|----------|---------------|
| Public API | Gateway |
| Internal tool | Backend |
| High traffic | Gateway (auto-scales) |
| Complex auth | Backend (custom logic) |
| Long-running queries | Backend (no 29s timeout) |
| Microservices | Gateway (per-service endpoints) |

## Tab 3 Showcase

Tab 3 now demonstrates **3 architectural patterns**:

1. **Decentralized** (Tab 2) - Single account, backend proxy
2. **Centralized with MCP** (Tab 3, Backend mode) - Multi-account, backend proxy
3. **Gateway** (Tab 3, Gateway mode) - Multi-account, serverless API access

This showcases the flexibility of AgentCore to support different deployment patterns.

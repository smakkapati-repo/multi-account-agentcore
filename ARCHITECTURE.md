# Architecture Overview

**Multi-Account Hub-and-Spoke Pattern with AgentCore Gateways**

```
┌─────────────────────────────────────────────────────────────────┐
│  Central Account (164543933824) - Hub                          │
│                                                                 │
│  ┌──────────┐      ┌────────────────┐      ┌──────────────┐  │
│  │ React UI │─────▶│ API Gateway +  │─────▶│ Orchestrator │  │
│  │CloudFront│      │ Lambda         │      │ Agent        │  │
│  └──────────┘      └────────────────┘      └──────┬───────┘  │
│                                                     │          │
└─────────────────────────────────────────────────────┼──────────┘
                                                      │
                        ┌─────────────────────────────┴─────────────────────────┐
                        │ HTTP POST (JSON-RPC)                                  │
                        │ {"jsonrpc":"2.0","method":"tools/call",...}          │
                        │                                                       │
        ┌───────────────▼──────────────┐              ┌──────────────────────▼─┐
        │ Corporate Banking LOB        │              │ Treasury & Risk LOB    │
        │ Account: 891377397197        │              │ Account: 058264155998  │
        │                              │              │                        │
        │ ┌──────────────────────┐    │              │ ┌────────────────────┐ │
        │ │ AgentCore Gateway    │    │              │ │ AgentCore Gateway  │ │
        │ │ (NONE auth)          │    │              │ │ (NONE auth)        │ │
        │ └──────────┬───────────┘    │              │ └─────────┬──────────┘ │
        │            │                 │              │           │            │
        │ ┌──────────▼───────────┐    │              │ ┌─────────▼──────────┐ │
        │ │ Lambda Function      │    │              │ │ Lambda Function    │ │
        │ │ - query_customer_    │    │              │ │ - query_risk_      │ │
        │ │   loans              │    │              │ │   models           │ │
        │ │ - get_bank_aggregate │    │              │ │ - get_market_data  │ │
        │ │ - get_industry_      │    │              │ │ - calculate_       │ │
        │ │   exposure           │    │              │ │   expected_loss    │ │
        │ └──────────┬───────────┘    │              │ └─────────┬──────────┘ │
        │            │                 │              │           │            │
        │ ┌──────────▼───────────┐    │              │ ┌─────────▼──────────┐ │
        │ │ S3 Bucket            │    │              │ │ S3 Bucket          │ │
        │ │ customer_loans.json  │    │              │ │ risk_models.json   │ │
        │ └──────────────────────┘    │              │ └────────────────────┘ │
        └─────────────────────────────┘              └────────────────────────┘
```

## Key Components

### 1. Frontend (Central Account)
- React app hosted on CloudFront + S3
- Sends user queries to API Gateway

### 2. API Gateway + Lambda (Central Account)
- API Gateway endpoint: `/invoke`
- Lambda function invokes orchestrator agent via `bedrock-agentcore` API
- Parses SSE streaming response with byte + line buffering
- Returns final text to frontend

### 3. Orchestrator Agent (Central Account)
- Strands-based agent with custom `@tool` functions
- Tools make HTTP POST requests to LOB gateway URLs
- Uses JSON-RPC format: `{"jsonrpc":"2.0","method":"tools/call","params":{...}}`
- No data storage - pure orchestration

### 4. LOB Gateways (Child Accounts)
- AgentCore Gateway with Lambda targets
- NONE authorization (demo only - use IAM/JWT in production)
- Tool schemas explicitly defined (not auto-discovered)
- Routes requests to Lambda functions

### 5. LOB Lambda Functions (Child Accounts)
- Receive direct property mapping from gateway (not MCP protocol)
- Query S3 data and return JSON results
- **Corporate Banking**: customer loans, bank aggregates, industry exposure
- **Treasury & Risk**: risk models, market data, expected loss calculations

### 6. Data Storage (Child Accounts)
- S3 buckets with synthetic data (customer loans, risk models)
- Each LOB owns and controls its data
- No data duplication or centralization

## Data Flow

1. User enters query in React UI
2. Frontend → API Gateway → Lambda
3. Lambda invokes orchestrator agent
4. Orchestrator determines which LOB tools to call
5. Orchestrator → HTTP POST (JSON-RPC) → LOB Gateway
6. Gateway → Lambda → S3 data
7. Results flow back through chain
8. Lambda parses SSE stream, returns final text
9. Frontend displays response

## Security Model

- **Cross-Account Access**: IAM roles with least-privilege permissions
- **Gateway Auth**: NONE (demo) - use IAM or JWT in production
- **Data Isolation**: Each LOB controls its own S3 bucket
- **No Data Transfer**: Data stays in source accounts

## Key Technical Insights

✅ **Centralized AI reasoning, distributed data ownership**
- Orchestrator agent has no data storage
- Each LOB maintains full control over sensitive data

✅ **Direct HTTP JSON-RPC, no MCP client needed**
- Orchestrator tools make standard HTTP POST requests
- Simpler than MCP client context managers

✅ **Gateway tool schemas must be explicitly defined**
- AgentCore Gateway does not auto-discover tools from Lambda
- Tool schemas defined in `tool_schema.json` files

✅ **Lambda receives direct property mapping**
- Gateway passes tool arguments as event properties
- Not MCP protocol format

✅ **Streaming response requires careful buffering**
- SSE chunks don't respect UTF-8 character boundaries
- Byte-level buffering prevents decode errors
- Line-level buffering prevents incomplete JSON parsing

## Production Considerations

1. **Authentication**: Replace NONE auth with IAM roles or JWT tokens
2. **Monitoring**: Add CloudWatch metrics and X-Ray tracing
3. **Error Handling**: Implement retry logic and circuit breakers
4. **Rate Limiting**: Add API Gateway throttling
5. **Data Sources**: Replace synthetic data with commercial providers (Moody's, S&P, Bloomberg)
6. **Compliance**: Ensure data residency and audit logging requirements are met

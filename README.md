# Centralized Amazon Bedrock AgentCore with Distributed MCP Data Sources
**A Multi-Account Pattern for Enterprise AI**

**Authors:** Shashi Makkapati, Senthil Kamala Rathinam, Jacob Scheatzle

> **Blog Post Demo**: This repository demonstrates a multi-account architecture pattern using **Amazon Bedrock AgentCore** and **Model Context Protocol (MCP)** to enable centralized AI agents to securely access distributed data sources across AWS accounts without data duplication or ownership transfer.

## 🎯 The Enterprise Challenge

Enterprise organizations face a critical architectural challenge:
- **Distributed Data Ownership**: Different LOBs control different datasets across separate AWS accounts
- **Compliance Requirements**: Each LOB must retain full control over sensitive data
- **Business Need**: AI assistants must provide unified insights across these boundaries

**Traditional approaches fail:**
- ❌ **Centralizing data** increases governance complexity and duplicates regulated data
- ❌ **Point-to-point integrations** create tight coupling and operational overhead
- ❌ **Neither approach** aligns with enterprise multi-account strategies

## 💡 The Solution

This pattern combines **Amazon Bedrock AgentCore** with **Model Context Protocol (MCP)** to:
- ✅ Enable centralized AI agent to orchestrate queries across LOB-owned data sources
- ✅ Preserve data isolation, security, and compliance boundaries
- ✅ Eliminate data duplication and ownership transfer
- ✅ Standardize access through MCP protocol
- ✅ Enforce least-privilege cross-account IAM roles

## 🏗️ Architecture Overview

![Multi-Account Architecture](arch/bankiq_plus_agentcore_architecture.png)

```
┌───────────────────────────────────────────────────────────────┐
│  Central Account (Hub) - AgentCore Orchestrator             │
│  • Centralized AI reasoning                                 │
│  • No data storage                                          │
│  • Cross-account IAM roles                                  │
└────────────────────────┬──────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
        ▼                                 ▼
┌─────────────────────────┐      ┌─────────────────────────┐
│ Corporate Banking LOB   │      │ Treasury & Risk LOB     │
│ Account: 891...97       │      │ Account: 058...98       │
│                         │      │                         │
│ • MCP-enabled           │      │ • MCP-enabled           │
│ • Customer data         │      │ • Risk models           │
│ • Loan exposure         │      │ • Treasury positions    │
│ • Banks: JPM,BAC,C      │      │ • Banks: WFC,USB,SCHW   │
└─────────────────────────┘      └─────────────────────────┘
```

**Key Components:**
1. **Central Account**: Orchestrator agent (no data storage)
2. **LOB Accounts**: MCP-enabled agents with LOB-owned data
3. **Cross-Account Access**: IAM roles with least-privilege
4. **MCP Protocol**: Standardized data access interface

## 📊 Use Case: Commercial Banking Credit Risk Assessment

This demo implements a banking analytics platform where:
- **Central Agent**: Orchestrates credit risk assessment queries
- **Corporate Banking LOB**: Owns customer relationship data and loan exposure (JPMorgan, Bank of America, Citigroup)
- **Treasury & Risk LOB**: Owns treasury positions and risk models (Wells Fargo, U.S. Bank, Charles Schwab)

**Business Value:**
- Evaluate credit risk across multiple LOBs without data centralization
- Each LOB maintains full control over sensitive financial data
- Real-time access to distributed data sources
- Compliance with regulatory data segregation requirements

### Data Sources

**Demo Implementation (This Repository):**
This demo uses **synthetic corporate customer data** to illustrate the multi-account pattern without requiring paid subscriptions or exposing sensitive information. The synthetic data includes:
- Fortune 500-style corporate profiles
- Simulated loan exposure ($1M-$500M)
- Credit ratings (AAA-CCC)
- Industry classifications and risk metrics

**Enterprise Production Options:**
Enterprises have access to commercial-grade data providers for production implementations:

| Provider | Data Type | Use Case |
|----------|-----------|----------|
| **[Moody's Analytics](https://www.moodysanalytics.com/)** | Credit ratings, risk models, financial data | Credit risk assessment, portfolio analysis |
| **[S&P Global Market Intelligence](https://www.spglobal.com/marketintelligence/)** | Corporate financials, credit data, industry analytics | Due diligence, credit decisioning |
| **[Bloomberg Terminal](https://www.bloomberg.com/professional/solution/bloomberg-terminal/)** | Real-time financial data, credit default swaps, market data | Trading, risk management, analytics |
| **[Refinitiv (LSEG)](https://www.refinitiv.com/)** | Financial data, risk analytics, regulatory data | Compliance, risk assessment, trading |
| **[Dun & Bradstreet](https://www.dnb.com/)** | Business credit reports, company profiles | Credit decisioning, supplier risk |
| **[Experian Business](https://www.experian.com/business/)** | Commercial credit data, risk scores | Small business lending, credit monitoring |

**Why Synthetic Data for This Demo:**
- ✅ No subscription costs or API keys required
- ✅ No exposure of real customer data
- ✅ Demonstrates architecture pattern without data licensing concerns
- ✅ Easy to customize for different industries
- ✅ Reproducible across any AWS account

**Production Recommendation:**
For production deployments, integrate with your enterprise's existing data providers using the same MCP-based architecture pattern demonstrated here. The agent tools can be easily adapted to call commercial APIs instead of synthetic data sources.

## 🔑 Key Benefits

| Benefit | Description |
|---------|-------------|
| **Data Isolation** | Each LOB maintains complete control over sensitive data |
| **Security** | Cross-account IAM roles provide secure, auditable access |
| **Compliance** | Meets regulatory requirements for data segregation |
| **Scalability** | Independent scaling per business unit |
| **Governance** | Centralized orchestration with distributed ownership |
| **No Duplication** | Data stays in source accounts, no replication needed |

## 📊 Agent Tools

**Multi-Account Orchestrator** (`agent-orchestrator/orchestrator_agent.py`):
- `query_corporate_banking` - Query customer relationships and loan exposure
- `query_treasury_risk` - Query treasury positions and risk models
- `compare_lobs` - Cross-LOB comparison

## 🛠️ Technology Stack

### Core AI Platform
- **[Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/)** - Managed agent runtime
- **[Strands Framework](https://github.com/awslabs/agents-for-amazon-bedrock-sample-code)** - Python agent framework
- **[Claude Sonnet 4.5](https://www.anthropic.com/claude)** - Foundation model

### Application Stack
- **Authentication**: [AWS Cognito](https://docs.aws.amazon.com/cognito/) + OAuth 2.0 + JWT
- **Backend**: [Express.js](https://expressjs.com/) (Node.js) + Python agent
- **Frontend**: [React](https://react.dev/) + [Material-UI](https://mui.com/)
- **Infrastructure**: [ECS Fargate](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html), [ALB](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/), [CloudFront](https://docs.aws.amazon.com/cloudfront/), [S3](https://docs.aws.amazon.com/s3/)

## 📚 Documentation

- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** - Detailed deployment steps
- **[CloudFormation Guide](docs/CLOUDFORMATION_GUIDE.md)** - Infrastructure templates
- **[Agent Development](docs/AGENT_DEVELOPMENT.md)** - Building custom tools
- **[Data Sources](docs/CREDIT_RISK_DATA_SOURCES.md)** - Synthetic vs. commercial data options

## 🚀 Quick Start

### Prerequisites
- 3 AWS Accounts with administrative access
- AWS Bedrock access enabled in all accounts
- AWS CLI configured with profiles: `default`, `child1`, `child2-demo`
- Node.js 18+, Python 3.11+
- AgentCore CLI: `pip install bedrock-agentcore-starter-toolkit`

### Deploy Multi-Account Pattern

```bash
git clone https://github.com/smakkapati-repo/multi-account-agentcore.git
cd multi-account-agentcore
./deploy-multi-account.sh
```

**Deploy Time**: ~30-40 minutes

## 💰 Cost Estimate

**Multi-Account Setup (3 AWS Accounts):**

Monthly costs for 24/7 operation:

**Central Account (Hub):**
- ECS Fargate (Backend): $15-20
- ALB: $16-20
- CloudFront: $1-5
- S3 (Frontend): $1-2
- Bedrock (Orchestrator Agent): $10-20
- **Subtotal**: ~$43-67/month

**LOB Accounts (2 accounts):**
- Bedrock (MCP Agents): $5-10 per account
- S3 (Data Storage): $1-2 per account
- IAM Roles: Free
- **Subtotal**: ~$12-24/month (both accounts)

**Total Estimated Cost**: ~$55-90/month

**Cost Optimization:**
- Stop ECS tasks when not in use: ~$20-30/month
- Use Bedrock on-demand pricing (pay per request)
- Delete after demo: $0

## 🧹 Cleanup

```bash
cd multi-account-agentcore
./cfn/scripts/cleanup.sh
```

## 📄 License

Apache License 2.0

## 👥 Authors

Shashi Makkapati, Senthil Kamala Rathinam, Jacob Scheatzle

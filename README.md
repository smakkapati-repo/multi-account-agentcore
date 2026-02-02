# Centralized Amazon Bedrock AgentCore with Distributed MCP Data Sources
**A Multi-Account Pattern for Enterprise AI**

**Project Name:** LoanIQ - Distributed Credit Risk Platform

**Authors:** Shashi Makkapati, Senthil Kamala Rathinam, Karthik Tharmarajan

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

**Detailed Architecture:** See [ARCHITECTURE.md](ARCHITECTURE.md) for comprehensive technical documentation.

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

**Key Components:**
1. **Central Account**: Orchestrator agent (no data storage)
2. **LOB Accounts**: AgentCore Gateways with Lambda targets and S3 data
3. **Cross-Account Access**: IAM roles with least-privilege
4. **Communication**: HTTP JSON-RPC over AgentCore Gateway

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
- **Authentication**: [AWS Cognito](https://docs.aws.amazon.com/cognito/) + OAuth 2.0 + JWT (optional)
- **Backend**: AgentCore Gateway (serverless API)
- **Frontend**: [React](https://react.dev/) + [Material-UI](https://mui.com/)
- **Infrastructure**: AgentCore (serverless), [CloudFront](https://docs.aws.amazon.com/cloudfront/), [S3](https://docs.aws.amazon.com/s3/)

## 📚 Documentation

- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** - Detailed deployment steps
- **[CloudFormation Guide](docs/CLOUDFORMATION_GUIDE.md)** - Infrastructure templates
- **[Agent Development](docs/AGENT_DEVELOPMENT.md)** - Building custom tools
- **[Data Sources](docs/CREDIT_RISK_DATA_SOURCES.md)** - Synthetic vs. commercial data options

## 📋 Prerequisites

### Required

**1. Three AWS Accounts**
- Central Account (orchestrator)
- Corporate Banking LOB Account
- Treasury & Risk LOB Account

**2. AWS CLI Configured**
```bash
# Configure profiles for each account
aws configure --profile default      # Central account
aws configure --profile child1       # Corporate Banking
aws configure --profile child2-demo  # Treasury & Risk

# Verify
aws sts get-caller-identity --profile default
aws sts get-caller-identity --profile child1
aws sts get-caller-identity --profile child2-demo
```

**3. Amazon Bedrock Model Access**
- Enable **Claude Sonnet 4.5** in all 3 accounts
- AWS Console → Bedrock → Model access → Request access

**4. Software**
- Python 3.11+: `python3 --version`
- Node.js 18+: `node --version`
- AgentCore CLI: `pip install bedrock-agentcore-starter-toolkit`

**5. IAM Permissions**
- AdministratorAccess (or Bedrock, S3, IAM, CloudWatch, CodeBuild permissions)

## 🚀 Quick Start

### One-Command Deployment

```bash
git clone https://github.com/smakkapati-repo/Centralized-Amazon-Bedrock-AgentCore-with-Distributed-MCP-Data-Sources.git
cd Centralized-Amazon-Bedrock-AgentCore-with-Distributed-MCP-Data-Sources
./scripts/deploy-all.sh
```

On first run, the script will:
1. ✅ Prompt for your 3 AWS account IDs and CLI profiles (one-time configuration)
2. ✅ Verify each account and save configuration
3. ✅ Generate synthetic data automatically
4. ✅ Create S3 buckets and IAM roles
5. ✅ Upload data to LOB accounts
6. ✅ Deploy LOB agents with MCP servers
7. ✅ Deploy orchestrator with MCP client + Gateway
8. ✅ Build and deploy React frontend to CloudFront

**Deploy Time**: ~30-40 minutes

**Estimated Cost**: ~$55-90/month (or $0 if deleted after demo)

## 💰 Cost Estimate

**Multi-Account Setup (3 AWS Accounts):**

Monthly costs for 24/7 operation:

**Central Account (Hub):**
- Bedrock (Orchestrator Agent): $10-20 (pay per request)
- AgentCore Gateway: $5-10
- S3 (Agent artifacts): $1-2
- CloudWatch Logs: $1-2
- **Subtotal**: ~$17-34/month

**LOB Accounts (2 accounts):**
- Bedrock (MCP Agents): $5-10 per account (pay per request)
- S3 (Data Storage): $1-2 per account
- IAM Roles: Free
- **Subtotal**: ~$12-24/month (both accounts)

**Frontend (Central Account):**
- CloudFront: $1-5
- S3 (Static hosting): $1-2
- **Subtotal**: ~$2-7/month

**Total Estimated Cost**: ~$31-65/month

**Cost Optimization:**
- Bedrock uses on-demand pricing (pay per request only)
- No ECS/Fargate costs (AgentCore is serverless)
- Delete after demo: $0
- Stop using when not needed: ~$5-10/month (storage only)

## 🧹 Cleanup

```bash
cd Centralized-Amazon-Bedrock-AgentCore-with-Distributed-MCP-Data-Sources
./scripts/cleanup-all.sh
```

This will delete:
- All AgentCore agents (orchestrator + LOB agents)
- S3 buckets in all 3 accounts
- IAM roles in all 3 accounts
- CloudFront distribution and frontend
- Local temporary files (.corp_agent_arn, .gateway_url, etc.)

## 📄 License

Apache License 2.0

## 👥 Authors

Shashi Makkapati, Senthil Kamala Rathinam, Karthik Tharmarajan

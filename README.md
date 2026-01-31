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

### Single-Account (Baseline)

![Single Account Architecture](arch/bankiq_plus_agentcore_architecture.png)

**Use Case**: Single department, all data in one account
- 1 AWS Account
- 1 Agent with 12 tools
- Direct data access
- Simple deployment

### Multi-Account (Enterprise Pattern)

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
2. **Regional Accounts**: MCP-enabled agents with LOB-owned data
3. **Cross-Account Access**: IAM roles with least-privilege
4. **MCP Protocol**: Standardized data access interface
5. **Shared Infrastructure**: Single UI/Backend for both patterns

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

**Single-Account Agent** (`backend/bank_iq_agent_v1.py`):
1. `get_fdic_data` - Live FDIC banking metrics
2. `search_fdic_bank` - Search banks by name
3. `compare_banks` - Peer performance comparison
4. `get_sec_filings` - SEC EDGAR 10-K/10-Q filings
5. `generate_bank_report` - Comprehensive analysis
6. `answer_banking_question` - General Q&A
7. `search_banks` - Bank search (500+ banks)
8. `upload_csv_to_s3` - Custom data upload
9. `analyze_csv_peer_performance` - CSV analysis
10. `analyze_and_upload_pdf` - PDF upload + analysis
11. `analyze_uploaded_pdf` - PDF deep analysis
12. `chat_with_documents` - Multi-turn document Q&A

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

## 🚀 Quick Start

### Prerequisites
- AWS Account with administrative access
- AWS Bedrock access enabled
- AWS CLI configured
- Node.js 18+, Python 3.11+
- AgentCore CLI: `pip install bedrock-agentcore-starter-toolkit`

### Deploy Single-Account (Simple)

```bash
git clone https://github.com/smakkapati-repo/multi-account-agentcore.git
cd multi-account-agentcore
./cfn/scripts/deploy-all.sh
```

**Deploy Time**: ~20-25 minutes

### Deploy Multi-Account (Enterprise)

**Prerequisites**: 3 AWS accounts with CLI profiles configured

```bash
cd multi-account-agentcore
./deploy-multi-account.sh
```

**Deploy Time**: ~30-40 minutes

## 💰 Cost Estimate

Monthly costs (24/7 operation):
- ECS Fargate: $15-20
- ALB: $16-20
- CloudFront: $1-5
- S3: $1-2
- Bedrock: $10-30

**Total**: ~$50-90/month

## 🧹 Cleanup

```bash
cd multi-account-agentcore
./cfn/scripts/cleanup.sh
```

## 📄 License

Apache License 2.0

## 👥 Authors

Shashi Makkapati, Senthil Kamala Rathinam, Jacob Scheatzle

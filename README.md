# BankIQ+ - AI Banking Analytics Platform
**Powered by [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/)**

**Authors:** Shashi Makkapati, Senthil Kamala Rathinam, Karthik Tharmarajan

> **Reference Implementation**: This project demonstrates **Amazon Bedrock AgentCore** (AWS's managed agent runtime) with two deployment patterns: **Single-Account** (simple) and **Multi-Account** (enterprise hub-and-spoke).

## 🎯 What You Get

**One Platform, Two Deployment Modes:**

### Mode 1: Single-Account (Decentralized)
- **1 AWS Account** - Everything in one place
- **1 Agent** - 12 banking tools (FDIC, SEC EDGAR, PDF analysis)
- **1 Backend** - Express.js on ECS Fargate
- **1 Frontend** - React + Material-UI on CloudFront
- **Deploy Time**: 20-25 minutes
- **Use Case**: Startups, demos, single-region operations

### Mode 2: Multi-Account (Centralized Hub-and-Spoke)
- **3 AWS Accounts** - Central hub + 2 regional child accounts
- **1 Orchestrator Agent** - Routes queries to regional agents via MCP
- **2 Child Agents** - East/West region banking data
- **Same Backend & Frontend** - Shared infrastructure
- **Deploy Time**: 30-40 minutes
- **Use Case**: Enterprises, data sovereignty, multi-region compliance

## 🏗️ Architecture Patterns

### Single-Account (Decentralized)
```
User → CloudFront → ALB → ECS Backend → AgentCore Agent (12 tools) → FDIC/SEC APIs
```
- **1 Account**: All resources in one place
- **Direct Access**: Agent directly calls FDIC/SEC APIs
- **Simple**: Easy to deploy and manage
- **Use Case**: Startups, demos, single-region

### Multi-Account (Centralized Hub-and-Spoke)
```
User → CloudFront → ALB → ECS Backend → Orchestrator Agent
                                              ↓
                        ┌─────────────────────┴─────────────────────┐
                        ↓                                           ↓
              East Child Agent (MCP)                    West Child Agent (MCP)
              Account: 891377397197                     Account: 058264155998
              Banks: JPM, BAC, C                        Banks: WFC, USB, SCHW
```
- **3 Accounts**: Central hub + 2 regional child accounts
- **MCP Protocol**: Cross-account agent communication
- **Data Sovereignty**: Each region owns its data
- **Use Case**: Enterprises, multi-region, compliance

### Key Differences

| Aspect | Single-Account | Multi-Account |
|--------|---------------|---------------|
| **Accounts** | 1 | 3 |
| **Agents** | 1 (12 tools) | 3 (orchestrator + 2 regional) |
| **Data** | Centralized | Distributed |
| **Complexity** | Low | High |
| **Cost** | Lower | Higher |
| **Compliance** | Simple | Regional boundaries |
| **Deploy Time** | 20-25 min | 30-40 min |

## 🚀 Why This Matters

### Amazon Bedrock AgentCore Benefits
- ✅ **Managed Runtime** - No infrastructure to manage
- ✅ **Built-in Memory** - Conversational context across sessions
- ✅ **Tool Orchestration** - Claude Sonnet 4.5 auto-selects tools
- ✅ **Streaming** - Real-time token streaming
- ✅ **Scalability** - Serverless auto-scaling

### Banking Analytics Use Case
Transforms raw FDIC/SEC data into conversational insights. Ask "Why is our ROA underperforming?" and get comprehensive analysis considering market conditions, peer performance, and regulatory environment.


## 📊 Agent Tools (12 Banking Tools)

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

**Multi-Account Orchestrator** (`agent-centralized/orchestrator_agent.py`):
- `query_east_region` - Query East region banks
- `query_west_region` - Query West region banks
- `compare_regions` - Cross-regional comparison

**How It Works:**
- User asks: "Compare JPMorgan and Bank of America ROA"
- Claude Sonnet 4.5 selects: `compare_banks` tool
- Agent fetches FDIC data, analyzes trends, returns insights

## 🛠️ Technology Stack

### Core AI Platform (NEW AWS Services)
- **[Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/)** - Managed agent runtime with built-in memory and tool orchestration
- **[Strands Framework](https://github.com/awslabs/agents-for-amazon-bedrock-sample-code)** - Python agent framework for defining tools and workflows
- **[Claude Sonnet 4.5](https://www.anthropic.com/claude)** - Foundation model for natural language understanding and reasoning

### Application Stack
- **Authentication**: [AWS Cognito](https://docs.aws.amazon.com/cognito/) + [AWS Amplify v6](https://aws.amazon.com/amplify/) (OAuth 2.0 + JWT)
- **Backend**: [Express.js](https://expressjs.com/) (Node.js) + Python agent
- **Frontend**: [React](https://react.dev/) + [Material-UI](https://mui.com/) + AWS Amplify Auth
- **Infrastructure**: [ECS Fargate](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html), [ALB](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/), [CloudFront](https://docs.aws.amazon.com/cloudfront/), [S3](https://docs.aws.amazon.com/s3/)
- **Security**: [VPC](https://docs.aws.amazon.com/vpc/) private subnets, JWT verification, [IAM roles](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html), [Security Groups](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html)

## 📚 Documentation

- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** - Detailed deployment steps
- **[CloudFormation Guide](docs/CLOUDFORMATION_GUIDE.md)** - Infrastructure templates
- **[Agent Development](docs/AGENT_DEVELOPMENT.md)** - Building custom tools

## ✨ Platform Features

### 📊 Peer Bank Analytics
- **500+ Banks**: Access entire SEC EDGAR database
- **Live FDIC Data**: Real-time financial metrics and trends
- **Custom CSV Upload**: Analyze your own peer data
- **AI-Powered Comparison**: Automated tool selection by Claude

### 📋 Financial Reports Analyzer
- **SEC Filings**: 10-K and 10-Q analysis for any public bank
- **Document Upload**: Analyze your own financial PDFs
- **Conversational Memory**: Context-aware across queries
- **AI Chat**: Interactive Q&A about uploaded documents

### 🔧 Analysis Modes
1. **Live FDIC**: Real-time banking metrics from FDIC Call Reports
2. **SEC EDGAR**: Direct integration with SEC.gov APIs
3. **Document Upload**: PDF analysis with metadata extraction
4. **Chat Mode**: Conversational analysis with memory










## 🚀 Deployment Guide

### Prerequisites

**Required:**
- AWS Account with administrative access
- AWS Bedrock access enabled (see setup below)
- AWS CLI configured (`aws configure`)
- Node.js 18+ (for frontend build)
- Python 3.11+ (for AgentCore CLI)
- AgentCore CLI: `pip install bedrock-agentcore-starter-toolkit`

### Install Prerequisites

**Mac/Linux:**
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install required tools
brew install awscli node python@3.11 git
pip install bedrock-agentcore-starter-toolkit
```

**Windows (PowerShell as Administrator):**
```powershell
# Install Chocolatey + all tools
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
choco install python git awscli nodejs jq -y
pip install bedrock-agentcore-starter-toolkit

# Add Python Scripts to PATH permanently (for agentcore command)
echo 'export PATH="$PATH:/d/Users/$USER/AppData/Roaming/Python/Python314/Scripts"' >> ~/.bashrc
source ~/.bashrc
```

**Enable Bedrock Access:**
1. Go to [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. Navigate to **Model Access** in the left sidebar
3. Click **Request model access**
4. Enable: **Anthropic Claude Sonnet 4.5**
5. Wait for approval (usually instant)

### Step-by-Step Deployment

**Step 1: Clone Repository**
```bash
git clone https://github.com/smakkapati-repo/multi-account-agentcore.git
cd multi-account-agentcore
```



**Step 2: Configure AWS CLI**

**Mac/Linux/Windows:**
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter region: (choose your preferred region, e.g., us-east-1, us-west-2, eu-west-1)
# Enter output format: json
```

**Step 3: Choose Your Deployment Mode**

### Option A: Single-Account (Recommended for Getting Started)

```bash
cd multi-account-agentcore
./cfn/scripts/deploy-all.sh
```

**What Gets Deployed:**
- ✅ Cognito User Pool (authentication)
- ✅ VPC + ALB + ECS Fargate (infrastructure)
- ✅ Single agent with 12 banking tools
- ✅ Express.js backend (proxies to agent)
- ✅ React frontend on CloudFront

### Option B: Multi-Account (Enterprise Hub-and-Spoke)

**Prerequisites:**
- 3 AWS accounts configured
- AWS CLI profiles: `default`, `child1`, `child2-demo`

```bash
cd multi-account-agentcore
./deploy-multi-account.sh
```

**What Gets Deployed:**
- ✅ Infrastructure in all 3 accounts
- ✅ MCP-enabled child agents (East/West)
- ✅ Orchestrator agent in central account
- ✅ Same backend/frontend (shared)

**Deployment Progress:**
- 🔵 **[0/4] Auth (Cognito)** (~2-3 minutes)
  - Creates Cognito User Pool
  - Configures OAuth 2.0 authentication
  - Sets up Hosted UI

- 🔵 **[1/4] Infrastructure** (~5-7 minutes)
  - VPC with public/private subnets
  - Application Load Balancer
  - ECS cluster
  - S3 buckets
  - ECR repositories

- 🔵 **[2/4] AgentCore Agent** (~5-7 minutes)
  - Builds and deploys Python agent with 12 tools
  - Adds S3 permissions automatically
  - Creates conversational memory

- 🔵 **[3/4] Backend** (~7-10 minutes)
  - Creates CodeBuild project
  - Uploads source to S3
  - Builds Docker image via CodeBuild
  - Pushes to ECR
  - Deploys ECS service

- 🔵 **[4/4] Frontend** (~2-3 minutes)
  - Builds React app
  - Uploads to S3
  - Creates CloudFront distribution
  - Updates Cognito callback URLs

**Total Time**: ~20-25 minutes

**Step 4: Access Your Application**

After deployment completes, you'll see:
```
✅ DEPLOYMENT COMPLETE WITH COGNITO!
🌐 Application URL: https://[your-cloudfront-url].cloudfront.net
🔐 Login URL: https://bankiq-auth-[account-id].auth.us-east-1.amazoncognito.com
```

**Next Steps:**
1. Visit the Application URL
2. Click 'Sign In with AWS Cognito'
3. Click 'Sign up' to create your account
4. Verify your email and log in

## 🔍 Verify Deployment

**Check Health:**

**Mac/Linux:**
```bash
# Get CloudFront URL
CLOUDFRONT_URL=$(aws cloudfront list-distributions --query "DistributionList.Items[?contains(Origins.Items[0].DomainName, 'bankiq-frontend')].DomainName" --output text)

# Test health endpoint
curl https://$CLOUDFRONT_URL/api/health
# Expected: {"status":"healthy","service":"BankIQ+ Backend"}
```

**Windows (PowerShell):**
```powershell
# Get CloudFront URL
$CLOUDFRONT_URL = aws cloudfront list-distributions --query "DistributionList.Items[?contains(Origins.Items[0].DomainName, 'bankiq-frontend')].DomainName" --output text

# Test health endpoint
Invoke-WebRequest -Uri "https://$CLOUDFRONT_URL/api/health"
```

**View Logs (All Platforms):**
```bash
# ECS backend logs
aws logs start-live-tail --log-group-identifiers /ecs/bankiq-backend

# AgentCore logs
agentcore status
```

## ⚡ Performance & Caching

BankIQ+ uses **node-cache** for in-memory caching to dramatically improve performance:

- **SEC Filings**: 2000ms → 1ms (24 hour cache)
- **Bank Search**: 500ms → 1ms (7 day cache)
- **FDIC Data**: 1500ms → 1ms (1 hour cache)

**Cache Management:**
```bash
# View cache statistics
curl http://localhost:3001/api/admin/cache-stats

# Clear all caches
curl -X POST http://localhost:3001/api/admin/clear-cache \
  -H "Content-Type: application/json" \
  -d '{"type": "all"}'
```

## 💰 Cost Estimate

Monthly costs (24/7 operation):
- ECS Fargate: $15-20
- ALB: $16-20
- CloudFront: $1-5
- S3: $1-2
- Bedrock: $10-30

**Total**: ~$50-90/month



## 🧹 Cleanup

To delete all resources:

**Mac/Linux/Windows:**
```bash
# IMPORTANT: Run from project root directory
cd multi-account-agentcore
./cfn/scripts/cleanup.sh
```

This will remove:
- ✅ CloudFormation stacks (frontend, backend, infrastructure, auth)
- ✅ Cognito User Pool and all users
- ✅ S3 buckets (with contents)
- ✅ ECR images and repositories
- ✅ ECS cluster and services
- ✅ CloudFront distribution
- ✅ AgentCore agent
- ✅ All associated resources

**Time**: ~10-15 minutes

## 📝 Monitoring

**All Platforms:**
```bash
# View ECS logs
aws logs tail /ecs/bankiq-backend --follow

# View AgentCore logs (run from backend directory)
cd backend && agentcore status
```



## 🆘 Troubleshooting

**Issue**: CloudFront returns 502
- Check ECS task health
- Check ALB target health
- View logs: `aws logs start-live-tail --log-group-identifiers /ecs/bankiq-backend`

**Issue**: Agent not responding
- Check AgentCore status: `cd backend && agentcore status`
- Verify agent ARN in ECS task environment variables

For detailed troubleshooting, see the [Deployment Guide](docs/DEPLOYMENT_GUIDE.md).

## 📄 License

Apache License 2.0

## 👥 Authors

Shashi Makkapati, Senthil Kamala Rathinam, Jacob Scheatzle

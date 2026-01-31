#!/bin/bash
set -e

echo "=========================================================================="
echo "Multi-Account AgentCore Deployment with MCP"
echo "=========================================================================="
echo ""
echo "This script will deploy:"
echo "  1. Infrastructure in all 3 accounts (S3, IAM, KBs)"
echo "  2. MCP-enabled agents in child accounts"
echo "  3. Orchestrator agent in central account"
echo "  4. Backend and frontend"
echo ""
echo "=========================================================================="
echo ""

# Check prerequisites
echo "🔍 Checking prerequisites..."
command -v python3 >/dev/null 2>&1 || { echo "❌ python3 required but not installed"; exit 1; }
command -v aws >/dev/null 2>&1 || { echo "❌ AWS CLI required but not installed"; exit 1; }
command -v agentcore >/dev/null 2>&1 || { echo "❌ agentcore CLI required. Install: pip install bedrock-agentcore-starter-toolkit"; exit 1; }
echo "✅ All prerequisites met"
echo ""

# Phase 1: Setup infrastructure in all accounts
echo "=========================================================================="
echo "Phase 1: Multi-Account Infrastructure Setup"
echo "=========================================================================="
echo ""

echo "📦 Setting up Central Account infrastructure..."
python3 infra/setup_accounts.py central
echo ""

echo "📦 Setting up East Region (Child 1) infrastructure..."
python3 infra/setup_accounts.py east_region
echo ""

echo "📦 Setting up West Region (Child 2) infrastructure..."
python3 infra/setup_accounts.py west_region
echo ""

# Phase 2: Deploy MCP-enabled agents to child accounts
echo "=========================================================================="
echo "Phase 2: Deploy MCP-Enabled Agents to Child Accounts"
echo "=========================================================================="
echo ""

echo "🚀 Deploying East Region MCP Agent..."
cd agent-child-east
AWS_PROFILE=child1 agentcore deploy --enable-mcp
EAST_AGENT_ARN=$(AWS_PROFILE=child1 agentcore status | grep "agent_arn" | cut -d'"' -f4)
echo "✅ East Agent ARN: $EAST_AGENT_ARN"
cd ..
echo ""

echo "🚀 Deploying West Region MCP Agent..."
cd agent-child-west
AWS_PROFILE=child2-demo agentcore deploy --enable-mcp
WEST_AGENT_ARN=$(AWS_PROFILE=child2-demo agentcore status | grep "agent_arn" | cut -d'"' -f4)
echo "✅ West Agent ARN: $WEST_AGENT_ARN"
cd ..
echo ""

# Phase 3: Deploy orchestrator agent to central account
echo "=========================================================================="
echo "Phase 3: Deploy Orchestrator Agent to Central Account"
echo "=========================================================================="
echo ""

echo "🚀 Deploying Central Orchestrator Agent..."
cd agent-centralized
# Set environment variables for child agent ARNs
export EAST_AGENT_ARN=$EAST_AGENT_ARN
export WEST_AGENT_ARN=$WEST_AGENT_ARN
agentcore deploy
ORCHESTRATOR_ARN=$(agentcore status | grep "agent_arn" | cut -d'"' -f4)
echo "✅ Orchestrator ARN: $ORCHESTRATOR_ARN"
echo ""

echo "🌐 Deploying AgentCore Gateway..."
agentcore gateway deploy
GATEWAY_URL=$(agentcore gateway status | grep "api_endpoint" | cut -d'"' -f4)
echo "✅ Gateway URL: $GATEWAY_URL"
cd ..
echo ""

# Phase 4: Deploy backend and frontend (reuse existing scripts)
echo "=========================================================================="
echo "Phase 4: Deploy Backend and Frontend"
echo "=========================================================================="
echo ""

echo "🚀 Running existing deployment scripts..."
./cfn/scripts/deploy-all.sh

echo ""
echo "=========================================================================="
echo "✅ MULTI-ACCOUNT DEPLOYMENT COMPLETE!"
echo "=========================================================================="
echo ""
echo "📋 Deployment Summary:"
echo "  Central Account: 164543933824"
echo "    - Orchestrator Agent: $ORCHESTRATOR_ARN"
echo "    - Gateway URL: $GATEWAY_URL"
echo ""
echo "  East Region: 891377397197"
echo "    - MCP Agent: $EAST_AGENT_ARN"
echo "    - S3 Bucket: east-region-banking-891377397197"
echo ""
echo "  West Region: 058264155998"
echo "    - MCP Agent: $WEST_AGENT_ARN"
echo "    - S3 Bucket: west-region-banking-058264155998"
echo ""
echo "🌐 Access your application at the CloudFront URL shown above"
echo ""
echo "=========================================================================="

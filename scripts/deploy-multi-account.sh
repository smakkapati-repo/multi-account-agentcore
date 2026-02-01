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

echo "📦 Setting up Corporate Banking LOB infrastructure..."
python3 infra/setup_accounts.py corporate_banking
echo ""

echo "📦 Setting up Treasury & Risk LOB infrastructure..."
python3 infra/setup_accounts.py treasury_risk
echo ""

# Phase 2: Deploy MCP-enabled agents to child accounts
echo "=========================================================================="
echo "Phase 2: Deploy MCP-Enabled Agents to Child Accounts"
echo "=========================================================================="
echo ""

echo "🚀 Deploying Corporate Banking MCP Agent..."
cd agent-corporate-banking
AWS_PROFILE=child1 agentcore deploy --enable-mcp
CORPORATE_BANKING_AGENT_ARN=$(AWS_PROFILE=child1 agentcore status | grep "agent_arn" | cut -d'"' -f4)
echo "✅ Corporate Banking Agent ARN: $CORPORATE_BANKING_AGENT_ARN"
cd ..
echo ""

echo "🚀 Deploying Treasury & Risk MCP Agent..."
cd agent-treasury-risk
AWS_PROFILE=child2-demo agentcore deploy --enable-mcp
TREASURY_RISK_AGENT_ARN=$(AWS_PROFILE=child2-demo agentcore status | grep "agent_arn" | cut -d'"' -f4)
echo "✅ Treasury & Risk Agent ARN: $TREASURY_RISK_AGENT_ARN"
cd ..
echo ""

# Phase 3: Deploy orchestrator agent to central account
echo "=========================================================================="
echo "Phase 3: Deploy Orchestrator Agent to Central Account"
echo "=========================================================================="
echo ""

echo "🚀 Deploying Central Orchestrator Agent..."
cd agent-orchestrator
# Set environment variables for LOB agent ARNs
export CORPORATE_BANKING_AGENT_ARN=$CORPORATE_BANKING_AGENT_ARN
export TREASURY_RISK_AGENT_ARN=$TREASURY_RISK_AGENT_ARN
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
echo "  Corporate Banking LOB: 891377397197"
echo "    - MCP Agent: $CORPORATE_BANKING_AGENT_ARN"
echo "    - S3 Bucket: corporate-banking-891377397197"
echo ""
echo "  Treasury & Risk LOB: 058264155998"
echo "    - MCP Agent: $TREASURY_RISK_AGENT_ARN"
echo "    - S3 Bucket: treasury-risk-058264155998"
echo ""
echo "🌐 Access your application at the CloudFront URL shown above"
echo ""
echo "=========================================================================="

#!/bin/bash
# Quick Start Script for Multi-Account POC
# Runs all setup steps in sequence

set -e  # Exit on error

echo "=========================================="
echo "Multi-Account POC - Quick Start"
echo "=========================================="
echo ""

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.11+"
    exit 1
fi

if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install AWS CLI"
    exit 1
fi

if ! command -v agentcore &> /dev/null; then
    echo "❌ AgentCore CLI not found. Install with: pip install bedrock-agentcore-starter-toolkit"
    exit 1
fi

echo "✅ Prerequisites OK"
echo ""

# Phase 1: Data Collection
echo "=========================================="
echo "Phase 1: Data Collection"
echo "=========================================="
echo ""

echo "📄 Fetching SEC financial data..."
python3 scripts/fetch_sec_data.py

echo ""
echo "🌍 Fetching trade risk data..."
python3 scripts/fetch_trade_data.py

echo ""
echo "✅ Phase 1 Complete"
echo ""

# Phase 2: Infrastructure Setup
echo "=========================================="
echo "Phase 2: Infrastructure Setup"
echo "=========================================="
echo ""

echo "🏗️  Setting up Child1 account..."
python3 infra/setup_child1.py

echo ""
echo "🏗️  Setting up Child2-Demo account..."
python3 infra/setup_child2.py

echo ""
echo "🏗️  Setting up Central account..."
python3 infra/setup_central.py

echo ""
echo "✅ Phase 2 Complete"
echo ""

# Wait for OpenSearch collections
echo "=========================================="
echo "Waiting for OpenSearch Collections"
echo "=========================================="
echo ""
echo "⏳ OpenSearch Serverless collections take 3-5 minutes to become active"
echo "   You can check status with:"
echo "   - aws opensearchserverless list-collections --profile child1"
echo "   - aws opensearchserverless list-collections --profile child2-demo"
echo ""
read -p "Press Enter when collections are ACTIVE..."

# Phase 3: Deploy Agent
echo ""
echo "=========================================="
echo "Phase 3: Deploy Agent"
echo "=========================================="
echo ""

cd agent

# Set environment variable for role ARN
export AGENTCORE_ROLE_ARN=$(cat ../infra/central_config.json | python3 -c "import sys, json; print(json.load(sys.stdin)['agentcore_role_arn'])")

echo "🤖 Deploying AgentCore agent..."
agentcore deploy

echo ""
echo "✅ Phase 3 Complete"
echo ""

cd ..

# Phase 4: Test
echo "=========================================="
echo "Phase 4: Test"
echo "=========================================="
echo ""

echo "🧪 Testing agent..."
cd agent
agentcore invoke '{"prompt": "What companies do you have data for?"}'

echo ""
echo "=========================================="
echo "✅ Multi-Account POC Setup Complete!"
echo "=========================================="
echo ""
echo "🎉 Your multi-account agent is ready!"
echo ""
echo "Try these queries:"
echo "  agentcore invoke '{\"prompt\": \"Assess risk for Apple Inc\"}'"
echo "  agentcore invoke '{\"prompt\": \"What are China'\''s trade risks?\"}'"
echo "  agentcore invoke '{\"prompt\": \"Show me Microsoft'\''s financial health\"}'"
echo ""
echo "📊 Architecture:"
echo "  - Central Account (164543933824): AgentCore orchestration"
echo "  - Child1 (891377397197): Financial KB"
echo "  - Child2-Demo (058264155998): Trade Risk KB"
echo ""

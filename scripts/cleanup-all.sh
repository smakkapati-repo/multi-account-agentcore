#!/bin/bash
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║              LoanIQ - Complete Cleanup                        ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

echo -e "${YELLOW}⚠️  WARNING: This will delete ALL LoanIQ resources${NC}"
echo ""
read -p "Are you sure you want to continue? (type 'yes' to confirm): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Cleanup cancelled"
    exit 0
fi

# Load config
if [ ! -f "infra/accounts_config.json" ]; then
    echo -e "${RED}❌ Configuration file not found: infra/accounts_config.json${NC}"
    exit 1
fi

CENTRAL_ACCOUNT=$(python3 -c "import json; print(json.load(open('infra/accounts_config.json'))['central']['account_id'])")
CENTRAL_PROFILE=$(python3 -c "import json; print(json.load(open('infra/accounts_config.json'))['central']['profile'])")
CORP_ACCOUNT=$(python3 -c "import json; print(json.load(open('infra/accounts_config.json'))['children'][0]['account_id'])")
CORP_PROFILE=$(python3 -c "import json; print(json.load(open('infra/accounts_config.json'))['children'][0]['profile'])")
RISK_ACCOUNT=$(python3 -c "import json; print(json.load(open('infra/accounts_config.json'))['children'][1]['account_id'])")
RISK_PROFILE=$(python3 -c "import json; print(json.load(open('infra/accounts_config.json'))['children'][1]['profile'])")

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "Phase 1: Delete Frontend (CloudFront + S3)"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Delete CloudFront stack
echo "🗑️  Deleting CloudFront stack..."
aws cloudformation delete-stack --stack-name loaniq-frontend --profile $CENTRAL_PROFILE 2>/dev/null || echo "Stack not found"
echo "✅ CloudFront stack deletion initiated"

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "Phase 2: Delete Orchestrator Agent + Gateway"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""

echo "🗑️  Deleting Orchestrator Agent..."
cd agents/agent-orchestrator
AWS_PROFILE=$CENTRAL_PROFILE agentcore destroy 2>/dev/null || echo "Agent not found"
cd ../..
echo "✅ Orchestrator Agent deleted"

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "Phase 3: Delete LOB Agents"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""

echo "🗑️  Deleting Corporate Banking Agent..."
cd agents/agent-corporate-banking
AWS_PROFILE=$CORP_PROFILE agentcore destroy 2>/dev/null || echo "Agent not found"
cd ../..
echo "✅ Corporate Banking Agent deleted"

echo "🗑️  Deleting Treasury & Risk Agent..."
cd agents/agent-treasury-risk
AWS_PROFILE=$RISK_PROFILE agentcore destroy 2>/dev/null || echo "Agent not found"
cd ../..
echo "✅ Treasury & Risk Agent deleted"

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "Phase 4: Delete S3 Buckets"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Central account
CENTRAL_BUCKET="agentcore-multiaccountpoc-$CENTRAL_ACCOUNT"
echo "🗑️  Deleting central S3 bucket: $CENTRAL_BUCKET"
aws s3 rb s3://$CENTRAL_BUCKET --force --profile $CENTRAL_PROFILE 2>/dev/null || echo "Bucket not found"
echo "✅ Central bucket deleted"

# Corporate Banking
CORP_BUCKET="corporate-banking-$CORP_ACCOUNT"
echo "🗑️  Deleting Corporate Banking S3 bucket: $CORP_BUCKET"
aws s3 rb s3://$CORP_BUCKET --force --profile $CORP_PROFILE 2>/dev/null || echo "Bucket not found"
echo "✅ Corporate Banking bucket deleted"

# Treasury & Risk
RISK_BUCKET="treasury-risk-$RISK_ACCOUNT"
echo "🗑️  Deleting Treasury & Risk S3 bucket: $RISK_BUCKET"
aws s3 rb s3://$RISK_BUCKET --force --profile $RISK_PROFILE 2>/dev/null || echo "Bucket not found"
echo "✅ Treasury & Risk bucket deleted"

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "Phase 5: Delete IAM Roles"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Central account roles
echo "🗑️  Deleting central account IAM roles..."
aws iam delete-role-policy --role-name AgentCoreMultiAccountRole --policy-name AgentCoreMultiAccountRolePolicy --profile $CENTRAL_PROFILE 2>/dev/null || true
aws iam delete-role --role-name AgentCoreMultiAccountRole --profile $CENTRAL_PROFILE 2>/dev/null || echo "Role not found"
echo "✅ Central account roles deleted"

# Corporate Banking roles
echo "🗑️  Deleting Corporate Banking IAM roles..."
aws iam delete-role-policy --role-name CentralAccountAccessRole --policy-name CentralAccountAccessRolePolicy --profile $CORP_PROFILE 2>/dev/null || true
aws iam delete-role --role-name CentralAccountAccessRole --profile $CORP_PROFILE 2>/dev/null || echo "Role not found"
aws iam delete-role-policy --role-name AgentCoreCorporateBankingRole --policy-name AgentCoreCorporateBankingRolePolicy --profile $CORP_PROFILE 2>/dev/null || true
aws iam delete-role --role-name AgentCoreCorporateBankingRole --profile $CORP_PROFILE 2>/dev/null || echo "Role not found"
echo "✅ Corporate Banking roles deleted"

# Treasury & Risk roles
echo "🗑️  Deleting Treasury & Risk IAM roles..."
aws iam delete-role-policy --role-name CentralAccountAccessRole --policy-name CentralAccountAccessRolePolicy --profile $RISK_PROFILE 2>/dev/null || true
aws iam delete-role --role-name CentralAccountAccessRole --profile $RISK_PROFILE 2>/dev/null || echo "Role not found"
aws iam delete-role-policy --role-name AgentCoreTreasuryRiskRole --policy-name AgentCoreTreasuryRiskRolePolicy --profile $RISK_PROFILE 2>/dev/null || true
aws iam delete-role --role-name AgentCoreTreasuryRiskRole --profile $RISK_PROFILE 2>/dev/null || echo "Role not found"
echo "✅ Treasury & Risk roles deleted"

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "Phase 6: Clean Local Files"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""

echo "🗑️  Removing local temporary files..."
rm -f .corp_agent_arn .risk_agent_arn .gateway_url .cloudfront_url
rm -f infra/central_config.json infra/corporate_banking_config.json infra/treasury_risk_config.json
rm -f agents/agent-orchestrator/agentcore.yaml.bak
echo "✅ Local files cleaned"

echo ""
echo -e "${GREEN}✅ Cleanup Complete!${NC}"
echo ""
echo -e "${YELLOW}Note: CloudFront deletion may take 15-30 minutes to complete${NC}"
echo ""

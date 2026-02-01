#!/bin/bash
set -e

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Change to project root (parent of scripts directory)
cd "$SCRIPT_DIR/.."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║              LoanIQ - Configuration Setup                     ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

echo -e "${WHITE}This script will configure your AWS accounts for LoanIQ deployment.${NC}"
echo ""
echo -e "${YELLOW}You will need:${NC}"
echo "  • 3 AWS Account IDs"
echo "  • AWS CLI profiles configured for each account"
echo ""

# Get Central Account
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${WHITE}Central Account (Orchestrator)${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
read -p "Enter Central Account ID (12 digits): " CENTRAL_ACCOUNT
read -p "Enter AWS CLI profile name for Central Account [default]: " CENTRAL_PROFILE
CENTRAL_PROFILE=${CENTRAL_PROFILE:-default}

# Verify profile
if ! aws sts get-caller-identity --profile $CENTRAL_PROFILE &>/dev/null; then
    echo -e "${YELLOW}⚠️  Profile '$CENTRAL_PROFILE' not configured or invalid${NC}"
    echo "Configure it with: aws configure --profile $CENTRAL_PROFILE"
    exit 1
fi

VERIFIED_CENTRAL=$(aws sts get-caller-identity --profile $CENTRAL_PROFILE --query Account --output text)
if [ "$VERIFIED_CENTRAL" != "$CENTRAL_ACCOUNT" ]; then
    echo -e "${YELLOW}⚠️  Profile '$CENTRAL_PROFILE' is for account $VERIFIED_CENTRAL, not $CENTRAL_ACCOUNT${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Central Account verified: $CENTRAL_ACCOUNT${NC}"
echo ""

# Get Corporate Banking Account
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${WHITE}Corporate Banking LOB${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
read -p "Enter Corporate Banking Account ID (12 digits): " CORP_ACCOUNT
read -p "Enter AWS CLI profile name for Corporate Banking [child1]: " CORP_PROFILE
CORP_PROFILE=${CORP_PROFILE:-child1}

if ! aws sts get-caller-identity --profile $CORP_PROFILE &>/dev/null; then
    echo -e "${YELLOW}⚠️  Profile '$CORP_PROFILE' not configured or invalid${NC}"
    echo "Configure it with: aws configure --profile $CORP_PROFILE"
    exit 1
fi

VERIFIED_CORP=$(aws sts get-caller-identity --profile $CORP_PROFILE --query Account --output text)
if [ "$VERIFIED_CORP" != "$CORP_ACCOUNT" ]; then
    echo -e "${YELLOW}⚠️  Profile '$CORP_PROFILE' is for account $VERIFIED_CORP, not $CORP_ACCOUNT${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Corporate Banking Account verified: $CORP_ACCOUNT${NC}"
echo ""

# Get Treasury & Risk Account
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${WHITE}Treasury & Risk LOB${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
read -p "Enter Treasury & Risk Account ID (12 digits): " RISK_ACCOUNT
read -p "Enter AWS CLI profile name for Treasury & Risk [child2-demo]: " RISK_PROFILE
RISK_PROFILE=${RISK_PROFILE:-child2-demo}

if ! aws sts get-caller-identity --profile $RISK_PROFILE &>/dev/null; then
    echo -e "${YELLOW}⚠️  Profile '$RISK_PROFILE' not configured or invalid${NC}"
    echo "Configure it with: aws configure --profile $RISK_PROFILE"
    exit 1
fi

VERIFIED_RISK=$(aws sts get-caller-identity --profile $RISK_PROFILE --query Account --output text)
if [ "$VERIFIED_RISK" != "$RISK_ACCOUNT" ]; then
    echo -e "${YELLOW}⚠️  Profile '$RISK_PROFILE' is for account $VERIFIED_RISK, not $RISK_ACCOUNT${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Treasury & Risk Account verified: $RISK_ACCOUNT${NC}"
echo ""

# Update accounts_config.json
echo -e "${BLUE}▶ Updating configuration...${NC}"

cat > infra/accounts_config.json <<EOF
{
  "central": {
    "account_id": "$CENTRAL_ACCOUNT",
    "profile": "$CENTRAL_PROFILE",
    "region": "us-east-1",
    "agentcore_role_name": "AgentCoreMultiAccountRole",
    "s3_bucket_prefix": "agentcore-multiaccountpoc"
  },
  "children": [
    {
      "id": "corporate_banking",
      "account_id": "$CORP_ACCOUNT",
      "profile": "$CORP_PROFILE",
      "name": "Corporate Banking LOB",
      "description": "Corporate customer relationships and loan exposure (JPMorgan, Bank of America, Citigroup)",
      "s3_bucket_prefix": "corporate-banking",
      "iam_role_name": "CentralAccountAccessRole",
      "opensearch_collection_name": "corporate-banking-kb",
      "data_directory": "data/corporate_banking"
    },
    {
      "id": "treasury_risk",
      "account_id": "$RISK_ACCOUNT",
      "profile": "$RISK_PROFILE",
      "name": "Treasury & Risk LOB",
      "description": "Treasury positions and risk models (Wells Fargo, U.S. Bank, Charles Schwab)",
      "s3_bucket_prefix": "treasury-risk",
      "iam_role_name": "CentralAccountAccessRole",
      "opensearch_collection_name": "treasury-risk-kb",
      "data_directory": "data/treasury_risk"
    }
  ]
}
EOF

echo -e "${GREEN}✅ Configuration saved to infra/accounts_config.json${NC}"
echo ""

# Summary
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${WHITE}Configuration Summary${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${WHITE}Central Account:${NC}"
echo "  Account ID: $CENTRAL_ACCOUNT"
echo "  Profile: $CENTRAL_PROFILE"
echo ""
echo -e "${WHITE}Corporate Banking LOB:${NC}"
echo "  Account ID: $CORP_ACCOUNT"
echo "  Profile: $CORP_PROFILE"
echo ""
echo -e "${WHITE}Treasury & Risk LOB:${NC}"
echo "  Account ID: $RISK_ACCOUNT"
echo "  Profile: $RISK_PROFILE"
echo ""
echo -e "${GREEN}✅ Configuration complete!${NC}"
echo ""
echo -e "${YELLOW}Next step: Run ./deploy-all.sh to deploy LoanIQ${NC}"
echo ""

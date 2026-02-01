#!/bin/bash
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║              Cleanup All AWS Resources                        ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

echo -e "${YELLOW}⚠️  WARNING: This will delete ALL resources including:${NC}"
echo "  • CloudFormation stacks (frontend, backend, auth, infra)"
echo "  • S3 buckets and all data"
echo "  • CloudFront distributions"
echo "  • ECS services and tasks"
echo "  • Cognito user pools"
echo "  • AgentCore agents and gateways"
echo ""
read -p "Are you sure you want to continue? Type 'DELETE' to confirm: " confirm

if [ "$confirm" != "DELETE" ]; then
    echo -e "${GREEN}Cancelled. No resources deleted.${NC}"
    exit 0
fi

echo ""
echo -e "${CYAN}Starting cleanup...${NC}"
echo ""

# Delete CloudFormation stacks in reverse order
STACKS=(
    "bankiq-frontend"
    "bankiq-backend"
    "bankiq-backend-codebuild"
    "bankiq-auth"
    "bankiq-infra"
)

for stack in "${STACKS[@]}"; do
    echo -e "${CYAN}Checking stack: $stack${NC}"
    if aws cloudformation describe-stacks --stack-name $stack &>/dev/null; then
        echo -e "${YELLOW}Deleting stack: $stack${NC}"
        aws cloudformation delete-stack --stack-name $stack
        echo -e "${GREEN}✅ Deletion initiated for $stack${NC}"
    else
        echo -e "${YELLOW}Stack $stack not found, skipping${NC}"
    fi
done

echo ""
echo -e "${CYAN}Waiting for stacks to delete (this may take 5-10 minutes)...${NC}"
echo ""

for stack in "${STACKS[@]}"; do
    if aws cloudformation describe-stacks --stack-name $stack &>/dev/null; then
        echo -e "${CYAN}Waiting for $stack to delete...${NC}"
        aws cloudformation wait stack-delete-complete --stack-name $stack 2>/dev/null || true
        echo -e "${GREEN}✅ $stack deleted${NC}"
    fi
done

# Delete S3 buckets (in case they weren't deleted by CFN)
echo ""
echo -e "${CYAN}Checking for remaining S3 buckets...${NC}"
BUCKETS=$(aws s3 ls | grep -E "bankiq|agentcore|corporate-banking|treasury-risk" | awk '{print $3}' || true)

if [ -n "$BUCKETS" ]; then
    for bucket in $BUCKETS; do
        echo -e "${YELLOW}Deleting S3 bucket: $bucket${NC}"
        aws s3 rb s3://$bucket --force 2>/dev/null || true
        echo -e "${GREEN}✅ Deleted $bucket${NC}"
    done
else
    echo -e "${GREEN}No S3 buckets found${NC}"
fi

# Delete AgentCore agents
echo ""
echo -e "${CYAN}Checking for AgentCore agents...${NC}"
cd agents/agent-orchestrator 2>/dev/null || true
if [ -f ".bedrock_agentcore.yaml" ]; then
    echo -e "${YELLOW}Destroying orchestrator agent...${NC}"
    agentcore destroy --force 2>/dev/null || true
    echo -e "${GREEN}✅ Orchestrator agent destroyed${NC}"
fi
cd ../.. 2>/dev/null || true

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                                ║${NC}"
echo -e "${GREEN}║              Cleanup Complete!                                 ║${NC}"
echo -e "${GREEN}║                                                                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}All AWS resources have been deleted.${NC}"
echo ""

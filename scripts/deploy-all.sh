#!/bin/bash
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Emojis
CHECK="✅"
ROCKET="🚀"
PACKAGE="📦"
LOCK="🔐"
UPLOAD="📤"
CLOUD="☁️"
GLOBE="🌐"
WRENCH="🔧"
SPARKLES="✨"

# Banner
print_banner() {
    echo -e "${PURPLE}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                                                                ║"
    echo "║              LoanIQ - Multi-Account Deployment                ║"
    echo "║         Distributed Credit Risk Platform with MCP             ║"
    echo "║                                                                ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Section header
print_section() {
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${WHITE}$1${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
}

# Step
print_step() {
    echo -e "${BLUE}▶ $1${NC}"
}

# Success
print_success() {
    echo -e "${GREEN}${CHECK} $1${NC}"
}

# Warning
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Error
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Info
print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

# Prompt for confirmation
confirm() {
    echo -e "${YELLOW}$1 (y/n)${NC} "
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        print_warning "Skipped by user"
        return 1
    fi
    return 0
}

# Check prerequisites
check_prerequisites() {
    print_section "${WRENCH} Checking Prerequisites"
    
    local all_good=true
    
    # Check Python
    print_step "Checking Python 3..."
    if command -v python3 &> /dev/null; then
        print_success "Python 3 found: $(python3 --version)"
    else
        print_error "Python 3 not found"
        all_good=false
    fi
    
    # Check AWS CLI
    print_step "Checking AWS CLI..."
    if command -v aws &> /dev/null; then
        print_success "AWS CLI found: $(aws --version)"
    else
        print_error "AWS CLI not found"
        all_good=false
    fi
    
    # Check AgentCore CLI
    print_step "Checking AgentCore CLI..."
    if command -v agentcore &> /dev/null; then
        print_success "AgentCore CLI found"
    else
        print_error "AgentCore CLI not found. Install: pip install bedrock-agentcore-starter-toolkit"
        all_good=false
    fi
    
    # Check Node.js
    print_step "Checking Node.js..."
    if command -v node &> /dev/null; then
        print_success "Node.js found: $(node --version)"
    else
        print_error "Node.js not found"
        all_good=false
    fi
    
    # Check AWS profiles
    print_step "Checking AWS profiles..."
    if aws configure list --profile default &> /dev/null; then
        print_success "Profile 'default' configured"
    else
        print_warning "Profile 'default' not configured"
    fi
    
    if aws configure list --profile child1 &> /dev/null; then
        print_success "Profile 'child1' configured"
    else
        print_warning "Profile 'child1' not configured"
    fi
    
    if aws configure list --profile child2-demo &> /dev/null; then
        print_success "Profile 'child2-demo' configured"
    else
        print_warning "Profile 'child2-demo' not configured"
    fi
    
    if [ "$all_good" = false ]; then
        print_error "Prerequisites check failed. Please install missing tools."
        exit 1
    fi
    
    print_success "All prerequisites met!"
}

# Phase 1: Infrastructure Setup
setup_infrastructure() {
    print_section "${PACKAGE} Phase 1: Infrastructure Setup (S3 + IAM + Data)"
    
    # Generate synthetic data first
    print_step "Generating synthetic data..."
    python3 data/generate_synthetic_data.py
    print_success "Synthetic data generated"
    print_info "Created: customer_loans.json, risk_models.json"
    
    if confirm "Setup infrastructure in all 3 AWS accounts?"; then
        print_step "Setting up Central Account (164543933824)..."
        python3 infra/setup_accounts.py central
        print_success "Central account setup complete"
        
        print_step "Setting up Corporate Banking LOB (891377397197)..."
        python3 infra/setup_accounts.py corporate_banking
        print_success "Corporate Banking LOB setup complete"
        
        print_step "Setting up Treasury & Risk LOB (058264155998)..."
        python3 infra/setup_accounts.py treasury_risk
        print_success "Treasury & Risk LOB setup complete"
        
        print_success "Infrastructure setup complete!"
        print_info "Created: S3 buckets, IAM roles, uploaded data files"
    fi
}

# Phase 2: Deploy LOB Agents
deploy_lob_agents() {
    print_section "${ROCKET} Phase 2: Deploy LOB Agents (MCP Servers)"
    
    if confirm "Deploy Corporate Banking Agent?"; then
        print_step "Deploying Corporate Banking Agent to account 891377397197..."
        cd agents/agent-corporate-banking
        AWS_PROFILE=child1 agentcore launch
        CORP_AGENT_ARN=$(AWS_PROFILE=child1 agentcore status | grep "agent_arn" | cut -d'"' -f4 || echo "")
        cd ../..
        print_success "Corporate Banking Agent deployed"
        print_info "Agent ARN: $CORP_AGENT_ARN"
        echo "$CORP_AGENT_ARN" > .corp_agent_arn
    fi
    
    if confirm "Deploy Treasury & Risk Agent?"; then
        print_step "Deploying Treasury & Risk Agent to account 058264155998..."
        cd agents/agent-treasury-risk
        AWS_PROFILE=child2-demo agentcore launch
        RISK_AGENT_ARN=$(AWS_PROFILE=child2-demo agentcore status | grep "agent_arn" | cut -d'"' -f4 || echo "")
        cd ../..
        print_success "Treasury & Risk Agent deployed"
        print_info "Agent ARN: $RISK_AGENT_ARN"
        echo "$RISK_AGENT_ARN" > .risk_agent_arn
    fi
}

# Phase 3: Deploy Orchestrator + Gateway
deploy_orchestrator() {
    print_section "${CLOUD} Phase 3: Deploy Orchestrator + Gateway (MCP Client)"
    
    if confirm "Deploy Orchestrator Agent with Gateway?"; then
        # Set environment variables for LOB agent ARNs
        if [ -f .corp_agent_arn ]; then
            export CORPORATE_BANKING_AGENT_ARN=$(cat .corp_agent_arn)
            print_info "Using Corporate Banking Agent ARN: $CORPORATE_BANKING_AGENT_ARN"
        fi
        
        if [ -f .risk_agent_arn ]; then
            export TREASURY_RISK_AGENT_ARN=$(cat .risk_agent_arn)
            print_info "Using Treasury & Risk Agent ARN: $TREASURY_RISK_AGENT_ARN"
        fi
        
        print_step "Deploying Orchestrator Agent to central account..."
        cd agents/agent-orchestrator
        agentcore launch
        print_success "Orchestrator Agent deployed"
        
        print_step "Deploying AgentCore Gateway..."
        agentcore gateway deploy
        GATEWAY_URL=$(agentcore gateway status | grep "api_endpoint" | cut -d'"' -f4 || echo "")
        cd ../..
        print_success "Gateway deployed"
        print_info "Gateway URL: $GATEWAY_URL"
        echo "$GATEWAY_URL" > .gateway_url
    fi
}

# Phase 4: Deploy Frontend
deploy_frontend() {
    print_section "${GLOBE} Phase 4: Deploy Frontend (CloudFront + S3)"
    
    if confirm "Deploy CloudFront + S3 infrastructure?"; then
        print_step "Deploying CloudFormation stack..."
        aws cloudformation deploy \
            --template-file cfn/templates/frontend.yaml \
            --stack-name loaniq-frontend \
            --parameter-overrides ProjectName=loaniq \
            --capabilities CAPABILITY_IAM
        print_success "CloudFront + S3 infrastructure deployed"
        
        CLOUDFRONT_DIST_ID=$(aws cloudformation describe-stacks --stack-name loaniq-frontend --query "Stacks[0].Outputs[?OutputKey=='CloudFrontDistributionId'].OutputValue" --output text)
        S3_BUCKET=$(aws cloudformation describe-stacks --stack-name loaniq-frontend --query "Stacks[0].Outputs[?OutputKey=='FrontendBucket'].OutputValue" --output text)
        CLOUDFRONT_URL=$(aws cloudformation describe-stacks --stack-name loaniq-frontend --query "Stacks[0].Outputs[?OutputKey=='ApplicationUrl'].OutputValue" --output text)
        
        print_info "CloudFront URL: $CLOUDFRONT_URL"
        print_info "S3 Bucket: $S3_BUCKET (private)"
    fi
    
    if [ ! -f .gateway_url ]; then
        print_warning "Gateway URL not found. Skipping frontend build."
        print_info "Deploy gateway first, then run this script again."
        return
    fi
    
    GATEWAY_URL=$(cat .gateway_url)
    
    if confirm "Build and deploy React app?"; then
        print_step "Installing frontend dependencies..."
        cd frontend
        if [ ! -d "node_modules" ]; then
            npm install
            print_success "Dependencies installed"
        else
            print_info "Dependencies already installed"
        fi
        
        print_step "Configuring Gateway URL..."
        echo "REACT_APP_GATEWAY_URL=$GATEWAY_URL" > .env
        cd ..
        print_success "Gateway URL configured"
        
        print_step "Building React app..."
        cd frontend
        npm run build
        cd ..
        print_success "React app built"
        
        print_step "Deploying to CloudFront..."
        ./deploy-frontend.sh
        print_success "Frontend deployed"
    fi
}

# Summary
print_summary() {
    print_section "${SPARKLES} Deployment Summary"
    
    echo -e "${WHITE}Accounts:${NC}"
    echo -e "  ${CYAN}Central (164543933824)${NC}"
    if [ -f .gateway_url ]; then
        echo -e "    ${GREEN}${CHECK} Orchestrator Agent${NC}"
        echo -e "    ${GREEN}${CHECK} Gateway: $(cat .gateway_url)${NC}"
    fi
    
    echo -e "  ${CYAN}Corporate Banking (891377397197)${NC}"
    if [ -f .corp_agent_arn ]; then
        echo -e "    ${GREEN}${CHECK} MCP Agent${NC}"
        echo -e "    ${GREEN}${CHECK} S3: s3://corporate-banking-891377397197${NC}"
    fi
    
    echo -e "  ${CYAN}Treasury & Risk (058264155998)${NC}"
    if [ -f .risk_agent_arn ]; then
        echo -e "    ${GREEN}${CHECK} MCP Agent${NC}"
        echo -e "    ${GREEN}${CHECK} S3: s3://treasury-risk-058264155998${NC}"
    fi
    
    echo ""
    echo -e "${WHITE}Frontend:${NC}"
    echo -e "  ${GREEN}${CHECK} CloudFront: https://d3ips4uebwo7az.cloudfront.net${NC}"
    
    echo ""
    echo -e "${GREEN}${SPARKLES} Deployment Complete! ${SPARKLES}${NC}"
    echo ""
}

# Main execution
main() {
    print_banner
    
    # Check if accounts_config.json exists, if not run configuration
    if [ ! -f "infra/accounts_config.json" ]; then
        print_warning "Configuration file not found. Running initial setup..."
        ./configure.sh
        if [ $? -ne 0 ]; then
            print_error "Configuration failed. Please fix errors and try again."
            exit 1
        fi
    else
        print_info "Using existing configuration from infra/accounts_config.json"
        if confirm "Do you want to reconfigure accounts?"; then
            ./configure.sh
        fi
    fi
    
    check_prerequisites
    
    setup_infrastructure
    
    deploy_lob_agents
    
    deploy_orchestrator
    
    deploy_frontend
    
    print_summary
}

# Run main
main

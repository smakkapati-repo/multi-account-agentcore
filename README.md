# Multi-Account AgentCore Demo

## Business Use Case: Intelligent Credit Risk Assessment

### The Banking Challenge

Commercial banks face critical operational challenges when assessing credit risk due to fragmented customer data across multiple lines of business:

- **Incomplete Risk Assessment**: Credit officers miss 30% of customer relationships during loan decisions because data sits in separate business units
- **Slow Turnaround**: Manual data gathering across departments takes 3-5 days, delaying loan approvals and frustrating customers  
- **Hidden Concentration Risk**: Banks cannot calculate total exposure to a single customer in real-time, creating regulatory and financial risk
- **Siloed Operations**: Each business unit operates independently, preventing holistic customer understanding

### Business Impact

| Metric | Current State | Target State | Improvement |
|--------|---------------|--------------|-------------|
| **Assessment Time** | 2-3 days | 2-4 hours | 85% faster |
| **Data Gathering** | 6-8 manual calls | Automated queries | 100% coverage |
| **Senior Analyst Time** | 4-6 hours per $10M+ deal | 45 minutes review | 80% time savings |
| **Cross-LOB Visibility** | Quarterly reports only | Real-time dashboard | Risk transparency |

### Financial Benefits (Mid-size Regional Bank)
- **$180K** annual savings (3 senior analysts @ $120K, 50% time reduction)
- **$450K** faster deal closure (15% improvement on $50M monthly originations)
- **$200K** risk mitigation (early warning on 2-3 problem accounts annually)
- **Total Annual Benefit: $830K** vs $150K implementation cost

## Our Solution: Multi-Account AgentCore Architecture

### What We Built

An intelligent assistant powered by Amazon Bedrock AgentCore that automatically gathers and synthesizes customer information from all business units in real-time, providing credit officers with a complete 360-degree view for faster, more informed lending decisions.

**Example Scenario**: A credit officer evaluates a $50M equipment loan for TechCorp Industries. Instead of spending days calling colleagues across departments, they submit one request. Within 30 minutes, they receive a comprehensive credit memo pulling together data from all 6 lines of business plus external sources.

### Why Multi-Account Architecture?

- **Data Isolation**: Each LOB maintains complete control over their sensitive data
- **Security**: Cross-account IAM roles provide secure, auditable access
- **Compliance**: Meets regulatory requirements for data segregation
- **Scalability**: Independent scaling per business unit
- **Governance**: Centralized orchestration with distributed data ownership

## Architecture

### Multi-Account Credit Risk Assessment Architecture

![Multi-Account Architecture](arch/credit_risk_multi_account_architecture.png?t=1730548891)

### Architecture Components

**Central Account - Credit Hub**:
- **Bedrock AgentCore**: Orchestration engine with conversation memory
- **Strands Agent**: 11 specialized tools for cross-account and external data access
- **Claude Sonnet 4.5**: Advanced reasoning and synthesis capabilities
- **Cross-Account IAM**: Secure AssumeRole patterns to all LOB accounts

**6 LOB Accounts** with MCP Entry Points:
- **Corporate Banking MCP**: Loan documents, credit memos, payment history
- **Treasury Services MCP**: FX positions, derivatives, cash management
- **Investment Banking MCP**: M&A deals, capital markets, analyst ratings
- **Trade Finance MCP**: Letters of credit, import/export financing
- **Credit Risk MCP**: Internal ratings, risk scores, covenant compliance
- **CRM MCP**: Customer relationships, meeting notes, ownership structure

**External Data Sources**:
- Dun & Bradstreet credit reports
- Moody's Analytics ratings
- S&P Capital IQ financials
- SEC EDGAR filings
- News & sentiment APIs

## Implementation Details

### Quick Start

```bash
./quick-start.sh
```

### Components

- **Agent**: Bedrock AgentCore configuration and multi-account agent
- **Infrastructure**: Setup scripts for central and child accounts
- **Data**: Sample financial and trade risk data
- **Frontend**: React dashboard for demonstrations
- **Backend**: Node.js API server

### Data Flow

1. **Credit Officer Request**: Submit loan evaluation via React frontend
2. **AgentCore Orchestration**: Connects to all 6 LOB MCP servers + external sources
3. **MCP Protocol Queries**: Parallel data gathering through standardized MCP interface
4. **Data Synthesis**: Claude processes and combines information from 11+ sources
5. **Risk Calculation**: Total exposure, concentration risk, credit scoring
6. **Credit Memo Generation**: Comprehensive report with recommendation
7. **Officer Review**: Structured decision support with full audit trail

**Total Processing Time: 20-30 seconds**

### Key Features

- **MCP Standardization**: All LOBs expose data through standardized MCP protocol
- **Real-time Data Access**: Live queries across all business units via MCP servers
- **Intelligent Synthesis**: AI-powered analysis and recommendation generation
- **Audit Trail**: Complete data lineage and source citations
- **Security**: Cross-account IAM with MCP-controlled access to LOB resources
- **Scalability**: Parallel processing and caching optimization
- **Cost Efficiency**: $10-20 in API costs vs. $500 in analyst time per assessment
# Architecture Comparison: Decentralized vs Centralized AgentCore

## Tab 2: Decentralized AgentCore (Single Account)

### Architecture Diagram
```
┌─────────────────────────────────────────────────────────┐
│  AWS Account: 164543933824 (Central Account)           │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Banking Analytics Agent                        │  │
│  │  - 12 tools (FDIC, SEC, PDF analysis)          │  │
│  │  - Direct access to all data                   │  │
│  └─────────────────────────────────────────────────┘  │
│                      │                                  │
│                      ▼                                  │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Knowledge Bases + S3 Buckets                   │  │
│  │  - All banking data in same account             │  │
│  │  - FDIC data, SEC filings, uploaded PDFs        │  │
│  └─────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘

User Query → Agent → Direct Data Access → Response
```

### Characteristics
- ✅ **Simple**: One account, one agent
- ✅ **Fast**: No cross-account latency
- ✅ **Cost-effective**: Minimal infrastructure
- ✅ **Easy to manage**: Single deployment
- ✅ **Good for**: Startups, small teams, single department

### Sample Queries
- "Analyze JPMorgan's 10-K filing"
- "Compare Wells Fargo vs Bank of America ROA"
- "What are the key risks in this uploaded document?"

---

## Tab 3: Centralized AgentCore (Hub-and-Spoke)

### Architecture Diagram
```
┌─────────────────────────────────────────────────────────┐
│  AWS Account: 164543933824 (Central/Hub Account)       │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Orchestrator Agent                             │  │
│  │  - 3 tools (query_east, query_west, compare)   │  │
│  │  - Coordinates cross-account queries           │  │
│  └─────────────────────────────────────────────────┘  │
│           │                           │                 │
│           │ AssumeRole                │ AssumeRole      │
│           ▼                           ▼                 │
└───────────┼───────────────────────────┼─────────────────┘
            │                           │
┌───────────▼─────────────┐  ┌─────────▼───────────────┐
│ Account: 891377397197   │  │ Account: 058264155998   │
│ (East Region)           │  │ (West Region)           │
│                         │  │                         │
│ ┌─────────────────────┐ │  │ ┌─────────────────────┐ │
│ │ Regional Agent      │ │  │ │ Regional Agent      │ │
│ │ - Banking tools     │ │  │ │ - Banking tools     │ │
│ └─────────────────────┘ │  │ └─────────────────────┘ │
│          │              │  │          │              │
│          ▼              │  │          ▼              │
│ ┌─────────────────────┐ │  │ ┌─────────────────────┐ │
│ │ Regional KB + S3    │ │  │ │ Regional KB + S3    │ │
│ │ - East region data  │ │  │ │ - West region data  │ │
│ └─────────────────────┘ │  │ └─────────────────────┘ │
└─────────────────────────┘  └─────────────────────────┘

User Query → Orchestrator → AssumeRole → Child Agents → Aggregate → Response
```

### Characteristics
- ✅ **Data Sovereignty**: Each region owns its data
- ✅ **Compliance**: Separate accounts for regulatory boundaries
- ✅ **Scalability**: Add regions without changing orchestrator
- ✅ **Security**: Cross-account IAM roles, no data replication
- ✅ **Good for**: Enterprises, multi-region banks, regulated industries

### Sample Queries
- "What is the banking performance in the East region?"
- "Compare East vs West region ROA and assets"
- "Which region has better loan quality?"

---

## Side-by-Side Comparison

| Aspect | Decentralized (Tab 2) | Centralized (Tab 3) |
|--------|----------------------|---------------------|
| **AWS Accounts** | 1 | 3 (1 central + 2 child) |
| **Agents** | 1 agent | 3 agents (1 orchestrator + 2 regional) |
| **Data Location** | All in one account | Distributed across accounts |
| **Data Access** | Direct | AssumeRole → Child account |
| **IAM Complexity** | Low (single account) | High (cross-account roles) |
| **Latency** | Low | Medium (cross-account calls) |
| **Data Sovereignty** | Single account | Per-region accounts |
| **Compliance** | Simple | Complex (regional boundaries) |
| **Scalability** | Vertical (add resources) | Horizontal (add accounts) |
| **Cost** | Lower | Higher (multiple accounts) |
| **Management** | Simple | Complex (multi-account) |
| **Use Case** | Single department | Multi-region enterprise |

---

## When to Use Each Pattern

### Use Decentralized (Tab 2) When:
- ✅ Single department or team
- ✅ All data can reside in one account
- ✅ No regulatory data residency requirements
- ✅ Simple compliance needs
- ✅ Cost optimization is priority
- ✅ Fast time-to-market needed

### Use Centralized (Tab 3) When:
- ✅ Multi-region operations
- ✅ Data sovereignty requirements (e.g., GDPR, data residency)
- ✅ Separate LOBs with independent data ownership
- ✅ Complex compliance requirements
- ✅ Need for centralized analytics + regional autonomy
- ✅ Enterprise-scale deployments

---

## Key Takeaway

**Both architectures use the SAME banking data and tools!**

The difference is **HOW** the data is organized and accessed:
- **Decentralized**: All data in one place, direct access
- **Centralized**: Data distributed across accounts, orchestrated access

This demo shows that Amazon Bedrock AgentCore supports **both patterns**, allowing you to choose the right architecture for your use case.

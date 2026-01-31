# Centralized Multi-Account Orchestrator Agent

## Architecture: Hub-and-Spoke Pattern

This agent demonstrates the **centralized multi-account architecture** where a central orchestrator agent coordinates queries across multiple child account agents.

### Account Structure

```
Central Account (111111111111)
├── Orchestrator Agent (orchestrator_agent.py)
└── Cross-account IAM roles to:
    ├── East Region Account (222222222222)
    │   ├── Regional Banking Agent
    │   ├── Regional Knowledge Base
    │   └── Regional S3 Data
    └── West Region Account (333333333333)
        ├── Regional Banking Agent
        ├── Regional Knowledge Base
        └── Regional S3 Data
```

### How It Works

1. **User Query**: "Compare East vs West region banking performance"
2. **Orchestrator Agent**: Receives query in central account
3. **Cross-Account Access**: 
   - AssumeRole into East region account (222222222222)
   - Query East region agent
   - AssumeRole into West region account (333333333333)
   - Query West region agent
4. **Aggregation**: Combine results from both regions
5. **Response**: Return unified analysis to user

### Tools

The orchestrator agent has 3 tools:

1. **query_east_region(query)**: Query East region banking data
2. **query_west_region(query)**: Query West region banking data
3. **compare_regions(metric)**: Compare both regions on a specific metric

### Deployment

```bash
# Deploy orchestrator agent to central account
cd agent-centralized
agentcore deploy

# Get agent ARN
agentcore status

# Set environment variable in backend
export AGENTCORE_CENTRALIZED_AGENT_ARN="<your-orchestrator-agent-arn>"
```

### Sample Queries

- "What is the banking performance in the East region?"
- "Analyze West region banking metrics"
- "Compare East vs West region ROA and assets"
- "Which region has better loan quality?"
- "Show me top banks in each region"

### Key Benefits

✅ **Data Sovereignty**: Each region owns its data in separate accounts
✅ **Compliance**: Separate accounts for regulatory boundaries
✅ **Scalability**: Add more regions without changing orchestrator
✅ **Security**: Cross-account IAM roles, no data replication
✅ **Centralized Analytics**: Unified view across all regions

### Comparison with Decentralized (Tab 2)

| Feature | Decentralized (Tab 2) | Centralized (Tab 3) |
|---------|----------------------|---------------------|
| Accounts | 1 | 3 (1 central + 2 child) |
| Agents | 1 | 3 (1 orchestrator + 2 regional) |
| Data Access | Direct | AssumeRole → Child |
| Use Case | Single department | Multi-region enterprise |
| Complexity | Low | High (IAM, cross-account) |

### Demo Note

For demonstration purposes, this agent **simulates** cross-account calls with mock data. In production:
- Deploy actual agents to child accounts (222222222222, 333333333333)
- Configure IAM trust relationships
- Use real STS AssumeRole calls
- Query actual child account agents via Bedrock AgentCore API

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import Lambda
from diagrams.aws.database import RDS, Dynamodb
from diagrams.aws.storage import S3
from diagrams.aws.ml import Bedrock
from diagrams.aws.security import IAM, Cognito, SecretsManager
from diagrams.aws.network import APIGateway
from diagrams.aws.integration import Eventbridge
from diagrams.aws.management import Cloudwatch
from diagrams.aws.analytics import AmazonOpensearchService
from diagrams.onprem.client import Users
from diagrams.onprem.compute import Server
from diagrams.custom import Custom
import os

# Professional configuration
graph_attr = {
    "fontsize": "14",
    "fontname": "Arial, sans-serif",
    "bgcolor": "#FFFFFF",
    "pad": "0.5",
    "splines": "ortho",
    "nodesep": "0.6",
    "ranksep": "1.0",
}

node_attr = {
    "fontsize": "11",
    "fontname": "Arial, sans-serif",
}

edge_attr = {
    "fontsize": "9",
    "fontname": "Arial, sans-serif",
}

with Diagram(
    "Multi-Account Credit Risk Assessment Architecture",
    show=False,
    direction="TB",
    graph_attr=graph_attr,
    node_attr=node_attr,
    edge_attr=edge_attr,
    filename="credit_risk_multi_account_architecture"
):
    
    # Credit Officers
    credit_officers = Users("Credit Officers")
    
    # AWS Organization Boundary
    with Cluster("AWS Organization - Multi-Account Architecture", graph_attr={"bgcolor": "#FAFAFA", "style": "dashed", "color": "#FF9900", "penwidth": "3"}):
        
        # Central Credit Hub Account
        with Cluster("Central Account - Credit Hub", graph_attr={"bgcolor": "#E8F4F8", "style": "rounded", "penwidth": "2"}):
            
            with Cluster("User Interface"):
                cognito = Cognito("Cognito\nAuthentication")
                frontend = S3("React Frontend\nCredit Dashboard")
            
            with Cluster("AgentCore Runtime"):
                agentcore = Bedrock("Bedrock AgentCore\nOrchestration Engine")
                agentcore_memory = Dynamodb("AgentCore Memory\nConversation History")
                agentcore_identity = IAM("AgentCore Identity\nExecution Role")
                strands_agent = Custom("Strands Agent\n11 Tools (Pydantic)\nCross-Account + External", "./strands_image.png")
                claude = Bedrock("Claude Sonnet 4.5\nReasoning & Synthesis")
                
                agentcore >> agentcore_memory
                agentcore >> strands_agent
                strands_agent >> claude
            
            with Cluster("Cross-Account Access"):
                central_iam = IAM("IAM Roles\nAssumeRole to LOBs")
                secrets = SecretsManager("Secrets Manager\nExternal API Keys")
            
            with Cluster("Observability"):
                cloudwatch = Cloudwatch("CloudWatch\nLogs & Metrics")
            
            with Cluster("Results Storage"):
                results_s3 = S3("S3 Bucket\nCredit Memos")
        
        # Internal LOB Accounts (6 separate AWS accounts)
        with Cluster("LOB Account 1 - Corporate Banking", graph_attr={"bgcolor": "#FFF4E6", "style": "rounded", "penwidth": "2"}):
            corp_iam = IAM("IAM Role\nTrust Central Account")
            corp_mcp = Custom("Corporate Banking\nMCP Server", "./mcp.png")
            corp_kb = Bedrock("Knowledge Base\nLoan Documents")
            corp_opensearch = AmazonOpensearchService("OpenSearch\nVector Store")
            corp_db = RDS("RDS Database\nLoans & Deposits")
            corp_s3 = S3("S3 Bucket\nCredit Memos")
            corp_iam >> corp_mcp
            corp_mcp >> corp_kb
            corp_mcp >> corp_db
            corp_mcp >> corp_s3
            corp_kb >> corp_opensearch
        
        with Cluster("LOB Account 2 - Treasury Services", graph_attr={"bgcolor": "#F3E5F5", "style": "rounded", "penwidth": "2"}):
            treasury_iam = IAM("IAM Role\nTrust Central Account")
            treasury_mcp = Custom("Treasury Services\nMCP Server", "./mcp.png")
            treasury_kb = Bedrock("Knowledge Base\nTreasury Docs")
            treasury_opensearch = AmazonOpensearchService("OpenSearch\nVector Store")
            treasury_db = RDS("RDS Database\nFX & Derivatives")
            treasury_iam >> treasury_mcp
            treasury_mcp >> treasury_kb
            treasury_mcp >> treasury_db
            treasury_kb >> treasury_opensearch
        
        with Cluster("LOB Account 3 - Investment Banking", graph_attr={"bgcolor": "#E8F5E9", "style": "rounded", "penwidth": "2"}):
            ib_iam = IAM("IAM Role\nTrust Central Account")
            ib_mcp = Custom("Investment Banking\nMCP Server", "./mcp.png")
            ib_kb = Bedrock("Knowledge Base\nDeal Documents")
            ib_opensearch = AmazonOpensearchService("OpenSearch\nVector Store")
            ib_db = RDS("RDS Database\nM&A & Capital Markets")
            ib_s3 = S3("S3 Bucket\nDeal Documents")
            ib_iam >> ib_mcp
            ib_mcp >> ib_kb
            ib_mcp >> ib_db
            ib_mcp >> ib_s3
            ib_kb >> ib_opensearch
        
        with Cluster("LOB Account 4 - Trade Finance", graph_attr={"bgcolor": "#FFF3E0", "style": "rounded", "penwidth": "2"}):
            trade_iam = IAM("IAM Role\nTrust Central Account")
            trade_mcp = Custom("Trade Finance\nMCP Server", "./mcp.png")
            trade_kb = Bedrock("Knowledge Base\nTrade Docs")
            trade_opensearch = AmazonOpensearchService("OpenSearch\nVector Store")
            trade_db = RDS("RDS Database\nLetters of Credit")
            trade_iam >> trade_mcp
            trade_mcp >> trade_kb
            trade_mcp >> trade_db
            trade_kb >> trade_opensearch
        
        with Cluster("LOB Account 5 - Credit Risk", graph_attr={"bgcolor": "#FFEBEE", "style": "rounded", "penwidth": "2"}):
            risk_iam = IAM("IAM Role\nTrust Central Account")
            risk_mcp = Custom("Credit Risk\nMCP Server", "./mcp.png")
            risk_kb = Bedrock("Knowledge Base\nRisk Reports")
            risk_opensearch = AmazonOpensearchService("OpenSearch\nVector Store")
            risk_db = RDS("RDS Database\nRisk Ratings & Scores")
            risk_iam >> risk_mcp
            risk_mcp >> risk_kb
            risk_mcp >> risk_db
            risk_kb >> risk_opensearch
        
        with Cluster("LOB Account 6 - CRM", graph_attr={"bgcolor": "#E3F2FD", "style": "rounded", "penwidth": "2"}):
            crm_iam = IAM("IAM Role\nTrust Central Account")
            crm_mcp = Custom("CRM\nMCP Server", "./mcp.png")
            crm_kb = Bedrock("Knowledge Base\nCustomer Notes")
            crm_opensearch = AmazonOpensearchService("OpenSearch\nVector Store")
            crm_db = Dynamodb("DynamoDB\nCustomer Relationships")
            crm_iam >> crm_mcp
            crm_mcp >> crm_kb
            crm_mcp >> crm_db
            crm_kb >> crm_opensearch
    
    # External Data Sources (outside AWS Organization)
    with Cluster("External Data Sources", graph_attr={"bgcolor": "#F5F5F5", "style": "rounded"}):
        dun_bradstreet = Server("Dun & Bradstreet\nCredit Reports")
        moodys = Server("Moody's Analytics\nCredit Ratings")
        sp_capiq = Server("S&P Capital IQ\nFinancials")
        sec_edgar = Server("SEC EDGAR\nPublic Filings")
        news_api = Server("News APIs\nSentiment")
    
    # User Flow
    credit_officers >> Edge(label="1. Login", color="#FF9900") >> cognito
    credit_officers >> Edge(label="2. Submit Request", color="#FF9900") >> frontend
    
    # Frontend to AgentCore
    frontend >> Edge(label="3. Invoke Agent", color="#2196F3") >> agentcore
    
    # AgentCore uses identity
    agentcore >> Edge(label="Use Identity", color="#9C27B0", style="dashed") >> agentcore_identity
    
    # Strands Agent orchestration
    strands_agent >> Edge(label="Tool Calls", color="#E91E63") >> central_iam
    
    # Cross-Account Access via MCP - Internal LOBs
    central_iam >> Edge(label="MCP Protocol", color="#4CAF50") >> corp_mcp
    central_iam >> Edge(label="MCP Protocol", color="#4CAF50") >> treasury_mcp
    central_iam >> Edge(label="MCP Protocol", color="#4CAF50") >> ib_mcp
    central_iam >> Edge(label="MCP Protocol", color="#4CAF50") >> trade_mcp
    central_iam >> Edge(label="MCP Protocol", color="#4CAF50") >> risk_mcp
    central_iam >> Edge(label="MCP Protocol", color="#4CAF50") >> crm_mcp
    
    # External API Calls via Strands Agent
    strands_agent >> Edge(label="API Call", color="#FF5722") >> secrets
    strands_agent >> Edge(label="Query", color="#FF5722") >> dun_bradstreet
    strands_agent >> Edge(label="Query", color="#FF5722") >> moodys
    strands_agent >> Edge(label="Query", color="#FF5722") >> sp_capiq
    strands_agent >> Edge(label="Query", color="#FF5722") >> sec_edgar
    strands_agent >> Edge(label="Query", color="#FF5722") >> news_api
    
    # Observability
    agentcore >> Edge(label="Logs", color="#607D8B", style="dashed") >> cloudwatch
    strands_agent >> Edge(label="Metrics", color="#607D8B", style="dashed") >> cloudwatch
    
    # Results
    claude >> Edge(label="Generate Memo", color="#9C27B0") >> results_s3
    results_s3 >> Edge(label="Return Results", color="#FF9900") >> frontend
    frontend >> Edge(label="Display", color="#FF9900") >> credit_officers

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import ECS, Fargate, ECR
from diagrams.aws.devtools import Codebuild
from diagrams.aws.network import InternetGateway, ElasticLoadBalancing, VPC, CloudFront
from diagrams.aws.storage import S3
from diagrams.aws.ml import Bedrock
from diagrams.aws.analytics import AmazonOpensearchService
from diagrams.aws.management import Cloudwatch
from diagrams.aws.security import IAM, Cognito, Shield, SecretsManager
from diagrams.aws.general import User
from diagrams.onprem.client import Users as ExternalUsers
from diagrams.onprem.compute import Server
from diagrams.custom import Custom

# AWS-style professional configuration
graph_attr = {
    "fontsize": "14",
    "fontname": "Amazon Ember, Arial, sans-serif",
    "bgcolor": "#FFFFFF",
    "pad": "0.5",
    "splines": "ortho",
    "nodesep": "0.8",
    "ranksep": "1.2",
    "compound": "true"
}

node_attr = {
    "fontsize": "11",
    "fontname": "Amazon Ember, Arial, sans-serif",
    "style": "",
    "fillcolor": "none",
    "color": "#232F3E"
}

edge_attr = {
    "fontsize": "9",
    "fontname": "Amazon Ember, Arial, sans-serif",
    "color": "#232F3E"
}

with Diagram(
    "Credit360 - Multi-Account Credit Risk Assessment Architecture",
    show=False,
    direction="TB",
    graph_attr=graph_attr,
    node_attr=node_attr,
    edge_attr=edge_attr,
    filename="credit360_architecture"
):
    
    users = ExternalUsers("Credit Officers\n& Risk Analysts")
    
    with Cluster("AWS Cloud - Central Credit Hub Account", graph_attr={"bgcolor": "#F7F9FC", "style": "rounded,dashed", "color": "#FF9900", "penwidth": "2"}):
        
        # Authentication
        with Cluster("Authentication & Security", graph_attr={"bgcolor": "white", "style": "rounded"}):
            cognito = Cognito("Cognito User Pool\nMFA + JWT\nRole-Based Access")
            secrets = SecretsManager("Secrets Manager\nExternal API Keys")
        
        # CloudFront CDN
        cloudfront = CloudFront("CloudFront CDN\n300s Timeout")
        
        # Frontend Storage
        with Cluster("Frontend Layer", graph_attr={"bgcolor": "white", "style": "rounded"}):
            s3_frontend = S3("S3 Bucket\nReact App\nCredit360 UI")
        
        # VPC
        with Cluster("VPC - Multi-AZ", graph_attr={"bgcolor": "white", "style": "rounded"}):
            
            # Public Subnets
            with Cluster("Public Subnets", graph_attr={"bgcolor": "white", "style": "rounded"}):
                alb = ElasticLoadBalancing("Application\nLoad Balancer\n300s Timeout")
            
            # Private Subnets
            with Cluster("Private Subnets - ECS Fargate", graph_attr={"bgcolor": "white", "style": "rounded"}):
                ecs_backend = Fargate("Backend API\nNode.js Express\nOrchestration Layer\nJWT Verification")
            
            # Data Services
            with Cluster("Storage & Cache", graph_attr={"bgcolor": "white", "style": "rounded"}):
                s3_docs = S3("S3 Bucket\nCredit Memos\nAudit Logs")
        
        # AgentCore Runtime
        with Cluster("Bedrock AgentCore + Strands Framework", graph_attr={"bgcolor": "white", "style": "rounded"}):
            guardrails = Shield("Bedrock Guardrails\nPII Protection\nContent Filtering")
            agentcore = Bedrock("AgentCore Runtime\nAgent Orchestration\nMemory + Context")
            
            with Cluster("Strands Agents", graph_attr={"bgcolor": "#FFF9E6", "style": "rounded"}):
                credit_agent = Custom("Credit Analysis Agent\n11 Tools (Pydantic)\nData Aggregation", "strands_framework.png")
                risk_agent = Custom("Risk Calculation Agent\n5 Tools (Pydantic)\nExposure Analysis", "strands_framework.png")
                memo_agent = Custom("Memo Generation Agent\n3 Tools (Pydantic)\nReport Synthesis", "strands_framework.png")
            
            claude = Bedrock("Claude Sonnet 4.5\n200K Context\nReasoning Engine")
            opensearch = AmazonOpensearchService("OpenSearch Serverless\nVector Store\nHistorical Memos")
            
            guardrails >> agentcore
            agentcore >> Edge(label="Orchestrate", color="#E91E63") >> credit_agent
            agentcore >> Edge(label="Orchestrate", color="#E91E63") >> risk_agent
            agentcore >> Edge(label="Orchestrate", color="#E91E63") >> memo_agent
            credit_agent >> Edge(label="LLM Reasoning", color="#E91E63") >> claude
            risk_agent >> Edge(label="LLM Reasoning", color="#E91E63") >> claude
            memo_agent >> Edge(label="RAG Query", color="#E91E63") >> opensearch
        
        # Management & Monitoring
        with Cluster("Management & Monitoring", graph_attr={"bgcolor": "white", "style": "rounded"}):
            cloudwatch = Cloudwatch("CloudWatch\nLogs & Metrics\nAudit Trail")
            iam_central = IAM("IAM Roles\nCross-Account\nAssumeRole")
    
    # LOB AWS Accounts (Internal Data Sources)
    with Cluster("LOB AWS Accounts - Internal Data Sources", graph_attr={"bgcolor": "#E8F5E9", "style": "rounded,dashed", "color": "#4CAF50", "penwidth": "2"}):
        
        with Cluster("Corporate Banking Account", graph_attr={"bgcolor": "white", "style": "rounded"}):
            corp_kb = Bedrock("Knowledge Base\nLoan History\nPayment Data")
            corp_s3 = S3("S3 Bucket\nCredit Memos\nDocuments")
            corp_iam = IAM("IAM Role\nTrust Central")
            corp_kb - corp_s3 - corp_iam
        
        with Cluster("Treasury Services Account", graph_attr={"bgcolor": "white", "style": "rounded"}):
            treasury_kb = Bedrock("Knowledge Base\nFX Positions\nDerivatives")
            treasury_s3 = S3("S3 Bucket\nTrade Data")
            treasury_iam = IAM("IAM Role\nTrust Central")
            treasury_kb - treasury_s3 - treasury_iam
        
        with Cluster("Investment Banking Account", graph_attr={"bgcolor": "white", "style": "rounded"}):
            ib_kb = Bedrock("Knowledge Base\nM&A Deals\nRatings")
            ib_s3 = S3("S3 Bucket\nDeal Files")
            ib_iam = IAM("IAM Role\nTrust Central")
            ib_kb - ib_s3 - ib_iam
        
        with Cluster("Trade Finance Account", graph_attr={"bgcolor": "white", "style": "rounded"}):
            trade_kb = Bedrock("Knowledge Base\nL/C Data\nCountry Risk")
            trade_s3 = S3("S3 Bucket\nShipping Docs")
            trade_iam = IAM("IAM Role\nTrust Central")
            trade_kb - trade_s3 - trade_iam
        
        with Cluster("Credit Risk Account", graph_attr={"bgcolor": "white", "style": "rounded"}):
            risk_kb = Bedrock("Knowledge Base\nInternal Ratings\nRisk Scores")
            risk_s3 = S3("S3 Bucket\nRisk Models")
            risk_iam = IAM("IAM Role\nTrust Central")
            risk_kb - risk_s3 - risk_iam
        
        with Cluster("CRM Account", graph_attr={"bgcolor": "white", "style": "rounded"}):
            crm_kb = Bedrock("Knowledge Base\nRelationships\nContacts")
            crm_s3 = S3("S3 Bucket\nMeeting Notes")
            crm_iam = IAM("IAM Role\nTrust Central")
            crm_kb - crm_s3 - crm_iam
    
    # External Data Sources
    with Cluster("External Data Sources (Third-Party APIs)", graph_attr={"bgcolor": "#FFF3E0", "style": "rounded,dashed", "color": "#FF9800", "penwidth": "2"}):
        dnb_api = Server("Dun & Bradstreet\nCredit Reports\nREST API")
        moodys_api = Server("Moody's Analytics\nRatings & EDF\nREST API")
        sp_api = Server("S&P Capital IQ\nFinancials\nREST API")
        sec_api = Server("SEC EDGAR\nPublic Filings\nFree API")
        news_api = Server("News API\nSentiment\nBloomberg/Reuters")
        
        dnb_api - moodys_api - sp_api - sec_api - news_api
    
    # User Flow
    users >> Edge(label="1. Login (MFA)", color="#FF9900", style="bold") >> cognito
    cognito >> Edge(label="JWT Token", color="#FF9900", style="dashed") >> users
    users >> Edge(label="2. Request Assessment", color="#FF9900", style="bold") >> cloudfront
    cloudfront >> Edge(label="Static Assets", color="#4CAF50") >> s3_frontend
    cloudfront >> Edge(label="API Calls", color="#2196F3") >> alb
    alb >> Edge(label="Route + Verify JWT", color="#9C27B0") >> ecs_backend
    
    # Backend to AgentCore
    ecs_backend >> Edge(label="3. Invoke AgentCore", color="#FF5722", style="bold") >> agentcore
    ecs_backend >> Edge(label="Content Check", color="#FF5722", style="dashed") >> guardrails
    
    # Cross-Account Access (Internal Sources)
    credit_agent >> Edge(label="4a. AssumeRole", color="#4CAF50", style="bold") >> iam_central
    iam_central >> Edge(label="Query", color="#4CAF50") >> corp_iam
    iam_central >> Edge(label="Query", color="#4CAF50") >> treasury_iam
    iam_central >> Edge(label="Query", color="#4CAF50") >> ib_iam
    iam_central >> Edge(label="Query", color="#4CAF50") >> trade_iam
    iam_central >> Edge(label="Query", color="#4CAF50") >> risk_iam
    iam_central >> Edge(label="Query", color="#4CAF50") >> crm_iam
    
    corp_iam >> Edge(label="Data", color="#4CAF50", style="dashed") >> corp_kb
    treasury_iam >> Edge(label="Data", color="#4CAF50", style="dashed") >> treasury_kb
    ib_iam >> Edge(label="Data", color="#4CAF50", style="dashed") >> ib_kb
    trade_iam >> Edge(label="Data", color="#4CAF50", style="dashed") >> trade_kb
    risk_iam >> Edge(label="Data", color="#4CAF50", style="dashed") >> risk_kb
    crm_iam >> Edge(label="Data", color="#4CAF50", style="dashed") >> crm_kb
    
    # External API Access
    credit_agent >> Edge(label="4b. API Calls", color="#FF9800", style="bold") >> secrets
    secrets >> Edge(label="Credentials", color="#FF9800", style="dashed") >> credit_agent
    credit_agent >> Edge(label="Query", color="#FF9800") >> dnb_api
    credit_agent >> Edge(label="Query", color="#FF9800") >> moodys_api
    credit_agent >> Edge(label="Query", color="#FF9800") >> sp_api
    credit_agent >> Edge(label="Query", color="#FF9800") >> sec_api
    credit_agent >> Edge(label="Query", color="#FF9800") >> news_api
    
    # Risk Calculation
    risk_agent >> Edge(label="5. Calculate Exposure", color="#E91E63") >> ecs_backend
    
    # Memo Generation & Storage
    memo_agent >> Edge(label="6. Generate Memo", color="#E91E63") >> s3_docs
    ecs_backend >> Edge(label="7. Return Results", color="#2196F3", style="bold") >> cloudfront
    cloudfront >> Edge(label="Display", color="#2196F3") >> users
    
    # Monitoring
    ecs_backend >> Edge(label="Logs", color="#607D8B") >> cloudwatch
    agentcore >> Edge(label="Traces", color="#607D8B") >> cloudwatch
    credit_agent >> Edge(label="Metrics", color="#607D8B") >> cloudwatch

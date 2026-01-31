from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import Fargate
from diagrams.aws.network import ElasticLoadBalancing, CloudFront
from diagrams.aws.storage import S3
from diagrams.aws.ml import Bedrock
from diagrams.aws.security import Cognito, IAM
from diagrams.onprem.client import Users as ExternalUsers
from diagrams.onprem.compute import Server

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
    "BankIQ+ Multi-Account Hub-and-Spoke Architecture",
    show=False,
    direction="LR",
    graph_attr=graph_attr,
    node_attr=node_attr,
    edge_attr=edge_attr,
    filename="multi_account_architecture"
):
    
    users = ExternalUsers("Banking Analysts\n& Executives")
    
    # Central Account (Hub)
    with Cluster("Central Account (164543933824) - Hub", graph_attr={"bgcolor": "#F7F9FC", "style": "rounded,dashed", "color": "#FF9900", "penwidth": "2"}):
        
        with Cluster("Authentication", graph_attr={"bgcolor": "white", "style": "rounded"}):
            cognito = Cognito("Cognito User Pool\nHosted UI + JWT")
        
        cloudfront = CloudFront("CloudFront CDN\n300s Timeout")
        
        with Cluster("Frontend", graph_attr={"bgcolor": "white", "style": "rounded"}):
            s3_frontend = S3("S3 Bucket\nReact App")
        
        with Cluster("VPC - Multi-AZ", graph_attr={"bgcolor": "white", "style": "rounded"}):
            with Cluster("Public Subnets", graph_attr={"bgcolor": "white", "style": "rounded"}):
                alb = ElasticLoadBalancing("Application\nLoad Balancer")
            
            with Cluster("Private Subnets", graph_attr={"bgcolor": "white", "style": "rounded"}):
                backend = Fargate("Backend Container\nNode.js Express\nJWT Verification")
        
        with Cluster("Bedrock AgentCore", graph_attr={"bgcolor": "white", "style": "rounded"}):
            orchestrator = Bedrock("Orchestrator Agent\n3 Tools:\nquery_east\nquery_west\ncompare_regions")
            claude_hub = Bedrock("Claude Sonnet 4.5\nOrchestration")
    
    # East Region Account
    with Cluster("East Region Account (891377397197)", graph_attr={"bgcolor": "#E8F5E9", "style": "rounded,dashed", "color": "#4CAF50", "penwidth": "2"}):
        
        with Cluster("Cross-Account Access", graph_attr={"bgcolor": "white", "style": "rounded"}):
            east_iam = IAM("IAM Role\nCentralAccountAccessRole")
        
        with Cluster("Bedrock AgentCore", graph_attr={"bgcolor": "white", "style": "rounded"}):
            east_agent = Bedrock("East Agent\nMCP-Enabled\n12 Banking Tools")
            claude_east = Bedrock("Claude Sonnet 4.5\nRegional Analysis")
        
        with Cluster("Regional Data", graph_attr={"bgcolor": "white", "style": "rounded"}):
            east_s3 = S3("S3 Bucket\nEast Banking Data\nJPM, BAC, C, PNC")
        
        east_agent - claude_east
        east_agent - east_s3
    
    # West Region Account
    with Cluster("West Region Account (058264155998)", graph_attr={"bgcolor": "#F3E5F5", "style": "rounded,dashed", "color": "#9C27B0", "penwidth": "2"}):
        
        with Cluster("Cross-Account Access", graph_attr={"bgcolor": "white", "style": "rounded"}):
            west_iam = IAM("IAM Role\nCentralAccountAccessRole")
        
        with Cluster("Bedrock AgentCore", graph_attr={"bgcolor": "white", "style": "rounded"}):
            west_agent = Bedrock("West Agent\nMCP-Enabled\n12 Banking Tools")
            claude_west = Bedrock("Claude Sonnet 4.5\nRegional Analysis")
        
        with Cluster("Regional Data", graph_attr={"bgcolor": "white", "style": "rounded"}):
            west_s3 = S3("S3 Bucket\nWest Banking Data\nWFC, USB, SCHW")
        
        west_agent - claude_west
        west_agent - west_s3
    
    # External Data Sources
    with Cluster("External Data Sources", graph_attr={"bgcolor": "white", "style": "rounded"}):
        fdic_api = Server("FDIC Call Reports\n2024-2025 Data")
        sec_api = Server("SEC EDGAR API\nLive Filings")
        fdic_api - sec_api
    
    # User flow
    users >> Edge(label="1. Login", color="#FF9900", style="bold") >> cognito
    cognito >> Edge(label="JWT Token", color="#FF9900", style="dashed") >> users
    users >> Edge(label="2. HTTPS Request", color="#FF9900", style="bold") >> cloudfront
    cloudfront >> Edge(label="Static Files", color="#4CAF50") >> s3_frontend
    cloudfront >> Edge(label="API Calls", color="#2196F3") >> alb
    alb >> backend
    backend >> Edge(label="Verify JWT", color="#9C27B0", style="dashed") >> cognito
    backend >> Edge(label="3. Query", color="#FF5722", style="bold") >> orchestrator
    orchestrator >> claude_hub
    
    # Cross-account calls to East
    orchestrator >> Edge(label="4a. AssumeRole\nMCP Call", color="#4CAF50", style="bold") >> east_iam
    east_iam >> Edge(label="Authorized", color="#4CAF50") >> east_agent
    east_agent >> Edge(label="FDIC/SEC Data", color="#00BCD4") >> fdic_api
    east_agent >> Edge(label="5a. Response", color="#4CAF50", style="dashed") >> orchestrator
    
    # Cross-account calls to West
    orchestrator >> Edge(label="4b. AssumeRole\nMCP Call", color="#9C27B0", style="bold") >> west_iam
    west_iam >> Edge(label="Authorized", color="#9C27B0") >> west_agent
    west_agent >> Edge(label="FDIC/SEC Data", color="#00BCD4") >> sec_api
    west_agent >> Edge(label="5b. Response", color="#9C27B0", style="dashed") >> orchestrator

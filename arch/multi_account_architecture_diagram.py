from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import Fargate
from diagrams.aws.network import ElasticLoadBalancing, CloudFront
from diagrams.aws.storage import S3
from diagrams.aws.ml import Bedrock
from diagrams.aws.security import Cognito, IAM
from diagrams.onprem.client import Users as ExternalUsers

graph_attr = {
    "fontsize": "14",
    "fontname": "Amazon Ember, Arial, sans-serif",
    "bgcolor": "#FFFFFF",
    "pad": "0.5",
    "splines": "ortho",
    "nodesep": "0.8",
    "ranksep": "1.2"
}

node_attr = {
    "fontsize": "11",
    "fontname": "Amazon Ember, Arial, sans-serif",
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
    direction="TB",
    graph_attr=graph_attr,
    node_attr=node_attr,
    edge_attr=edge_attr,
    filename="multi_account_architecture"
):
    
    users = ExternalUsers("Banking Analysts")
    
    # Central Account (Hub)
    with Cluster("Central Account (164543933824)", graph_attr={"bgcolor": "#E8F4F8", "style": "rounded,bold", "color": "#FF9900", "penwidth": "3"}):
        
        cognito = Cognito("Cognito\nAuth")
        cloudfront = CloudFront("CloudFront")
        
        with Cluster("VPC", graph_attr={"bgcolor": "white", "style": "rounded"}):
            alb = ElasticLoadBalancing("ALB")
            backend = Fargate("Backend\nExpress.js")
        
        s3_frontend = S3("Frontend\nReact App")
        
        orchestrator = Bedrock("Orchestrator Agent\n3 Tools:\n- query_east\n- query_west\n- compare")
    
    # East Region Account
    with Cluster("East Region (891377397197)", graph_attr={"bgcolor": "#FFF3E0", "style": "rounded,bold", "color": "#4CAF50", "penwidth": "3"}):
        east_agent = Bedrock("East Agent\nMCP-Enabled\nBanks: JPM, BAC, C")
        east_s3 = S3("East Data\nRegional KB")
        east_iam = IAM("Cross-Account\nIAM Role")
        
        east_agent - east_s3
    
    # West Region Account
    with Cluster("West Region (058264155998)", graph_attr={"bgcolor": "#F3E5F5", "style": "rounded,bold", "color": "#9C27B0", "penwidth": "3"}):
        west_agent = Bedrock("West Agent\nMCP-Enabled\nBanks: WFC, USB")
        west_s3 = S3("West Data\nRegional KB")
        west_iam = IAM("Cross-Account\nIAM Role")
        
        west_agent - west_s3
    
    # User flow
    users >> Edge(label="1. Login", color="#FF9900") >> cognito
    users >> Edge(label="2. Request", color="#FF9900") >> cloudfront
    cloudfront >> Edge(label="Static", color="#4CAF50") >> s3_frontend
    cloudfront >> Edge(label="API", color="#2196F3") >> alb
    alb >> backend
    backend >> Edge(label="3. Query", color="#FF5722") >> orchestrator
    
    # Cross-account calls
    orchestrator >> Edge(label="4a. AssumeRole\nMCP Call", color="#4CAF50", style="bold") >> east_iam
    east_iam >> east_agent
    
    orchestrator >> Edge(label="4b. AssumeRole\nMCP Call", color="#9C27B0", style="bold") >> west_iam
    west_iam >> west_agent
    
    # Response flow
    east_agent >> Edge(label="5a. Response", color="#4CAF50", style="dashed") >> orchestrator
    west_agent >> Edge(label="5b. Response", color="#9C27B0", style="dashed") >> orchestrator

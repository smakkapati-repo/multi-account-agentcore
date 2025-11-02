#!/usr/bin/env python3
"""
Setup Central Account Infrastructure
- IAM role for AgentCore with AssumeRole permissions
- S3 bucket for results
- Store child account role ARNs in SSM Parameter Store
"""
import boto3
import json
import sys
from pathlib import Path

# Account IDs
CENTRAL_ACCOUNT_ID = "164543933824"
CHILD1_ACCOUNT_ID = "891377397197"
CHILD2_ACCOUNT_ID = "058264155998"

# AWS profile for central account
PROFILE = "default"

# Resource names
IAM_ROLE_NAME = "AgentCoreMultiAccountRole"
S3_BUCKET_NAME = f"agentcore-multiaccountpoc-{CENTRAL_ACCOUNT_ID}"

def create_s3_bucket(s3_client):
    """Create S3 bucket for results"""
    print(f"\n📦 Creating S3 bucket: {S3_BUCKET_NAME}")
    
    try:
        s3_client.create_bucket(Bucket=S3_BUCKET_NAME)
        print(f"  ✅ Created bucket: {S3_BUCKET_NAME}")
        return S3_BUCKET_NAME
        
    except s3_client.exceptions.BucketAlreadyOwnedByYou:
        print(f"  ℹ️  Bucket already exists: {S3_BUCKET_NAME}")
        return S3_BUCKET_NAME
    except Exception as e:
        print(f"  ❌ Error creating bucket: {str(e)}")
        return None

def create_agentcore_role(iam_client):
    """Create IAM role for AgentCore with cross-account permissions"""
    print(f"\n🔐 Creating IAM role: {IAM_ROLE_NAME}")
    
    # Trust policy - allow Bedrock to assume this role
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "bedrock.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    try:
        response = iam_client.create_role(
            RoleName=IAM_ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="AgentCore role with cross-account access to child accounts",
            MaxSessionDuration=3600
        )
        role_arn = response['Role']['Arn']
        print(f"  ✅ Created role: {role_arn}")
        
    except iam_client.exceptions.EntityAlreadyExistsException:
        response = iam_client.get_role(RoleName=IAM_ROLE_NAME)
        role_arn = response['Role']['Arn']
        print(f"  ℹ️  Role already exists: {role_arn}")
    except Exception as e:
        print(f"  ❌ Error creating role: {str(e)}")
        return None
    
    # Attach policies
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "BedrockAccess",
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream"
                ],
                "Resource": "arn:aws:bedrock:*::foundation-model/*"
            },
            {
                "Sid": "AssumeChildRoles",
                "Effect": "Allow",
                "Action": "sts:AssumeRole",
                "Resource": [
                    f"arn:aws:iam::{CHILD1_ACCOUNT_ID}:role/CentralAccountAccessRole",
                    f"arn:aws:iam::{CHILD2_ACCOUNT_ID}:role/CentralAccountAccessRole"
                ]
            },
            {
                "Sid": "S3Access",
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:ListBucket"
                ],
                "Resource": [
                    f"arn:aws:s3:::{S3_BUCKET_NAME}",
                    f"arn:aws:s3:::{S3_BUCKET_NAME}/*"
                ]
            },
            {
                "Sid": "SSMAccess",
                "Effect": "Allow",
                "Action": [
                    "ssm:GetParameter",
                    "ssm:GetParameters"
                ],
                "Resource": f"arn:aws:ssm:us-east-1:{CENTRAL_ACCOUNT_ID}:parameter/multiaccountpoc/*"
            },
            {
                "Sid": "CloudWatchLogs",
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": "arn:aws:logs:*:*:*"
            }
        ]
    }
    
    policy_name = f"{IAM_ROLE_NAME}Policy"
    
    try:
        iam_client.put_role_policy(
            RoleName=IAM_ROLE_NAME,
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_document)
        )
        print(f"  ✅ Attached inline policy: {policy_name}")
    except Exception as e:
        print(f"  ❌ Error attaching policy: {str(e)}")
    
    return role_arn

def store_child_role_arns(ssm_client):
    """Store child account role ARNs in SSM Parameter Store"""
    print(f"\n💾 Storing child account role ARNs in SSM...")
    
    # Load child account configs
    child1_config_path = Path("infra/child1_config.json")
    child2_config_path = Path("infra/child2_config.json")
    
    if not child1_config_path.exists():
        print(f"  ⚠️  Child1 config not found: {child1_config_path}")
        print(f"  ℹ️  Run setup_child1.py first")
        return False
    
    if not child2_config_path.exists():
        print(f"  ⚠️  Child2 config not found: {child2_config_path}")
        print(f"  ℹ️  Run setup_child2.py first")
        return False
    
    child1_config = json.loads(child1_config_path.read_text())
    child2_config = json.loads(child2_config_path.read_text())
    
    # Store parameters
    parameters = {
        "/multiaccountpoc/child1/role_arn": child1_config["iam_role_arn"],
        "/multiaccountpoc/child1/opensearch_collection": child1_config["opensearch_collection_name"],
        "/multiaccountpoc/child2/role_arn": child2_config["iam_role_arn"],
        "/multiaccountpoc/child2/opensearch_collection": child2_config["opensearch_collection_name"],
    }
    
    for param_name, param_value in parameters.items():
        try:
            ssm_client.put_parameter(
                Name=param_name,
                Value=param_value,
                Type='String',
                Overwrite=True,
                Description='Multi-account POC configuration'
            )
            print(f"  ✓ Stored: {param_name}")
        except Exception as e:
            print(f"  ❌ Error storing {param_name}: {str(e)}")
    
    print(f"  ✅ Stored {len(parameters)} parameters")
    return True

def save_config(role_arn, bucket_name):
    """Save configuration for later use"""
    config = {
        "account_id": CENTRAL_ACCOUNT_ID,
        "profile": PROFILE,
        "agentcore_role_arn": role_arn,
        "s3_bucket": bucket_name,
        "child1_account_id": CHILD1_ACCOUNT_ID,
        "child2_account_id": CHILD2_ACCOUNT_ID
    }
    
    config_file = Path("infra/central_config.json")
    config_file.write_text(json.dumps(config, indent=2))
    print(f"\n💾 Saved configuration to: {config_file}")
    
    return config

def main():
    print("=" * 70)
    print("Central Account Infrastructure Setup")
    print(f"Account: {CENTRAL_ACCOUNT_ID} (profile: {PROFILE})")
    print("=" * 70)
    
    # Initialize AWS clients
    try:
        session = boto3.Session(profile_name=PROFILE, region_name='us-east-1')
        s3_client = session.client('s3')
        iam_client = session.client('iam')
        ssm_client = session.client('ssm')
        
        # Verify we're in the right account
        sts_client = session.client('sts')
        identity = sts_client.get_caller_identity()
        current_account = identity['Account']
        
        if current_account != CENTRAL_ACCOUNT_ID:
            print(f"❌ Error: Expected account {CENTRAL_ACCOUNT_ID}, but got {current_account}")
            print(f"   Check your AWS profile: {PROFILE}")
            sys.exit(1)
        
        print(f"✅ Connected to account: {current_account}")
        print(f"   User: {identity['Arn']}")
        
    except Exception as e:
        print(f"❌ Error connecting to AWS: {str(e)}")
        print(f"   Make sure profile '{PROFILE}' is configured")
        sys.exit(1)
    
    # Step 1: Create S3 bucket
    bucket_name = create_s3_bucket(s3_client)
    if not bucket_name:
        print("\n❌ Failed to create S3 bucket")
        sys.exit(1)
    
    # Step 2: Create IAM role
    role_arn = create_agentcore_role(iam_client)
    if not role_arn:
        print("\n❌ Failed to create IAM role")
        sys.exit(1)
    
    # Step 3: Store child account role ARNs
    store_child_role_arns(ssm_client)
    
    # Step 4: Save configuration
    config = save_config(role_arn, bucket_name)
    
    print("\n" + "=" * 70)
    print("✅ Central Account Infrastructure Setup Complete!")
    print("=" * 70)
    print(f"\n📦 S3 Bucket: {bucket_name}")
    print(f"🔐 AgentCore Role: {role_arn}")
    print(f"\n💾 Configuration saved to: infra/central_config.json")
    print("\n🔜 Next steps:")
    print("   1. Create and deploy the multi-account agent")
    print("   2. Run: cd agent && agentcore deploy")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Setup Child1 Account Infrastructure
- S3 bucket for financial documents
- IAM role trusting central account
- OpenSearch Serverless collection
"""
import boto3
import json
import sys
from pathlib import Path

# Account IDs
CENTRAL_ACCOUNT_ID = "164543933824"
CHILD1_ACCOUNT_ID = "891377397197"

# AWS profile for child1
PROFILE = "child1"

# Resource names
S3_BUCKET_NAME = f"child1-financial-kb-{CHILD1_ACCOUNT_ID}"
IAM_ROLE_NAME = "CentralAccountAccessRole"
OPENSEARCH_COLLECTION_NAME = "financial-kb"

def create_s3_bucket(s3_client):
    """Create S3 bucket for financial documents"""
    print(f"\n📦 Creating S3 bucket: {S3_BUCKET_NAME}")
    
    try:
        s3_client.create_bucket(Bucket=S3_BUCKET_NAME)
        print(f"  ✅ Created bucket: {S3_BUCKET_NAME}")
        
        # Enable versioning
        s3_client.put_bucket_versioning(
            Bucket=S3_BUCKET_NAME,
            VersioningConfiguration={'Status': 'Enabled'}
        )
        print(f"  ✅ Enabled versioning")
        
        # Add bucket policy for central account access
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AllowCentralAccountAccess",
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": f"arn:aws:iam::{CENTRAL_ACCOUNT_ID}:root"
                    },
                    "Action": [
                        "s3:GetObject",
                        "s3:ListBucket"
                    ],
                    "Resource": [
                        f"arn:aws:s3:::{S3_BUCKET_NAME}",
                        f"arn:aws:s3:::{S3_BUCKET_NAME}/*"
                    ]
                }
            ]
        }
        
        s3_client.put_bucket_policy(
            Bucket=S3_BUCKET_NAME,
            Policy=json.dumps(bucket_policy)
        )
        print(f"  ✅ Added bucket policy for central account access")
        
        return S3_BUCKET_NAME
        
    except s3_client.exceptions.BucketAlreadyOwnedByYou:
        print(f"  ℹ️  Bucket already exists: {S3_BUCKET_NAME}")
        return S3_BUCKET_NAME
    except Exception as e:
        print(f"  ❌ Error creating bucket: {str(e)}")
        return None

def upload_data_to_s3(s3_client, bucket_name):
    """Upload financial data to S3"""
    print(f"\n📤 Uploading data to S3...")
    
    data_dir = Path("data/child1_financial")
    if not data_dir.exists():
        print(f"  ⚠️  Data directory not found: {data_dir}")
        print(f"  ℹ️  Run fetch_sec_data.py first")
        return False
    
    uploaded_count = 0
    for file_path in data_dir.glob("*.md"):
        try:
            s3_client.upload_file(
                str(file_path),
                bucket_name,
                f"documents/{file_path.name}"
            )
            print(f"  ✓ Uploaded: {file_path.name}")
            uploaded_count += 1
        except Exception as e:
            print(f"  ❌ Error uploading {file_path.name}: {str(e)}")
    
    print(f"  ✅ Uploaded {uploaded_count} files")
    return uploaded_count > 0

def create_iam_role(iam_client):
    """Create IAM role that trusts central account"""
    print(f"\n🔐 Creating IAM role: {IAM_ROLE_NAME}")
    
    # Trust policy - allow central account to assume this role
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "AWS": f"arn:aws:iam::{CENTRAL_ACCOUNT_ID}:root"
                },
                "Action": "sts:AssumeRole",
                "Condition": {}
            }
        ]
    }
    
    try:
        response = iam_client.create_role(
            RoleName=IAM_ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="Allows central account to access Child1 resources",
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
    
    # Attach policies for OpenSearch and S3 access
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "aoss:APIAccessAll",
                    "aoss:List*",
                    "aoss:Get*"
                ],
                "Resource": f"arn:aws:aoss:us-east-1:{CHILD1_ACCOUNT_ID}:collection/*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:ListBucket"
                ],
                "Resource": [
                    f"arn:aws:s3:::{S3_BUCKET_NAME}",
                    f"arn:aws:s3:::{S3_BUCKET_NAME}/*"
                ]
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

def create_opensearch_collection(aoss_client):
    """Create OpenSearch Serverless collection"""
    print(f"\n🔍 Creating OpenSearch Serverless collection: {OPENSEARCH_COLLECTION_NAME}")
    
    try:
        # Create collection
        response = aoss_client.create_collection(
            name=OPENSEARCH_COLLECTION_NAME,
            type='VECTORSEARCH',
            description='Financial knowledge base for Child1 LOB'
        )
        
        collection_id = response['createCollectionDetail']['id']
        collection_arn = response['createCollectionDetail']['arn']
        
        print(f"  ✅ Created collection: {collection_id}")
        print(f"  📍 ARN: {collection_arn}")
        print(f"  ⏳ Collection is being created (this takes 3-5 minutes)...")
        print(f"  ℹ️  Check status with: aws opensearchserverless list-collections --profile {PROFILE}")
        
        return collection_id
        
    except aoss_client.exceptions.ConflictException:
        print(f"  ℹ️  Collection already exists: {OPENSEARCH_COLLECTION_NAME}")
        # Get existing collection
        response = aoss_client.list_collections(
            collectionFilters={'name': OPENSEARCH_COLLECTION_NAME}
        )
        if response['collectionSummaries']:
            collection_id = response['collectionSummaries'][0]['id']
            print(f"  📍 Collection ID: {collection_id}")
            return collection_id
        return None
    except Exception as e:
        print(f"  ❌ Error creating collection: {str(e)}")
        print(f"  ℹ️  Note: OpenSearch Serverless may not be available in all regions")
        return None

def save_config(bucket_name, role_arn, collection_id):
    """Save configuration for later use"""
    config = {
        "account_id": CHILD1_ACCOUNT_ID,
        "profile": PROFILE,
        "s3_bucket": bucket_name,
        "iam_role_arn": role_arn,
        "opensearch_collection_id": collection_id,
        "opensearch_collection_name": OPENSEARCH_COLLECTION_NAME
    }
    
    config_file = Path("infra/child1_config.json")
    config_file.write_text(json.dumps(config, indent=2))
    print(f"\n💾 Saved configuration to: {config_file}")
    
    return config

def main():
    print("=" * 70)
    print("Child1 Account Infrastructure Setup")
    print(f"Account: {CHILD1_ACCOUNT_ID} (profile: {PROFILE})")
    print("=" * 70)
    
    # Initialize AWS clients
    try:
        session = boto3.Session(profile_name=PROFILE, region_name='us-east-1')
        s3_client = session.client('s3')
        iam_client = session.client('iam')
        aoss_client = session.client('opensearchserverless')
        
        # Verify we're in the right account
        sts_client = session.client('sts')
        identity = sts_client.get_caller_identity()
        current_account = identity['Account']
        
        if current_account != CHILD1_ACCOUNT_ID:
            print(f"❌ Error: Expected account {CHILD1_ACCOUNT_ID}, but got {current_account}")
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
    
    # Step 2: Upload data
    upload_data_to_s3(s3_client, bucket_name)
    
    # Step 3: Create IAM role
    role_arn = create_iam_role(iam_client)
    if not role_arn:
        print("\n❌ Failed to create IAM role")
        sys.exit(1)
    
    # Step 4: Create OpenSearch collection
    collection_id = create_opensearch_collection(aoss_client)
    
    # Step 5: Save configuration
    config = save_config(bucket_name, role_arn, collection_id)
    
    print("\n" + "=" * 70)
    print("✅ Child1 Infrastructure Setup Complete!")
    print("=" * 70)
    print(f"\n📦 S3 Bucket: {bucket_name}")
    print(f"🔐 IAM Role: {role_arn}")
    if collection_id:
        print(f"🔍 OpenSearch Collection: {collection_id}")
    print(f"\n💾 Configuration saved to: infra/child1_config.json")
    print("\n🔜 Next steps:")
    print("   1. Wait for OpenSearch collection to be ACTIVE (3-5 minutes)")
    print("   2. Run: python scripts/embed_child1_data.py")

if __name__ == "__main__":
    main()

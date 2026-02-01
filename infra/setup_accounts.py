#!/usr/bin/env python3
"""
Generalized Multi-Account Setup
Supports any number of child accounts defined in accounts_config.json
"""
import boto3
import json
import sys
from pathlib import Path

def load_accounts_config():
    """Load accounts configuration"""
    config_path = Path("infra/accounts_config.json")
    if not config_path.exists():
        print(f"❌ Configuration file not found: {config_path}")
        sys.exit(1)
    return json.loads(config_path.read_text())

def setup_central_account(config):
    """Setup central account infrastructure"""
    central = config['central']
    children = config['children']
    
    print("=" * 70)
    print("Central Account Infrastructure Setup")
    print(f"Account: {central['account_id']} (profile: {central['profile']})")
    print("=" * 70)
    
    session = boto3.Session(profile_name=central['profile'], region_name=central['region'])
    s3_client = session.client('s3')
    iam_client = session.client('iam')
    sts_client = session.client('sts')
    
    # Verify account
    identity = sts_client.get_caller_identity()
    if identity['Account'] != central['account_id']:
        print(f"❌ Account mismatch: expected {central['account_id']}, got {identity['Account']}")
        sys.exit(1)
    
    print(f"✅ Connected to account: {identity['Account']}")
    
    # Create S3 bucket
    bucket_name = f"{central['s3_bucket_prefix']}-{central['account_id']}"
    print(f"\n📦 Creating S3 bucket: {bucket_name}")
    try:
        s3_client.create_bucket(Bucket=bucket_name)
        print(f"  ✅ Created bucket")
    except s3_client.exceptions.BucketAlreadyOwnedByYou:
        print(f"  ℹ️  Bucket already exists")
    
    # Create IAM role with dynamic child account permissions
    role_name = central['agentcore_role_name']
    print(f"\n🔐 Creating IAM role: {role_name}")
    
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "bedrock.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }
    
    # Build AssumeRole resources for all child accounts
    child_role_resources = [
        f"arn:aws:iam::{child['account_id']}:role/{child['iam_role_name']}"
        for child in children
    ]
    
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "BedrockAccess",
                "Effect": "Allow",
                "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
                "Resource": "arn:aws:bedrock:*::foundation-model/*"
            },
            {
                "Sid": "AssumeChildRoles",
                "Effect": "Allow",
                "Action": "sts:AssumeRole",
                "Resource": child_role_resources
            },
            {
                "Sid": "S3Access",
                "Effect": "Allow",
                "Action": ["s3:GetObject", "s3:PutObject", "s3:ListBucket"],
                "Resource": [f"arn:aws:s3:::{bucket_name}", f"arn:aws:s3:::{bucket_name}/*"]
            },
            {
                "Sid": "CloudWatchLogs",
                "Effect": "Allow",
                "Action": ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
                "Resource": "arn:aws:logs:*:*:*"
            }
        ]
    }
    
    try:
        response = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="AgentCore role with cross-account access",
            MaxSessionDuration=3600
        )
        role_arn = response['Role']['Arn']
        print(f"  ✅ Created role: {role_arn}")
    except iam_client.exceptions.EntityAlreadyExistsException:
        response = iam_client.get_role(RoleName=role_name)
        role_arn = response['Role']['Arn']
        print(f"  ℹ️  Role already exists: {role_arn}")
    
    iam_client.put_role_policy(
        RoleName=role_name,
        PolicyName=f"{role_name}Policy",
        PolicyDocument=json.dumps(policy_document)
    )
    print(f"  ✅ Attached inline policy")
    
    # Save config
    output_config = {
        "account_id": central['account_id'],
        "profile": central['profile'],
        "region": central['region'],
        "agentcore_role_arn": role_arn,
        "s3_bucket": bucket_name,
        "children": [
            {
                "id": child['id'],
                "account_id": child['account_id'],
                "name": child['name'],
                "role_arn": f"arn:aws:iam::{child['account_id']}:role/{child['iam_role_name']}"
            }
            for child in children
        ]
    }
    
    Path("infra/central_config.json").write_text(json.dumps(output_config, indent=2))
    
    print("\n" + "=" * 70)
    print("✅ Central Account Setup Complete!")
    print("=" * 70)
    print(f"📦 S3 Bucket: {bucket_name}")
    print(f"🔐 Role: {role_arn}")
    print(f"👥 Child Accounts: {len(children)}")
    for child in children:
        print(f"   - {child['id']}: {child['name']} ({child['account_id']})")

def setup_child_account(config, child_id):
    """Setup a specific child account"""
    central = config['central']
    child = next((c for c in config['children'] if c['id'] == child_id), None)
    
    if not child:
        print(f"❌ Child account '{child_id}' not found in config")
        sys.exit(1)
    
    print("=" * 70)
    print(f"Child Account Setup: {child['name']}")
    print(f"Account: {child['account_id']} (profile: {child['profile']})")
    print("=" * 70)
    
    session = boto3.Session(profile_name=child['profile'], region_name=central['region'])
    s3_client = session.client('s3')
    iam_client = session.client('iam')
    sts_client = session.client('sts')
    
    # Verify account
    identity = sts_client.get_caller_identity()
    if identity['Account'] != child['account_id']:
        print(f"❌ Account mismatch: expected {child['account_id']}, got {identity['Account']}")
        sys.exit(1)
    
    print(f"✅ Connected to account: {identity['Account']}")
    
    # Create S3 bucket
    bucket_name = f"{child['s3_bucket_prefix']}-{child['account_id']}"
    print(f"\n📦 Creating S3 bucket: {bucket_name}")
    try:
        s3_client.create_bucket(Bucket=bucket_name)
        print(f"  ✅ Created bucket")
    except s3_client.exceptions.BucketAlreadyOwnedByYou:
        print(f"  ℹ️  Bucket already exists")
    
    # Bucket policy for central account
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"AWS": f"arn:aws:iam::{central['account_id']}:root"},
            "Action": ["s3:GetObject", "s3:ListBucket"],
            "Resource": [f"arn:aws:s3:::{bucket_name}", f"arn:aws:s3:::{bucket_name}/*"]
        }]
    }
    s3_client.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(bucket_policy))
    
    # Upload data if exists
    data_dir = Path(child['data_directory'])
    if data_dir.exists():
        print(f"\n📤 Uploading data from {data_dir}")
        count = 0
        for file_path in data_dir.glob("*.json"):
            if file_path.is_file():
                # Upload to data/ prefix for agent access
                s3_key = f"data/{file_path.name}"
                s3_client.upload_file(str(file_path), bucket_name, s3_key)
                print(f"  ✅ Uploaded {file_path.name} to s3://{bucket_name}/{s3_key}")
                count += 1
        if count > 0:
            print(f"  ✅ Uploaded {count} files")
        else:
            print(f"  ⚠️  No JSON files found in {data_dir}")
    else:
        print(f"  ⚠️  Data directory not found: {data_dir}")
        print(f"  💡 Run: python3 data/generate_synthetic_data.py")
    
    # Create IAM role for cross-account access only
    role_name = child['iam_role_name']
    
    print(f"\n🔐 Creating IAM role...")
    
    # Cross-account access role (for orchestrator)
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"AWS": f"arn:aws:iam::{central['account_id']}:root"},
            "Action": "sts:AssumeRole"
        }]
    }
    
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": ["s3:GetObject", "s3:ListBucket"],
                "Resource": [f"arn:aws:s3:::{bucket_name}", f"arn:aws:s3:::{bucket_name}/*"]
            }
        ]
    }
    
    try:
        response = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description=f"Allows central account to access {child['name']}",
            MaxSessionDuration=3600
        )
        role_arn = response['Role']['Arn']
        print(f"  ✅ Created cross-account role: {role_arn}")
    except iam_client.exceptions.EntityAlreadyExistsException:
        response = iam_client.get_role(RoleName=role_name)
        role_arn = response['Role']['Arn']
        print(f"  ℹ️  Cross-account role already exists: {role_arn}")
    
    iam_client.put_role_policy(
        RoleName=role_name,
        PolicyName=f"{role_name}Policy",
        PolicyDocument=json.dumps(policy_document)
    )
    print(f"  ✅ Attached policy")
    
    # Save config
    output_config = {
        "id": child['id'],
        "account_id": child['account_id'],
        "profile": child['profile'],
        "name": child['name'],
        "description": child['description'],
        "s3_bucket": bucket_name,
        "iam_role_arn": role_arn,
        "opensearch_collection_name": child['opensearch_collection_name']
    }
    
    Path(f"infra/{child_id}_config.json").write_text(json.dumps(output_config, indent=2))
    
    print("\n" + "=" * 70)
    print(f"✅ {child['name']} Setup Complete!")
    print("=" * 70)
    print(f"📦 S3 Bucket: {bucket_name}")
    print(f"🔐 Cross-Account Role: {role_arn}")
    print(f"💡 AgentCore will auto-create execution role during deployment")

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python setup_accounts.py central              # Setup central account")
        print("  python setup_accounts.py corporate_banking    # Setup Corporate Banking LOB (creates S3 + uploads data)")
        print("  python setup_accounts.py treasury_risk        # Setup Treasury & Risk LOB (creates S3 + uploads data)")
        print("  python setup_accounts.py all                  # Setup all accounts")
        sys.exit(1)
    
    config = load_accounts_config()
    target = sys.argv[1]
    
    if target == "central":
        setup_central_account(config)
    elif target == "all":
        setup_central_account(config)
        for child in config['children']:
            print("\n")
            setup_child_account(config, child['id'])
    else:
        # Try to find matching child account by ID
        setup_child_account(config, target)

if __name__ == "__main__":
    main()

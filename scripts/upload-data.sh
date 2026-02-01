#!/bin/bash
set -e

echo "=========================================="
echo "Upload Data to LOB S3 Buckets"
echo "=========================================="
echo ""

# Load config
CORP_ACCOUNT=$(python3 -c "import json; print(json.load(open('infra/accounts_config.json'))['children'][0]['account_id'])")
CORP_PROFILE=$(python3 -c "import json; print(json.load(open('infra/accounts_config.json'))['children'][0]['profile'])")
RISK_ACCOUNT=$(python3 -c "import json; print(json.load(open('infra/accounts_config.json'))['children'][1]['account_id'])")
RISK_PROFILE=$(python3 -c "import json; print(json.load(open('infra/accounts_config.json'))['children'][1]['profile'])")

# Corporate Banking LOB
CORP_BUCKET="corporate-banking-$CORP_ACCOUNT"
echo "📤 Uploading Corporate Banking data..."
aws s3 cp data/corporate_banking/customer_loans.json \
  s3://$CORP_BUCKET/data/customer_loans.json \
  --profile $CORP_PROFILE

echo "✅ Corporate Banking data uploaded to s3://$CORP_BUCKET/data/"
echo ""

# Treasury & Risk LOB
RISK_BUCKET="treasury-risk-$RISK_ACCOUNT"
echo "📤 Uploading Treasury & Risk data..."
aws s3 cp data/treasury_risk/risk_models.json \
  s3://$RISK_BUCKET/data/risk_models.json \
  --profile $RISK_PROFILE

echo "✅ Treasury & Risk data uploaded to s3://$RISK_BUCKET/data/"
echo ""

echo "=========================================="
echo "✅ All data uploaded successfully!"
echo "=========================================="
echo ""
echo "Buckets:"
echo "  - s3://$CORP_BUCKET/data/customer_loans.json"
echo "  - s3://$RISK_BUCKET/data/risk_models.json"
echo ""

#!/bin/bash
set -e

echo "=========================================="
echo "Upload Data to LOB S3 Buckets"
echo "=========================================="
echo ""

# Corporate Banking LOB
CORP_BUCKET="corporate-banking-891377397197"
echo "📤 Uploading Corporate Banking data..."
aws s3 cp data/corporate_banking/customer_loans.json \
  s3://$CORP_BUCKET/data/customer_loans.json \
  --profile child1

echo "✅ Corporate Banking data uploaded to s3://$CORP_BUCKET/data/"
echo ""

# Treasury & Risk LOB
RISK_BUCKET="treasury-risk-058264155998"
echo "📤 Uploading Treasury & Risk data..."
aws s3 cp data/treasury_risk/risk_models.json \
  s3://$RISK_BUCKET/data/risk_models.json \
  --profile child2-demo

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

#!/bin/bash
set -e

echo "=========================================="
echo "LoanIQ Frontend Deployment to CloudFront"
echo "=========================================="
echo ""

# Get CloudFront distribution ID and S3 bucket
STACK_NAME="bankiq-frontend"
PREREQ_STACK="bankiq-prerequisites"

echo "📋 Getting infrastructure details..."
DISTRIBUTION_ID=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --query "Stacks[0].Outputs[?OutputKey=='CloudFrontDistributionId'].OutputValue" \
  --output text 2>/dev/null || echo "")

S3_BUCKET=$(aws cloudformation describe-stacks \
  --stack-name $PREREQ_STACK \
  --query "Stacks[0].Outputs[?OutputKey=='FrontendBucket'].OutputValue" \
  --output text 2>/dev/null || echo "")

if [ -z "$DISTRIBUTION_ID" ] || [ -z "$S3_BUCKET" ]; then
  echo "❌ Could not find CloudFront distribution or S3 bucket"
  echo "   Make sure stacks are deployed: $STACK_NAME, $PREREQ_STACK"
  exit 1
fi

echo "✅ Found infrastructure:"
echo "   CloudFront Distribution: $DISTRIBUTION_ID"
echo "   S3 Bucket: $S3_BUCKET"
echo ""

# Check if Gateway URL is configured
if [ -z "$REACT_APP_GATEWAY_URL" ]; then
  echo "⚠️  REACT_APP_GATEWAY_URL not set"
  echo "   Set it with: export REACT_APP_GATEWAY_URL=<your-gateway-url>"
  echo "   Or create frontend/.env file"
  echo ""
  read -p "Continue anyway? (y/n) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
  fi
fi

# Build React app
echo "🔨 Building React app..."
cd frontend
npm run build

if [ ! -d "build" ]; then
  echo "❌ Build failed - no build directory found"
  exit 1
fi

echo "✅ Build complete"
echo ""

# Upload to S3
echo "📤 Uploading to S3..."
aws s3 sync build/ s3://$S3_BUCKET --delete --cache-control "public, max-age=31536000, immutable"

# Upload index.html with no-cache
aws s3 cp build/index.html s3://$S3_BUCKET/index.html --cache-control "no-cache, no-store, must-revalidate"

echo "✅ Upload complete"
echo ""

# Invalidate CloudFront cache
echo "🔄 Invalidating CloudFront cache..."
INVALIDATION_ID=$(aws cloudfront create-invalidation \
  --distribution-id $DISTRIBUTION_ID \
  --paths "/*" \
  --query "Invalidation.Id" \
  --output text)

echo "✅ Invalidation created: $INVALIDATION_ID"
echo ""

# Get CloudFront URL
CLOUDFRONT_URL=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --query "Stacks[0].Outputs[?OutputKey=='ApplicationUrl'].OutputValue" \
  --output text)

echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo ""
echo "🌐 Application URL: $CLOUDFRONT_URL"
echo ""
echo "⏳ Note: CloudFront invalidation may take 1-2 minutes to propagate"
echo ""

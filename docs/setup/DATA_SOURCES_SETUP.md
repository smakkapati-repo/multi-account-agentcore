# Data Sources Setup

## S3-Based Data Loading

Agents load hybrid data from S3 buckets at runtime instead of bundling files in the deployment package.

### Architecture

```
Corporate Banking Agent → s3://corporate-banking-891377397197/data/customer_loans.json
Treasury & Risk Agent   → s3://treasury-risk-058264155998/data/risk_models.json
```

### Upload Data to S3

```bash
./upload-data.sh
```

This uploads:
- `data/corporate_banking/customer_loans.json` → Corporate Banking S3 bucket
- `data/treasury_risk/risk_models.json` → Treasury & Risk S3 bucket

### IAM Permissions Required

Each agent's execution role needs S3 read access:

```json
{
  "Effect": "Allow",
  "Action": ["s3:GetObject", "s3:ListBucket"],
  "Resource": [
    "arn:aws:s3:::corporate-banking-891377397197",
    "arn:aws:s3:::corporate-banking-891377397197/*"
  ]
}
```

### Environment Variables

Agents use these environment variables (with defaults):
- `DATA_BUCKET` - S3 bucket name (defaults to account-specific bucket)

### Benefits

✅ Separate data from code
✅ Update data without redeploying agents
✅ Smaller deployment packages
✅ Follows AWS best practices

### Deployment Order

1. **Upload data**: `./upload-data.sh`
2. **Deploy agents**: `agentcore launch`
3. Agents load data from S3 on startup

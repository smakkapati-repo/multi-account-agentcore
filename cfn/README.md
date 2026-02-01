# CloudFormation Templates

This directory contains CloudFormation templates for the **existing infrastructure** (CloudFront, S3, ALB, ECS, Cognito).

## Status

⚠️ **These templates are for reference only.** The infrastructure is already deployed.

The new deployment script (`scripts/deploy-all.sh`) does NOT use these templates. It:
- Uses existing CloudFront distribution
- Uploads frontend to existing S3 bucket
- Deploys agents via AgentCore CLI

## Templates

- `prerequisites.yaml` - S3 buckets, ECR repositories
- `auth.yaml` - Cognito user pool and hosted UI
- `backend.yaml` - ECS Fargate, ALB, backend service
- `frontend.yaml` - CloudFront distribution

## If You Need to Redeploy Infrastructure

```bash
./cfn/scripts/deploy-all.sh
```

This will recreate the CloudFront + S3 + ALB + ECS infrastructure.

## For New Deployments

Use the simplified deployment:
```bash
./scripts/deploy-all.sh
```

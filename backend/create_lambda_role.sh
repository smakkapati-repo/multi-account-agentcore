#!/bin/bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

aws iam create-role \
    --role-name lambda-bedrock-role \
    --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "lambda.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }' 2>/dev/null || echo "Role exists"

aws iam attach-role-policy \
    --role-name lambda-bedrock-role \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam put-role-policy \
    --role-name lambda-bedrock-role \
    --policy-name bedrock-invoke \
    --policy-document '{
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": [
                "bedrock-agent-runtime:InvokeAgent",
                "bedrock:InvokeModel"
            ],
            "Resource": "*"
        }]
    }'

echo "Waiting for role to propagate..."
sleep 10

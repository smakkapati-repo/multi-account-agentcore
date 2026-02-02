#!/bin/bash
set -e

AGENT_ARN=$(cat ../.orchestrator_agent_arn 2>/dev/null || echo "")
if [ -z "$AGENT_ARN" ]; then
    echo "Error: Orchestrator agent ARN not found"
    exit 1
fi

AGENT_ID=$(echo $AGENT_ARN | awk -F'/' '{print $2}')
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION="us-east-1"

echo "Creating Lambda function..."
zip function.zip invoke_agent.py

aws lambda create-function \
    --function-name orchestrator-invoke-api \
    --runtime python3.11 \
    --role arn:aws:iam::${ACCOUNT_ID}:role/lambda-bedrock-role \
    --handler invoke_agent.lambda_handler \
    --zip-file fileb://function.zip \
    --environment Variables={AGENT_ID=${AGENT_ID}} \
    --timeout 300 \
    --region ${REGION} 2>/dev/null || \
aws lambda update-function-code \
    --function-name orchestrator-invoke-api \
    --zip-file fileb://function.zip \
    --region ${REGION}

aws lambda update-function-configuration \
    --function-name orchestrator-invoke-api \
    --environment Variables={AGENT_ID=${AGENT_ID}} \
    --region ${REGION}

echo "Creating API Gateway..."
API_ID=$(aws apigateway create-rest-api \
    --name orchestrator-api \
    --region ${REGION} \
    --query 'id' --output text 2>/dev/null || \
    aws apigateway get-rest-apis --region ${REGION} --query "items[?name=='orchestrator-api'].id" --output text)

ROOT_ID=$(aws apigateway get-resources --rest-api-id ${API_ID} --region ${REGION} --query 'items[0].id' --output text)

RESOURCE_ID=$(aws apigateway create-resource \
    --rest-api-id ${API_ID} \
    --parent-id ${ROOT_ID} \
    --path-part invoke \
    --region ${REGION} \
    --query 'id' --output text 2>/dev/null || \
    aws apigateway get-resources --rest-api-id ${API_ID} --region ${REGION} --query "items[?path=='/invoke'].id" --output text)

aws apigateway put-method \
    --rest-api-id ${API_ID} \
    --resource-id ${RESOURCE_ID} \
    --http-method POST \
    --authorization-type NONE \
    --region ${REGION} 2>/dev/null || true

aws apigateway put-integration \
    --rest-api-id ${API_ID} \
    --resource-id ${RESOURCE_ID} \
    --http-method POST \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri arn:aws:apigateway:${REGION}:lambda:path/2015-03-31/functions/arn:aws:lambda:${REGION}:${ACCOUNT_ID}:function:orchestrator-invoke-api/invocations \
    --region ${REGION} 2>/dev/null || true

aws lambda add-permission \
    --function-name orchestrator-invoke-api \
    --statement-id apigateway-invoke \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:${REGION}:${ACCOUNT_ID}:${API_ID}/*/*" \
    --region ${REGION} 2>/dev/null || true

aws apigateway create-deployment \
    --rest-api-id ${API_ID} \
    --stage-name prod \
    --region ${REGION}

API_URL="https://${API_ID}.execute-api.${REGION}.amazonaws.com/prod/invoke"
echo $API_URL > .api_gateway_url
echo "API Gateway URL: $API_URL"

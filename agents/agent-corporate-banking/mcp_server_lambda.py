"""Corporate Banking MCP Server Lambda
Exposes customer loan data as MCP tools via AgentCore Gateway
"""
import json
import boto3

s3 = boto3.client('s3')
S3_BUCKET = 'corporate-banking-891377397197'
S3_KEY = 'data/customer_loans.json'

def load_data():
    """Load customer loans from S3"""
    try:
        response = s3.get_object(Bucket=S3_BUCKET, Key=S3_KEY)
        return json.loads(response['Body'].read().decode('utf-8'))
    except Exception as e:
        print(f"Error loading data: {e}")
        return {"banks": []}

CORPORATE_DATA = load_data()

def query_customer_loans(bank_name=None, customer_name=None, industry=None):
    """Query customer loans with filters"""
    results = []
    for bank in CORPORATE_DATA["banks"]:
        if bank_name and bank_name.lower() not in bank["bank_name"].lower():
            continue
        for loan in bank["customer_loans"]:
            if customer_name and customer_name.lower() not in loan["customer_name"].lower():
                continue
            if industry and industry.lower() not in loan["industry"].lower():
                continue
            results.append({
                "bank": bank["bank_name"],
                "customer": loan["customer_name"],
                "industry": loan["industry"],
                "loan_amount_millions": loan["loan_amount_millions"],
                "credit_rating": loan["credit_rating"],
                "loan_type": loan["loan_type"]
            })
    return {
        "lob": "Corporate Banking",
        "account_id": CORPORATE_DATA["account_id"],
        "results": results,
        "total_results": len(results)
    }

def get_bank_aggregate_data(bank_name):
    """Get aggregate data for a bank"""
    for bank in CORPORATE_DATA["banks"]:
        if bank_name.lower() in bank["bank_name"].lower():
            return {
                "bank_name": bank["bank_name"],
                "total_ci_loans_billions": bank["total_ci_loans_billions"],
                "total_customers": bank["total_customers"],
                "total_exposure_millions": bank["total_exposure_millions"]
            }
    return {"error": f"Bank {bank_name} not found"}

def get_industry_exposure(industry):
    """Get industry exposure across all banks"""
    exposure_by_bank = {}
    for bank in CORPORATE_DATA["banks"]:
        bank_exposure = 0
        customers = []
        for loan in bank["customer_loans"]:
            if industry.lower() in loan["industry"].lower():
                bank_exposure += loan["loan_amount_millions"]
                customers.append(loan["customer_name"])
        if bank_exposure > 0:
            exposure_by_bank[bank["bank_name"]] = {
                "exposure_millions": bank_exposure,
                "customers": customers
            }
    return {
        "industry": industry,
        "exposure_by_bank": exposure_by_bank,
        "total_exposure_millions": sum(b["exposure_millions"] for b in exposure_by_bank.values())
    }

# MCP Tool Registry
TOOLS = {
    "query_customer_loans": {
        "function": query_customer_loans,
        "description": "Query customer relationships and loan exposure",
        "inputSchema": {
            "type": "object",
            "properties": {
                "bank_name": {"type": "string", "description": "Filter by bank"},
                "customer_name": {"type": "string", "description": "Filter by customer"},
                "industry": {"type": "string", "description": "Filter by industry"}
            }
        }
    },
    "get_bank_aggregate_data": {
        "function": get_bank_aggregate_data,
        "description": "Get aggregate loan portfolio data for a bank",
        "inputSchema": {
            "type": "object",
            "properties": {
                "bank_name": {"type": "string", "description": "Bank name"}
            },
            "required": ["bank_name"]
        }
    },
    "get_industry_exposure": {
        "function": get_industry_exposure,
        "description": "Get total loan exposure by industry",
        "inputSchema": {
            "type": "object",
            "properties": {
                "industry": {"type": "string", "description": "Industry name"}
            },
            "required": ["industry"]
        }
    }
}

def lambda_handler(event, context):
    """Gateway Lambda Handler - receives direct property mapping"""
    try:
        # Gateway passes tool arguments directly as event properties
        # If no arguments, default to query_customer_loans (returns all)
        
        if not event or len(event) == 0:
            # No arguments - return all customer loans
            result = query_customer_loans()
        elif 'customer_name' in event or ('industry' in event and ('bank_name' in event or 'customer_name' in event)):
            # query_customer_loans
            result = query_customer_loans(
                bank_name=event.get('bank_name'),
                customer_name=event.get('customer_name'),
                industry=event.get('industry')
            )
        elif 'bank_name' in event and 'industry' not in event:
            # get_bank_aggregate_data
            result = get_bank_aggregate_data(event['bank_name'])
        elif 'industry' in event and 'bank_name' not in event and 'customer_name' not in event:
            # get_industry_exposure
            result = get_industry_exposure(event['industry'])
        else:
            # Fallback to query_customer_loans with filters
            result = query_customer_loans(
                bank_name=event.get('bank_name'),
                customer_name=event.get('customer_name'),
                industry=event.get('industry')
            )
        
        return result
    
    except Exception as e:
        return {"error": str(e)}

"""Treasury & Risk MCP Server Lambda
Exposes risk models as MCP tools via AgentCore Gateway
"""
import json
import boto3

s3 = boto3.client('s3')
S3_BUCKET = 'treasury-risk-058264155998'
S3_KEY = 'data/risk_models.json'

def load_data():
    """Load risk models from S3"""
    try:
        response = s3.get_object(Bucket=S3_BUCKET, Key=S3_KEY)
        return json.loads(response['Body'].read().decode('utf-8'))
    except Exception as e:
        print(f"Error loading data: {e}")
        return {"banks": [], "market_data": {}}

RISK_DATA = load_data()

def query_risk_models(bank_name=None, industry=None):
    """Query risk models by bank and industry"""
    results = []
    for bank in RISK_DATA["banks"]:
        if bank_name and bank_name.lower() not in bank["bank_name"].lower():
            continue
        for model in bank["risk_models"]:
            if industry and industry.lower() not in model["industry"].lower():
                continue
            results.append({
                "bank": bank["bank_name"],
                "industry": model["industry"],
                "probability_of_default_pct": model["probability_of_default_pct"],
                "loss_given_default_pct": model["loss_given_default_pct"],
                "expected_loss_pct": model["expected_loss_pct"],
                "rating_equivalent": model["rating_equivalent"]
            })
    return {
        "lob": "Treasury & Risk",
        "account_id": RISK_DATA["account_id"],
        "results": results,
        "total_results": len(results)
    }

def get_market_data():
    """Get current market data"""
    return {
        "market_data": RISK_DATA["market_data"],
        "note": "Use live FRED/Treasury APIs in production"
    }

def calculate_expected_loss(industry, exposure_millions):
    """Calculate expected loss for industry and exposure"""
    industry_models = []
    for bank in RISK_DATA["banks"]:
        for model in bank["risk_models"]:
            if industry.lower() in model["industry"].lower():
                industry_models.append(model)
    
    if not industry_models:
        return {"error": f"No risk models found for industry: {industry}"}
    
    avg_pd = sum(m["probability_of_default_pct"] for m in industry_models) / len(industry_models)
    avg_lgd = sum(m["loss_given_default_pct"] for m in industry_models) / len(industry_models)
    avg_el = sum(m["expected_loss_pct"] for m in industry_models) / len(industry_models)
    expected_loss_amount = exposure_millions * (avg_el / 100)
    
    return {
        "industry": industry,
        "exposure_millions": exposure_millions,
        "average_pd_pct": round(avg_pd, 2),
        "average_lgd_pct": round(avg_lgd, 2),
        "average_el_pct": round(avg_el, 2),
        "expected_loss_millions": round(expected_loss_amount, 2),
        "models_used": len(industry_models)
    }

# MCP Tool Registry
TOOLS = {
    "query_risk_models": {
        "function": query_risk_models,
        "description": "Query risk models (PD, LGD, Expected Loss) by bank and industry",
        "inputSchema": {
            "type": "object",
            "properties": {
                "bank_name": {"type": "string", "description": "Filter by bank"},
                "industry": {"type": "string", "description": "Filter by industry"}
            }
        }
    },
    "get_market_data": {
        "function": get_market_data,
        "description": "Get current market data (Treasury yields, Fed Funds rate)",
        "inputSchema": {"type": "object", "properties": {}}
    },
    "calculate_expected_loss": {
        "function": calculate_expected_loss,
        "description": "Calculate expected loss for a given industry and exposure amount",
        "inputSchema": {
            "type": "object",
            "properties": {
                "industry": {"type": "string", "description": "Industry name"},
                "exposure_millions": {"type": "number", "description": "Loan exposure in millions"}
            },
            "required": ["industry", "exposure_millions"]
        }
    }
}

def lambda_handler(event, context):
    """Gateway Lambda Handler - receives direct property mapping"""
    try:
        # Gateway passes tool arguments directly as event properties
        
        if 'industry' in event and 'exposure_millions' in event:
            # calculate_expected_loss
            result = calculate_expected_loss(event['industry'], event['exposure_millions'])
        elif 'bank_name' in event or 'industry' in event:
            # query_risk_models
            result = query_risk_models(
                bank_name=event.get('bank_name'),
                industry=event.get('industry')
            )
        elif len(event) == 0:
            # get_market_data
            result = get_market_data()
        else:
            return {"error": "Unknown tool or missing parameters"}
        
        return result
    
    except Exception as e:
        return {"error": str(e)}

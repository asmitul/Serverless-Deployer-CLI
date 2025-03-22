"""
Example serverless function
"""
import json
import os
from datetime import datetime


def lambda_handler(event, context):
    """
    AWS Lambda handler function
    """
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "message": "Hello from Serverless Deployer!",
            "timestamp": datetime.now().isoformat(),
            "env": os.environ.get("ENVIRONMENT", "development")
        })
    }


# For Vercel serverless functions
def handler(request, response):
    """
    Vercel serverless function handler
    """
    return {
        "body": json.dumps({
            "message": "Hello from Serverless Deployer!",
            "timestamp": datetime.now().isoformat(),
            "env": os.environ.get("ENVIRONMENT", "development")
        }),
        "status": 200,
        "headers": {
            "Content-Type": "application/json"
        }
    } 
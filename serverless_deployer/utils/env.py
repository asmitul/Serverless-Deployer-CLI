"""
Environment variable handling for Serverless Deployer
"""
import os
import json
from dotenv import load_dotenv


def load_env_vars(env_file=None):
    """
    Load environment variables from .env file
    
    Args:
        env_file: Path to .env file (optional)
        
    Returns:
        Dictionary of environment variables
    """
    if env_file and os.path.exists(env_file):
        load_dotenv(env_file)
        
    # Get environment variables relevant to serverless deployments
    # This is a basic implementation - expand as needed
    env_vars = {}
    
    # AWS credentials
    if os.environ.get("AWS_ACCESS_KEY_ID"):
        env_vars["AWS_ACCESS_KEY_ID"] = os.environ.get("AWS_ACCESS_KEY_ID")
    if os.environ.get("AWS_SECRET_ACCESS_KEY"):
        env_vars["AWS_SECRET_ACCESS_KEY"] = os.environ.get("AWS_SECRET_ACCESS_KEY")
    if os.environ.get("AWS_REGION"):
        env_vars["AWS_REGION"] = os.environ.get("AWS_REGION")
        
    # Vercel credentials
    if os.environ.get("VERCEL_TOKEN"):
        env_vars["VERCEL_TOKEN"] = os.environ.get("VERCEL_TOKEN")
    if os.environ.get("VERCEL_ORG_ID"):
        env_vars["VERCEL_ORG_ID"] = os.environ.get("VERCEL_ORG_ID")
    if os.environ.get("VERCEL_PROJECT_ID"):
        env_vars["VERCEL_PROJECT_ID"] = os.environ.get("VERCEL_PROJECT_ID")
        
    return env_vars


def format_env_for_provider(env_vars, provider):
    """
    Format environment variables for a specific provider
    
    Args:
        env_vars: Dictionary of environment variables
        provider: Provider to format for (aws, vercel)
        
    Returns:
        Provider-specific environment variable format
    """
    if provider == "aws":
        # AWS Lambda expects env vars in a specific format for CloudFormation/SAM
        return {
            "Variables": env_vars
        }
    elif provider == "vercel":
        # Vercel expects env vars in a different format
        return {
            "env": [{"key": k, "value": v} for k, v in env_vars.items()]
        }
    else:
        return env_vars


def read_env_file(env_file):
    """
    Read environment variables from a .env file into a dictionary
    
    Args:
        env_file: Path to .env file
        
    Returns:
        Dictionary of environment variables
    """
    if not os.path.exists(env_file):
        return {}
        
    env_vars = {}
    with open(env_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
                
            key, value = line.split("=", 1)
            env_vars[key.strip()] = value.strip().strip("\"'")
            
    return env_vars 
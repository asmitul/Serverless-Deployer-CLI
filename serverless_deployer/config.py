"""
Configuration handling for Serverless Deployer
"""
import os
import yaml
from datetime import datetime


def load_config(config_file="serverless.yml"):
    """
    Load configuration from YAML file
    """
    if not os.path.exists(config_file):
        raise FileNotFoundError(
            f"Configuration file '{config_file}' not found. Run 'serverless-deployer init' to create it."
        )
        
    with open(config_file, "r") as f:
        return yaml.safe_load(f)


def save_config(config, config_file="serverless.yml"):
    """
    Save configuration to YAML file
    """
    with open(config_file, "w") as f:
        yaml.dump(config, f, default_flow_style=False)


def init_config(name, provider):
    """
    Initialize a new configuration with defaults
    """
    return {
        "project": name,
        "provider": provider,
        "created_at": datetime.now().isoformat(),
        "functions": [
            {
                "name": "example-function",
                "path": "./src/handler.py",
                "memory": 128,
                "timeout": 30,
                "env_file": ".env"
            }
        ],
        "deployments": []
    }


def add_deployment_record(config, provider, function_name=None, artifacts=None):
    """
    Add a record of a deployment to the configuration
    """
    if "deployments" not in config:
        config["deployments"] = []
        
    deployment = {
        "id": f"deploy-{len(config['deployments']) + 1}",
        "timestamp": datetime.now().isoformat(),
        "provider": provider,
        "functions": [function_name] if function_name else [f["name"] for f in config.get("functions", [])],
    }
    
    if artifacts:
        deployment["artifacts"] = artifacts
        
    config["deployments"].insert(0, deployment)  # Add at the beginning for chronological order
    save_config(config)
    
    return deployment["id"] 
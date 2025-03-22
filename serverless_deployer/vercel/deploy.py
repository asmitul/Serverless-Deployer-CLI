"""
Vercel deployment module for Serverless Deployer
"""
import os
import json
import logging
import requests
from requests.exceptions import RequestException

from ..utils.packaging import create_deployment_package
from ..utils.env import load_env_vars, read_env_file, format_env_for_provider
from ..config import add_deployment_record

logger = logging.getLogger("serverless_deployer")

VERCEL_API_URL = "https://api.vercel.com"


def deploy(config, function_name=None, env_file=None):
    """
    Deploy functions to Vercel
    
    Args:
        config: Configuration dictionary
        function_name: Name of specific function to deploy (optional)
        env_file: Path to .env file (optional)
        
    Returns:
        True if successful, False otherwise
    """
    # Load environment variables
    env_vars = load_env_vars(env_file)
    
    # Get Vercel credentials
    vercel_token = env_vars.get("VERCEL_TOKEN")
    vercel_org_id = env_vars.get("VERCEL_ORG_ID")
    vercel_project_id = env_vars.get("VERCEL_PROJECT_ID")
    
    if not vercel_token:
        logger.error("Vercel token not found. Set VERCEL_TOKEN environment variable.")
        return False
    
    # Set up HTTP headers
    headers = {
        "Authorization": f"Bearer {vercel_token}",
        "Content-Type": "application/json"
    }
    
    if vercel_org_id:
        headers["X-Vercel-Org-Id"] = vercel_org_id
        
    if not vercel_project_id:
        # Try to create a project if it doesn't exist
        project_name = config.get("project")
        if not project_name:
            logger.error("Project name not specified in configuration and VERCEL_PROJECT_ID not set.")
            return False
            
        try:
            vercel_project_id = _ensure_project_exists(project_name, headers)
        except Exception as e:
            logger.error(f"Failed to create/get Vercel project: {str(e)}")
            return False
            
    # Get functions to deploy
    functions = config.get("functions", [])
    if not functions:
        logger.error("No functions defined in configuration")
        return False
    
    # Filter to specific function if provided
    if function_name:
        functions = [f for f in functions if f["name"] == function_name]
        if not functions:
            logger.error(f"Function '{function_name}' not found in configuration")
            return False
    
    deployed_functions = []
    
    # Deploy each function
    for func in functions:
        try:
            function_path = func.get("path")
            if not function_path:
                logger.error(f"Path not specified for function '{func['name']}'")
                continue
                
            # Load function-specific environment variables
            func_env_file = func.get("env_file") or env_file
            if func_env_file:
                func_env_vars = read_env_file(func_env_file)
            else:
                func_env_vars = {}
                
            # Create deployment package
            logger.info(f"Creating deployment package for '{func['name']}'")
            zip_file_path = create_deployment_package(function_path)
            
            # Deploy to Vercel
            logger.info(f"Deploying '{func['name']}' to Vercel")
            
            # Set environment variables for this deployment
            _set_environment_variables(vercel_project_id, func_env_vars, headers)
            
            # Create deployment
            deployment_url = f"{VERCEL_API_URL}/v13/deployments"
            
            with open(zip_file_path, "rb") as zip_file:
                files = {
                    "file": (os.path.basename(zip_file_path), zip_file, "application/zip")
                }
                
                deployment_data = {
                    "name": func["name"],
                    "projectId": vercel_project_id,
                    "target": func.get("target", "production")
                }
                
                response = requests.post(
                    deployment_url,
                    headers={"Authorization": f"Bearer {vercel_token}"},
                    data={"meta": json.dumps(deployment_data)},
                    files=files
                )
            
            if response.status_code >= 400:
                logger.error(f"Failed to deploy function '{func['name']}': {response.text}")
                continue
                
            deployment_result = response.json()
            logger.info(f"Successfully deployed function '{func['name']}' to Vercel")
            
            # Cleanup deployment package
            os.remove(zip_file_path)
            
            # Add to deployment record
            deployed_functions.append({
                "name": func["name"],
                "url": deployment_result.get("url"),
                "deployment_id": deployment_result.get("id")
            })
            
        except Exception as e:
            logger.error(f"Failed to deploy function '{func['name']}': {str(e)}")
    
    # Add deployment record to config
    if deployed_functions:
        add_deployment_record(
            config, 
            "vercel", 
            function_name=function_name, 
            artifacts=deployed_functions
        )
        return True
    else:
        return False


def _ensure_project_exists(project_name, headers):
    """Ensure a Vercel project exists, create it if it doesn't"""
    # First check if project already exists
    projects_url = f"{VERCEL_API_URL}/v9/projects"
    
    try:
        response = requests.get(projects_url, headers=headers)
        response.raise_for_status()
        
        projects = response.json().get("projects", [])
        for project in projects:
            if project["name"] == project_name:
                return project["id"]
                
        # Project doesn't exist, create it
        project_data = {
            "name": project_name,
            "framework": None  # Detect automatically
        }
        
        response = requests.post(projects_url, headers=headers, json=project_data)
        response.raise_for_status()
        
        return response.json().get("id")
        
    except RequestException as e:
        logger.error(f"Failed to ensure project exists: {str(e)}")
        raise


def _set_environment_variables(project_id, env_vars, headers):
    """Set environment variables for a Vercel project"""
    if not env_vars:
        return
        
    env_url = f"{VERCEL_API_URL}/v9/projects/{project_id}/env"
    
    try:
        # Get existing env vars
        response = requests.get(env_url, headers=headers)
        response.raise_for_status()
        
        existing_envs = response.json().get("envs", [])
        existing_keys = {env["key"] for env in existing_envs}
        
        # Add new env vars
        for key, value in env_vars.items():
            if key in existing_keys:
                # Update existing env var
                for env in existing_envs:
                    if env["key"] == key:
                        env_id = env["id"]
                        update_url = f"{env_url}/{env_id}"
                        response = requests.patch(
                            update_url,
                            headers=headers,
                            json={"value": value}
                        )
                        response.raise_for_status()
            else:
                # Create new env var
                response = requests.post(
                    env_url,
                    headers=headers,
                    json={
                        "key": key,
                        "value": value,
                        "target": ["production", "preview", "development"]
                    }
                )
                response.raise_for_status()
                
    except RequestException as e:
        logger.warning(f"Failed to set environment variables: {str(e)}")
        # Continue with deployment anyway 
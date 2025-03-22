"""
AWS Lambda deployment module for Serverless Deployer
"""
import os
import json
import logging
import boto3
from botocore.exceptions import ClientError

from ..utils.packaging import create_deployment_package
from ..utils.env import load_env_vars, read_env_file, format_env_for_provider
from ..config import add_deployment_record

logger = logging.getLogger("serverless_deployer")


def deploy(config, function_name=None, env_file=None):
    """
    Deploy functions to AWS Lambda
    
    Args:
        config: Configuration dictionary
        function_name: Name of specific function to deploy (optional)
        env_file: Path to .env file (optional)
        
    Returns:
        True if successful, False otherwise
    """
    # Load environment variables
    env_vars = load_env_vars(env_file)
    
    # Get AWS credentials from environment
    aws_access_key = env_vars.get("AWS_ACCESS_KEY_ID")
    aws_secret_key = env_vars.get("AWS_SECRET_ACCESS_KEY")
    aws_region = env_vars.get("AWS_REGION", "us-east-1")
    
    if not aws_access_key or not aws_secret_key:
        logger.error("AWS credentials not found. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables.")
        return False
    
    # Initialize AWS client
    try:
        lambda_client = boto3.client(
            'lambda',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )
    except Exception as e:
        logger.error(f"Failed to initialize AWS client: {str(e)}")
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
            
            # Read deployment package
            with open(zip_file_path, "rb") as zip_file:
                zip_bytes = zip_file.read()
                
            # Format environment variables
            env_vars_config = format_env_for_provider(func_env_vars, "aws")
            
            # Determine handler
            handler = func.get("handler", "handler.lambda_handler")
            timeout = func.get("timeout", 30)
            memory_size = func.get("memory", 128)
            runtime = func.get("runtime", "python3.9")
            
            # Check if function exists
            try:
                lambda_client.get_function(FunctionName=func["name"])
                
                # Update existing function
                logger.info(f"Updating existing function '{func['name']}'")
                response = lambda_client.update_function_code(
                    FunctionName=func["name"],
                    ZipFile=zip_bytes,
                    Publish=True
                )
                
                # Update configuration if needed
                lambda_client.update_function_configuration(
                    FunctionName=func["name"],
                    Handler=handler,
                    Timeout=timeout,
                    MemorySize=memory_size,
                    Environment=env_vars_config
                )
                
            except ClientError as e:
                if e.response['Error']['Code'] == 'ResourceNotFoundException':
                    # Create new function
                    logger.info(f"Creating new function '{func['name']}'")
                    response = lambda_client.create_function(
                        FunctionName=func["name"],
                        Runtime=runtime,
                        Role=env_vars.get("AWS_LAMBDA_ROLE_ARN", ""),
                        Handler=handler,
                        Code={'ZipFile': zip_bytes},
                        Timeout=timeout,
                        MemorySize=memory_size,
                        Environment=env_vars_config
                    )
                else:
                    raise
                    
            logger.info(f"Successfully deployed function '{func['name']}'")
            
            # Cleanup deployment package
            os.remove(zip_file_path)
            
            # Add to deployment record
            deployed_functions.append({
                "name": func["name"],
                "version": response.get("Version"),
                "arn": response.get("FunctionArn")
            })
            
        except Exception as e:
            logger.error(f"Failed to deploy function '{func['name']}': {str(e)}")
            
    # Add deployment record to config
    if deployed_functions:
        add_deployment_record(
            config, 
            "aws", 
            function_name=function_name, 
            artifacts=deployed_functions
        )
        return True
    else:
        return False 
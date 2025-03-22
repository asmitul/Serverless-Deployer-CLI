"""
Packaging utilities for Serverless Deployer
"""
import os
import shutil
import tempfile
import zipfile
import logging

logger = logging.getLogger("serverless_deployer")


def create_deployment_package(function_path, include_deps=True, exclude=None):
    """
    Create a deployment package (ZIP) for a function
    
    Args:
        function_path: Path to the function code
        include_deps: Whether to include dependencies
        exclude: List of patterns to exclude
        
    Returns:
        Path to the created deployment package
    """
    if exclude is None:
        exclude = [".git", "__pycache__", "*.pyc", "*.pyo", "*.pyd", ".DS_Store", "node_modules"]
        
    # Get absolute path of function
    abs_function_path = os.path.abspath(function_path)
    function_dir = os.path.dirname(abs_function_path)
    function_name = os.path.splitext(os.path.basename(abs_function_path))[0]
    
    # Create temp directory for building
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Determine if we're packaging a single file or a directory
        if os.path.isfile(abs_function_path):
            # Single file
            target_file = os.path.join(temp_dir, os.path.basename(abs_function_path))
            shutil.copy2(abs_function_path, target_file)
        elif os.path.isdir(abs_function_path):
            # Directory
            _copy_directory(abs_function_path, temp_dir, exclude)
        else:
            raise ValueError(f"Path {function_path} does not exist or is not a file/directory")
            
        # Create zip file
        zip_path = os.path.join(os.getcwd(), f"{function_name}-deployment.zip")
        _create_zip_from_dir(temp_dir, zip_path)
        
        logger.info(f"Created deployment package at {zip_path}")
        return zip_path
        
    finally:
        # Clean up temp directory
        shutil.rmtree(temp_dir)


def _should_exclude(path, exclude_patterns):
    """Check if a path should be excluded based on patterns"""
    for pattern in exclude_patterns:
        if pattern.startswith("*"):
            # Check file extension
            if path.endswith(pattern[1:]):
                return True
        elif pattern in path:
            return True
    return False


def _copy_directory(source, target, exclude):
    """Copy directory contents recursively, respecting exclusions"""
    for item in os.listdir(source):
        s = os.path.join(source, item)
        
        # Skip if it matches exclusion pattern
        if _should_exclude(s, exclude):
            continue
            
        d = os.path.join(target, item)
        if os.path.isdir(s):
            os.makedirs(d, exist_ok=True)
            _copy_directory(s, d, exclude)
        else:
            shutil.copy2(s, d)


def _create_zip_from_dir(source_dir, output_path):
    """Create a zip file from a directory"""
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arcname)
                
    return output_path 
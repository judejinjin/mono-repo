"""
AWS Systems Manager Parameter Store Utilities
Provides utilities for storing and retrieving configuration parameters from AWS SSM Parameter Store.
"""

import boto3
import json
import logging
from typing import Dict, List, Optional, Any, Union
from botocore.exceptions import ClientError, NoCredentialsError
from pathlib import Path
import os

logger = logging.getLogger(__name__)


class ParameterStoreManager:
    """Manages AWS Systems Manager Parameter Store operations."""
    
    def __init__(self, region_name: str = None, profile_name: str = None):
        """
        Initialize Parameter Store manager.
        
        Args:
            region_name: AWS region name (defaults to AWS_DEFAULT_REGION env var)
            profile_name: AWS profile name (optional)
        """
        self.region_name = region_name or os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        self.profile_name = profile_name
        self._ssm_client = None
        
    @property
    def ssm_client(self):
        """Get or create SSM client."""
        if self._ssm_client is None:
            try:
                if self.profile_name:
                    session = boto3.Session(profile_name=self.profile_name)
                    self._ssm_client = session.client('ssm', region_name=self.region_name)
                else:
                    self._ssm_client = boto3.client('ssm', region_name=self.region_name)
            except NoCredentialsError:
                logger.error("AWS credentials not found. Please configure AWS credentials.")
                raise
        return self._ssm_client
    
    def put_parameter(
        self, 
        name: str, 
        value: str, 
        parameter_type: str = 'String',
        description: str = None,
        overwrite: bool = True,
        tags: List[Dict[str, str]] = None
    ) -> bool:
        """
        Store a parameter in Parameter Store.
        
        Args:
            name: Parameter name (e.g., '/dev/fastapi/port')
            value: Parameter value
            parameter_type: 'String', 'SecureString', or 'StringList'
            description: Optional parameter description
            overwrite: Whether to overwrite existing parameter
            tags: Optional list of tags
            
        Returns:
            True if successful, False otherwise
        """
        try:
            put_kwargs = {
                'Name': name,
                'Value': str(value),
                'Type': parameter_type,
                'Overwrite': overwrite
            }
            
            if description:
                put_kwargs['Description'] = description
                
            if tags:
                put_kwargs['Tags'] = tags
                
            response = self.ssm_client.put_parameter(**put_kwargs)
            logger.info(f"Successfully stored parameter: {name}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to store parameter {name}: {e}")
            return False
    
    def get_parameter(
        self, 
        name: str, 
        decrypt: bool = True
    ) -> Optional[str]:
        """
        Get a single parameter from Parameter Store.
        
        Args:
            name: Parameter name
            decrypt: Whether to decrypt SecureString parameters
            
        Returns:
            Parameter value or None if not found
        """
        try:
            response = self.ssm_client.get_parameter(
                Name=name,
                WithDecryption=decrypt
            )
            return response['Parameter']['Value']
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ParameterNotFound':
                logger.warning(f"Parameter not found: {name}")
            else:
                logger.error(f"Failed to get parameter {name}: {e}")
            return None
    
    def get_parameters_by_path(
        self, 
        path: str, 
        recursive: bool = True,
        decrypt: bool = True
    ) -> Dict[str, str]:
        """
        Get multiple parameters by path prefix.
        
        Args:
            path: Parameter path prefix (e.g., '/dev/fastapi/')
            recursive: Whether to get parameters recursively
            decrypt: Whether to decrypt SecureString parameters
            
        Returns:
            Dictionary of parameter names to values
        """
        parameters = {}
        
        try:
            paginator = self.ssm_client.get_paginator('get_parameters_by_path')
            
            for page in paginator.paginate(
                Path=path,
                Recursive=recursive,
                WithDecryption=decrypt
            ):
                for param in page['Parameters']:
                    # Remove the path prefix to get the parameter key
                    key = param['Name'].replace(path.rstrip('/') + '/', '')
                    parameters[key] = param['Value']
                    
            logger.info(f"Retrieved {len(parameters)} parameters from path: {path}")
            return parameters
            
        except ClientError as e:
            logger.error(f"Failed to get parameters from path {path}: {e}")
            return {}
    
    def get_environment_parameters(
        self, 
        environment: str, 
        app_name: str = None
    ) -> Dict[str, str]:
        """
        Get all parameters for a specific environment and optionally app.
        
        Args:
            environment: Environment name (dev, uat, prod)
            app_name: Optional app name to filter by
            
        Returns:
            Dictionary of parameter names to values
        """
        if app_name:
            path = f"/{environment}/{app_name}/"
        else:
            path = f"/{environment}/"
            
        return self.get_parameters_by_path(path, recursive=True)
    
    def put_environment_parameters(
        self, 
        environment: str, 
        app_name: str, 
        parameters: Dict[str, Any],
        secure_parameters: List[str] = None
    ) -> Dict[str, bool]:
        """
        Store multiple parameters for an environment and app.
        
        Args:
            environment: Environment name (dev, uat, prod)
            app_name: Application name
            parameters: Dictionary of parameter names to values
            secure_parameters: List of parameter names that should be SecureString
            
        Returns:
            Dictionary of parameter names to success status
        """
        secure_params = secure_parameters or []
        results = {}
        
        for param_name, param_value in parameters.items():
            full_name = f"/{environment}/{app_name}/{param_name}"
            param_type = 'SecureString' if param_name in secure_params else 'String'
            
            success = self.put_parameter(
                name=full_name,
                value=str(param_value),
                parameter_type=param_type,
                description=f"{app_name} {param_name} for {environment} environment"
            )
            results[param_name] = success
            
        return results
    
    def delete_parameter(self, name: str) -> bool:
        """
        Delete a parameter from Parameter Store.
        
        Args:
            name: Parameter name to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.ssm_client.delete_parameter(Name=name)
            logger.info(f"Successfully deleted parameter: {name}")
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ParameterNotFound':
                logger.warning(f"Parameter not found for deletion: {name}")
                return True  # Consider this success since the end result is the same
            else:
                logger.error(f"Failed to delete parameter {name}: {e}")
                return False
    
    def list_parameters(
        self, 
        path_prefix: str = None
    ) -> List[Dict[str, Any]]:
        """
        List parameters with optional path filtering.
        
        Args:
            path_prefix: Optional path prefix to filter by
            
        Returns:
            List of parameter metadata dictionaries
        """
        try:
            paginator = self.ssm_client.get_paginator('describe_parameters')
            
            paginate_kwargs = {}
            if path_prefix:
                paginate_kwargs['ParameterFilters'] = [
                    {
                        'Key': 'Name',
                        'Option': 'BeginsWith',
                        'Values': [path_prefix]
                    }
                ]
            
            parameters = []
            for page in paginator.paginate(**paginate_kwargs):
                parameters.extend(page['Parameters'])
                
            return parameters
            
        except ClientError as e:
            logger.error(f"Failed to list parameters: {e}")
            return []
    
    def parameter_exists(self, name: str) -> bool:
        """
        Check if a parameter exists.
        
        Args:
            name: Parameter name to check
            
        Returns:
            True if parameter exists, False otherwise
        """
        try:
            self.ssm_client.get_parameter(Name=name)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ParameterNotFound':
                return False
            else:
                logger.error(f"Error checking parameter existence {name}: {e}")
                return False
    
    def validate_parameter_access(self, environment: str) -> bool:
        """
        Validate that we can access parameters for the given environment.
        
        Args:
            environment: Environment to validate access for
            
        Returns:
            True if access is valid, False otherwise
        """
        test_param_name = f"/{environment}/test/access_validation"
        test_value = "validation_test"
        
        # Try to put and get a test parameter
        if self.put_parameter(test_param_name, test_value):
            retrieved_value = self.get_parameter(test_param_name)
            if retrieved_value == test_value:
                # Clean up test parameter
                self.delete_parameter(test_param_name)
                logger.info(f"Parameter Store access validated for environment: {environment}")
                return True
        
        logger.error(f"Parameter Store access validation failed for environment: {environment}")
        return False


class ParameterStoreConfig:
    """Configuration wrapper that loads from Parameter Store."""
    
    def __init__(
        self, 
        environment: str,
        region_name: str = None,
        cache_parameters: bool = True
    ):
        """
        Initialize Parameter Store configuration.
        
        Args:
            environment: Environment name (dev, uat, prod)
            region_name: AWS region name
            cache_parameters: Whether to cache parameters in memory
        """
        self.environment = environment
        self.cache_parameters = cache_parameters
        self.parameter_manager = ParameterStoreManager(region_name)
        self._parameter_cache = {}
        
    def get(self, app_name: str, parameter_name: str, default: Any = None) -> Any:
        """
        Get a configuration parameter.
        
        Args:
            app_name: Application name
            parameter_name: Parameter name
            default: Default value if parameter not found
            
        Returns:
            Parameter value or default
        """
        cache_key = f"{app_name}.{parameter_name}"
        
        # Check cache first if caching is enabled
        if self.cache_parameters and cache_key in self._parameter_cache:
            return self._parameter_cache[cache_key]
        
        full_name = f"/{self.environment}/{app_name}/{parameter_name}"
        value = self.parameter_manager.get_parameter(full_name)
        
        if value is None:
            value = default
        
        # Cache the value if caching is enabled
        if self.cache_parameters:
            self._parameter_cache[cache_key] = value
            
        return value
    
    def get_app_config(self, app_name: str) -> Dict[str, str]:
        """
        Get all configuration parameters for an application.
        
        Args:
            app_name: Application name
            
        Returns:
            Dictionary of parameter names to values
        """
        cache_key = f"_app_config_{app_name}"
        
        # Check cache first if caching is enabled
        if self.cache_parameters and cache_key in self._parameter_cache:
            return self._parameter_cache[cache_key]
        
        config = self.parameter_manager.get_environment_parameters(
            self.environment, 
            app_name
        )
        
        # Cache the config if caching is enabled
        if self.cache_parameters:
            self._parameter_cache[cache_key] = config
            
        return config
    
    def refresh_cache(self):
        """Clear the parameter cache to force fresh reads."""
        self._parameter_cache.clear()
        logger.info("Parameter cache cleared")


# Convenience functions for common operations
def get_parameter_store_manager(region_name: str = None) -> ParameterStoreManager:
    """Get a ParameterStoreManager instance."""
    return ParameterStoreManager(region_name)


def get_environment_config(
    environment: str, 
    app_name: str = None,
    region_name: str = None
) -> Dict[str, str]:
    """
    Get all parameters for an environment and optionally an app.
    
    Args:
        environment: Environment name (dev, uat, prod)
        app_name: Optional application name
        region_name: AWS region name
        
    Returns:
        Dictionary of parameter names to values
    """
    manager = ParameterStoreManager(region_name)
    return manager.get_environment_parameters(environment, app_name)


def put_environment_config(
    environment: str,
    app_name: str,
    config: Dict[str, Any],
    secure_parameters: List[str] = None,
    region_name: str = None
) -> Dict[str, bool]:
    """
    Store configuration parameters for an environment and app.
    
    Args:
        environment: Environment name (dev, uat, prod)
        app_name: Application name
        config: Dictionary of parameter names to values
        secure_parameters: List of parameter names that should be SecureString
        region_name: AWS region name
        
    Returns:
        Dictionary of parameter names to success status
    """
    manager = ParameterStoreManager(region_name)
    return manager.put_environment_parameters(
        environment, 
        app_name, 
        config, 
        secure_parameters
    )
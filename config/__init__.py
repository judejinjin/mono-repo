"""
Configuration management module for mono-repo project.
Handles environment-specific configuration loading with AWS Parameter Store and .env fallback support.
"""

import os
import json
import yaml
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Load environment variables from .env file as fallback
try:
    from dotenv import load_dotenv
    # Load .env file from config directory
    CONFIG_PATH = Path(__file__).parent
    env_path = CONFIG_PATH / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Loaded environment variables from {env_path}")
    else:
        print(f"⚠️  No .env file found at {env_path}")
except ImportError:
    print("⚠️  python-dotenv not installed. Run: pip install python-dotenv")

# Determine current environment
ENVIRONMENT = os.getenv('ENVIRONMENT', os.getenv('ENV', 'dev')).lower()
CONFIG_DIR = Path(__file__).parent

# Configuration source priority: Parameter Store > .env > YAML files
USE_PARAMETER_STORE = os.getenv('USE_PARAMETER_STORE', 'true').lower() == 'true'


class ConfigManager:
    """Manages configuration loading and caching with Parameter Store support."""
    
    def __init__(self):
        self._config_cache = {}
        self._parameter_store_config = None
        
        # Initialize Parameter Store if enabled
        self._use_parameter_store = USE_PARAMETER_STORE
        if self._use_parameter_store:
            try:
                from libs.cloud.parameter_store import ParameterStoreConfig
                self._parameter_store_config = ParameterStoreConfig(ENVIRONMENT)
                logger.info("✅ Parameter Store configuration initialized")
            except Exception as e:
                logger.warning(f"⚠️  Parameter Store initialization failed, falling back to YAML: {e}")
                self._use_parameter_store = False
        
        # Load YAML configurations (fallback or primary)
        self._load_base_config()
        self._load_environment_config()
    
    def _load_base_config(self):
        """Load base configuration that applies to all environments."""
        base_config_path = CONFIG_DIR / 'base.yaml'
        if base_config_path.exists():
            with open(base_config_path, 'r') as f:
                self._config_cache['base'] = yaml.safe_load(f)
        else:
            self._config_cache['base'] = {}
    
    def _load_environment_config(self):
        """Load environment-specific configuration."""
        env_config_path = CONFIG_DIR / f'{ENVIRONMENT}.yaml'
        if env_config_path.exists():
            with open(env_config_path, 'r') as f:
                env_config = yaml.safe_load(f)
                # Merge with base config
                self._config_cache[ENVIRONMENT] = self._deep_merge(
                    self._config_cache['base'].copy(), 
                    env_config
                )
        else:
            self._config_cache[ENVIRONMENT] = self._config_cache['base'].copy()
    
    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """Deep merge two dictionaries."""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    def get_config(self, key: Optional[str] = None) -> Any:
        """Get configuration value with Parameter Store priority."""
        # Start with YAML configuration
        config = self._config_cache.get(ENVIRONMENT, {})
        
        # Override with Parameter Store values if available
        if self._use_parameter_store and self._parameter_store_config:
            try:
                # Get all parameter store configurations for common apps
                apps = ['terraform', 'eks', 'rds', 'fastapi', 'web', 'dash', 'airflow', 'security', 'monitoring', 'ecr', 's3']
                
                for app in apps:
                    app_config = self._parameter_store_config.get_app_config(app)
                    if app_config:
                        # Convert parameter store keys to nested structure
                        if app not in config:
                            config[app] = {}
                        config[app].update(app_config)
                        
            except Exception as e:
                logger.warning(f"⚠️  Error loading from Parameter Store, using YAML fallback: {e}")
        
        if key:
            return config.get(key)
        return config
    
    def get_database_config(self, db_name: str) -> Dict[str, Any]:
        """Get database configuration for specific database."""
        db_configs = self.get_config('databases')
        if not db_configs or db_name not in db_configs:
            raise ValueError(f"Database configuration for '{db_name}' not found")
        
        db_config = db_configs[db_name].copy()
        
        # Load secrets if using AWS Secrets Manager
        if db_config.get('use_secrets_manager'):
            secret_name = db_config.get('secret_name')
            if secret_name:
                # Import here to avoid circular imports
                from libs.cloud.aws_secrets import get_secret
                secret = get_secret(secret_name)
                db_config.update(secret)
        
        return db_config
    
    def get_cloud_config(self, service: str) -> Dict[str, Any]:
        """Get cloud service configuration."""
        cloud_configs = self.get_config('cloud')
        if not cloud_configs or service not in cloud_configs:
            raise ValueError(f"Cloud configuration for '{service}' not found")
        
        return cloud_configs[service]


# Global configuration manager instance
_config_manager = ConfigManager()

# Public API
def refresh_config_cache():
    """Refresh configuration cache to reload from Parameter Store."""
    global _config_manager
    if _config_manager._use_parameter_store and _config_manager._parameter_store_config:
        _config_manager._parameter_store_config.refresh_cache()
    _config_manager._config_cache.clear()
    _config_manager._load_base_config()
    _config_manager._load_environment_config()
    logger.info("Configuration cache refreshed")

def get_parameter_store_value(app_name: str, param_name: str, default: Any = None) -> Any:
    """
    Get a value directly from Parameter Store.
    
    Args:
        app_name: Application name
        param_name: Parameter name
        default: Default value if not found
        
    Returns:
        Parameter value or default
    """
    if _config_manager._use_parameter_store and _config_manager._parameter_store_config:
        return _config_manager._parameter_store_config.get(app_name, param_name, default)
    return default

def set_parameter_store_value(
    app_name: str, 
    param_name: str, 
    value: Any,
    secure: bool = False
) -> bool:
    """
    Set a value in Parameter Store.
    
    Args:
        app_name: Application name
        param_name: Parameter name
        value: Parameter value
        secure: Whether to store as SecureString
        
    Returns:
        True if successful, False otherwise
    """
    if _config_manager._use_parameter_store and _config_manager._parameter_store_config:
        full_name = f"/{ENVIRONMENT}/{app_name}/{param_name}"
        param_type = 'SecureString' if secure else 'String'
        return _config_manager._parameter_store_config.parameter_manager.put_parameter(
            full_name, str(value), param_type
        )
    return False
def get_config(key: Optional[str] = None) -> Any:
    """Get configuration value."""
    return _config_manager.get_config(key)

def get_db_config(db_name: str) -> Dict[str, Any]:
    """Get database configuration."""
    return _config_manager.get_database_config(db_name)

def get_cloud_config(service: str) -> Dict[str, Any]:
    """Get cloud service configuration."""
    return _config_manager.get_cloud_config(service)

def get_environment() -> str:
    """Get current environment."""
    return ENVIRONMENT


def get_aws_credentials() -> Dict[str, str]:
    """Get AWS credentials from Parameter Store or environment variables."""
    credentials = {}
    
    # Try Parameter Store first if enabled
    if _config_manager._use_parameter_store and _config_manager._parameter_store_config:
        try:
            param_config = _config_manager._parameter_store_config
            credentials['aws_access_key_id'] = param_config.get('aws', 'access_key_id')
            credentials['aws_secret_access_key'] = param_config.get('aws', 'secret_access_key')
            credentials['aws_session_token'] = param_config.get('aws', 'session_token')
            credentials['region_name'] = param_config.get('aws', 'region', 'us-east-1')
            credentials['profile_name'] = param_config.get('aws', 'profile')
            
            # Filter out None values
            credentials = {k: v for k, v in credentials.items() if v is not None}
            
            if credentials:
                logger.info("✅ AWS credentials loaded from Parameter Store")
                return credentials
        except Exception as e:
            logger.warning(f"⚠️  Failed to load AWS credentials from Parameter Store: {e}")
    
    # Fallback to environment variables
    if os.getenv('AWS_ACCESS_KEY_ID'):
        credentials['aws_access_key_id'] = os.getenv('AWS_ACCESS_KEY_ID')
    if os.getenv('AWS_SECRET_ACCESS_KEY'):
        credentials['aws_secret_access_key'] = os.getenv('AWS_SECRET_ACCESS_KEY')
    if os.getenv('AWS_SESSION_TOKEN'):
        credentials['aws_session_token'] = os.getenv('AWS_SESSION_TOKEN')
    
    # Region settings
    credentials['region_name'] = os.getenv('AWS_REGION', os.getenv('AWS_DEFAULT_REGION', 'us-east-1'))
    
    # Profile (for CLI compatibility)
    if os.getenv('AWS_PROFILE'):
        credentials['profile_name'] = os.getenv('AWS_PROFILE')
    
    return credentials


def setup_aws_environment():
    """Set up AWS environment variables for consistent access."""
    # Ensure AWS environment variables are properly set
    aws_creds = get_aws_credentials()
    
    if 'aws_access_key_id' in aws_creds:
        os.environ['AWS_ACCESS_KEY_ID'] = aws_creds['aws_access_key_id']
    if 'aws_secret_access_key' in aws_creds:
        os.environ['AWS_SECRET_ACCESS_KEY'] = aws_creds['aws_secret_access_key']
    if 'aws_session_token' in aws_creds:
        os.environ['AWS_SESSION_TOKEN'] = aws_creds['aws_session_token']
    
    os.environ['AWS_DEFAULT_REGION'] = aws_creds['region_name']
    os.environ['AWS_REGION'] = aws_creds['region_name']
    
    return aws_creds


def get_boto3_session():
    """Get a boto3 session with credentials from config/.env file."""
    try:
        import boto3
        credentials = get_aws_credentials()
        
        session_kwargs = {
            'region_name': credentials['region_name']
        }
        
        if 'aws_access_key_id' in credentials:
            session_kwargs['aws_access_key_id'] = credentials['aws_access_key_id']
        if 'aws_secret_access_key' in credentials:
            session_kwargs['aws_secret_access_key'] = credentials['aws_secret_access_key']
        if 'aws_session_token' in credentials:
            session_kwargs['aws_session_token'] = credentials['aws_session_token']
        if 'profile_name' in credentials:
            session_kwargs['profile_name'] = credentials['profile_name']
        
        return boto3.Session(**session_kwargs)
    
    except ImportError:
        print("⚠️  boto3 not installed. Run: pip install boto3")
        return None

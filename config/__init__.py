"""
Configuration management module for mono-repo project.
Handles environment-specific configuration loading with .env support.
"""

import os
import json
import yaml
from typing import Dict, Any, Optional
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load .env file from project root
    PROJECT_ROOT = Path(__file__).parent.parent
    env_path = PROJECT_ROOT / '.env'
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


class ConfigManager:
    """Manages configuration loading and caching."""
    
    def __init__(self):
        self._config_cache = {}
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
        """Get configuration value."""
        config = self._config_cache.get(ENVIRONMENT, {})
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
    """Get AWS credentials from environment variables."""
    credentials = {}
    
    # Primary AWS credentials
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
    """Get a boto3 session with credentials from .env file."""
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

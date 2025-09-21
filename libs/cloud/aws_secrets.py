"""
AWS Secrets Manager integration module.
"""

try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def get_secret(secret_name: str) -> Dict[str, Any]:
    """Retrieve secret from AWS Secrets Manager."""
    if not BOTO3_AVAILABLE:
        raise ImportError("boto3 is required for AWS Secrets Manager integration")
    
    from config import get_cloud_config
    
    config = get_cloud_config('secrets_manager')
    client = boto3.client('secretsmanager', region_name=config['region'])
    
    try:
        # Add environment prefix if configured
        prefix = config.get('prefix', '')
        full_secret_name = f"{prefix}{secret_name}" if prefix else secret_name
        
        response = client.get_secret_value(SecretId=full_secret_name)
        secret_string = response['SecretString']
        return json.loads(secret_string)
    except ClientError as e:
        logger.error(f"Failed to retrieve secret {secret_name}: {e}")
        raise

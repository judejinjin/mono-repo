"""
Cloud services abstraction layer.
Provides unified access to AWS services across environments.
"""

import boto3
import json
import logging
from typing import Dict, Any, Optional, List
from botocore.exceptions import ClientError
from config import get_cloud_config

logger = logging.getLogger(__name__)


class AWSSecretsManager:
    """AWS Secrets Manager client wrapper."""
    
    def __init__(self):
        self.config = get_cloud_config('secrets_manager')
        self.client = boto3.client('secretsmanager', region_name=self.config['region'])
    
    def get_secret(self, secret_name: str) -> Dict[str, Any]:
        """Retrieve secret from AWS Secrets Manager."""
        try:
            # Add environment prefix if configured
            prefix = self.config.get('prefix', '')
            full_secret_name = f"{prefix}{secret_name}" if prefix else secret_name
            
            response = self.client.get_secret_value(SecretId=full_secret_name)
            secret_string = response['SecretString']
            return json.loads(secret_string)
        except ClientError as e:
            logger.error(f"Failed to retrieve secret {secret_name}: {e}")
            raise
    
    def put_secret(self, secret_name: str, secret_value: Dict[str, Any]) -> bool:
        """Store secret in AWS Secrets Manager."""
        try:
            prefix = self.config.get('prefix', '')
            full_secret_name = f"{prefix}{secret_name}" if prefix else secret_name
            
            self.client.put_secret_value(
                SecretId=full_secret_name,
                SecretString=json.dumps(secret_value)
            )
            return True
        except ClientError as e:
            logger.error(f"Failed to store secret {secret_name}: {e}")
            return False


class S3Manager:
    """S3 client wrapper with environment-specific configuration."""
    
    def __init__(self):
        self.config = get_cloud_config('s3')
        self.aws_config = get_cloud_config('aws')
        self.client = boto3.client('s3', region_name=self.aws_config['region'])
        self.default_bucket = self.config['default_bucket']
    
    def upload_file(self, file_path: str, key: str, bucket: Optional[str] = None) -> bool:
        """Upload file to S3."""
        bucket = bucket or self.default_bucket
        try:
            self.client.upload_file(file_path, bucket, key)
            logger.info(f"Uploaded {file_path} to s3://{bucket}/{key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to upload {file_path}: {e}")
            return False
    
    def download_file(self, key: str, file_path: str, bucket: Optional[str] = None) -> bool:
        """Download file from S3."""
        bucket = bucket or self.default_bucket
        try:
            self.client.download_file(bucket, key, file_path)
            logger.info(f"Downloaded s3://{bucket}/{key} to {file_path}")
            return True
        except ClientError as e:
            logger.error(f"Failed to download {key}: {e}")
            return False
    
    def list_objects(self, prefix: str = "", bucket: Optional[str] = None) -> List[str]:
        """List objects in S3 bucket with given prefix."""
        bucket = bucket or self.default_bucket
        try:
            response = self.client.list_objects_v2(Bucket=bucket, Prefix=prefix)
            return [obj['Key'] for obj in response.get('Contents', [])]
        except ClientError as e:
            logger.error(f"Failed to list objects: {e}")
            return []
    
    def delete_object(self, key: str, bucket: Optional[str] = None) -> bool:
        """Delete object from S3."""
        bucket = bucket or self.default_bucket
        try:
            self.client.delete_object(Bucket=bucket, Key=key)
            logger.info(f"Deleted s3://{bucket}/{key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete {key}: {e}")
            return False


# Global instances
_secrets_manager = AWSSecretsManager()
_s3_manager = S3Manager()

# Public API
def get_secret(secret_name: str) -> Dict[str, Any]:
    """Get secret from AWS Secrets Manager."""
    return _secrets_manager.get_secret(secret_name)

def put_secret(secret_name: str, secret_value: Dict[str, Any]) -> bool:
    """Store secret in AWS Secrets Manager."""
    return _secrets_manager.put_secret(secret_name, secret_value)

def upload_to_s3(file_path: str, key: str, bucket: Optional[str] = None) -> bool:
    """Upload file to S3."""
    return _s3_manager.upload_file(file_path, key, bucket)

def download_from_s3(key: str, file_path: str, bucket: Optional[str] = None) -> bool:
    """Download file from S3."""
    return _s3_manager.download_file(key, file_path, bucket)

def list_s3_objects(prefix: str = "", bucket: Optional[str] = None) -> List[str]:
    """List S3 objects."""
    return _s3_manager.list_objects(prefix, bucket)

def delete_from_s3(key: str, bucket: Optional[str] = None) -> bool:
    """Delete object from S3."""
    return _s3_manager.delete_object(key, bucket)

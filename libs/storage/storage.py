"""
Storage abstraction library for the mono-repo risk platform.
Provides unified interface for S3, Redis, and database operations.
"""

import boto3
import redis
from typing import Optional, Dict, Any, List, Union, IO
from datetime import datetime, timedelta
import logging
import json
import os
from pathlib import Path
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class S3Client:
    """AWS S3 client wrapper with error handling and convenience methods."""
    
    def __init__(self, bucket_name: str = None, region: str = None):
        """
        Initialize S3 client.
        Will work with local environment or AWS credentials when available.
        """
        self.bucket_name = bucket_name or os.getenv('S3_BUCKET_NAME')
        self.region = region or os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        
        # Initialize client - will use environment credentials when available
        try:
            self.client = boto3.client('s3', region_name=self.region)
            self.resource = boto3.resource('s3', region_name=self.region)
            logger.info(f"S3 client initialized for region: {self.region}")
        except Exception as e:
            logger.warning(f"S3 client initialization failed: {e}. Will work once AWS credentials are configured.")
            self.client = None
            self.resource = None
    
    def _ensure_client(self):
        """Ensure client is available or raise exception."""
        if self.client is None:
            raise RuntimeError("S3 client not initialized. Please configure AWS credentials.")
    
    def upload_file(self, local_path: str, s3_key: str, bucket: str = None) -> bool:
        """Upload file to S3."""
        self._ensure_client()
        bucket = bucket or self.bucket_name
        
        try:
            self.client.upload_file(local_path, bucket, s3_key)
            logger.info(f"Uploaded {local_path} to s3://{bucket}/{s3_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to upload {local_path} to S3: {e}")
            return False
    
    def download_file(self, s3_key: str, local_path: str, bucket: str = None) -> bool:
        """Download file from S3."""
        self._ensure_client()
        bucket = bucket or self.bucket_name
        
        try:
            # Ensure local directory exists
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)
            self.client.download_file(bucket, s3_key, local_path)
            logger.info(f"Downloaded s3://{bucket}/{s3_key} to {local_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to download {s3_key} from S3: {e}")
            return False
    
    def upload_string(self, content: str, s3_key: str, bucket: str = None, 
                     content_type: str = 'text/plain') -> bool:
        """Upload string content to S3."""
        self._ensure_client()
        bucket = bucket or self.bucket_name
        
        try:
            self.client.put_object(
                Bucket=bucket,
                Key=s3_key,
                Body=content,
                ContentType=content_type
            )
            logger.info(f"Uploaded string content to s3://{bucket}/{s3_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to upload string to S3: {e}")
            return False
    
    def download_string(self, s3_key: str, bucket: str = None) -> Optional[str]:
        """Download string content from S3."""
        self._ensure_client()
        bucket = bucket or self.bucket_name
        
        try:
            response = self.client.get_object(Bucket=bucket, Key=s3_key)
            content = response['Body'].read().decode('utf-8')
            logger.debug(f"Downloaded string from s3://{bucket}/{s3_key}")
            return content
        except Exception as e:
            logger.error(f"Failed to download string from S3: {e}")
            return None
    
    def upload_json(self, data: Dict[str, Any], s3_key: str, bucket: str = None) -> bool:
        """Upload JSON data to S3."""
        try:
            json_string = json.dumps(data, indent=2, default=str)
            return self.upload_string(json_string, s3_key, bucket, 'application/json')
        except Exception as e:
            logger.error(f"Failed to serialize JSON for S3 upload: {e}")
            return False
    
    def download_json(self, s3_key: str, bucket: str = None) -> Optional[Dict[str, Any]]:
        """Download JSON data from S3."""
        content = self.download_string(s3_key, bucket)
        if content is None:
            return None
        
        try:
            return json.loads(content)
        except Exception as e:
            logger.error(f"Failed to parse JSON from S3: {e}")
            return None
    
    def list_objects(self, prefix: str = '', bucket: str = None) -> List[str]:
        """List objects in S3 bucket with prefix."""
        self._ensure_client()
        bucket = bucket or self.bucket_name
        
        try:
            response = self.client.list_objects_v2(Bucket=bucket, Prefix=prefix)
            objects = []
            if 'Contents' in response:
                objects = [obj['Key'] for obj in response['Contents']]
            logger.debug(f"Listed {len(objects)} objects with prefix '{prefix}'")
            return objects
        except Exception as e:
            logger.error(f"Failed to list S3 objects: {e}")
            return []
    
    def delete_object(self, s3_key: str, bucket: str = None) -> bool:
        """Delete object from S3."""
        self._ensure_client()
        bucket = bucket or self.bucket_name
        
        try:
            self.client.delete_object(Bucket=bucket, Key=s3_key)
            logger.info(f"Deleted s3://{bucket}/{s3_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete S3 object: {e}")
            return False
    
    def object_exists(self, s3_key: str, bucket: str = None) -> bool:
        """Check if object exists in S3."""
        self._ensure_client()
        bucket = bucket or self.bucket_name
        
        try:
            self.client.head_object(Bucket=bucket, Key=s3_key)
            return True
        except self.client.exceptions.NoSuchKey:
            return False
        except Exception as e:
            logger.error(f"Error checking S3 object existence: {e}")
            return False

class RedisClient:
    """Redis client wrapper with error handling and convenience methods."""
    
    def __init__(self, host: str = None, port: int = None, db: int = None, 
                 password: str = None, decode_responses: bool = True):
        """
        Initialize Redis client.
        Uses environment variables when parameters not provided.
        """
        self.host = host or os.getenv('REDIS_HOST', 'localhost')
        self.port = port or int(os.getenv('REDIS_PORT', '6379'))
        self.db = db or int(os.getenv('REDIS_DB', '0'))
        self.password = password or os.getenv('REDIS_PASSWORD')
        
        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=decode_responses,
                socket_timeout=5,
                socket_connect_timeout=5
            )
            # Test connection
            self.client.ping()
            logger.info(f"Redis client connected to {self.host}:{self.port}")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Will work once Redis is available.")
            self.client = None
    
    def _ensure_client(self):
        """Ensure client is available or raise exception."""
        if self.client is None:
            raise RuntimeError("Redis client not initialized. Please check Redis connection.")
    
    def set(self, key: str, value: str, expire: int = None) -> bool:
        """Set key-value pair with optional expiration."""
        self._ensure_client()
        
        try:
            result = self.client.set(key, value, ex=expire)
            logger.debug(f"Set Redis key: {key}")
            return result
        except Exception as e:
            logger.error(f"Failed to set Redis key: {e}")
            return False
    
    def get(self, key: str) -> Optional[str]:
        """Get value by key."""
        self._ensure_client()
        
        try:
            value = self.client.get(key)
            logger.debug(f"Retrieved Redis key: {key}")
            return value
        except Exception as e:
            logger.error(f"Failed to get Redis key: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete key."""
        self._ensure_client()
        
        try:
            result = self.client.delete(key)
            logger.debug(f"Deleted Redis key: {key}")
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to delete Redis key: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        self._ensure_client()
        
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"Failed to check Redis key existence: {e}")
            return False
    
    def set_json(self, key: str, data: Dict[str, Any], expire: int = None) -> bool:
        """Set JSON data."""
        try:
            json_string = json.dumps(data, default=str)
            return self.set(key, json_string, expire)
        except Exception as e:
            logger.error(f"Failed to serialize JSON for Redis: {e}")
            return False
    
    def get_json(self, key: str) -> Optional[Dict[str, Any]]:
        """Get JSON data."""
        value = self.get(key)
        if value is None:
            return None
        
        try:
            return json.loads(value)
        except Exception as e:
            logger.error(f"Failed to parse JSON from Redis: {e}")
            return None
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment numeric key."""
        self._ensure_client()
        
        try:
            result = self.client.incrby(key, amount)
            logger.debug(f"Incremented Redis key {key} by {amount}")
            return result
        except Exception as e:
            logger.error(f"Failed to increment Redis key: {e}")
            return None
    
    def expire(self, key: str, seconds: int) -> bool:
        """Set expiration for key."""
        self._ensure_client()
        
        try:
            result = self.client.expire(key, seconds)
            logger.debug(f"Set expiration for Redis key: {key}")
            return result
        except Exception as e:
            logger.error(f"Failed to set Redis key expiration: {e}")
            return False
    
    def keys_pattern(self, pattern: str) -> List[str]:
        """Get keys matching pattern."""
        self._ensure_client()
        
        try:
            keys = self.client.keys(pattern)
            logger.debug(f"Found {len(keys)} keys matching pattern: {pattern}")
            return keys
        except Exception as e:
            logger.error(f"Failed to search Redis keys: {e}")
            return []

class CacheManager:
    """High-level cache management using Redis with fallback to in-memory."""
    
    def __init__(self, redis_client: RedisClient = None, default_ttl: int = 3600):
        """Initialize cache manager."""
        self.redis_client = redis_client or RedisClient()
        self.default_ttl = default_ttl
        self._memory_cache = {}  # Fallback for when Redis is unavailable
        
        # Check if Redis is available
        self.use_redis = self.redis_client.client is not None
        if not self.use_redis:
            logger.warning("Redis unavailable, using in-memory cache fallback")
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set cached value."""
        ttl = ttl or self.default_ttl
        
        if self.use_redis:
            # Try Redis first
            try:
                if isinstance(value, (dict, list)):
                    return self.redis_client.set_json(key, value, ttl)
                else:
                    return self.redis_client.set(key, str(value), ttl)
            except Exception as e:
                logger.warning(f"Redis cache set failed, using memory: {e}")
                self.use_redis = False
        
        # Fallback to memory cache
        expiry = datetime.now() + timedelta(seconds=ttl)
        self._memory_cache[key] = {
            'value': value,
            'expiry': expiry
        }
        return True
    
    def get(self, key: str) -> Any:
        """Get cached value."""
        if self.use_redis:
            # Try Redis first
            try:
                # Try as JSON first, then as string
                value = self.redis_client.get_json(key)
                if value is not None:
                    return value
                return self.redis_client.get(key)
            except Exception as e:
                logger.warning(f"Redis cache get failed, checking memory: {e}")
                self.use_redis = False
        
        # Fallback to memory cache
        cached = self._memory_cache.get(key)
        if cached is None:
            return None
        
        # Check expiry
        if datetime.now() > cached['expiry']:
            del self._memory_cache[key]
            return None
        
        return cached['value']
    
    def delete(self, key: str) -> bool:
        """Delete cached value."""
        if self.use_redis:
            try:
                return self.redis_client.delete(key)
            except Exception:
                self.use_redis = False
        
        # Memory cache cleanup
        if key in self._memory_cache:
            del self._memory_cache[key]
            return True
        return False
    
    def clear_expired(self):
        """Clear expired entries from memory cache."""
        now = datetime.now()
        expired_keys = [
            key for key, data in self._memory_cache.items()
            if now > data['expiry']
        ]
        
        for key in expired_keys:
            del self._memory_cache[key]
        
        if expired_keys:
            logger.info(f"Cleared {len(expired_keys)} expired cache entries")

# Global instances
_s3_client = None
_redis_client = None
_cache_manager = None

def get_s3_client() -> S3Client:
    """Get global S3 client instance."""
    global _s3_client
    if _s3_client is None:
        _s3_client = S3Client()
    return _s3_client

def get_redis_client() -> RedisClient:
    """Get global Redis client instance."""
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient()
    return _redis_client

def get_cache_manager() -> CacheManager:
    """Get global cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager(get_redis_client())
    return _cache_manager
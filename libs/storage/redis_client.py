"""
Redis client utilities for the risk platform.
Provides specialized Redis operations for common use cases.
"""

import redis
import json
import pickle
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from .storage import RedisClient
import logging

logger = logging.getLogger(__name__)

class SessionStore:
    """Redis-based session management."""
    
    def __init__(self, redis_client: RedisClient = None, prefix: str = 'session:'):
        self.redis_client = redis_client or RedisClient()
        self.prefix = prefix
        self.default_ttl = 86400  # 24 hours
    
    def create_session(self, user_id: str, session_data: Dict[str, Any], 
                      ttl: int = None) -> str:
        """Create new session and return session ID."""
        import uuid
        session_id = str(uuid.uuid4())
        
        session_data.update({
            'user_id': user_id,
            'created_at': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat()
        })
        
        session_key = f"{self.prefix}{session_id}"
        ttl = ttl or self.default_ttl
        
        if self.redis_client.set_json(session_key, session_data, ttl):
            logger.info(f"Created session for user: {user_id}")
            return session_id
        
        raise RuntimeError("Failed to create session")
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data."""
        session_key = f"{self.prefix}{session_id}"
        return self.redis_client.get_json(session_key)
    
    def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update session data."""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.update(updates)
        session['last_activity'] = datetime.now().isoformat()
        
        session_key = f"{self.prefix}{session_id}"
        return self.redis_client.set_json(session_key, session)
    
    def extend_session(self, session_id: str, ttl: int = None) -> bool:
        """Extend session expiration."""
        session_key = f"{self.prefix}{session_id}"
        ttl = ttl or self.default_ttl
        return self.redis_client.expire(session_key, ttl)
    
    def destroy_session(self, session_id: str) -> bool:
        """Delete session."""
        session_key = f"{self.prefix}{session_id}"
        return self.redis_client.delete(session_key)
    
    def get_user_sessions(self, user_id: str) -> List[str]:
        """Get all session IDs for a user."""
        pattern = f"{self.prefix}*"
        session_keys = self.redis_client.keys_pattern(pattern)
        
        user_sessions = []
        for key in session_keys:
            session_data = self.redis_client.get_json(key)
            if session_data and session_data.get('user_id') == user_id:
                # Extract session ID from key
                session_id = key[len(self.prefix):]
                user_sessions.append(session_id)
        
        return user_sessions

class RateLimiter:
    """Redis-based rate limiting."""
    
    def __init__(self, redis_client: RedisClient = None, prefix: str = 'ratelimit:'):
        self.redis_client = redis_client or RedisClient()
        self.prefix = prefix
    
    def is_allowed(self, identifier: str, limit: int, window: int) -> bool:
        """
        Check if request is allowed under rate limit.
        Uses sliding window log algorithm.
        """
        key = f"{self.prefix}{identifier}"
        now = datetime.now().timestamp()
        cutoff = now - window
        
        try:
            # Remove old entries
            self.redis_client.client.zremrangebyscore(key, 0, cutoff)
            
            # Count current requests
            current_count = self.redis_client.client.zcard(key)
            
            if current_count >= limit:
                return False
            
            # Add current request
            self.redis_client.client.zadd(key, {str(now): now})
            self.redis_client.expire(key, window)
            
            return True
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            return True  # Allow on error (fail open)
    
    def get_remaining(self, identifier: str, limit: int, window: int) -> int:
        """Get remaining requests in current window."""
        key = f"{self.prefix}{identifier}"
        now = datetime.now().timestamp()
        cutoff = now - window
        
        try:
            # Clean old entries
            self.redis_client.client.zremrangebyscore(key, 0, cutoff)
            current_count = self.redis_client.client.zcard(key)
            return max(0, limit - current_count)
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            return limit

class NotificationQueue:
    """Redis-based notification queue."""
    
    def __init__(self, redis_client: RedisClient = None, queue_name: str = 'notifications'):
        self.redis_client = redis_client or RedisClient()
        self.queue_name = queue_name
    
    def enqueue(self, notification: Dict[str, Any]) -> bool:
        """Add notification to queue."""
        notification['queued_at'] = datetime.now().isoformat()
        
        try:
            message = json.dumps(notification, default=str)
            self.redis_client.client.lpush(self.queue_name, message)
            logger.debug(f"Enqueued notification: {notification.get('type', 'unknown')}")
            return True
        except Exception as e:
            logger.error(f"Failed to enqueue notification: {e}")
            return False
    
    def dequeue(self, timeout: int = 0) -> Optional[Dict[str, Any]]:
        """Remove and return notification from queue."""
        try:
            if timeout > 0:
                result = self.redis_client.client.brpop(self.queue_name, timeout)
            else:
                result = self.redis_client.client.rpop(self.queue_name)
            
            if result:
                message = result[1] if isinstance(result, tuple) else result
                return json.loads(message)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to dequeue notification: {e}")
            return None
    
    def queue_size(self) -> int:
        """Get current queue size."""
        try:
            return self.redis_client.client.llen(self.queue_name)
        except Exception as e:
            logger.error(f"Failed to get queue size: {e}")
            return 0
    
    def clear_queue(self) -> bool:
        """Clear all notifications from queue."""
        try:
            self.redis_client.client.delete(self.queue_name)
            logger.info("Cleared notification queue")
            return True
        except Exception as e:
            logger.error(f"Failed to clear queue: {e}")
            return False

class DistributedLock:
    """Redis-based distributed lock."""
    
    def __init__(self, redis_client: RedisClient = None, prefix: str = 'lock:'):
        self.redis_client = redis_client or RedisClient()
        self.prefix = prefix
    
    def acquire(self, name: str, timeout: int = 10, blocking: bool = True) -> bool:
        """Acquire distributed lock."""
        key = f"{self.prefix}{name}"
        
        if not blocking:
            # Non-blocking acquire
            return self.redis_client.set(key, "1", timeout) if timeout else \
                   self.redis_client.client.setnx(key, "1")
        
        # Blocking acquire with retry
        import time
        end_time = time.time() + timeout
        
        while time.time() < end_time:
            if self.redis_client.set(key, "1", timeout):
                return True
            time.sleep(0.1)  # Wait 100ms before retry
        
        return False
    
    def release(self, name: str) -> bool:
        """Release distributed lock."""
        key = f"{self.prefix}{name}"
        return self.redis_client.delete(key)
    
    def is_locked(self, name: str) -> bool:
        """Check if lock is currently held."""
        key = f"{self.prefix}{name}"
        return self.redis_client.exists(key)

class TaskQueue:
    """Redis-based task queue for background processing."""
    
    def __init__(self, redis_client: RedisClient = None, queue_name: str = 'tasks'):
        self.redis_client = redis_client or RedisClient()
        self.queue_name = queue_name
        self.processing_key = f"{queue_name}:processing"
    
    def enqueue_task(self, task_type: str, task_data: Dict[str, Any], 
                    priority: int = 0) -> str:
        """Enqueue background task."""
        import uuid
        
        task = {
            'id': str(uuid.uuid4()),
            'type': task_type,
            'data': task_data,
            'priority': priority,
            'created_at': datetime.now().isoformat(),
            'status': 'queued'
        }
        
        try:
            # Use priority queue (sorted set)
            task_json = json.dumps(task, default=str)
            self.redis_client.client.zadd(self.queue_name, {task_json: priority})
            logger.info(f"Enqueued task: {task_type} (ID: {task['id']})")
            return task['id']
        except Exception as e:
            logger.error(f"Failed to enqueue task: {e}")
            raise RuntimeError("Task enqueue failed")
    
    def dequeue_task(self, timeout: int = 0) -> Optional[Dict[str, Any]]:
        """Dequeue highest priority task."""
        try:
            # Get highest priority task (lowest score)
            result = self.redis_client.client.zrange(
                self.queue_name, 0, 0, withscores=True
            )
            
            if not result:
                return None
            
            task_json, score = result[0]
            task = json.loads(task_json)
            
            # Move to processing queue
            self.redis_client.client.zrem(self.queue_name, task_json)
            task['status'] = 'processing'
            task['started_at'] = datetime.now().isoformat()
            
            processing_json = json.dumps(task, default=str)
            self.redis_client.client.hset(
                self.processing_key, task['id'], processing_json
            )
            
            logger.info(f"Dequeued task: {task['type']} (ID: {task['id']})")
            return task
            
        except Exception as e:
            logger.error(f"Failed to dequeue task: {e}")
            return None
    
    def complete_task(self, task_id: str) -> bool:
        """Mark task as completed."""
        try:
            self.redis_client.client.hdel(self.processing_key, task_id)
            logger.info(f"Completed task: {task_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to complete task: {e}")
            return False
    
    def fail_task(self, task_id: str, error_message: str) -> bool:
        """Mark task as failed."""
        try:
            # Get task from processing queue
            task_json = self.redis_client.client.hget(self.processing_key, task_id)
            if task_json:
                task = json.loads(task_json)
                task['status'] = 'failed'
                task['error'] = error_message
                task['failed_at'] = datetime.now().isoformat()
                
                # Move to failed queue for debugging
                failed_key = f"{self.queue_name}:failed"
                self.redis_client.client.hset(failed_key, task_id, json.dumps(task))
                self.redis_client.client.hdel(self.processing_key, task_id)
                
                logger.error(f"Failed task: {task_id} - {error_message}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Failed to mark task as failed: {e}")
            return False
    
    def queue_size(self) -> int:
        """Get number of queued tasks."""
        try:
            return self.redis_client.client.zcard(self.queue_name)
        except Exception as e:
            logger.error(f"Failed to get queue size: {e}")
            return 0
    
    def processing_size(self) -> int:
        """Get number of tasks currently processing."""
        try:
            return self.redis_client.client.hlen(self.processing_key)
        except Exception as e:
            logger.error(f"Failed to get processing size: {e}")
            return 0

# Global instances
_session_store = None
_rate_limiter = None
_notification_queue = None
_task_queue = None

def get_session_store() -> SessionStore:
    """Get global session store instance."""
    global _session_store
    if _session_store is None:
        _session_store = SessionStore()
    return _session_store

def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter

def get_notification_queue() -> NotificationQueue:
    """Get global notification queue instance."""
    global _notification_queue
    if _notification_queue is None:
        _notification_queue = NotificationQueue()
    return _notification_queue

def get_task_queue() -> TaskQueue:
    """Get global task queue instance."""
    global _task_queue
    if _task_queue is None:
        _task_queue = TaskQueue()
    return _task_queue
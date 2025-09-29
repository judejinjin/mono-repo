"""
Performance Optimization Framework
Database optimization, caching, connection pooling, and performance monitoring
"""

import os
import sys
import asyncio
import time
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Callable, AsyncGenerator
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
from functools import wraps, lru_cache
from pathlib import Path
import logging
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import weakref
import gc

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    import redis
    import aioredis
    from sqlalchemy import create_engine, text, MetaData, Index
    from sqlalchemy.pool import QueuePool, StaticPool
    from sqlalchemy.engine import Engine
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
    import pandas as pd
    import numpy as np
    from config import get_config
    from libs.monitoring import get_metrics_collector
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"Optional performance dependencies missing: {e}")
    redis = None
    aioredis = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Performance constants
DEFAULT_CACHE_TTL = 300  # 5 minutes
DEFAULT_POOL_SIZE = 20
DEFAULT_MAX_OVERFLOW = 10
SLOW_QUERY_THRESHOLD = 1.0  # seconds
MEMORY_USAGE_THRESHOLD = 85  # percent
CPU_USAGE_THRESHOLD = 80  # percent


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""
    timestamp: datetime
    request_count: int = 0
    average_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    error_count: int = 0
    cache_hit_rate: float = 0.0
    database_connection_count: int = 0
    memory_usage_percent: float = 0.0
    cpu_usage_percent: float = 0.0
    active_threads: int = 0
    slow_queries: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'request_count': self.request_count,
            'average_response_time': self.average_response_time,
            'p95_response_time': self.p95_response_time,
            'p99_response_time': self.p99_response_time,
            'error_count': self.error_count,
            'cache_hit_rate': self.cache_hit_rate,
            'database_connection_count': self.database_connection_count,
            'memory_usage_percent': self.memory_usage_percent,
            'cpu_usage_percent': self.cpu_usage_percent,
            'active_threads': self.active_threads,
            'slow_queries': self.slow_queries
        }


class CacheManager:
    """Advanced caching system with Redis backend."""
    
    def __init__(self, redis_url: str = None, default_ttl: int = DEFAULT_CACHE_TTL):
        self.redis_url = redis_url or os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        self.default_ttl = default_ttl
        self.redis_client = None
        self.async_redis_client = None
        self.local_cache = {}  # Fallback in-memory cache
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }
        
        # Initialize Redis connection
        self._init_redis()
    
    def _init_redis(self):
        """Initialize Redis connections."""
        try:
            if redis:
                self.redis_client = redis.from_url(
                    self.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=30
                )
                # Test connection
                self.redis_client.ping()
                logger.info("Redis connection established")
            else:
                logger.warning("Redis not available, using in-memory cache")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            self.redis_client = None
    
    async def _init_async_redis(self):
        """Initialize async Redis connection."""
        try:
            if aioredis and not self.async_redis_client:
                self.async_redis_client = await aioredis.from_url(
                    self.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True
                )
                logger.info("Async Redis connection established")
        except Exception as e:
            logger.error(f"Async Redis connection failed: {e}")
            self.async_redis_client = None
    
    def get(self, key: str) -> Any:
        """Get value from cache."""
        try:
            if self.redis_client:
                value = self.redis_client.get(key)
                if value is not None:
                    self.cache_stats['hits'] += 1
                    return json.loads(value)
                else:
                    self.cache_stats['misses'] += 1
                    return None
            else:
                # Fallback to local cache
                if key in self.local_cache:
                    item = self.local_cache[key]
                    if item['expires_at'] > datetime.utcnow():
                        self.cache_stats['hits'] += 1
                        return item['value']
                    else:
                        del self.local_cache[key]
                
                self.cache_stats['misses'] += 1
                return None
                
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            self.cache_stats['misses'] += 1
            return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache."""
        try:
            ttl = ttl or self.default_ttl
            
            if self.redis_client:
                serialized_value = json.dumps(value, default=str)
                result = self.redis_client.setex(key, ttl, serialized_value)
                if result:
                    self.cache_stats['sets'] += 1
                return result
            else:
                # Fallback to local cache
                self.local_cache[key] = {
                    'value': value,
                    'expires_at': datetime.utcnow() + timedelta(seconds=ttl)
                }
                self.cache_stats['sets'] += 1
                return True
                
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def async_get(self, key: str) -> Any:
        """Async get value from cache."""
        try:
            if not self.async_redis_client:
                await self._init_async_redis()
            
            if self.async_redis_client:
                value = await self.async_redis_client.get(key)
                if value is not None:
                    self.cache_stats['hits'] += 1
                    return json.loads(value)
                else:
                    self.cache_stats['misses'] += 1
                    return None
            else:
                return self.get(key)  # Fallback to sync method
                
        except Exception as e:
            logger.error(f"Async cache get error: {e}")
            self.cache_stats['misses'] += 1
            return None
    
    async def async_set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Async set value in cache."""
        try:
            if not self.async_redis_client:
                await self._init_async_redis()
            
            ttl = ttl or self.default_ttl
            
            if self.async_redis_client:
                serialized_value = json.dumps(value, default=str)
                result = await self.async_redis_client.setex(key, ttl, serialized_value)
                if result:
                    self.cache_stats['sets'] += 1
                return result
            else:
                return self.set(key, value, ttl)  # Fallback to sync method
                
        except Exception as e:
            logger.error(f"Async cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            if self.redis_client:
                result = self.redis_client.delete(key)
                if result:
                    self.cache_stats['deletes'] += 1
                return result > 0
            else:
                if key in self.local_cache:
                    del self.local_cache[key]
                    self.cache_stats['deletes'] += 1
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all cache."""
        try:
            if self.redis_client:
                self.redis_client.flushdb()
            
            self.local_cache.clear()
            return True
            
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        stats = {
            'hits': self.cache_stats['hits'],
            'misses': self.cache_stats['misses'],
            'sets': self.cache_stats['sets'],
            'deletes': self.cache_stats['deletes'],
            'hit_rate_percent': round(hit_rate, 2),
            'total_requests': total_requests
        }
        
        # Add Redis-specific stats if available
        if self.redis_client:
            try:
                redis_info = self.redis_client.info()
                stats['redis_memory_used'] = redis_info.get('used_memory_human', 'N/A')
                stats['redis_connected_clients'] = redis_info.get('connected_clients', 0)
                stats['redis_keyspace_hits'] = redis_info.get('keyspace_hits', 0)
                stats['redis_keyspace_misses'] = redis_info.get('keyspace_misses', 0)
            except Exception as e:
                logger.error(f"Error getting Redis stats: {e}")
        
        return stats


class DatabaseOptimizer:
    """Database performance optimization."""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv('DATABASE_URL', 'sqlite:///performance.db')
        self.engine = None
        self.async_engine = None
        self.query_stats = {}
        self.slow_queries = []
        
        self._init_engines()
    
    def _init_engines(self):
        """Initialize database engines with optimized settings."""
        try:
            # Sync engine with connection pooling
            self.engine = create_engine(
                self.database_url,
                poolclass=QueuePool,
                pool_size=DEFAULT_POOL_SIZE,
                max_overflow=DEFAULT_MAX_OVERFLOW,
                pool_pre_ping=True,
                pool_recycle=3600,  # Recycle connections every hour
                echo=False  # Set to True for SQL logging
            )
            
            # Async engine
            if 'sqlite' not in self.database_url:
                async_url = self.database_url.replace('postgresql://', 'postgresql+asyncpg://')
                self.async_engine = create_async_engine(
                    async_url,
                    pool_size=DEFAULT_POOL_SIZE,
                    max_overflow=DEFAULT_MAX_OVERFLOW,
                    pool_pre_ping=True,
                    pool_recycle=3600
                )
            
            logger.info("Database engines initialized")
            
        except Exception as e:
            logger.error(f"Database engine initialization failed: {e}")
    
    def execute_query(self, query: str, params: Dict[str, Any] = None) -> Any:
        """Execute query with performance monitoring."""
        start_time = time.time()
        query_key = hash(query)
        
        try:
            with self.engine.connect() as conn:
                if params:
                    result = conn.execute(text(query), params)
                else:
                    result = conn.execute(text(query))
                
                # Fetch results for SELECT queries
                if query.strip().upper().startswith('SELECT'):
                    data = result.fetchall()
                    execution_time = time.time() - start_time
                    
                    # Track query performance
                    self._track_query_performance(query, query_key, execution_time)
                    
                    return data
                else:
                    conn.commit()
                    execution_time = time.time() - start_time
                    self._track_query_performance(query, query_key, execution_time)
                    
                    return result.rowcount
                    
        except Exception as e:
            execution_time = time.time() - start_time
            self._track_query_performance(query, query_key, execution_time, error=str(e))
            raise
    
    async def async_execute_query(self, query: str, params: Dict[str, Any] = None) -> Any:
        """Async execute query with performance monitoring."""
        if not self.async_engine:
            logger.warning("Async engine not available, falling back to sync")
            return self.execute_query(query, params)
        
        start_time = time.time()
        query_key = hash(query)
        
        try:
            async with self.async_engine.connect() as conn:
                if params:
                    result = await conn.execute(text(query), params)
                else:
                    result = await conn.execute(text(query))
                
                if query.strip().upper().startswith('SELECT'):
                    data = result.fetchall()
                    execution_time = time.time() - start_time
                    self._track_query_performance(query, query_key, execution_time)
                    return data
                else:
                    await conn.commit()
                    execution_time = time.time() - start_time
                    self._track_query_performance(query, query_key, execution_time)
                    return result.rowcount
                    
        except Exception as e:
            execution_time = time.time() - start_time
            self._track_query_performance(query, query_key, execution_time, error=str(e))
            raise
    
    def _track_query_performance(self, query: str, query_key: int, execution_time: float, error: str = None):
        """Track query performance metrics."""
        if query_key not in self.query_stats:
            self.query_stats[query_key] = {
                'query': query[:200] + '...' if len(query) > 200 else query,
                'execution_count': 0,
                'total_time': 0.0,
                'min_time': float('inf'),
                'max_time': 0.0,
                'error_count': 0
            }
        
        stats = self.query_stats[query_key]
        stats['execution_count'] += 1
        stats['total_time'] += execution_time
        stats['min_time'] = min(stats['min_time'], execution_time)
        stats['max_time'] = max(stats['max_time'], execution_time)
        
        if error:
            stats['error_count'] += 1
        
        # Track slow queries
        if execution_time > SLOW_QUERY_THRESHOLD:
            self.slow_queries.append({
                'query': query[:500] + '...' if len(query) > 500 else query,
                'execution_time': execution_time,
                'timestamp': datetime.utcnow().isoformat(),
                'error': error
            })
            
            # Keep only last 100 slow queries
            if len(self.slow_queries) > 100:
                self.slow_queries = self.slow_queries[-100:]
    
    def create_indexes(self, table_name: str, indexes: List[Dict[str, Any]]) -> bool:
        """Create database indexes for performance."""
        try:
            with self.engine.connect() as conn:
                for index_config in indexes:
                    index_name = index_config['name']
                    columns = index_config['columns']
                    unique = index_config.get('unique', False)
                    
                    # Create index SQL
                    columns_str = ', '.join(columns)
                    unique_str = 'UNIQUE ' if unique else ''
                    
                    create_index_sql = f"""
                        CREATE {unique_str}INDEX IF NOT EXISTS {index_name} 
                        ON {table_name} ({columns_str})
                    """
                    
                    conn.execute(text(create_index_sql))
                    logger.info(f"Created index {index_name} on {table_name}")
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Index creation failed: {e}")
            return False
    
    def analyze_query_performance(self) -> Dict[str, Any]:
        """Analyze query performance and provide recommendations."""
        if not self.query_stats:
            return {'message': 'No query statistics available'}
        
        # Calculate overall statistics
        total_queries = sum(stats['execution_count'] for stats in self.query_stats.values())
        total_time = sum(stats['total_time'] for stats in self.query_stats.values())
        avg_time = total_time / total_queries if total_queries > 0 else 0
        
        # Find slowest queries
        slowest_queries = sorted(
            [
                {
                    'query': stats['query'],
                    'avg_time': stats['total_time'] / stats['execution_count'],
                    'max_time': stats['max_time'],
                    'execution_count': stats['execution_count'],
                    'error_rate': stats['error_count'] / stats['execution_count'] * 100
                }
                for stats in self.query_stats.values()
            ],
            key=lambda x: x['avg_time'],
            reverse=True
        )[:10]
        
        # Generate recommendations
        recommendations = []
        
        for query_stat in slowest_queries[:5]:
            if query_stat['avg_time'] > SLOW_QUERY_THRESHOLD:
                recommendations.append(f"Consider optimizing query: {query_stat['query'][:100]}...")
            
            if query_stat['error_rate'] > 5:
                recommendations.append(f"Query has high error rate ({query_stat['error_rate']:.1f}%): {query_stat['query'][:100]}...")
        
        return {
            'total_queries': total_queries,
            'total_execution_time': round(total_time, 3),
            'average_execution_time': round(avg_time, 3),
            'slow_queries_count': len(self.slow_queries),
            'slowest_queries': slowest_queries,
            'recent_slow_queries': self.slow_queries[-10:],
            'recommendations': recommendations
        }
    
    def get_connection_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics."""
        try:
            pool = self.engine.pool
            return {
                'pool_size': pool.size(),
                'checked_in_connections': pool.checkedin(),
                'checked_out_connections': pool.checkedout(),
                'overflow_connections': pool.overflow(),
                'invalid_connections': pool.invalid()
            }
        except Exception as e:
            logger.error(f"Error getting pool stats: {e}")
            return {}


class PerformanceProfiler:
    """Application performance profiler."""
    
    def __init__(self):
        self.request_times = []
        self.response_times = []
        self.system_metrics = []
        self.profiling_enabled = True
        self.max_stored_metrics = 1000
    
    def profile_function(self, func_name: str = None):
        """Decorator for profiling function performance."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not self.profiling_enabled:
                    return func(*args, **kwargs)
                
                start_time = time.time()
                start_memory = psutil.Process().memory_info().rss
                
                try:
                    result = func(*args, **kwargs)
                    success = True
                    error = None
                except Exception as e:
                    result = None
                    success = False
                    error = str(e)
                    raise
                finally:
                    end_time = time.time()
                    end_memory = psutil.Process().memory_info().rss
                    
                    execution_time = end_time - start_time
                    memory_delta = end_memory - start_memory
                    
                    # Record performance metrics
                    self._record_function_metrics(
                        func_name or func.__name__,
                        execution_time,
                        memory_delta,
                        success,
                        error
                    )
                
                return result
            return wrapper
        return decorator
    
    def profile_async_function(self, func_name: str = None):
        """Decorator for profiling async function performance."""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                if not self.profiling_enabled:
                    return await func(*args, **kwargs)
                
                start_time = time.time()
                start_memory = psutil.Process().memory_info().rss
                
                try:
                    result = await func(*args, **kwargs)
                    success = True
                    error = None
                except Exception as e:
                    result = None
                    success = False
                    error = str(e)
                    raise
                finally:
                    end_time = time.time()
                    end_memory = psutil.Process().memory_info().rss
                    
                    execution_time = end_time - start_time
                    memory_delta = end_memory - start_memory
                    
                    self._record_function_metrics(
                        func_name or func.__name__,
                        execution_time,
                        memory_delta,
                        success,
                        error
                    )
                
                return result
            return wrapper
        return decorator
    
    def _record_function_metrics(self, func_name: str, execution_time: float, 
                                memory_delta: int, success: bool, error: str = None):
        """Record function performance metrics."""
        metric = {
            'function_name': func_name,
            'execution_time': execution_time,
            'memory_delta_bytes': memory_delta,
            'success': success,
            'error': error,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.request_times.append(metric)
        
        # Keep only recent metrics
        if len(self.request_times) > self.max_stored_metrics:
            self.request_times = self.request_times[-self.max_stored_metrics:]
    
    def collect_system_metrics(self) -> PerformanceMetrics:
        """Collect current system performance metrics."""
        try:
            # CPU and memory usage
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Process information
            process = psutil.Process()
            process_memory = process.memory_info().rss / 1024 / 1024  # MB
            thread_count = process.num_threads()
            
            # Calculate response time statistics
            recent_times = [r['execution_time'] for r in self.request_times[-100:] if r['success']]
            
            avg_response_time = np.mean(recent_times) if recent_times else 0.0
            p95_response_time = np.percentile(recent_times, 95) if recent_times else 0.0
            p99_response_time = np.percentile(recent_times, 99) if recent_times else 0.0
            
            # Error count
            recent_errors = sum(1 for r in self.request_times[-100:] if not r['success'])
            
            # Slow queries (if available)
            slow_query_count = sum(1 for r in self.request_times[-100:] if r['execution_time'] > SLOW_QUERY_THRESHOLD)
            
            metrics = PerformanceMetrics(
                timestamp=datetime.utcnow(),
                request_count=len(self.request_times),
                average_response_time=avg_response_time,
                p95_response_time=p95_response_time,
                p99_response_time=p99_response_time,
                error_count=recent_errors,
                memory_usage_percent=memory_percent,
                cpu_usage_percent=cpu_percent,
                active_threads=thread_count,
                slow_queries=slow_query_count
            )
            
            # Store metrics
            self.system_metrics.append(metrics)
            
            # Keep only recent metrics
            if len(self.system_metrics) > 100:
                self.system_metrics = self.system_metrics[-100:]
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return PerformanceMetrics(timestamp=datetime.utcnow())
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        if not self.request_times:
            return {'message': 'No performance data available'}
        
        # Function performance analysis
        func_stats = {}
        for metric in self.request_times:
            func_name = metric['function_name']
            if func_name not in func_stats:
                func_stats[func_name] = {
                    'call_count': 0,
                    'total_time': 0.0,
                    'min_time': float('inf'),
                    'max_time': 0.0,
                    'error_count': 0,
                    'total_memory_delta': 0
                }
            
            stats = func_stats[func_name]
            stats['call_count'] += 1
            stats['total_time'] += metric['execution_time']
            stats['min_time'] = min(stats['min_time'], metric['execution_time'])
            stats['max_time'] = max(stats['max_time'], metric['execution_time'])
            stats['total_memory_delta'] += metric['memory_delta_bytes']
            
            if not metric['success']:
                stats['error_count'] += 1
        
        # Calculate averages and add recommendations
        for func_name, stats in func_stats.items():
            stats['avg_time'] = stats['total_time'] / stats['call_count']
            stats['error_rate'] = stats['error_count'] / stats['call_count'] * 100
            stats['avg_memory_delta_mb'] = stats['total_memory_delta'] / stats['call_count'] / 1024 / 1024
        
        # System metrics summary
        recent_system_metrics = self.system_metrics[-10:] if self.system_metrics else []
        
        avg_cpu = np.mean([m.cpu_usage_percent for m in recent_system_metrics]) if recent_system_metrics else 0
        avg_memory = np.mean([m.memory_usage_percent for m in recent_system_metrics]) if recent_system_metrics else 0
        
        # Generate recommendations
        recommendations = []
        
        # Check for high resource usage
        if avg_cpu > CPU_USAGE_THRESHOLD:
            recommendations.append(f"High CPU usage detected ({avg_cpu:.1f}%). Consider optimizing CPU-intensive operations.")
        
        if avg_memory > MEMORY_USAGE_THRESHOLD:
            recommendations.append(f"High memory usage detected ({avg_memory:.1f}%). Consider implementing memory optimization.")
        
        # Check for slow functions
        slow_functions = [
            (name, stats) for name, stats in func_stats.items() 
            if stats['avg_time'] > SLOW_QUERY_THRESHOLD
        ]
        
        for func_name, stats in slow_functions[:5]:
            recommendations.append(f"Function '{func_name}' is slow (avg: {stats['avg_time']:.3f}s). Consider optimization.")
        
        return {
            'summary': {
                'total_function_calls': len(self.request_times),
                'unique_functions': len(func_stats),
                'average_cpu_usage': round(avg_cpu, 2),
                'average_memory_usage': round(avg_memory, 2),
                'slow_functions_count': len(slow_functions)
            },
            'function_performance': dict(sorted(
                func_stats.items(), 
                key=lambda x: x[1]['avg_time'], 
                reverse=True
            )),
            'system_metrics': [m.to_dict() for m in recent_system_metrics],
            'recommendations': recommendations,
            'timestamp': datetime.utcnow().isoformat()
        }


class AsyncTaskManager:
    """Async task management for improved performance."""
    
    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.running_tasks = weakref.WeakSet()
        self.task_results = {}
        
    async def run_in_background(self, func: Callable, *args, **kwargs) -> str:
        """Run function in background thread."""
        task_id = f"task_{int(time.time() * 1000)}"
        
        future = self.executor.submit(func, *args, **kwargs)
        self.running_tasks.add(future)
        
        # Store result when complete
        def store_result(fut):
            try:
                result = fut.result()
                self.task_results[task_id] = {
                    'status': 'completed',
                    'result': result,
                    'completed_at': datetime.utcnow().isoformat()
                }
            except Exception as e:
                self.task_results[task_id] = {
                    'status': 'failed',
                    'error': str(e),
                    'completed_at': datetime.utcnow().isoformat()
                }
        
        future.add_done_callback(store_result)
        
        return task_id
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of background task."""
        if task_id in self.task_results:
            return self.task_results[task_id]
        else:
            return {
                'status': 'running',
                'message': 'Task is still executing'
            }
    
    def get_running_tasks_count(self) -> int:
        """Get count of currently running tasks."""
        return len(self.running_tasks)


# Global instances
_cache_manager = None
_db_optimizer = None
_performance_profiler = None
_task_manager = None


def get_cache_manager() -> CacheManager:
    """Get global cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def get_db_optimizer() -> DatabaseOptimizer:
    """Get global database optimizer instance."""
    global _db_optimizer
    if _db_optimizer is None:
        _db_optimizer = DatabaseOptimizer()
    return _db_optimizer


def get_performance_profiler() -> PerformanceProfiler:
    """Get global performance profiler instance."""
    global _performance_profiler
    if _performance_profiler is None:
        _performance_profiler = PerformanceProfiler()
    return _performance_profiler


def get_task_manager() -> AsyncTaskManager:
    """Get global task manager instance."""
    global _task_manager
    if _task_manager is None:
        _task_manager = AsyncTaskManager()
    return _task_manager


# Performance decorators
def cached(ttl: int = DEFAULT_CACHE_TTL, key_prefix: str = None):
    """Cache function results."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_manager = get_cache_manager()
            
            # Generate cache key
            key_parts = [key_prefix or func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(key_parts)
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


def async_cached(ttl: int = DEFAULT_CACHE_TTL, key_prefix: str = None):
    """Cache async function results."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_manager = get_cache_manager()
            
            # Generate cache key
            key_parts = [key_prefix or func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(key_parts)
            
            # Try to get from cache
            cached_result = await cache_manager.async_get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_manager.async_set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


def profiled(func_name: str = None):
    """Profile function performance."""
    def decorator(func):
        profiler = get_performance_profiler()
        return profiler.profile_function(func_name)(func)
    return decorator


def async_profiled(func_name: str = None):
    """Profile async function performance."""
    def decorator(func):
        profiler = get_performance_profiler()
        return profiler.profile_async_function(func_name)(func)
    return decorator


# Memory management utilities
def cleanup_memory():
    """Force garbage collection and memory cleanup."""
    gc.collect()
    logger.info("Memory cleanup completed")


def get_memory_usage() -> Dict[str, Any]:
    """Get current memory usage statistics."""
    process = psutil.Process()
    memory_info = process.memory_info()
    system_memory = psutil.virtual_memory()
    
    return {
        'process_memory_mb': round(memory_info.rss / 1024 / 1024, 2),
        'process_memory_percent': round(process.memory_percent(), 2),
        'system_memory_percent': system_memory.percent,
        'system_memory_available_gb': round(system_memory.available / 1024 / 1024 / 1024, 2)
    }
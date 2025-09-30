# Performance Optimization Implementation Guide

> **📁 FILE LOCATION UPDATE**: All performance optimization files have been moved to `tests/performance_optimization/` directory.
> 
> To run performance optimization scripts, navigate to: `cd tests/performance_optimization/`

## Overview
This document provides comprehensive guidance for implementing, testing, and monitoring the performance optimization framework across the risk management infrastructure.

## Table of Contents
1. [Performance Framework Overview](#performance-framework-overview)
2. [Implementation Guide](#implementation-guide)
3. [Testing and Benchmarking](#testing-and-benchmarking)
4. [Monitoring and Alerting](#monitoring-and-alerting)
5. [Deployment and Configuration](#deployment-and-configuration)
6. [Troubleshooting](#troubleshooting)
7. [Performance Tuning](#performance-tuning)

## Performance Framework Overview

### Core Components

#### 1. Caching Layer (`libs/performance/optimization.py`)
- **Redis-based caching** with fallback to in-memory cache
- **Intelligent TTL management** based on data type and usage patterns
- **Cache hit rate monitoring** and optimization
- **Distributed caching** support for horizontal scaling

```python
# Usage example
from libs.performance import get_cache_manager

cache = get_cache_manager()
cache.set("market_data:AAPL", price_data, ttl=60)
cached_data = cache.get("market_data:AAPL")
```

#### 2. Database Optimization (`libs/performance/optimization.py`)
- **Connection pooling** with configurable pool sizes
- **Query performance tracking** and analysis
- **Slow query detection** and logging
- **Connection health monitoring**

```python
# Usage example
from libs.performance import get_db_optimizer

db_optimizer = get_db_optimizer()
result = db_optimizer.execute_query("SELECT * FROM portfolios", use_cache=True)
performance_stats = db_optimizer.analyze_query_performance()
```

#### 3. Performance Profiling (`libs/performance/optimization.py`)
- **Function-level profiling** with decorators
- **System metrics collection** (CPU, memory, I/O)
- **Performance bottleneck identification**
- **Real-time performance monitoring**

```python
# Usage example
from libs.performance import get_performance_profiler, profile_function

profiler = get_performance_profiler()

@profile_function
def expensive_calculation():
    # Your code here
    pass

metrics = profiler.collect_system_metrics()
```

#### 4. Load Testing Framework (`libs/performance/monitoring.py`)
- **Concurrent user simulation**
- **API endpoint testing**
- **Performance regression detection**
- **Comprehensive reporting**

```python
# Usage example
from libs.performance import get_load_tester

load_tester = get_load_tester()
results = load_tester.run_load_test(
    endpoint="/api/v1/risk-analysis",
    concurrent_users=100,
    duration_seconds=300
)
```

## Implementation Guide

### 1. Setup Performance Infrastructure

#### Install Dependencies
```bash
# Install performance optimization dependencies
pip install -r tests/performance_optimization/requirements-performance.txt

# Install Redis for caching
sudo apt-get install redis-server
# or using Docker
docker run -d --name redis -p 6379:6379 redis:7.0-alpine
```

#### Environment Configuration
```bash
# Performance optimization environment variables
export CACHE_TTL_DEFAULT=300
export CACHE_MAX_MEMORY=256mb
export DB_POOL_SIZE=20
export DB_MAX_OVERFLOW=30
export ASYNC_WORKERS=4
export PROFILER_ENABLED=true
export MONITORING_ENABLED=true
export REDIS_HOST=localhost
export REDIS_PORT=6379
```

### 2. Integrate Performance Framework

#### Update Existing Services
```python
# Example: Adding performance optimization to existing API
from fastapi import FastAPI
from libs.performance import performance_monitor, get_cache_manager, profile_function

app = FastAPI()
cache = get_cache_manager()

@app.middleware("http")
async def performance_middleware(request, call_next):
    with performance_monitor():
        response = await call_next(request)
        return response

@app.get("/api/data/{item_id}")
@profile_function
async def get_data(item_id: str):
    # Check cache first
    cached_data = cache.get(f"data:{item_id}")
    if cached_data:
        return cached_data
    
    # Fetch and cache data
    data = await fetch_data(item_id)
    cache.set(f"data:{item_id}", data, ttl=300)
    return data
```

### 3. Deploy Optimized Services

#### Docker Build with Performance Optimization
```dockerfile
# Use optimized base image
FROM python:3.11-slim

# Performance optimization build arguments
ARG ENABLE_PROFILING=true
ARG CACHE_SIZE=256mb

# Install performance monitoring tools
RUN apt-get update && apt-get install -y \
    htop \
    iotop \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

# Copy performance framework
COPY libs/performance/ /app/libs/performance/
COPY requirements-performance.txt /app/

# Install dependencies with performance optimizations
RUN pip install --no-cache-dir -r requirements-performance.txt

# Set performance environment
ENV PYTHONOPTIMIZE=1
ENV PYTHONUNBUFFERED=1
ENV PROFILER_ENABLED=${ENABLE_PROFILING}
ENV CACHE_MAX_MEMORY=${CACHE_SIZE}

# Copy optimized application
COPY services/risk_api_optimized.py /app/
COPY config/ /app/config/

WORKDIR /app
EXPOSE 8001

# Use performance-optimized startup
CMD ["python", "-O", "services/risk_api_optimized.py"]
```

## Testing and Benchmarking

### 1. Run Comprehensive Performance Tests

#### Execute All Performance Tests
```bash
# Navigate to performance optimization directory
cd tests/performance_optimization

# Run complete performance optimization suite
python run_performance_optimization.py --all

# Run specific test categories
python run_performance_optimization.py --cache
python run_performance_optimization.py --database  
python run_performance_optimization.py --system
python run_performance_optimization.py --load-test http://localhost:8001
python run_performance_optimization.py --components
python run_performance_optimization.py --async
python run_performance_optimization.py --monitor 10
```

#### Cache Performance Testing
```bash
```bash
# Test cache performance with different scenarios
cd tests/performance_optimization
python run_performance_optimization.py --cache
```

# Expected output:
# Cache Performance:
#   Hit Rate: 85.2%
#   Total Requests: 10,000
#   Average Response Time: 2.3ms
#   Memory Usage: 45.6MB
```

#### Database Performance Testing
```bash
# Test database optimization
python run_performance_optimization.py --database

# Expected output:
# Database Performance:
#   Average Query Time: 0.045s
#   Slow Queries: 0
#   Connection Pool Usage: 65%
#   Query Cache Hit Rate: 78%
```

#### API Load Testing
```bash
# Test API performance under load
python run_performance_optimization.py --load-test http://localhost:8001

# Expected output:
# Load Test Results:
#   /health: 2,450.5 RPS, 0.0% errors
#   /api/v1/risk-analysis: 145.2 RPS, 0.2% errors
#   Average Response Time: 245ms
#   95th Percentile: 450ms
```

### 2. Benchmark Real Components

#### Risk Analysis Performance
```python
from libs.performance import benchmark_suite

# Benchmark risk calculations
suite = benchmark_suite()
result = suite.benchmark_function(
    lambda: calculate_portfolio_var(portfolio, prices),
    "portfolio_var_calculation",
    iterations=100
)

print(f"Average time: {result.average_time:.3f}s")
print(f"95th percentile: {result.percentile_95:.3f}s")
```

#### Market Data Performance
```python
# Benchmark market data retrieval
result = suite.benchmark_function(
    lambda: market_data_provider.get_current_price("AAPL"),
    "market_data_single_price",
    iterations=50
)
```

### 3. Performance Regression Testing

#### Automated Performance Testing
```python
# Create performance test suite
import unittest
from libs.performance import get_benchmark_suite, get_performance_profiler

class PerformanceRegressionTests(unittest.TestCase):
    def setUp(self):
        self.benchmark_suite = get_benchmark_suite()
        self.profiler = get_performance_profiler()
    
    def test_cache_performance_regression(self):
        """Test that cache performance hasn't regressed."""
        cache = get_cache_manager()
        
        # Benchmark cache operations
        result = self.benchmark_suite.benchmark_function(
            lambda: cache.set("test_key", {"test": "data"}),
            "cache_set_operation"
        )
        
        # Assert performance criteria
        self.assertLess(result.average_time, 0.005)  # < 5ms
        self.assertGreater(result.operations_per_second, 1000)  # > 1000 ops/sec
    
    def test_api_response_time_regression(self):
        """Test API response time regression."""
        import requests
        
        response_times = []
        for _ in range(10):
            start = time.time()
            response = requests.get("http://localhost:8001/health")
            response_times.append(time.time() - start)
        
        avg_response_time = sum(response_times) / len(response_times)
        self.assertLess(avg_response_time, 0.1)  # < 100ms average
```

## Monitoring and Alerting

### 1. Performance Metrics Collection

#### Prometheus Metrics Integration
```python
# Custom metrics for performance monitoring
from prometheus_client import Counter, Histogram, Gauge

# Define performance metrics
CACHE_HITS = Counter('cache_hits_total', 'Total cache hits')
CACHE_MISSES = Counter('cache_misses_total', 'Total cache misses')
RESPONSE_TIME = Histogram('http_request_duration_seconds', 'HTTP request duration')
ACTIVE_CONNECTIONS = Gauge('database_connections_active', 'Active database connections')

# Usage in application
@app.middleware("http")
async def metrics_middleware(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    RESPONSE_TIME.observe(time.time() - start_time)
    return response
```

#### Custom Performance Dashboard
```python
# Create performance dashboard
from libs.performance import get_performance_reporter

reporter = get_performance_reporter()
dashboard_data = {
    'cache_metrics': cache_manager.get_stats(),
    'database_metrics': db_optimizer.get_connection_pool_stats(),
    'system_metrics': profiler.collect_system_metrics().to_dict(),
    'api_metrics': load_tester.get_recent_results()
}

dashboard_file = reporter.create_dashboard(dashboard_data)
```

### 2. Performance Alerting

#### Alert Thresholds Configuration
```yaml
# Performance alert configuration
performance_alerts:
  cache:
    hit_rate_threshold: 80  # Alert if cache hit rate < 80%
    response_time_threshold: 10  # Alert if cache response > 10ms
  
  database:
    connection_pool_threshold: 85  # Alert if pool usage > 85%
    query_time_threshold: 100  # Alert if query time > 100ms
  
  api:
    response_time_threshold: 1000  # Alert if response time > 1s
    error_rate_threshold: 5  # Alert if error rate > 5%
  
  system:
    cpu_threshold: 80  # Alert if CPU usage > 80%
    memory_threshold: 85  # Alert if memory usage > 85%
```

#### Alerting Implementation
```python
class PerformanceAlerter:
    def __init__(self, config):
        self.config = config
        self.alert_handlers = []
    
    def check_performance_thresholds(self, metrics):
        alerts = []
        
        # Check cache performance
        if metrics['cache_hit_rate'] < self.config['cache']['hit_rate_threshold']:
            alerts.append({
                'severity': 'warning',
                'message': f"Cache hit rate below threshold: {metrics['cache_hit_rate']}%"
            })
        
        # Check API response times
        if metrics['avg_response_time'] > self.config['api']['response_time_threshold']:
            alerts.append({
                'severity': 'critical',
                'message': f"API response time exceeded: {metrics['avg_response_time']}ms"
            })
        
        return alerts
```

## Deployment and Configuration

### 1. Kubernetes Deployment

#### Deploy Performance-Optimized Risk API
```bash
# Deploy Redis cache cluster
kubectl apply -f deploy/kubernetes/redis-cluster.yaml

# Deploy optimized risk API
envsubst < deploy/kubernetes/risk-api-optimized.yaml | kubectl apply -f -

# Verify deployment
kubectl get pods -l app=risk-api-optimized
kubectl get svc risk-api-optimized-service
```

#### Monitor Deployment Status
```bash
# Check pod performance
kubectl top pods -l app=risk-api-optimized

# View performance logs
kubectl logs -f deployment/risk-api-optimized -c risk-api-optimized

# Check horizontal pod autoscaler
kubectl get hpa risk-api-optimized-hpa
```

### 2. Performance Configuration Tuning

#### Redis Cache Configuration
```redis
# /etc/redis/redis.conf
maxmemory 512mb
maxmemory-policy allkeys-lru
timeout 300
tcp-keepalive 300
hz 10
hash-max-ziplist-entries 512
maxclients 1000
```

#### Database Pool Configuration
```python
# Database connection pool tuning
DATABASE_CONFIG = {
    'pool_size': 20,          # Base number of connections
    'max_overflow': 30,       # Additional connections under load  
    'pool_timeout': 30,       # Timeout to get connection
    'pool_recycle': 3600,     # Recycle connections every hour
    'pool_pre_ping': True,    # Verify connections before use
}
```

#### Application Performance Tuning
```python
# FastAPI performance configuration
app = FastAPI(
    title="Optimized Risk API",
    docs_url="/docs" if config.environment != "production" else None,
    redoc_url="/redoc" if config.environment != "production" else None,
)

# Add performance middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## Troubleshooting

### 1. Performance Issues

#### High Response Times
```bash
# Check system resources
kubectl top pods
kubectl describe pod <pod-name>

# Check application logs for bottlenecks
kubectl logs <pod-name> | grep "slow\|timeout\|error"

# Run performance analysis
python run_performance_optimization.py --system --monitor 5
```

#### Cache Performance Issues
```bash
# Check Redis status
kubectl exec -it <redis-pod> -- redis-cli info memory
kubectl exec -it <redis-pod> -- redis-cli info stats

# Monitor cache hit rates
curl http://localhost:8001/metrics | grep cache_
```

#### Database Performance Issues
```bash
# Check database connections
curl http://localhost:8001/metrics | grep database_

# Analyze slow queries
python -c "
from libs.performance import get_db_optimizer
db = get_db_optimizer()
analysis = db.analyze_query_performance()
print('Slow queries:', analysis.get('slow_queries_count', 0))
print('Average time:', analysis.get('average_execution_time', 0))
"
```

### 2. Memory Issues

#### Memory Usage Analysis
```python
# Check memory usage patterns
from libs.performance import get_memory_usage, cleanup_memory

memory_usage = get_memory_usage()
print(f"Process memory: {memory_usage['process_memory_mb']:.2f} MB")
print(f"Memory percent: {memory_usage['process_memory_percent']:.2f}%")

# Force memory cleanup
cleanup_memory()
```

#### Memory Leak Detection
```python
# Monitor memory over time
import time
from libs.performance import get_performance_profiler

profiler = get_performance_profiler()

for i in range(10):
    metrics = profiler.collect_system_metrics()
    print(f"Iteration {i}: Memory {metrics.memory_usage_percent:.1f}%")
    time.sleep(60)  # Wait 1 minute between checks
```

### 3. Scaling Issues

#### Horizontal Pod Autoscaler Troubleshooting
```bash
# Check HPA status
kubectl describe hpa risk-api-optimized-hpa

# View HPA metrics
kubectl get hpa risk-api-optimized-hpa -o yaml

# Check custom metrics
kubectl get --raw "/apis/custom.metrics.k8s.io/v1beta1/namespaces/default/pods/*/requests_per_second"
```

## Performance Tuning

### 1. Cache Optimization

#### Cache Strategy Selection
```python
# Different caching strategies for different data types
CACHE_STRATEGIES = {
    'market_data': {'ttl': 60, 'strategy': 'write-through'},
    'risk_calculations': {'ttl': 300, 'strategy': 'write-behind'},
    'user_sessions': {'ttl': 1800, 'strategy': 'write-around'},
    'static_data': {'ttl': 3600, 'strategy': 'cache-aside'}
}

def get_cache_config(data_type):
    return CACHE_STRATEGIES.get(data_type, {'ttl': 300, 'strategy': 'cache-aside'})
```

#### Cache Warming Strategies
```python
async def warm_cache():
    """Proactively warm frequently accessed data."""
    cache = get_cache_manager()
    market_provider = get_market_data_provider()
    
    # Popular symbols for warming
    symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']
    
    for symbol in symbols:
        try:
            price = await asyncio.to_thread(market_provider.get_current_price, symbol)
            cache.set(f"market_data:{symbol}", price, ttl=60)
        except Exception as e:
            logger.warning(f"Cache warming failed for {symbol}: {e}")
```

### 2. Database Optimization

#### Query Optimization
```python
# Optimize frequently used queries
OPTIMIZED_QUERIES = {
    'portfolio_positions': """
        SELECT p.portfolio_id, p.symbol, p.quantity, m.current_price
        FROM portfolio_positions p
        JOIN market_data m ON p.symbol = m.symbol
        WHERE p.portfolio_id = %s
        AND m.timestamp > NOW() - INTERVAL '5 minutes'
    """,
    
    'risk_metrics': """
        SELECT portfolio_id, var_95, var_99, calculated_at
        FROM risk_metrics 
        WHERE portfolio_id = %s 
        AND calculated_at > %s
        ORDER BY calculated_at DESC
        LIMIT 1
    """
}

def execute_optimized_query(query_name, params):
    db_optimizer = get_db_optimizer()
    query = OPTIMIZED_QUERIES[query_name]
    return db_optimizer.execute_query(query, params, use_cache=True)
```

#### Connection Pool Tuning
```python
# Dynamic connection pool sizing based on load
class DynamicConnectionPool:
    def __init__(self):
        self.base_pool_size = 10
        self.max_pool_size = 50
        self.current_load = 0
    
    def get_optimal_pool_size(self):
        if self.current_load > 0.8:
            return min(self.base_pool_size * 2, self.max_pool_size)
        elif self.current_load < 0.3:
            return max(self.base_pool_size // 2, 5)
        return self.base_pool_size
```

### 3. API Optimization

#### Request Batching
```python
@app.post("/api/v1/batch-risk-analysis")
async def batch_risk_analysis(requests: List[RiskAnalysisRequest]):
    """Process multiple risk analysis requests in batch for better performance."""
    
    # Group requests by similar parameters for optimization
    grouped_requests = defaultdict(list)
    for req in requests:
        key = (req.confidence_level, req.time_horizon_days)
        grouped_requests[key].append(req)
    
    results = []
    for (confidence_level, time_horizon), req_group in grouped_requests.items():
        # Process similar requests together
        batch_results = await process_risk_batch(req_group, confidence_level, time_horizon)
        results.extend(batch_results)
    
    return results
```

#### Response Compression and Caching
```python
@app.middleware("http")
async def compression_middleware(request, call_next):
    response = await call_next(request)
    
    # Add caching headers for appropriate responses
    if request.url.path.startswith("/api/v1/market-data"):
        response.headers["Cache-Control"] = "public, max-age=60"
    elif request.url.path.startswith("/api/v1/risk-analysis"):
        response.headers["Cache-Control"] = "private, max-age=300"
    
    return response
```

### 4. System-Level Optimization

#### Async Processing Optimization
```python
# Optimize async task management
from libs.performance import get_async_task_manager

async def optimize_async_processing():
    task_manager = get_async_task_manager()
    
    # Configure optimal worker count based on CPU cores
    import os
    cpu_count = os.cpu_count()
    optimal_workers = min(cpu_count * 2, 16)  # Cap at 16 workers
    
    task_manager.set_worker_count(optimal_workers)
    
    # Use task batching for better throughput
    await task_manager.process_batch([
        ('risk_calculation', portfolio_1),
        ('risk_calculation', portfolio_2),
        ('risk_calculation', portfolio_3),
    ])
```

#### Memory Management
```python
# Implement intelligent garbage collection
import gc
from libs.performance import cleanup_memory

async def periodic_cleanup():
    """Periodic memory cleanup task."""
    while True:
        await asyncio.sleep(300)  # Every 5 minutes
        
        # Force garbage collection
        collected = gc.collect()
        logger.info(f"Garbage collection freed {collected} objects")
        
        # Clean up performance framework memory
        cleanup_memory()
        
        # Check memory usage
        memory_usage = get_memory_usage()
        if memory_usage['process_memory_percent'] > 80:
            logger.warning(f"High memory usage: {memory_usage['process_memory_percent']:.1f}%")
```

## Performance Benchmarks and Targets

### 1. Performance Targets

#### API Performance Targets
- **Response Time**: < 200ms (95th percentile)
- **Throughput**: > 1000 RPS per instance  
- **Error Rate**: < 0.1%
- **Availability**: > 99.9%

#### Cache Performance Targets
- **Hit Rate**: > 85%
- **Cache Response Time**: < 5ms
- **Memory Usage**: < 80% of allocated

#### Database Performance Targets
- **Query Time**: < 50ms (average)
- **Connection Pool Usage**: < 80%
- **Slow Queries**: < 1% of total queries

### 2. Performance Monitoring Schedule

#### Continuous Monitoring
- **Real-time metrics**: Every 10 seconds
- **Performance alerts**: Immediate
- **Dashboard updates**: Every 30 seconds

#### Periodic Analysis
- **Daily performance reports**: Automated
- **Weekly performance analysis**: Manual review
- **Monthly optimization review**: Team review

#### Performance Testing Schedule
- **Smoke tests**: After each deployment
- **Load tests**: Weekly
- **Stress tests**: Monthly
- **Performance regression tests**: On every release

## Conclusion

The performance optimization framework provides comprehensive tools for monitoring, testing, and optimizing the risk management infrastructure. By following this implementation guide and maintaining regular performance monitoring, the system can achieve high throughput, low latency, and optimal resource utilization.

Key success factors:
1. **Proactive monitoring** with comprehensive metrics
2. **Regular performance testing** and benchmarking
3. **Continuous optimization** based on real-world usage patterns
4. **Scalable architecture** with horizontal scaling capabilities
5. **Robust alerting** for early issue detection

For additional support or advanced optimization needs, refer to the specific component documentation or contact the performance engineering team.
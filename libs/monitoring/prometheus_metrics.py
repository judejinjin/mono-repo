"""
Prometheus Metrics Integration
Comprehensive monitoring endpoints for all services
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import time
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import threading
import logging
from dataclasses import dataclass
from enum import Enum

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST
    from prometheus_client.multiprocess import MultiProcessCollector
    from fastapi import FastAPI, Response
    from fastapi.responses import PlainTextResponse
    import psutil
except ImportError:
    # Mock Prometheus client for environments without it
    class MockMetric:
        def inc(self, *args, **kwargs): pass
        def observe(self, *args, **kwargs): pass
        def set(self, *args, **kwargs): pass
        def info(self, *args, **kwargs): pass
    
    Counter = Histogram = Gauge = Info = MockMetric
    generate_latest = lambda *args: b"# Metrics not available"
    CollectorRegistry = lambda: None
    MultiProcessCollector = lambda *args: None
    CONTENT_TYPE_LATEST = "text/plain"

try:
    from config import get_config
    from libs.monitoring.health_endpoints import HealthCheckManager
except ImportError:
    get_config = lambda: {}
    HealthCheckManager = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics."""
    COUNTER = "counter"
    HISTOGRAM = "histogram"
    GAUGE = "gauge"
    INFO = "info"


@dataclass
class MetricConfig:
    """Configuration for a metric."""
    name: str
    help: str
    labels: List[str] = None
    metric_type: MetricType = MetricType.COUNTER


class PrometheusMetricsCollector:
    """Comprehensive Prometheus metrics collector."""
    
    def __init__(self, service_name: str = "risk_management", environment: str = None):
        self.service_name = service_name
        self.environment = environment or os.getenv('ENVIRONMENT', 'dev')
        self.config = get_config()
        
        # Initialize registry
        self.registry = CollectorRegistry()
        
        # Initialize metrics
        self._init_system_metrics()
        self._init_application_metrics()
        self._init_business_metrics()
        
        # Performance tracking
        self._request_durations = defaultdict(list)
        self._error_counts = Counter()
        self._lock = threading.Lock()
        
        # Health check integration
        self.health_manager = HealthCheckManager() if HealthCheckManager else None
        
        logger.info(f"Prometheus metrics collector initialized for {service_name} in {environment}")
    
    def _init_system_metrics(self):
        """Initialize system-level metrics."""
        # System info
        self.system_info = Info(
            'system_info',
            'System information',
            registry=self.registry
        )
        self.system_info.info({
            'service': self.service_name,
            'environment': self.environment,
            'version': os.getenv('APP_VERSION', '1.0.0'),
            'python_version': sys.version.split()[0]
        })
        
        # CPU metrics
        self.cpu_usage = Gauge(
            'cpu_usage_percent',
            'CPU usage percentage',
            ['core'],
            registry=self.registry
        )
        
        # Memory metrics
        self.memory_usage = Gauge(
            'memory_usage_bytes',
            'Memory usage in bytes',
            ['type'],
            registry=self.registry
        )
        
        # Disk metrics
        self.disk_usage = Gauge(
            'disk_usage_bytes',
            'Disk usage in bytes',
            ['device', 'type'],
            registry=self.registry
        )
        
        # Network metrics
        self.network_bytes = Counter(
            'network_bytes_total',
            'Total network bytes',
            ['direction', 'interface'],
            registry=self.registry
        )
        
        # Process metrics
        self.process_open_fds = Gauge(
            'process_open_file_descriptors',
            'Number of open file descriptors',
            registry=self.registry
        )
        
        self.process_threads = Gauge(
            'process_threads_total',
            'Number of threads',
            registry=self.registry
        )
    
    def _init_application_metrics(self):
        """Initialize application-level metrics."""
        # HTTP request metrics
        self.http_requests_total = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status_code'],
            registry=self.registry
        )
        
        self.http_request_duration = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint'],
            buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
            registry=self.registry
        )
        
        # Error metrics
        self.errors_total = Counter(
            'errors_total',
            'Total errors',
            ['type', 'component'],
            registry=self.registry
        )
        
        # Database metrics
        self.db_connections_active = Gauge(
            'database_connections_active',
            'Active database connections',
            ['database'],
            registry=self.registry
        )
        
        self.db_query_duration = Histogram(
            'database_query_duration_seconds',
            'Database query duration in seconds',
            ['database', 'operation'],
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0],
            registry=self.registry
        )
        
        self.db_queries_total = Counter(
            'database_queries_total',
            'Total database queries',
            ['database', 'operation', 'status'],
            registry=self.registry
        )
        
        # Cache metrics
        self.cache_operations_total = Counter(
            'cache_operations_total',
            'Total cache operations',
            ['operation', 'result'],
            registry=self.registry
        )
        
        self.cache_size = Gauge(
            'cache_size_bytes',
            'Cache size in bytes',
            ['cache_name'],
            registry=self.registry
        )
        
        # API rate limiting
        self.rate_limit_exceeded = Counter(
            'rate_limit_exceeded_total',
            'Total rate limit exceeded events',
            ['endpoint', 'client'],
            registry=self.registry
        )
    
    def _init_business_metrics(self):
        """Initialize business-specific metrics."""
        # Portfolio metrics
        self.portfolios_processed = Counter(
            'portfolios_processed_total',
            'Total portfolios processed',
            ['operation'],
            registry=self.registry
        )
        
        self.portfolio_processing_duration = Histogram(
            'portfolio_processing_duration_seconds',
            'Portfolio processing duration in seconds',
            ['operation'],
            buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 300.0],
            registry=self.registry
        )
        
        # Risk calculation metrics
        self.risk_calculations_total = Counter(
            'risk_calculations_total',
            'Total risk calculations',
            ['metric_type', 'status'],
            registry=self.registry
        )
        
        self.risk_calculation_duration = Histogram(
            'risk_calculation_duration_seconds',
            'Risk calculation duration in seconds',
            ['metric_type'],
            buckets=[0.1, 0.5, 1.0, 5.0, 10.0, 30.0],
            registry=self.registry
        )
        
        # Market data metrics
        self.market_data_requests = Counter(
            'market_data_requests_total',
            'Total market data requests',
            ['source', 'symbol', 'status'],
            registry=self.registry
        )
        
        self.market_data_latency = Histogram(
            'market_data_latency_seconds',
            'Market data request latency in seconds',
            ['source'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
            registry=self.registry
        )
        
        # User activity metrics
        self.user_actions = Counter(
            'user_actions_total',
            'Total user actions',
            ['action_type', 'user_role'],
            registry=self.registry
        )
        
        self.user_sessions_active = Gauge(
            'user_sessions_active',
            'Active user sessions',
            registry=self.registry
        )
        
        # Data quality metrics
        self.data_quality_checks = Counter(
            'data_quality_checks_total',
            'Total data quality checks',
            ['check_type', 'result'],
            registry=self.registry
        )
        
        self.data_freshness = Gauge(
            'data_freshness_seconds',
            'Data freshness in seconds since last update',
            ['data_type'],
            registry=self.registry
        )
    
    def update_system_metrics(self):
        """Update system metrics with current values."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
            for i, usage in enumerate(cpu_percent):
                self.cpu_usage.labels(core=f'cpu{i}').set(usage)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.memory_usage.labels(type='used').set(memory.used)
            self.memory_usage.labels(type='available').set(memory.available)
            self.memory_usage.labels(type='total').set(memory.total)
            
            # Disk usage
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    device = partition.device.replace('/', '_')
                    self.disk_usage.labels(device=device, type='used').set(usage.used)
                    self.disk_usage.labels(device=device, type='free').set(usage.free)
                    self.disk_usage.labels(device=device, type='total').set(usage.total)
                except PermissionError:
                    continue
            
            # Network I/O
            network = psutil.net_io_counters(pernic=True)
            for interface, stats in network.items():
                self.network_bytes.labels(direction='sent', interface=interface)._value._value = stats.bytes_sent
                self.network_bytes.labels(direction='received', interface=interface)._value._value = stats.bytes_recv
            
            # Process metrics
            process = psutil.Process()
            self.process_open_fds.set(process.num_fds())
            self.process_threads.set(process.num_threads())
            
        except Exception as e:
            logger.error(f"Error updating system metrics: {e}")
    
    def record_http_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics."""
        self.http_requests_total.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
        self.http_request_duration.labels(method=method, endpoint=endpoint).observe(duration)
    
    def record_error(self, error_type: str, component: str):
        """Record error metrics."""
        self.errors_total.labels(type=error_type, component=component).inc()
        
        with self._lock:
            self._error_counts[f"{component}:{error_type}"] += 1
    
    def record_database_query(self, database: str, operation: str, duration: float, status: str = 'success'):
        """Record database query metrics."""
        self.db_queries_total.labels(database=database, operation=operation, status=status).inc()
        self.db_query_duration.labels(database=database, operation=operation).observe(duration)
    
    def set_active_db_connections(self, database: str, count: int):
        """Set active database connection count."""
        self.db_connections_active.labels(database=database).set(count)
    
    def record_cache_operation(self, operation: str, result: str):
        """Record cache operation metrics."""
        self.cache_operations_total.labels(operation=operation, result=result).inc()
    
    def set_cache_size(self, cache_name: str, size_bytes: int):
        """Set cache size metrics."""
        self.cache_size.labels(cache_name=cache_name).set(size_bytes)
    
    def record_rate_limit_exceeded(self, endpoint: str, client: str):
        """Record rate limit exceeded events."""
        self.rate_limit_exceeded.labels(endpoint=endpoint, client=client).inc()
    
    def record_portfolio_processing(self, operation: str, duration: float):
        """Record portfolio processing metrics."""
        self.portfolios_processed.labels(operation=operation).inc()
        self.portfolio_processing_duration.labels(operation=operation).observe(duration)
    
    def record_risk_calculation(self, metric_type: str, duration: float, status: str = 'success'):
        """Record risk calculation metrics."""
        self.risk_calculations_total.labels(metric_type=metric_type, status=status).inc()
        self.risk_calculation_duration.labels(metric_type=metric_type).observe(duration)
    
    def record_market_data_request(self, source: str, symbol: str, latency: float, status: str = 'success'):
        """Record market data request metrics."""
        self.market_data_requests.labels(source=source, symbol=symbol, status=status).inc()
        self.market_data_latency.labels(source=source).observe(latency)
    
    def record_user_action(self, action_type: str, user_role: str = 'unknown'):
        """Record user action metrics."""
        self.user_actions.labels(action_type=action_type, user_role=user_role).inc()
    
    def set_active_user_sessions(self, count: int):
        """Set active user session count."""
        self.user_sessions_active.set(count)
    
    def record_data_quality_check(self, check_type: str, result: str):
        """Record data quality check metrics."""
        self.data_quality_checks.labels(check_type=check_type, result=result).inc()
    
    def set_data_freshness(self, data_type: str, last_update: datetime):
        """Set data freshness metrics."""
        freshness_seconds = (datetime.utcnow() - last_update).total_seconds()
        self.data_freshness.labels(data_type=data_type).set(freshness_seconds)
    
    def get_metrics(self) -> str:
        """Get all metrics in Prometheus format."""
        # Update system metrics before returning
        self.update_system_metrics()
        
        # Include health check metrics if available
        if self.health_manager:
            try:
                health_status = self.health_manager.get_health_status()
                
                # Create health metrics
                health_gauge = Gauge('service_health', 'Service health status', ['component'], registry=None)
                
                for component, status in health_status.items():
                    if component != 'overall':
                        health_value = 1 if status.get('status') == 'healthy' else 0
                        health_gauge.labels(component=component).set(health_value)
            
            except Exception as e:
                logger.error(f"Error adding health metrics: {e}")
        
        return generate_latest(self.registry).decode('utf-8')
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics."""
        with self._lock:
            error_summary = dict(self._error_counts.most_common(10))
        
        return {
            'service': self.service_name,
            'environment': self.environment,
            'uptime_seconds': time.time() - self._start_time if hasattr(self, '_start_time') else 0,
            'top_errors': error_summary,
            'registry_collectors': len(self.registry._collector_to_names),
        }


class MetricsMiddleware:
    """FastAPI middleware for automatic metrics collection."""
    
    def __init__(self, app: FastAPI, metrics_collector: PrometheusMetricsCollector):
        self.app = app
        self.metrics = metrics_collector
        self._setup_middleware()
    
    def _setup_middleware(self):
        """Setup middleware for automatic metrics collection."""
        @self.app.middleware("http")
        async def metrics_middleware(request, call_next):
            start_time = time.time()
            
            try:
                response = await call_next(request)
                duration = time.time() - start_time
                
                # Record metrics
                self.metrics.record_http_request(
                    method=request.method,
                    endpoint=request.url.path,
                    status_code=response.status_code,
                    duration=duration
                )
                
                return response
                
            except Exception as e:
                duration = time.time() - start_time
                
                # Record error
                self.metrics.record_error(
                    error_type=type(e).__name__,
                    component='http_request'
                )
                
                # Record failed request
                self.metrics.record_http_request(
                    method=request.method,
                    endpoint=request.url.path,
                    status_code=500,
                    duration=duration
                )
                
                raise


def setup_metrics_endpoints(app: FastAPI, metrics_collector: PrometheusMetricsCollector):
    """Setup metrics endpoints in FastAPI app."""
    
    @app.get("/metrics", response_class=PlainTextResponse)
    async def get_metrics():
        """Prometheus metrics endpoint."""
        return metrics_collector.get_metrics()
    
    @app.get("/metrics/summary")
    async def get_metrics_summary():
        """Get metrics summary."""
        return metrics_collector.get_summary_stats()
    
    # Setup middleware
    MetricsMiddleware(app, metrics_collector)
    
    logger.info("Metrics endpoints configured")


# Global instance
_metrics_collector = None

def get_metrics_collector() -> PrometheusMetricsCollector:
    """Get global metrics collector instance."""
    global _metrics_collector
    if _metrics_collector is None:
        service_name = os.getenv('SERVICE_NAME', 'risk_management')
        _metrics_collector = PrometheusMetricsCollector(service_name)
        _metrics_collector._start_time = time.time()
    return _metrics_collector


# Decorator for automatic timing
def timed_operation(operation_name: str, component: str = 'unknown'):
    """Decorator for timing operations."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            metrics = get_metrics_collector()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Record success
                if hasattr(metrics, 'record_operation_duration'):
                    metrics.record_operation_duration(operation_name, duration, 'success')
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                # Record error
                metrics.record_error(type(e).__name__, component)
                
                if hasattr(metrics, 'record_operation_duration'):
                    metrics.record_operation_duration(operation_name, duration, 'error')
                
                raise
                
        return wrapper
    return decorator


# Context manager for timing
class TimedOperation:
    """Context manager for timing operations."""
    
    def __init__(self, operation_name: str, component: str = 'unknown'):
        self.operation_name = operation_name
        self.component = component
        self.start_time = None
        self.metrics = get_metrics_collector()
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        
        if exc_type is None:
            # Success
            if hasattr(self.metrics, 'record_operation_duration'):
                self.metrics.record_operation_duration(self.operation_name, duration, 'success')
        else:
            # Error
            self.metrics.record_error(exc_type.__name__, self.component)
            if hasattr(self.metrics, 'record_operation_duration'):
                self.metrics.record_operation_duration(self.operation_name, duration, 'error')
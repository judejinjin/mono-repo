"""
Prometheus metrics integration for the risk platform.
Provides Prometheus-compatible metrics export when client is available.
"""

import time
from typing import Dict, Any, Optional, List
from .monitoring import MetricsCollector
import logging

logger = logging.getLogger(__name__)

class PrometheusExporter:
    """Exports metrics in Prometheus format."""
    
    def __init__(self, metrics_collector: MetricsCollector = None):
        self.metrics = metrics_collector
        self._prometheus_available = False
        self._registry = None
        self._metrics_cache = {}
        
        # Try to import Prometheus client
        try:
            import prometheus_client
            self._prometheus_available = True
            self._registry = prometheus_client.CollectorRegistry()
            logger.info("Prometheus client available, metrics will be exported")
        except ImportError:
            logger.info("Prometheus client not available, using fallback metrics")
    
    def create_counter(self, name: str, description: str, labels: List[str] = None):
        """Create Prometheus Counter."""
        if not self._prometheus_available:
            return None
        
        try:
            from prometheus_client import Counter
            counter = Counter(name, description, labels or [], registry=self._registry)
            self._metrics_cache[name] = counter
            return counter
        except Exception as e:
            logger.error(f"Failed to create counter {name}: {e}")
            return None
    
    def create_gauge(self, name: str, description: str, labels: List[str] = None):
        """Create Prometheus Gauge."""
        if not self._prometheus_available:
            return None
        
        try:
            from prometheus_client import Gauge
            gauge = Gauge(name, description, labels or [], registry=self._registry)
            self._metrics_cache[name] = gauge
            return gauge
        except Exception as e:
            logger.error(f"Failed to create gauge {name}: {e}")
            return None
    
    def create_histogram(self, name: str, description: str, 
                        buckets: tuple = None, labels: List[str] = None):
        """Create Prometheus Histogram."""
        if not self._prometheus_available:
            return None
        
        try:
            from prometheus_client import Histogram
            histogram = Histogram(
                name, description, 
                labels or [], 
                buckets=buckets,
                registry=self._registry
            )
            self._metrics_cache[name] = histogram
            return histogram
        except Exception as e:
            logger.error(f"Failed to create histogram {name}: {e}")
            return None
    
    def generate_prometheus_metrics(self) -> str:
        """Generate Prometheus metrics format."""
        if self._prometheus_available:
            try:
                from prometheus_client import generate_latest
                return generate_latest(self._registry).decode('utf-8')
            except Exception as e:
                logger.error(f"Failed to generate Prometheus metrics: {e}")
        
        # Fallback: generate simple text format from our metrics
        return self._generate_fallback_metrics()
    
    def _generate_fallback_metrics(self) -> str:
        """Generate simple metrics format when Prometheus client unavailable."""
        if not self.metrics:
            return "# No metrics available\n"
        
        metrics_data = self.metrics.get_metrics()
        lines = []
        
        # Add metadata
        lines.append("# HELP risk_platform_info Information about the risk platform")
        lines.append("# TYPE risk_platform_info gauge")
        lines.append("risk_platform_info{version=\"1.0.0\"} 1")
        lines.append("")
        
        # Add uptime
        uptime = metrics_data.get('uptime_seconds', 0)
        lines.append("# HELP risk_platform_uptime_seconds Total uptime in seconds")
        lines.append("# TYPE risk_platform_uptime_seconds gauge")
        lines.append(f"risk_platform_uptime_seconds {uptime}")
        lines.append("")
        
        # Add counters
        for name, value in metrics_data.get('counters', {}).items():
            safe_name = self._sanitize_metric_name(name)
            lines.append(f"# HELP {safe_name} Counter metric")
            lines.append(f"# TYPE {safe_name} counter")
            lines.append(f"{safe_name} {value}")
            lines.append("")
        
        # Add gauges
        for name, value in metrics_data.get('gauges', {}).items():
            safe_name = self._sanitize_metric_name(name)
            lines.append(f"# HELP {safe_name} Gauge metric")
            lines.append(f"# TYPE {safe_name} gauge")
            lines.append(f"{safe_name} {value}")
            lines.append("")
        
        # Add histogram summaries
        for name, data in metrics_data.get('histograms', {}).items():
            safe_name = self._sanitize_metric_name(name)
            lines.append(f"# HELP {safe_name} Histogram metric")
            lines.append(f"# TYPE {safe_name} summary")
            lines.append(f"{safe_name}_count {data['count']}")
            lines.append(f"{safe_name}_sum {data['sum']}")
            lines.append(f"{safe_name}{{quantile=\"0.5\"}} {data['p50']}")
            lines.append(f"{safe_name}{{quantile=\"0.95\"}} {data['p95']}")
            lines.append(f"{safe_name}{{quantile=\"0.99\"}} {data['p99']}")
            lines.append("")
        
        return '\n'.join(lines)
    
    def _sanitize_metric_name(self, name: str) -> str:
        """Sanitize metric name for Prometheus."""
        # Replace invalid characters with underscores
        safe_name = ''.join(c if c.isalnum() else '_' for c in name.lower())
        # Remove multiple consecutive underscores
        while '__' in safe_name:
            safe_name = safe_name.replace('__', '_')
        # Remove leading/trailing underscores
        safe_name = safe_name.strip('_')
        # Ensure it doesn't start with a number
        if safe_name and safe_name[0].isdigit():
            safe_name = 'metric_' + safe_name
        return safe_name or 'unnamed_metric'

class RiskPlatformMetrics:
    """Risk platform specific metrics collection."""
    
    def __init__(self, prometheus_exporter: PrometheusExporter = None):
        self.exporter = prometheus_exporter or PrometheusExporter()
        self._setup_standard_metrics()
    
    def _setup_standard_metrics(self):
        """Set up standard risk platform metrics."""
        # HTTP request metrics
        self.http_requests_total = self.exporter.create_counter(
            'risk_platform_http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status']
        )
        
        self.http_request_duration = self.exporter.create_histogram(
            'risk_platform_http_request_duration_seconds',
            'HTTP request duration in seconds',
            buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
            labels=['method', 'endpoint']
        )
        
        # Authentication metrics
        self.auth_attempts_total = self.exporter.create_counter(
            'risk_platform_auth_attempts_total',
            'Total authentication attempts',
            ['result']  # success, failure, error
        )
        
        self.active_sessions = self.exporter.create_gauge(
            'risk_platform_active_sessions',
            'Number of active user sessions'
        )
        
        # Risk calculation metrics
        self.risk_calculations_total = self.exporter.create_counter(
            'risk_platform_risk_calculations_total',
            'Total risk calculations performed',
            ['portfolio_type', 'status']
        )
        
        self.risk_calculation_duration = self.exporter.create_histogram(
            'risk_platform_risk_calculation_duration_seconds',
            'Risk calculation duration in seconds',
            buckets=(1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0),
            labels=['portfolio_type']
        )
        
        # Database metrics
        self.db_connections_active = self.exporter.create_gauge(
            'risk_platform_db_connections_active',
            'Number of active database connections'
        )
        
        self.db_query_duration = self.exporter.create_histogram(
            'risk_platform_db_query_duration_seconds',
            'Database query duration in seconds',
            buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0),
            labels=['operation']
        )
        
        # JupyterHub metrics
        self.jupyter_sessions_active = self.exporter.create_gauge(
            'risk_platform_jupyter_sessions_active',
            'Number of active JupyterHub sessions'
        )
        
        self.jupyter_notebook_executions = self.exporter.create_counter(
            'risk_platform_jupyter_notebook_executions_total',
            'Total notebook executions',
            ['user_role', 'status']
        )
        
        # Cache metrics
        self.cache_operations_total = self.exporter.create_counter(
            'risk_platform_cache_operations_total',
            'Total cache operations',
            ['operation', 'result']  # hit, miss, set, delete
        )
        
        # System resource metrics
        self.memory_usage_bytes = self.exporter.create_gauge(
            'risk_platform_memory_usage_bytes',
            'Memory usage in bytes'
        )
        
        self.cpu_usage_percent = self.exporter.create_gauge(
            'risk_platform_cpu_usage_percent',
            'CPU usage percentage'
        )
    
    def record_http_request(self, method: str, endpoint: str, status_code: int, 
                           duration_seconds: float):
        """Record HTTP request metrics."""
        status_class = f"{status_code // 100}xx"
        
        if self.http_requests_total:
            self.http_requests_total.labels(
                method=method, 
                endpoint=endpoint, 
                status=status_class
            ).inc()
        
        if self.http_request_duration:
            self.http_request_duration.labels(
                method=method, 
                endpoint=endpoint
            ).observe(duration_seconds)
    
    def record_auth_attempt(self, result: str):
        """Record authentication attempt."""
        if self.auth_attempts_total:
            self.auth_attempts_total.labels(result=result).inc()
    
    def set_active_sessions(self, count: int):
        """Set active sessions count."""
        if self.active_sessions:
            self.active_sessions.set(count)
    
    def record_risk_calculation(self, portfolio_type: str, status: str, 
                              duration_seconds: float):
        """Record risk calculation metrics."""
        if self.risk_calculations_total:
            self.risk_calculations_total.labels(
                portfolio_type=portfolio_type, 
                status=status
            ).inc()
        
        if self.risk_calculation_duration and status == 'success':
            self.risk_calculation_duration.labels(
                portfolio_type=portfolio_type
            ).observe(duration_seconds)
    
    def set_db_connections(self, count: int):
        """Set active database connections."""
        if self.db_connections_active:
            self.db_connections_active.set(count)
    
    def record_db_query(self, operation: str, duration_seconds: float):
        """Record database query metrics."""
        if self.db_query_duration:
            self.db_query_duration.labels(operation=operation).observe(duration_seconds)
    
    def set_jupyter_sessions(self, count: int):
        """Set active Jupyter sessions."""
        if self.jupyter_sessions_active:
            self.jupyter_sessions_active.set(count)
    
    def record_notebook_execution(self, user_role: str, status: str):
        """Record notebook execution."""
        if self.jupyter_notebook_executions:
            self.jupyter_notebook_executions.labels(
                user_role=user_role, 
                status=status
            ).inc()
    
    def record_cache_operation(self, operation: str, result: str):
        """Record cache operation."""
        if self.cache_operations_total:
            self.cache_operations_total.labels(
                operation=operation, 
                result=result
            ).inc()
    
    def update_system_metrics(self, memory_bytes: float, cpu_percent: float):
        """Update system resource metrics."""
        if self.memory_usage_bytes:
            self.memory_usage_bytes.set(memory_bytes)
        if self.cpu_usage_percent:
            self.cpu_usage_percent.set(cpu_percent)

# Global instances
_prometheus_exporter = None
_risk_platform_metrics = None

def get_prometheus_exporter() -> PrometheusExporter:
    """Get global Prometheus exporter."""
    global _prometheus_exporter
    if _prometheus_exporter is None:
        _prometheus_exporter = PrometheusExporter()
    return _prometheus_exporter

def get_risk_platform_metrics() -> RiskPlatformMetrics:
    """Get global risk platform metrics."""
    global _risk_platform_metrics
    if _risk_platform_metrics is None:
        _risk_platform_metrics = RiskPlatformMetrics()
    return _risk_platform_metrics
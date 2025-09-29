"""
Monitoring library for the risk management platform.
Provides metrics collection, performance monitoring, health checks, and logging.
"""

from .monitoring import (
    MetricsCollector, 
    PerformanceMonitor, 
    HealthChecker,
    get_metrics_collector,
    get_performance_monitor,
    get_health_checker
)
from .prometheus import PrometheusExporter, setup_prometheus_metrics
from .health_endpoints import (
    HealthCheckManager,
    add_health_endpoints,
    create_standalone_health_app
)

__version__ = "0.1.0"

__all__ = [
    'MetricsCollector',
    'PerformanceMonitor', 
    'HealthChecker',
    'PrometheusExporter',
    'RequestContext',
    'StructuredFormatter',
    'LogAggregator',
    'AuditLogger',
    'SecurityLogger',
    'HealthCheckManager',
    'get_metrics_collector',
    'get_performance_monitor',
    'get_health_checker',
    'setup_prometheus_metrics',
    'get_log_aggregator',
    'get_audit_logger',
    'get_security_logger',
    'setup_structured_logging',
    'request_context',
    'set_request_context',
    'get_request_context',
    'log_user_action',
    'log_auth_event',
    'log_security_event',
    'add_health_endpoints',
    'create_standalone_health_app'
]
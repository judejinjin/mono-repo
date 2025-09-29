"""
Monitoring library for the mono-repo risk platform.
Provides metrics collection, logging, and health monitoring.
"""

import time
import logging
import json
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from contextlib import contextmanager
from functools import wraps
import threading
from collections import defaultdict, deque
import os

# Configure logging
class CustomFormatter(logging.Formatter):
    """Custom formatter for structured logging."""
    
    def format(self, record):
        """Format log record with additional context."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'duration_ms'):
            log_data['duration_ms'] = record.duration_ms
        if hasattr(record, 'status_code'):
            log_data['status_code'] = record.status_code
        
        return json.dumps(log_data)

class LoggerManager:
    """Centralized logging management."""
    
    def __init__(self, service_name: str = None):
        self.service_name = service_name or 'risk-platform'
        self._setup_logging()
    
    def _setup_logging(self):
        """Set up logging configuration."""
        # Get log level from environment
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        
        # Create custom formatter
        formatter = CustomFormatter()
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # Root logger configuration
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level))
        root_logger.addHandler(console_handler)
        
        # Prevent duplicate logs
        root_logger.propagate = False
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get logger with service context."""
        logger_name = f"{self.service_name}.{name}"
        return logging.getLogger(logger_name)
    
    def log_request(self, logger: logging.Logger, method: str, path: str, 
                   status_code: int, duration_ms: float, user_id: str = None):
        """Log HTTP request with structured data."""
        extra = {
            'request_method': method,
            'request_path': path,
            'status_code': status_code,
            'duration_ms': duration_ms
        }
        
        if user_id:
            extra['user_id'] = user_id
        
        level = logging.INFO if status_code < 400 else logging.ERROR
        logger.log(level, f"{method} {path} {status_code} {duration_ms}ms", extra=extra)

class MetricsCollector:
    """Collects application metrics without external dependencies."""
    
    def __init__(self):
        self._metrics = defaultdict(lambda: defaultdict(float))
        self._histograms = defaultdict(lambda: deque(maxlen=1000))
        self._counters = defaultdict(float)
        self._gauges = defaultdict(float)
        self._lock = threading.Lock()
        self.start_time = time.time()
    
    def increment_counter(self, name: str, value: float = 1.0, tags: Dict[str, str] = None):
        """Increment a counter metric."""
        with self._lock:
            key = self._make_key(name, tags)
            self._counters[key] += value
    
    def set_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """Set a gauge metric."""
        with self._lock:
            key = self._make_key(name, tags)
            self._gauges[key] = value
    
    def record_histogram(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a histogram value."""
        with self._lock:
            key = self._make_key(name, tags)
            self._histograms[key].append(value)
    
    def record_timer(self, name: str, duration_seconds: float, tags: Dict[str, str] = None):
        """Record timing metric."""
        self.record_histogram(f"{name}_duration_seconds", duration_seconds, tags)
        self.increment_counter(f"{name}_total", 1, tags)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics."""
        with self._lock:
            metrics = {
                'counters': dict(self._counters),
                'gauges': dict(self._gauges),
                'histograms': {},
                'uptime_seconds': time.time() - self.start_time
            }
            
            # Calculate histogram statistics
            for key, values in self._histograms.items():
                if values:
                    sorted_values = sorted(values)
                    count = len(sorted_values)
                    metrics['histograms'][key] = {
                        'count': count,
                        'sum': sum(sorted_values),
                        'min': sorted_values[0],
                        'max': sorted_values[-1],
                        'avg': sum(sorted_values) / count,
                        'p50': sorted_values[int(count * 0.5)],
                        'p95': sorted_values[int(count * 0.95)],
                        'p99': sorted_values[int(count * 0.99)]
                    }
            
            return metrics
    
    def reset_metrics(self):
        """Reset all metrics."""
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()
    
    def _make_key(self, name: str, tags: Dict[str, str] = None) -> str:
        """Create metric key with tags."""
        if not tags:
            return name
        
        tag_str = ','.join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}#{tag_str}"

class PerformanceMonitor:
    """Monitors application performance."""
    
    def __init__(self, metrics_collector: MetricsCollector = None):
        self.metrics = metrics_collector or MetricsCollector()
        self.logger = logging.getLogger(__name__)
    
    @contextmanager
    def time_operation(self, operation_name: str, tags: Dict[str, str] = None):
        """Context manager for timing operations."""
        start_time = time.time()
        
        try:
            yield
            status = "success"
        except Exception as e:
            status = "error"
            self.logger.error(f"Operation {operation_name} failed: {e}")
            raise
        finally:
            duration = time.time() - start_time
            
            final_tags = tags or {}
            final_tags['status'] = status
            
            self.metrics.record_timer(operation_name, duration, final_tags)
    
    def time_function(self, name: str = None, tags: Dict[str, str] = None):
        """Decorator for timing functions."""
        def decorator(func: Callable) -> Callable:
            operation_name = name or f"{func.__module__}.{func.__name__}"
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                with self.time_operation(operation_name, tags):
                    return func(*args, **kwargs)
            
            return wrapper
        return decorator
    
    def monitor_resource_usage(self):
        """Monitor system resource usage."""
        try:
            import psutil
            
            # CPU usage
            cpu_percent = psutil.cpu_percent()
            self.metrics.set_gauge('system_cpu_percent', cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.metrics.set_gauge('system_memory_percent', memory.percent)
            self.metrics.set_gauge('system_memory_available_bytes', memory.available)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self.metrics.set_gauge('system_disk_percent', disk.percent)
            self.metrics.set_gauge('system_disk_free_bytes', disk.free)
            
        except ImportError:
            # psutil not available, skip system metrics
            pass
        except Exception as e:
            self.logger.warning(f"Failed to collect system metrics: {e}")

class HealthChecker:
    """Application health monitoring."""
    
    def __init__(self):
        self._health_checks = {}
        self.logger = logging.getLogger(__name__)
    
    def register_check(self, name: str, check_func: Callable[[], bool], 
                      timeout: float = 5.0):
        """Register a health check."""
        self._health_checks[name] = {
            'func': check_func,
            'timeout': timeout
        }
    
    def run_check(self, name: str) -> Dict[str, Any]:
        """Run a single health check."""
        if name not in self._health_checks:
            return {
                'name': name,
                'status': 'error',
                'message': 'Check not registered'
            }
        
        check = self._health_checks[name]
        start_time = time.time()
        
        try:
            # Simple timeout implementation
            result = check['func']()
            duration = time.time() - start_time
            
            return {
                'name': name,
                'status': 'healthy' if result else 'unhealthy',
                'duration_ms': round(duration * 1000, 2),
                'timestamp': datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"Health check {name} failed: {e}")
            
            return {
                'name': name,
                'status': 'error',
                'error': str(e),
                'duration_ms': round(duration * 1000, 2),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all registered health checks."""
        results = {}
        overall_status = 'healthy'
        
        for name in self._health_checks:
            check_result = self.run_check(name)
            results[name] = check_result
            
            if check_result['status'] != 'healthy':
                overall_status = 'unhealthy'
        
        return {
            'status': overall_status,
            'checks': results,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def get_basic_health(self) -> Dict[str, Any]:
        """Get basic application health."""
        return {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'uptime_seconds': time.time() - self.start_time if hasattr(self, 'start_time') else 0
        }

class AlertManager:
    """Simple alerting system for critical issues."""
    
    def __init__(self, metrics_collector: MetricsCollector = None):
        self.metrics = metrics_collector or MetricsCollector()
        self.logger = logging.getLogger(__name__)
        self._alert_rules = {}
        self._fired_alerts = {}
        self._alert_cooldown = 300  # 5 minutes
    
    def add_rule(self, name: str, condition_func: Callable[[], bool], 
                severity: str = 'warning', message: str = None):
        """Add an alert rule."""
        self._alert_rules[name] = {
            'condition': condition_func,
            'severity': severity,
            'message': message or f"Alert condition met for {name}"
        }
    
    def check_alerts(self):
        """Check all alert conditions."""
        current_time = time.time()
        
        for rule_name, rule in self._alert_rules.items():
            try:
                if rule['condition']():
                    self._handle_alert(rule_name, rule, current_time)
            except Exception as e:
                self.logger.error(f"Alert rule {rule_name} check failed: {e}")
    
    def _handle_alert(self, rule_name: str, rule: Dict[str, Any], current_time: float):
        """Handle fired alert."""
        # Check cooldown
        last_fired = self._fired_alerts.get(rule_name, 0)
        if current_time - last_fired < self._alert_cooldown:
            return  # Still in cooldown
        
        # Fire alert
        self._fired_alerts[rule_name] = current_time
        
        alert_data = {
            'rule': rule_name,
            'severity': rule['severity'],
            'message': rule['message'],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Log alert
        if rule['severity'] == 'critical':
            self.logger.critical(f"ALERT: {alert_data}")
        else:
            self.logger.warning(f"ALERT: {alert_data}")
        
        # Count alert
        self.metrics.increment_counter(
            'alerts_fired_total',
            tags={'rule': rule_name, 'severity': rule['severity']}
        )

# Default health checks
def database_health_check() -> bool:
    """Check database connectivity."""
    try:
        from libs.db import get_session
        with get_session() as session:
            session.execute("SELECT 1")
        return True
    except Exception:
        return False

def redis_health_check() -> bool:
    """Check Redis connectivity."""
    try:
        from libs.storage import get_redis_client
        redis_client = get_redis_client()
        return redis_client.client is not None and redis_client.client.ping()
    except Exception:
        return False

def s3_health_check() -> bool:
    """Check S3 connectivity."""
    try:
        from libs.storage import get_s3_client
        s3_client = get_s3_client()
        return s3_client.client is not None
    except Exception:
        return False

# Global instances
_logger_manager = None
_metrics_collector = None
_performance_monitor = None
_health_checker = None
_alert_manager = None

def get_logger_manager() -> LoggerManager:
    """Get global logger manager."""
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = LoggerManager()
    return _logger_manager

def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector

def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor."""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor

def get_health_checker() -> HealthChecker:
    """Get global health checker."""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
        # Register default health checks
        _health_checker.register_check('database', database_health_check)
        _health_checker.register_check('redis', redis_health_check)
        _health_checker.register_check('s3', s3_health_check)
    return _health_checker

def get_alert_manager() -> AlertManager:
    """Get global alert manager."""
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager()
    return _alert_manager

# Utility functions
def get_logger(name: str) -> logging.Logger:
    """Get structured logger."""
    return get_logger_manager().get_logger(name)

def time_operation(operation_name: str, tags: Dict[str, str] = None):
    """Context manager for timing operations."""
    return get_performance_monitor().time_operation(operation_name, tags)

def time_function(name: str = None, tags: Dict[str, str] = None):
    """Decorator for timing functions."""
    return get_performance_monitor().time_function(name, tags)
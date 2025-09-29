"""
Advanced logging utilities for the risk platform.
Provides structured logging, correlation IDs, and log aggregation.
"""

import logging
import json
import uuid
import threading
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from contextlib import contextmanager
import os

# Thread-local storage for request context
_request_context = threading.local()

class RequestContext:
    """Request context management for correlation tracking."""
    
    def __init__(self, request_id: str = None, user_id: str = None, 
                 session_id: str = None):
        self.request_id = request_id or str(uuid.uuid4())
        self.user_id = user_id
        self.session_id = session_id
        self.start_time = datetime.utcnow()
        self.tags = {}
    
    def add_tag(self, key: str, value: str):
        """Add custom tag to context."""
        self.tags[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary."""
        return {
            'request_id': self.request_id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'start_time': self.start_time.isoformat(),
            'tags': self.tags
        }

def set_request_context(context: RequestContext):
    """Set request context for current thread."""
    _request_context.context = context

def get_request_context() -> Optional[RequestContext]:
    """Get request context for current thread."""
    return getattr(_request_context, 'context', None)

@contextmanager
def request_context(request_id: str = None, user_id: str = None, 
                   session_id: str = None):
    """Context manager for request tracking."""
    old_context = get_request_context()
    new_context = RequestContext(request_id, user_id, session_id)
    
    try:
        set_request_context(new_context)
        yield new_context
    finally:
        set_request_context(old_context)

class StructuredFormatter(logging.Formatter):
    """Structured JSON formatter with request context."""
    
    def __init__(self, service_name: str = 'risk-platform', 
                 include_context: bool = True):
        super().__init__()
        self.service_name = service_name
        self.include_context = include_context
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        # Base log data
        log_data = {
            'timestamp': datetime.utcfromtimestamp(record.created).isoformat() + 'Z',
            'level': record.levelname,
            'service': self.service_name,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add request context if available
        if self.include_context:
            context = get_request_context()
            if context:
                log_data.update({
                    'request_id': context.request_id,
                    'user_id': context.user_id,
                    'session_id': context.session_id
                })
                if context.tags:
                    log_data['tags'] = context.tags
        
        # Add exception information
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': self.formatException(record.exc_info)
            }
        
        # Add custom fields from extra
        extra_fields = {}
        for key, value in record.__dict__.items():
            if key not in {'name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'lineno', 'funcName', 'created',
                          'msecs', 'relativeCreated', 'thread', 'threadName',
                          'processName', 'process', 'exc_info', 'exc_text', 'stack_info'}:
                extra_fields[key] = value
        
        if extra_fields:
            log_data['extra'] = extra_fields
        
        return json.dumps(log_data, default=str)

class LogAggregator:
    """Aggregates logs for analysis and alerting."""
    
    def __init__(self, buffer_size: int = 1000):
        self.buffer_size = buffer_size
        self._buffer = []
        self._lock = threading.Lock()
        self._stats = {
            'total_logs': 0,
            'errors': 0,
            'warnings': 0,
            'by_logger': {},
            'by_user': {}
        }
    
    def add_log(self, record: logging.LogRecord):
        """Add log record to buffer."""
        with self._lock:
            # Update stats
            self._stats['total_logs'] += 1
            
            if record.levelno >= logging.ERROR:
                self._stats['errors'] += 1
            elif record.levelno >= logging.WARNING:
                self._stats['warnings'] += 1
            
            # Track by logger
            logger_name = record.name
            self._stats['by_logger'][logger_name] = \
                self._stats['by_logger'].get(logger_name, 0) + 1
            
            # Track by user if available
            context = get_request_context()
            if context and context.user_id:
                user_id = context.user_id
                self._stats['by_user'][user_id] = \
                    self._stats['by_user'].get(user_id, 0) + 1
            
            # Add to buffer
            log_entry = {
                'timestamp': record.created,
                'level': record.levelname,
                'logger': record.name,
                'message': record.getMessage(),
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno
            }
            
            if context:
                log_entry.update({
                    'request_id': context.request_id,
                    'user_id': context.user_id,
                    'session_id': context.session_id
                })
            
            self._buffer.append(log_entry)
            
            # Maintain buffer size
            if len(self._buffer) > self.buffer_size:
                self._buffer.pop(0)
    
    def get_recent_logs(self, count: int = 100, level: str = None) -> List[Dict[str, Any]]:
        """Get recent log entries."""
        with self._lock:
            logs = list(self._buffer)
        
        # Filter by level if specified
        if level:
            level_upper = level.upper()
            logs = [log for log in logs if log['level'] == level_upper]
        
        # Return most recent
        return logs[-count:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get logging statistics."""
        with self._lock:
            return dict(self._stats)
    
    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get error summary for specified time period."""
        cutoff_time = datetime.utcnow().timestamp() - (hours * 3600)
        
        with self._lock:
            recent_errors = [
                log for log in self._buffer
                if log['timestamp'] > cutoff_time and log['level'] == 'ERROR'
            ]
        
        # Group errors by module/function
        error_groups = {}
        for error in recent_errors:
            key = f"{error['module']}.{error['function']}"
            if key not in error_groups:
                error_groups[key] = []
            error_groups[key].append(error)
        
        # Sort by frequency
        summary = []
        for key, errors in error_groups.items():
            summary.append({
                'location': key,
                'count': len(errors),
                'latest_message': errors[-1]['message'],
                'latest_timestamp': errors[-1]['timestamp']
            })
        
        summary.sort(key=lambda x: x['count'], reverse=True)
        
        return {
            'total_errors': len(recent_errors),
            'unique_errors': len(error_groups),
            'top_errors': summary[:10],
            'time_period_hours': hours
        }

class AuditLogger:
    """Specialized logger for audit events."""
    
    def __init__(self, logger_name: str = 'audit'):
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.INFO)
    
    def log_user_action(self, action: str, user_id: str, resource: str = None, 
                       details: Dict[str, Any] = None, ip_address: str = None):
        """Log user action for audit purposes."""
        audit_data = {
            'action': action,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat(),
            'ip_address': ip_address,
            'resource': resource,
            'details': details or {}
        }
        
        context = get_request_context()
        if context:
            audit_data['request_id'] = context.request_id
            audit_data['session_id'] = context.session_id
        
        self.logger.info(f"User action: {action}", extra=audit_data)
    
    def log_auth_event(self, event_type: str, user_id: str = None, 
                      result: str = None, ip_address: str = None, 
                      details: Dict[str, Any] = None):
        """Log authentication/authorization events."""
        auth_data = {
            'event_type': event_type,  # login, logout, auth_failure, etc.
            'user_id': user_id,
            'result': result,  # success, failure, error
            'timestamp': datetime.utcnow().isoformat(),
            'ip_address': ip_address,
            'details': details or {}
        }
        
        context = get_request_context()
        if context:
            auth_data['request_id'] = context.request_id
        
        level = logging.WARNING if result == 'failure' else logging.INFO
        self.logger.log(level, f"Auth event: {event_type}", extra=auth_data)
    
    def log_system_event(self, event_type: str, component: str, 
                        status: str, details: Dict[str, Any] = None):
        """Log system events."""
        system_data = {
            'event_type': event_type,  # startup, shutdown, error, etc.
            'component': component,
            'status': status,  # success, failure, error
            'timestamp': datetime.utcnow().isoformat(),
            'details': details or {}
        }
        
        level = logging.ERROR if status == 'failure' else logging.INFO
        self.logger.log(level, f"System event: {event_type}", extra=system_data)

class SecurityLogger:
    """Specialized logger for security events."""
    
    def __init__(self, logger_name: str = 'security'):
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.WARNING)
    
    def log_suspicious_activity(self, activity_type: str, user_id: str = None,
                              ip_address: str = None, details: Dict[str, Any] = None):
        """Log suspicious security activity."""
        security_data = {
            'activity_type': activity_type,
            'user_id': user_id,
            'ip_address': ip_address,
            'timestamp': datetime.utcnow().isoformat(),
            'severity': 'high',
            'details': details or {}
        }
        
        self.logger.warning(f"Suspicious activity: {activity_type}", extra=security_data)
    
    def log_access_violation(self, resource: str, user_id: str, 
                           required_permission: str, ip_address: str = None):
        """Log unauthorized access attempts."""
        violation_data = {
            'violation_type': 'unauthorized_access',
            'resource': resource,
            'user_id': user_id,
            'required_permission': required_permission,
            'ip_address': ip_address,
            'timestamp': datetime.utcnow().isoformat(),
            'severity': 'medium'
        }
        
        self.logger.warning("Access violation", extra=violation_data)

# Handler that forwards logs to aggregator
class AggregatorHandler(logging.Handler):
    """Logging handler that forwards to log aggregator."""
    
    def __init__(self, aggregator: LogAggregator):
        super().__init__()
        self.aggregator = aggregator
    
    def emit(self, record):
        """Forward log record to aggregator."""
        try:
            self.aggregator.add_log(record)
        except Exception:
            pass  # Don't let logging errors break the application

# Global instances
_log_aggregator = None
_audit_logger = None
_security_logger = None

def get_log_aggregator() -> LogAggregator:
    """Get global log aggregator."""
    global _log_aggregator
    if _log_aggregator is None:
        _log_aggregator = LogAggregator()
    return _log_aggregator

def get_audit_logger() -> AuditLogger:
    """Get audit logger."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger

def get_security_logger() -> SecurityLogger:
    """Get security logger."""
    global _security_logger
    if _security_logger is None:
        _security_logger = SecurityLogger()
    return _security_logger

# Utility functions
def setup_structured_logging(service_name: str = 'risk-platform', 
                           log_level: str = None, 
                           enable_aggregation: bool = True):
    """Set up structured logging for the application."""
    log_level = log_level or os.getenv('LOG_LEVEL', 'INFO')
    
    # Create structured formatter
    formatter = StructuredFormatter(service_name)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add console handler with structured formatting
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Add aggregator handler if enabled
    if enable_aggregation:
        aggregator = get_log_aggregator()
        aggregator_handler = AggregatorHandler(aggregator)
        root_logger.addHandler(aggregator_handler)
    
    # Configure specific loggers to not propagate to avoid duplication
    for logger_name in ['audit', 'security']:
        logger = logging.getLogger(logger_name)
        logger.propagate = False
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            logger.addHandler(handler)

def log_user_action(action: str, user_id: str, **kwargs):
    """Convenience function for logging user actions."""
    get_audit_logger().log_user_action(action, user_id, **kwargs)

def log_auth_event(event_type: str, **kwargs):
    """Convenience function for logging auth events."""
    get_audit_logger().log_auth_event(event_type, **kwargs)

def log_security_event(activity_type: str, **kwargs):
    """Convenience function for logging security events."""
    get_security_logger().log_suspicious_activity(activity_type, **kwargs)
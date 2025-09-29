"""
Security Middleware for FastAPI
Authentication, authorization, rate limiting, and security headers
"""

import os
import json
import ipaddress
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Set
from fastapi import FastAPI, Request, Response, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import RequestResponseEndpoint
import logging

from .security_framework import (
    User, Role, Permission, 
    SecurityValidator, PasswordManager, JWTManager, 
    RateLimiter, SecurityEventLogger,
    get_security_validator, get_jwt_manager, get_rate_limiter, get_security_logger
)

logger = logging.getLogger(__name__)

# Security headers
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
}

# Rate limiting configuration
RATE_LIMITS = {
    'default': {'requests': 60, 'window_minutes': 1},
    'auth': {'requests': 5, 'window_minutes': 15},
    'data_export': {'requests': 10, 'window_minutes': 60},
    'risk_calculation': {'requests': 100, 'window_minutes': 1}
}

# IP whitelisting (for production environments)
WHITELISTED_IPS = set([
    '127.0.0.1',
    '::1',
    # Add your corporate IP ranges here
])

# Blocked IPs (can be populated from threat intelligence)
BLOCKED_IPS = set()


class SecurityHeaders(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        
        # Add security headers
        for header, value in SECURITY_HEADERS.items():
            response.headers[header] = value
        
        return response


class IPFilterMiddleware(BaseHTTPMiddleware):
    """Middleware for IP filtering and blocking."""
    
    def __init__(self, app, whitelist_enabled: bool = False):
        super().__init__(app)
        self.whitelist_enabled = whitelist_enabled
        self.security_logger = get_security_logger()
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        # Check for forwarded headers (when behind proxy)
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        # Fallback to client host
        return request.client.host if request.client else '127.0.0.1'
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        client_ip = self._get_client_ip(request)
        
        # Check blocked IPs
        if client_ip in BLOCKED_IPS:
            self.security_logger.log_security_event(
                'blocked_ip_access_attempt',
                ip_address=client_ip,
                details={'path': str(request.url.path), 'method': request.method}
            )
            return JSONResponse(
                status_code=403,
                content={"detail": "Access denied"}
            )
        
        # Check suspicious IPs
        if self.security_logger.is_suspicious_ip(client_ip):
            self.security_logger.log_security_event(
                'suspicious_ip_access_attempt',
                ip_address=client_ip,
                details={'path': str(request.url.path), 'method': request.method}
            )
            # Could implement CAPTCHA or additional verification here
        
        # Check whitelist (if enabled)
        if self.whitelist_enabled and client_ip not in WHITELISTED_IPS:
            try:
                # Check if IP is in whitelisted ranges
                ip_obj = ipaddress.ip_address(client_ip)
                is_whitelisted = False
                
                for whitelisted_ip in WHITELISTED_IPS:
                    try:
                        if '/' in whitelisted_ip:  # CIDR range
                            network = ipaddress.ip_network(whitelisted_ip, strict=False)
                            if ip_obj in network:
                                is_whitelisted = True
                                break
                        else:  # Individual IP
                            if str(ip_obj) == whitelisted_ip:
                                is_whitelisted = True
                                break
                    except ValueError:
                        continue
                
                if not is_whitelisted:
                    self.security_logger.log_security_event(
                        'non_whitelisted_ip_access_attempt',
                        ip_address=client_ip,
                        details={'path': str(request.url.path), 'method': request.method}
                    )
                    return JSONResponse(
                        status_code=403,
                        content={"detail": "Access denied - IP not whitelisted"}
                    )
            
            except ValueError:
                # Invalid IP format
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Invalid IP address"}
                )
        
        response = await call_next(request)
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting."""
    
    def __init__(self, app):
        super().__init__(app)
        self.rate_limiter = get_rate_limiter()
        self.security_logger = get_security_logger()
    
    def _get_rate_limit_key(self, request: Request) -> tuple[str, Dict[str, Any]]:
        """Get rate limiting key and configuration."""
        path = request.url.path
        client_ip = request.client.host if request.client else '127.0.0.1'
        
        # Determine rate limit type based on path
        if '/auth/' in path:
            limit_type = 'auth'
        elif '/export/' in path or '/download/' in path:
            limit_type = 'data_export'
        elif '/risk/' in path or '/calculate/' in path:
            limit_type = 'risk_calculation'
        else:
            limit_type = 'default'
        
        config = RATE_LIMITS.get(limit_type, RATE_LIMITS['default'])
        key = f"{limit_type}:{client_ip}"
        
        return key, config
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        key, config = self._get_rate_limit_key(request)
        
        # Check rate limit
        is_limited = self.rate_limiter.is_rate_limited(
            key, 
            config['requests'], 
            config['window_minutes']
        )
        
        if is_limited:
            self.security_logger.log_security_event(
                'rate_limit_exceeded',
                ip_address=request.client.host if request.client else '127.0.0.1',
                details={
                    'path': str(request.url.path),
                    'method': request.method,
                    'rate_limit_type': key.split(':')[0]
                }
            )
            
            # Get rate limit status for headers
            status = self.rate_limiter.get_rate_limit_status(
                key, 
                config['requests'], 
                config['window_minutes']
            )
            
            response = JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded",
                    "retry_after": status['reset_time']
                }
            )
            
            # Add rate limit headers
            response.headers["X-RateLimit-Limit"] = str(config['requests'])
            response.headers["X-RateLimit-Remaining"] = "0"
            response.headers["X-RateLimit-Reset"] = status['reset_time']
            
            return response
        
        response = await call_next(request)
        
        # Add rate limit headers to successful responses
        status = self.rate_limiter.get_rate_limit_status(
            key, 
            config['requests'], 
            config['window_minutes']
        )
        
        response.headers["X-RateLimit-Limit"] = str(config['requests'])
        response.headers["X-RateLimit-Remaining"] = str(status['remaining'])
        response.headers["X-RateLimit-Reset"] = status['reset_time']
        
        return response


class InputValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for input validation and sanitization."""
    
    def __init__(self, app):
        super().__init__(app)
        self.validator = get_security_validator()
        self.security_logger = get_security_logger()
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Skip validation for certain paths
        if request.url.path in ['/health', '/metrics', '/docs', '/openapi.json']:
            return await call_next(request)
        
        # Validate content type for POST/PUT requests
        if request.method in ['POST', 'PUT', 'PATCH']:
            content_type = request.headers.get('content-type', '')
            
            if not content_type.startswith(('application/json', 'application/x-www-form-urlencoded')):
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Unsupported content type"}
                )
        
        # Check request size
        content_length = request.headers.get('content-length')
        if content_length:
            try:
                size = int(content_length)
                max_size = 10 * 1024 * 1024  # 10MB limit
                
                if size > max_size:
                    self.security_logger.log_security_event(
                        'oversized_request',
                        ip_address=request.client.host if request.client else '127.0.0.1',
                        details={
                            'path': str(request.url.path),
                            'size': size,
                            'limit': max_size
                        }
                    )
                    return JSONResponse(
                        status_code=413,
                        content={"detail": "Request entity too large"}
                    )
            except ValueError:
                pass
        
        # Validate query parameters for SQL injection patterns
        for param_name, param_value in request.query_params.items():
            if isinstance(param_value, str):
                sanitized = self.validator.sanitize_sql_input(param_value)
                if sanitized != param_value:
                    self.security_logger.log_security_event(
                        'sql_injection_attempt',
                        ip_address=request.client.host if request.client else '127.0.0.1',
                        details={
                            'path': str(request.url.path),
                            'parameter': param_name,
                            'original_value': param_value[:100]  # Truncate for logging
                        }
                    )
                    return JSONResponse(
                        status_code=400,
                        content={"detail": "Invalid input detected"}
                    )
        
        return await call_next(request)


# Authentication dependencies
security = HTTPBearer(auto_error=False)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Dependency to get current authenticated user."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        jwt_manager = get_jwt_manager()
        payload = jwt_manager.decode_token(credentials.credentials)
        
        # In a real implementation, you would fetch the user from database
        # For now, create user from JWT payload
        user = User(
            user_id=payload.get('user_id', ''),
            username=payload.get('sub', ''),
            email='',  # Would be fetched from DB
            password_hash='',  # Not needed for authenticated user
            role=Role(payload.get('role', 'viewer')),
            permissions={Permission(p) for p in payload.get('permissions', [])}
        )
        
        return user
        
    except Exception as e:
        logger.error(f"Token validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_permission(permission: Permission):
    """Dependency factory to require specific permission."""
    async def permission_dependency(user: User = Depends(get_current_user)):
        if not user.has_permission(permission):
            security_logger = get_security_logger()
            security_logger.log_security_event(
                'unauthorized_access_attempt',
                user_id=user.user_id,
                details={
                    'required_permission': permission.value,
                    'user_permissions': [p.value for p in user.permissions]
                }
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission required: {permission.value}"
            )
        return user
    
    return permission_dependency


def require_role(role: Role):
    """Dependency factory to require specific role."""
    async def role_dependency(user: User = Depends(get_current_user)):
        if user.role != role:
            security_logger = get_security_logger()
            security_logger.log_security_event(
                'unauthorized_access_attempt',
                user_id=user.user_id,
                details={
                    'required_role': role.value,
                    'user_role': user.role.value
                }
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role required: {role.value}"
            )
        return user
    
    return role_dependency


class SecurityManager:
    """Main security manager for FastAPI application."""
    
    def __init__(self, app: FastAPI, config: Dict[str, Any] = None):
        self.app = app
        self.config = config or {}
        self.jwt_manager = get_jwt_manager()
        self.security_logger = get_security_logger()
        
        # Configure security middleware
        self.setup_middleware()
        self.setup_error_handlers()
    
    def setup_middleware(self):
        """Setup security middleware in correct order."""
        # Order matters: most restrictive first
        
        # 1. IP filtering (block malicious IPs early)
        whitelist_enabled = self.config.get('whitelist_enabled', False)
        self.app.add_middleware(IPFilterMiddleware, whitelist_enabled=whitelist_enabled)
        
        # 2. Rate limiting (prevent DoS attacks)
        self.app.add_middleware(RateLimitMiddleware)
        
        # 3. Input validation (sanitize inputs)
        self.app.add_middleware(InputValidationMiddleware)
        
        # 4. Security headers (add protective headers)
        self.app.add_middleware(SecurityHeaders)
    
    def setup_error_handlers(self):
        """Setup custom error handlers for security events."""
        
        @self.app.exception_handler(HTTPException)
        async def security_exception_handler(request: Request, exc: HTTPException):
            """Handle security-related HTTP exceptions."""
            
            # Log security events for specific status codes
            if exc.status_code in [401, 403, 429]:
                self.security_logger.log_security_event(
                    f'http_{exc.status_code}',
                    ip_address=request.client.host if request.client else '127.0.0.1',
                    details={
                        'path': str(request.url.path),
                        'method': request.method,
                        'detail': exc.detail
                    }
                )
            
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail}
            )
    
    def create_user_token(self, user: User) -> Dict[str, str]:
        """Create access and refresh tokens for user."""
        access_token = self.jwt_manager.generate_token(user, 'access')
        refresh_token = self.jwt_manager.generate_token(user, 'refresh')
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'bearer'
        }
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get current security status."""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'middleware_enabled': True,
            'whitelist_enabled': self.config.get('whitelist_enabled', False),
            'rate_limits': RATE_LIMITS,
            'security_summary': self.security_logger.get_security_summary()
        }


# Utility functions for security configuration
def configure_security(app: FastAPI, config: Dict[str, Any] = None) -> SecurityManager:
    """Configure security for FastAPI application."""
    return SecurityManager(app, config)


def add_blocked_ip(ip: str):
    """Add IP to blocked list."""
    BLOCKED_IPS.add(ip)


def remove_blocked_ip(ip: str):
    """Remove IP from blocked list."""
    BLOCKED_IPS.discard(ip)


def add_whitelisted_ip(ip: str):
    """Add IP to whitelist."""
    WHITELISTED_IPS.add(ip)


def get_blocked_ips() -> Set[str]:
    """Get list of blocked IPs."""
    return BLOCKED_IPS.copy()


def get_whitelisted_ips() -> Set[str]:
    """Get list of whitelisted IPs."""
    return WHITELISTED_IPS.copy()
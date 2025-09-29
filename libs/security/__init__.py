"""
Security Module Initialization
Provides easy access to all security components
"""

from .security_framework import (
    # Core classes
    User, Role, Permission, 
    SecurityValidator, PasswordManager, JWTManager, 
    RateLimiter, SecurityEventLogger, SecurityScanner,
    
    # Role-Permission mapping
    ROLE_PERMISSIONS,
    
    # Security decorators
    require_permission, rate_limit,
    
    # Global instances
    get_security_validator, get_password_manager, get_jwt_manager,
    get_rate_limiter, get_security_logger,
    
    # Utility functions
    run_security_scan
)

from .middleware import (
    # Middleware classes
    SecurityHeaders, IPFilterMiddleware, RateLimitMiddleware, 
    InputValidationMiddleware, SecurityManager,
    
    # Authentication dependencies
    get_current_user, require_permission as require_permission_dependency, 
    require_role,
    
    # Utility functions
    configure_security, add_blocked_ip, remove_blocked_ip, 
    add_whitelisted_ip, get_blocked_ips, get_whitelisted_ips
)

from .authentication import (
    # Authentication classes
    LoginAttempt, PasswordResetRequest, EmailVerification,
    MFAManager, EmailService, AuthenticationService,
    
    # Global service
    get_auth_service
)

__all__ = [
    # Core framework
    'User', 'Role', 'Permission', 
    'SecurityValidator', 'PasswordManager', 'JWTManager',
    'RateLimiter', 'SecurityEventLogger', 'SecurityScanner',
    'ROLE_PERMISSIONS',
    'require_permission', 'rate_limit',
    'get_security_validator', 'get_password_manager', 'get_jwt_manager',
    'get_rate_limiter', 'get_security_logger',
    'run_security_scan',
    
    # Middleware
    'SecurityHeaders', 'IPFilterMiddleware', 'RateLimitMiddleware',
    'InputValidationMiddleware', 'SecurityManager',
    'get_current_user', 'require_permission_dependency', 'require_role',
    'configure_security', 'add_blocked_ip', 'remove_blocked_ip',
    'add_whitelisted_ip', 'get_blocked_ips', 'get_whitelisted_ips',
    
    # Authentication
    'LoginAttempt', 'PasswordResetRequest', 'EmailVerification',
    'MFAManager', 'EmailService', 'AuthenticationService',
    'get_auth_service'
]
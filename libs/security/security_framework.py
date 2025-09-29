"""
Security Hardening Framework
Comprehensive security implementation including RBAC, input validation, and scanning
"""

import os
import sys
import hashlib
import secrets
import jwt
import bcrypt
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import re
import logging
from functools import wraps
import ipaddress
import json

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from config import get_config
    from libs.monitoring import log_user_action, get_metrics_collector
    from libs.storage import CacheManager
except ImportError:
    get_config = lambda: {}
    log_user_action = lambda *args, **kwargs: None
    get_metrics_collector = lambda: None
    CacheManager = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security constants
PASSWORD_MIN_LENGTH = 12
PASSWORD_COMPLEXITY_REQUIREMENTS = {
    'min_uppercase': 1,
    'min_lowercase': 1,
    'min_digits': 1,
    'min_special_chars': 1
}

JWT_ALGORITHM = 'HS256'
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60
JWT_REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Rate limiting
RATE_LIMIT_REQUESTS_PER_MINUTE = 60
RATE_LIMIT_LOGIN_ATTEMPTS = 5

# IP Whitelisting/Blacklisting
SUSPICIOUS_IP_THRESHOLD = 10  # Failed attempts before IP is flagged


class Permission(Enum):
    """System permissions."""
    # Portfolio permissions
    PORTFOLIO_READ = "portfolio:read"
    PORTFOLIO_WRITE = "portfolio:write"
    PORTFOLIO_DELETE = "portfolio:delete"
    
    # Risk permissions
    RISK_READ = "risk:read"
    RISK_CALCULATE = "risk:calculate"
    RISK_STRESS_TEST = "risk:stress_test"
    
    # Market data permissions
    MARKET_DATA_READ = "market_data:read"
    MARKET_DATA_PROCESS = "market_data:process"
    
    # Analytics permissions
    ANALYTICS_READ = "analytics:read"
    ANALYTICS_QUERY = "analytics:query"
    ANALYTICS_EXPORT = "analytics:export"
    
    # Admin permissions
    ADMIN_READ = "admin:read"
    ADMIN_WRITE = "admin:write"
    ADMIN_USERS = "admin:users"
    ADMIN_SYSTEM = "admin:system"
    
    # Audit permissions
    AUDIT_READ = "audit:read"
    AUDIT_EXPORT = "audit:export"


class Role(Enum):
    """User roles with associated permissions."""
    VIEWER = "viewer"
    ANALYST = "analyst"
    PORTFOLIO_MANAGER = "portfolio_manager"
    RISK_MANAGER = "risk_manager"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


# Role-Permission mapping
ROLE_PERMISSIONS = {
    Role.VIEWER: [
        Permission.PORTFOLIO_READ,
        Permission.RISK_READ,
        Permission.MARKET_DATA_READ,
        Permission.ANALYTICS_READ
    ],
    Role.ANALYST: [
        Permission.PORTFOLIO_READ,
        Permission.RISK_READ,
        Permission.RISK_CALCULATE,
        Permission.MARKET_DATA_READ,
        Permission.ANALYTICS_READ,
        Permission.ANALYTICS_QUERY
    ],
    Role.PORTFOLIO_MANAGER: [
        Permission.PORTFOLIO_READ,
        Permission.PORTFOLIO_WRITE,
        Permission.RISK_READ,
        Permission.RISK_CALCULATE,
        Permission.MARKET_DATA_READ,
        Permission.ANALYTICS_READ,
        Permission.ANALYTICS_QUERY
    ],
    Role.RISK_MANAGER: [
        Permission.PORTFOLIO_READ,
        Permission.RISK_READ,
        Permission.RISK_CALCULATE,
        Permission.RISK_STRESS_TEST,
        Permission.MARKET_DATA_READ,
        Permission.MARKET_DATA_PROCESS,
        Permission.ANALYTICS_READ,
        Permission.ANALYTICS_QUERY,
        Permission.ANALYTICS_EXPORT
    ],
    Role.ADMIN: [
        Permission.PORTFOLIO_READ,
        Permission.PORTFOLIO_WRITE,
        Permission.PORTFOLIO_DELETE,
        Permission.RISK_READ,
        Permission.RISK_CALCULATE,
        Permission.RISK_STRESS_TEST,
        Permission.MARKET_DATA_READ,
        Permission.MARKET_DATA_PROCESS,
        Permission.ANALYTICS_READ,
        Permission.ANALYTICS_QUERY,
        Permission.ANALYTICS_EXPORT,
        Permission.ADMIN_READ,
        Permission.ADMIN_WRITE,
        Permission.ADMIN_USERS,
        Permission.AUDIT_READ
    ],
    Role.SUPER_ADMIN: list(Permission)  # All permissions
}


@dataclass
class User:
    """User data model."""
    user_id: str
    username: str
    email: str
    password_hash: str
    role: Role
    first_name: str = ""
    last_name: str = ""
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    account_locked_until: Optional[datetime] = None
    permissions: Set[Permission] = field(default_factory=set)
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None
    
    def __post_init__(self):
        """Initialize permissions based on role."""
        if not self.permissions:
            self.permissions = set(ROLE_PERMISSIONS.get(self.role, []))
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if user has specific permission."""
        return permission in self.permissions
    
    def is_account_locked(self) -> bool:
        """Check if account is currently locked."""
        if self.account_locked_until is None:
            return False
        return datetime.utcnow() < self.account_locked_until
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary (excluding sensitive data)."""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'role': self.role.value,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'mfa_enabled': self.mfa_enabled,
            'permissions': [p.value for p in self.permissions]
        }


class SecurityValidator:
    """Input validation and security checks."""
    
    @staticmethod
    def validate_password(password: str) -> Dict[str, Any]:
        """Validate password strength."""
        errors = []
        
        if len(password) < PASSWORD_MIN_LENGTH:
            errors.append(f"Password must be at least {PASSWORD_MIN_LENGTH} characters long")
        
        if sum(1 for c in password if c.isupper()) < PASSWORD_COMPLEXITY_REQUIREMENTS['min_uppercase']:
            errors.append("Password must contain at least 1 uppercase letter")
        
        if sum(1 for c in password if c.islower()) < PASSWORD_COMPLEXITY_REQUIREMENTS['min_lowercase']:
            errors.append("Password must contain at least 1 lowercase letter")
        
        if sum(1 for c in password if c.isdigit()) < PASSWORD_COMPLEXITY_REQUIREMENTS['min_digits']:
            errors.append("Password must contain at least 1 digit")
        
        special_chars = set('!@#$%^&*()_+-=[]{}|;:,.<>?')
        if sum(1 for c in password if c in special_chars) < PASSWORD_COMPLEXITY_REQUIREMENTS['min_special_chars']:
            errors.append("Password must contain at least 1 special character")
        
        # Check for common weak passwords
        common_passwords = ['password', '123456', 'qwerty', 'admin', 'letmein', 'welcome']
        if password.lower() in common_passwords:
            errors.append("Password is too common")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'strength_score': max(0, 100 - len(errors) * 20)
        }
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_username(username: str) -> Dict[str, Any]:
        """Validate username."""
        errors = []
        
        if len(username) < 3:
            errors.append("Username must be at least 3 characters long")
        
        if len(username) > 30:
            errors.append("Username must be no more than 30 characters long")
        
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            errors.append("Username can only contain letters, numbers, underscores, and hyphens")
        
        if username.lower() in ['admin', 'root', 'system', 'test', 'guest']:
            errors.append("Username is reserved")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    @staticmethod
    def sanitize_sql_input(input_str: str) -> str:
        """Sanitize input to prevent SQL injection."""
        if not isinstance(input_str, str):
            return str(input_str)
        
        # Remove or escape dangerous SQL keywords and characters
        dangerous_patterns = [
            r'(\'|\"|;|--|\*|/\*|\*/)',
            r'\b(DROP|DELETE|INSERT|UPDATE|ALTER|CREATE|EXEC|EXECUTE)\b',
            r'\b(UNION|SELECT|FROM|WHERE|ORDER|GROUP|HAVING)\b'
        ]
        
        sanitized = input_str
        for pattern in dangerous_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        return sanitized.strip()
    
    @staticmethod
    def validate_ip_address(ip_str: str) -> bool:
        """Validate IP address format."""
        try:
            ipaddress.ip_address(ip_str)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_portfolio_id(portfolio_id: str) -> bool:
        """Validate portfolio ID format."""
        if not isinstance(portfolio_id, str):
            return False
        
        # Allow alphanumeric, underscore, hyphen
        pattern = r'^[A-Z0-9_-]{3,20}$'
        return re.match(pattern, portfolio_id) is not None
    
    @staticmethod
    def validate_date_range(start_date: str, end_date: str = None) -> Dict[str, Any]:
        """Validate date range."""
        errors = []
        
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        except ValueError:
            errors.append("Invalid start_date format. Use YYYY-MM-DD")
            return {'valid': False, 'errors': errors}
        
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                if end_dt < start_dt:
                    errors.append("end_date must be after start_date")
            except ValueError:
                errors.append("Invalid end_date format. Use YYYY-MM-DD")
        
        # Check reasonable date range
        max_date = datetime.now() + timedelta(days=1)
        min_date = datetime(2000, 1, 1)
        
        if start_dt > max_date:
            errors.append("start_date cannot be in the future")
        
        if start_dt < min_date:
            errors.append("start_date cannot be before 2000-01-01")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }


class PasswordManager:
    """Secure password handling."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt."""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    @staticmethod
    def generate_secure_password(length: int = 16) -> str:
        """Generate cryptographically secure password."""
        alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*'
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        
        # Ensure password meets complexity requirements
        validation = SecurityValidator.validate_password(password)
        if validation['valid']:
            return password
        else:
            # Recursively generate until valid
            return PasswordManager.generate_secure_password(length)


class JWTManager:
    """JWT token management."""
    
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or os.getenv('JWT_SECRET_KEY') or secrets.token_urlsafe(32)
        self.algorithm = JWT_ALGORITHM
    
    def generate_token(self, user: User, token_type: str = 'access') -> str:
        """Generate JWT token."""
        now = datetime.utcnow()
        
        if token_type == 'access':
            expire_minutes = JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        elif token_type == 'refresh':
            expire_minutes = JWT_REFRESH_TOKEN_EXPIRE_MINUTES
        else:
            expire_minutes = JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        
        payload = {
            'sub': user.username,
            'user_id': user.user_id,
            'role': user.role.value,
            'permissions': [p.value for p in user.permissions],
            'iat': now,
            'exp': now + timedelta(minutes=expire_minutes),
            'type': token_type
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """Decode and validate JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
    
    def refresh_token(self, refresh_token: str) -> str:
        """Generate new access token from refresh token."""
        payload = self.decode_token(refresh_token)
        
        if payload.get('type') != 'refresh':
            raise ValueError("Invalid refresh token")
        
        # Create new access token (simplified - would need user lookup in real implementation)
        new_payload = payload.copy()
        new_payload['type'] = 'access'
        new_payload['iat'] = datetime.utcnow()
        new_payload['exp'] = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        
        return jwt.encode(new_payload, self.secret_key, algorithm=self.algorithm)


class RateLimiter:
    """Rate limiting for API endpoints."""
    
    def __init__(self, cache_manager: Optional[CacheManager] = None):
        self.cache_manager = cache_manager or CacheManager() if CacheManager else None
        self.in_memory_store = {}  # Fallback if no cache manager
    
    def is_rate_limited(self, key: str, limit: int, window_minutes: int = 1) -> bool:
        """Check if request should be rate limited."""
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=window_minutes)
        
        if self.cache_manager:
            # Use Redis-based rate limiting
            cache_key = f"rate_limit:{key}"
            requests = self.cache_manager.get(cache_key) or []
            
            # Filter requests within window
            recent_requests = [
                req_time for req_time in requests 
                if datetime.fromisoformat(req_time) > window_start
            ]
            
            if len(recent_requests) >= limit:
                return True
            
            # Add current request
            recent_requests.append(now.isoformat())
            self.cache_manager.set(cache_key, recent_requests, ttl=window_minutes * 60)
            
        else:
            # Use in-memory store
            if key not in self.in_memory_store:
                self.in_memory_store[key] = []
            
            # Filter requests within window
            self.in_memory_store[key] = [
                req_time for req_time in self.in_memory_store[key]
                if req_time > window_start
            ]
            
            if len(self.in_memory_store[key]) >= limit:
                return True
            
            self.in_memory_store[key].append(now)
        
        return False
    
    def get_rate_limit_status(self, key: str, limit: int, window_minutes: int = 1) -> Dict[str, Any]:
        """Get rate limit status for a key."""
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=window_minutes)
        
        if self.cache_manager:
            cache_key = f"rate_limit:{key}"
            requests = self.cache_manager.get(cache_key) or []
            recent_requests = [
                req_time for req_time in requests 
                if datetime.fromisoformat(req_time) > window_start
            ]
        else:
            recent_requests = self.in_memory_store.get(key, [])
            recent_requests = [req for req in recent_requests if req > window_start]
        
        remaining = max(0, limit - len(recent_requests))
        reset_time = (now + timedelta(minutes=window_minutes)).isoformat()
        
        return {
            'limit': limit,
            'remaining': remaining,
            'reset_time': reset_time,
            'is_limited': remaining == 0
        }


class SecurityEventLogger:
    """Security event logging and monitoring."""
    
    def __init__(self, metrics_collector=None):
        self.metrics_collector = metrics_collector or get_metrics_collector()
        self.suspicious_ips = set()
        self.failed_attempts = {}
    
    def log_security_event(self, event_type: str, user_id: str = None, 
                          ip_address: str = None, details: Dict[str, Any] = None):
        """Log security events."""
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'user_id': user_id,
            'ip_address': ip_address,
            'details': details or {}
        }
        
        logger.warning(f"Security Event: {event_type} - {json.dumps(event)}")
        
        # Track failed login attempts by IP
        if event_type == 'failed_login' and ip_address:
            if ip_address not in self.failed_attempts:
                self.failed_attempts[ip_address] = 0
            
            self.failed_attempts[ip_address] += 1
            
            if self.failed_attempts[ip_address] >= SUSPICIOUS_IP_THRESHOLD:
                self.suspicious_ips.add(ip_address)
                self.log_security_event('suspicious_ip_detected', 
                                      ip_address=ip_address,
                                      details={'failed_attempts': self.failed_attempts[ip_address]})
        
        # Record metrics
        if self.metrics_collector:
            self.metrics_collector.record_error('security_event', 'security')
            if hasattr(self.metrics_collector, 'record_security_event'):
                self.metrics_collector.record_security_event(event_type, user_id or 'unknown')
    
    def is_suspicious_ip(self, ip_address: str) -> bool:
        """Check if IP is flagged as suspicious."""
        return ip_address in self.suspicious_ips
    
    def get_security_summary(self) -> Dict[str, Any]:
        """Get security event summary."""
        return {
            'suspicious_ips': list(self.suspicious_ips),
            'failed_attempts_by_ip': dict(self.failed_attempts),
            'total_suspicious_ips': len(self.suspicious_ips),
            'total_failed_attempts': sum(self.failed_attempts.values())
        }


class SecurityScanner:
    """Security vulnerability scanning."""
    
    @staticmethod
    def scan_dependencies() -> Dict[str, Any]:
        """Scan Python dependencies for known vulnerabilities."""
        try:
            import subprocess
            import json
            
            # Run safety check for Python dependencies
            result = subprocess.run([
                'safety', 'check', '--json'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                vulnerabilities = json.loads(result.stdout) if result.stdout else []
            else:
                vulnerabilities = []
            
            return {
                'scan_type': 'dependencies',
                'vulnerabilities_found': len(vulnerabilities),
                'vulnerabilities': vulnerabilities,
                'scan_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Dependency scan failed: {e}")
            return {
                'scan_type': 'dependencies',
                'error': str(e),
                'scan_timestamp': datetime.utcnow().isoformat()
            }
    
    @staticmethod
    def scan_secrets(directory: Path = None) -> Dict[str, Any]:
        """Scan for hardcoded secrets and credentials."""
        directory = directory or PROJECT_ROOT
        
        secret_patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', 'Hardcoded password'),
            (r'api_key\s*=\s*["\'][^"\']+["\']', 'Hardcoded API key'),
            (r'secret_key\s*=\s*["\'][^"\']+["\']', 'Hardcoded secret key'),
            (r'token\s*=\s*["\'][^"\']+["\']', 'Hardcoded token'),
            (r'aws_access_key_id\s*=\s*["\'][^"\']+["\']', 'AWS access key'),
            (r'aws_secret_access_key\s*=\s*["\'][^"\']+["\']', 'AWS secret key'),
        ]
        
        findings = []
        
        for file_path in directory.rglob('*.py'):
            try:
                content = file_path.read_text(encoding='utf-8')
                
                for pattern, description in secret_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        findings.append({
                            'file': str(file_path.relative_to(PROJECT_ROOT)),
                            'line': line_num,
                            'type': description,
                            'severity': 'HIGH'
                        })
                        
            except Exception as e:
                logger.warning(f"Could not scan file {file_path}: {e}")
        
        return {
            'scan_type': 'secrets',
            'findings': findings,
            'files_scanned': len(list(directory.rglob('*.py'))),
            'issues_found': len(findings),
            'scan_timestamp': datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def scan_permissions(file_path: Path) -> Dict[str, Any]:
        """Scan file permissions for security issues."""
        try:
            import stat
            
            file_stat = file_path.stat()
            mode = file_stat.st_mode
            
            issues = []
            
            # Check if file is world-writable
            if mode & stat.S_IWOTH:
                issues.append({
                    'type': 'World-writable file',
                    'severity': 'HIGH',
                    'description': f'{file_path} is writable by others'
                })
            
            # Check if file is world-readable (for sensitive files)
            if mode & stat.S_IROTH and file_path.suffix in ['.key', '.pem', '.env']:
                issues.append({
                    'type': 'World-readable sensitive file',
                    'severity': 'MEDIUM',
                    'description': f'{file_path} is readable by others'
                })
            
            return {
                'file': str(file_path),
                'permissions': oct(mode)[-3:],
                'issues': issues
            }
            
        except Exception as e:
            return {
                'file': str(file_path),
                'error': str(e)
            }


# Security decorators
def require_permission(permission: Permission):
    """Decorator to require specific permission."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # This would integrate with FastAPI dependency injection
            # For now, it's a placeholder
            return func(*args, **kwargs)
        return wrapper
    return decorator


def rate_limit(requests_per_minute: int = RATE_LIMIT_REQUESTS_PER_MINUTE):
    """Decorator for rate limiting."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # This would integrate with FastAPI middleware
            # For now, it's a placeholder
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Global instances
_security_validator = SecurityValidator()
_password_manager = PasswordManager()
_jwt_manager = JWTManager()
_rate_limiter = RateLimiter()
_security_logger = SecurityEventLogger()


def get_security_validator() -> SecurityValidator:
    """Get security validator instance."""
    return _security_validator


def get_password_manager() -> PasswordManager:
    """Get password manager instance."""
    return _password_manager


def get_jwt_manager() -> JWTManager:
    """Get JWT manager instance."""
    return _jwt_manager


def get_rate_limiter() -> RateLimiter:
    """Get rate limiter instance."""
    return _rate_limiter


def get_security_logger() -> SecurityEventLogger:
    """Get security event logger instance."""
    return _security_logger


def run_security_scan() -> Dict[str, Any]:
    """Run comprehensive security scan."""
    scanner = SecurityScanner()
    
    results = {
        'scan_timestamp': datetime.utcnow().isoformat(),
        'dependency_scan': scanner.scan_dependencies(),
        'secrets_scan': scanner.scan_secrets(),
        'security_summary': _security_logger.get_security_summary()
    }
    
    return results
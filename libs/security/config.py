"""
Security Configuration Management
Environment-specific security settings and policies
"""

import os
from typing import Dict, Any, List, Optional
from pathlib import Path

# Security configuration by environment
SECURITY_CONFIGS = {
    'development': {
        # Authentication settings
        'jwt_secret_key': 'dev-secret-key-change-in-production',
        'access_token_expire_minutes': 60,
        'refresh_token_expire_minutes': 60 * 24 * 7,
        
        # Password policies
        'password_min_length': 8,  # Relaxed for dev
        'password_require_uppercase': True,
        'password_require_lowercase': True,
        'password_require_numbers': True,
        'password_require_symbols': False,  # Relaxed for dev
        
        # Rate limiting
        'rate_limit_enabled': True,
        'rate_limit_requests_per_minute': 100,  # Higher for dev
        'rate_limit_login_attempts': 10,  # Relaxed for dev
        
        # IP filtering
        'ip_whitelist_enabled': False,
        'ip_blacklist_enabled': True,
        
        # MFA settings
        'mfa_required_for_admin': False,  # Optional in dev
        'mfa_app_name': 'Risk Management System (Dev)',
        
        # Session settings
        'session_timeout_minutes': 480,  # 8 hours
        'concurrent_sessions_allowed': 5,
        
        # Security headers
        'security_headers_enabled': True,
        'hsts_max_age': 3600,  # 1 hour for dev
        
        # Logging
        'security_event_logging': True,
        'log_failed_attempts': True,
        'log_suspicious_activity': True,
        
        # Email security
        'email_enabled': False,  # Disabled in dev
        'email_verification_required': False,
        
        # Database security
        'encrypt_sensitive_data': False,  # Disabled in dev
        'audit_data_access': True,
        
        # API security
        'api_versioning_required': False,
        'request_size_limit_mb': 10,
        'cors_origins': ['http://localhost:3000', 'http://localhost:8080'],
        
        # Monitoring
        'security_monitoring_enabled': True,
        'alert_thresholds': {
            'failed_logins_per_hour': 50,
            'suspicious_ips_per_hour': 10,
            'rate_limit_violations_per_hour': 100
        }
    },
    
    'uat': {
        # Authentication settings
        'jwt_secret_key': os.getenv('JWT_SECRET_KEY_UAT', 'uat-secret-key'),
        'access_token_expire_minutes': 60,
        'refresh_token_expire_minutes': 60 * 24 * 3,  # Shorter for UAT
        
        # Password policies (stricter)
        'password_min_length': 12,
        'password_require_uppercase': True,
        'password_require_lowercase': True,
        'password_require_numbers': True,
        'password_require_symbols': True,
        
        # Rate limiting (stricter)
        'rate_limit_enabled': True,
        'rate_limit_requests_per_minute': 60,
        'rate_limit_login_attempts': 5,
        
        # IP filtering
        'ip_whitelist_enabled': True,  # Enabled for UAT
        'ip_blacklist_enabled': True,
        'allowed_ip_ranges': [
            '10.0.0.0/8',      # Internal network
            '172.16.0.0/12',   # Private network
            '192.168.0.0/16'   # Local network
        ],
        
        # MFA settings (required for testing)
        'mfa_required_for_admin': True,
        'mfa_app_name': 'Risk Management System (UAT)',
        
        # Session settings (stricter)
        'session_timeout_minutes': 240,  # 4 hours
        'concurrent_sessions_allowed': 3,
        
        # Security headers
        'security_headers_enabled': True,
        'hsts_max_age': 86400,  # 24 hours
        
        # Logging (comprehensive)
        'security_event_logging': True,
        'log_failed_attempts': True,
        'log_suspicious_activity': True,
        'log_admin_actions': True,
        
        # Email security
        'email_enabled': True,
        'email_verification_required': True,
        
        # Database security
        'encrypt_sensitive_data': True,
        'audit_data_access': True,
        
        # API security
        'api_versioning_required': True,
        'request_size_limit_mb': 5,  # Stricter limit
        'cors_origins': [os.getenv('UAT_FRONTEND_URL', 'https://uat-risk.company.com')],
        
        # Monitoring (stricter thresholds)
        'security_monitoring_enabled': True,
        'alert_thresholds': {
            'failed_logins_per_hour': 20,
            'suspicious_ips_per_hour': 5,
            'rate_limit_violations_per_hour': 50
        }
    },
    
    'production': {
        # Authentication settings (production-grade)
        'jwt_secret_key': os.getenv('JWT_SECRET_KEY_PROD', ''),  # Must be set via environment
        'access_token_expire_minutes': 30,  # Shorter for production
        'refresh_token_expire_minutes': 60 * 24 * 1,  # 1 day max
        
        # Password policies (strictest)
        'password_min_length': 16,
        'password_require_uppercase': True,
        'password_require_lowercase': True,
        'password_require_numbers': True,
        'password_require_symbols': True,
        'password_history_count': 12,  # Remember last 12 passwords
        'password_max_age_days': 90,   # Force change every 90 days
        
        # Rate limiting (strictest)
        'rate_limit_enabled': True,
        'rate_limit_requests_per_minute': 30,
        'rate_limit_login_attempts': 3,  # Very strict
        
        # IP filtering (mandatory)
        'ip_whitelist_enabled': True,
        'ip_blacklist_enabled': True,
        'allowed_ip_ranges': [
            # Only corporate networks (to be configured)
            os.getenv('CORPORATE_IP_RANGE_1', '10.0.0.0/8'),
            os.getenv('CORPORATE_IP_RANGE_2', '172.16.0.0/12')
        ],
        
        # MFA settings (mandatory)
        'mfa_required_for_admin': True,
        'mfa_required_for_all_users': True,  # Mandatory in production
        'mfa_app_name': 'Risk Management System',
        'mfa_backup_codes_required': True,
        
        # Session settings (strictest)
        'session_timeout_minutes': 120,  # 2 hours max
        'concurrent_sessions_allowed': 1,  # Single session only
        'idle_timeout_minutes': 30,       # Auto-logout after 30 min idle
        
        # Security headers (mandatory)
        'security_headers_enabled': True,
        'security_headers_strict': True,
        'hsts_max_age': 31536000,  # 1 year
        'hsts_include_subdomains': True,
        'content_security_policy_strict': True,
        
        # Logging (comprehensive)
        'security_event_logging': True,
        'log_failed_attempts': True,
        'log_suspicious_activity': True,
        'log_admin_actions': True,
        'log_data_access': True,
        'log_retention_days': 365,
        
        # Email security (mandatory)
        'email_enabled': True,
        'email_verification_required': True,
        'email_encryption_required': True,
        
        # Database security (mandatory)
        'encrypt_sensitive_data': True,
        'encrypt_at_rest': True,
        'encrypt_in_transit': True,
        'audit_data_access': True,
        'backup_encryption': True,
        
        # API security (strictest)
        'api_versioning_required': True,
        'api_authentication_required': True,
        'request_size_limit_mb': 2,  # Strict limit
        'cors_origins': [os.getenv('PROD_FRONTEND_URL', 'https://risk.company.com')],
        'api_rate_limiting_strict': True,
        
        # SSL/TLS (mandatory)
        'ssl_required': True,
        'ssl_min_version': 'TLSv1.2',
        'ssl_cipher_suites': 'HIGH:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!SRP:!CAMELLIA',
        
        # Monitoring (critical thresholds)
        'security_monitoring_enabled': True,
        'security_alerting_enabled': True,
        'alert_thresholds': {
            'failed_logins_per_hour': 10,
            'suspicious_ips_per_hour': 3,
            'rate_limit_violations_per_hour': 20,
            'admin_actions_per_hour': 50,
            'data_export_requests_per_hour': 10
        },
        
        # Compliance
        'compliance_mode': True,
        'audit_trail_required': True,
        'data_residency_required': True,
        'gdpr_compliance': True,
        'sox_compliance': True,
        
        # Incident response
        'automatic_ip_blocking': True,
        'security_incident_response': True,
        'emergency_access_procedures': True
    }
}


class SecurityConfig:
    """Security configuration manager."""
    
    def __init__(self, environment: str = None):
        self.environment = environment or os.getenv('ENVIRONMENT', 'development')
        self.config = SECURITY_CONFIGS.get(self.environment, SECURITY_CONFIGS['development'])
        
        # Validate critical production settings
        if self.environment == 'production':
            self._validate_production_config()
    
    def _validate_production_config(self):
        """Validate critical production security settings."""
        errors = []
        
        # Check JWT secret key
        if not self.config.get('jwt_secret_key') or self.config['jwt_secret_key'] == '':
            errors.append("JWT_SECRET_KEY_PROD environment variable must be set")
        
        # Check SSL configuration
        if not os.getenv('SSL_CERT_FILE') or not os.getenv('SSL_KEY_FILE'):
            errors.append("SSL certificate files must be configured for production")
        
        # Check database encryption
        if not self.config.get('encrypt_sensitive_data'):
            errors.append("Data encryption must be enabled in production")
        
        # Check monitoring
        if not self.config.get('security_monitoring_enabled'):
            errors.append("Security monitoring must be enabled in production")
        
        if errors:
            raise ValueError(f"Production security validation failed: {', '.join(errors)}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values."""
        return self.config.copy()
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == 'production'
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == 'development'
    
    def get_password_policy(self) -> Dict[str, Any]:
        """Get password policy settings."""
        return {
            'min_length': self.get('password_min_length', 12),
            'require_uppercase': self.get('password_require_uppercase', True),
            'require_lowercase': self.get('password_require_lowercase', True),
            'require_numbers': self.get('password_require_numbers', True),
            'require_symbols': self.get('password_require_symbols', True),
            'history_count': self.get('password_history_count', 0),
            'max_age_days': self.get('password_max_age_days', 0)
        }
    
    def get_rate_limit_config(self) -> Dict[str, Any]:
        """Get rate limiting configuration."""
        return {
            'enabled': self.get('rate_limit_enabled', True),
            'requests_per_minute': self.get('rate_limit_requests_per_minute', 60),
            'login_attempts': self.get('rate_limit_login_attempts', 5)
        }
    
    def get_session_config(self) -> Dict[str, Any]:
        """Get session configuration."""
        return {
            'timeout_minutes': self.get('session_timeout_minutes', 240),
            'concurrent_allowed': self.get('concurrent_sessions_allowed', 3),
            'idle_timeout_minutes': self.get('idle_timeout_minutes', 60)
        }
    
    def get_mfa_config(self) -> Dict[str, Any]:
        """Get MFA configuration."""
        return {
            'required_for_admin': self.get('mfa_required_for_admin', False),
            'required_for_all_users': self.get('mfa_required_for_all_users', False),
            'app_name': self.get('mfa_app_name', 'Risk Management System'),
            'backup_codes_required': self.get('mfa_backup_codes_required', False)
        }
    
    def get_security_headers(self) -> Dict[str, str]:
        """Get security headers configuration."""
        headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
        }
        
        # HSTS
        hsts_value = f"max-age={self.get('hsts_max_age', 86400)}"
        if self.get('hsts_include_subdomains', False):
            hsts_value += "; includeSubDomains"
        headers["Strict-Transport-Security"] = hsts_value
        
        # CSP
        if self.get('content_security_policy_strict', False):
            headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"
        else:
            headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        
        return headers
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration."""
        return {
            'enabled': self.get('security_monitoring_enabled', True),
            'alerting_enabled': self.get('security_alerting_enabled', False),
            'thresholds': self.get('alert_thresholds', {}),
            'log_retention_days': self.get('log_retention_days', 30)
        }
    
    def should_require_mfa(self, user_role: str) -> bool:
        """Check if MFA should be required for user role."""
        if user_role in ['admin', 'super_admin']:
            return self.get('mfa_required_for_admin', False)
        
        return self.get('mfa_required_for_all_users', False)
    
    def get_allowed_cors_origins(self) -> List[str]:
        """Get allowed CORS origins."""
        return self.get('cors_origins', ['http://localhost:3000'])


# Global configuration instance
_security_config = None


def get_security_config() -> SecurityConfig:
    """Get global security configuration instance."""
    global _security_config
    if _security_config is None:
        _security_config = SecurityConfig()
    return _security_config


def reload_security_config(environment: str = None):
    """Reload security configuration."""
    global _security_config
    _security_config = SecurityConfig(environment)


# Security policy validation
def validate_security_policies():
    """Validate current security policies."""
    config = get_security_config()
    issues = []
    
    # Check password policy
    password_policy = config.get_password_policy()
    if password_policy['min_length'] < 12:
        issues.append("Password minimum length should be at least 12 characters")
    
    if not all([
        password_policy['require_uppercase'],
        password_policy['require_lowercase'],
        password_policy['require_numbers']
    ]):
        issues.append("Password should require uppercase, lowercase, and numbers")
    
    # Check rate limiting
    rate_config = config.get_rate_limit_config()
    if not rate_config['enabled']:
        issues.append("Rate limiting should be enabled")
    
    if rate_config['requests_per_minute'] > 100:
        issues.append("Rate limit seems too high (>100 requests/minute)")
    
    # Check MFA for production
    if config.is_production():
        mfa_config = config.get_mfa_config()
        if not mfa_config['required_for_admin']:
            issues.append("MFA should be required for admin users in production")
    
    # Check session timeouts
    session_config = config.get_session_config()
    if session_config['timeout_minutes'] > 480:  # 8 hours
        issues.append("Session timeout seems too long (>8 hours)")
    
    return {
        'valid': len(issues) == 0,
        'issues': issues,
        'environment': config.environment
    }
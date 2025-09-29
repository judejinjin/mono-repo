"""
Enhanced Authentication System
Multi-factor authentication, secure login, and user management
"""

import os
import sys
import secrets
import qrcode
import pyotp
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import logging
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import json

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from config import get_config
    from libs.monitoring import log_user_action, get_metrics_collector
    from libs.storage import CacheManager
    from libs.security.security_framework import (
        User, Role, Permission, SecurityValidator, PasswordManager, 
        JWTManager, SecurityEventLogger, ROLE_PERMISSIONS
    )
except ImportError:
    get_config = lambda: {}
    log_user_action = lambda *args, **kwargs: None
    get_metrics_collector = lambda: None
    CacheManager = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Authentication constants
MAX_LOGIN_ATTEMPTS = 5
ACCOUNT_LOCKOUT_DURATION_MINUTES = 30
PASSWORD_RESET_EXPIRE_MINUTES = 60
EMAIL_VERIFICATION_EXPIRE_MINUTES = 24 * 60  # 24 hours
MFA_BACKUP_CODES_COUNT = 8


@dataclass
class LoginAttempt:
    """Login attempt tracking."""
    username: str
    ip_address: str
    timestamp: datetime
    success: bool
    failure_reason: Optional[str] = None
    user_agent: Optional[str] = None


@dataclass 
class PasswordResetRequest:
    """Password reset request."""
    user_id: str
    token: str
    email: str
    expires_at: datetime
    used: bool = False
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def is_expired(self) -> bool:
        """Check if reset token is expired."""
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if reset request is valid."""
        return not self.used and not self.is_expired()


@dataclass
class EmailVerification:
    """Email verification request."""
    user_id: str
    email: str
    token: str
    expires_at: datetime
    verified: bool = False
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def is_expired(self) -> bool:
        """Check if verification token is expired."""
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if verification is valid."""
        return not self.verified and not self.is_expired()


class MFAManager:
    """Multi-factor authentication management."""
    
    def __init__(self):
        self.app_name = "Risk Management System"
        
    def generate_secret(self) -> str:
        """Generate TOTP secret for user."""
        return pyotp.random_base32()
    
    def generate_qr_code(self, user: User, secret: str) -> bytes:
        """Generate QR code for TOTP setup."""
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user.email,
            issuer_name=self.app_name
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        # Convert to bytes (would normally return image)
        # For demo purposes, return the URI
        return totp_uri.encode('utf-8')
    
    def verify_totp_token(self, secret: str, token: str, window: int = 1) -> bool:
        """Verify TOTP token."""
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(token, valid_window=window)
        except Exception as e:
            logger.error(f"TOTP verification failed: {e}")
            return False
    
    def generate_backup_codes(self, count: int = MFA_BACKUP_CODES_COUNT) -> List[str]:
        """Generate backup codes for MFA."""
        codes = []
        for _ in range(count):
            # Generate 8-character alphanumeric code
            code = ''.join(secrets.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(8))
            codes.append(code)
        return codes
    
    def hash_backup_codes(self, codes: List[str]) -> List[str]:
        """Hash backup codes for storage."""
        password_manager = PasswordManager()
        return [password_manager.hash_password(code) for code in codes]
    
    def verify_backup_code(self, hashed_codes: List[str], provided_code: str) -> Tuple[bool, Optional[int]]:
        """Verify backup code and return index if valid."""
        password_manager = PasswordManager()
        
        for i, hashed_code in enumerate(hashed_codes):
            if password_manager.verify_password(provided_code, hashed_code):
                return True, i
        
        return False, None


class EmailService:
    """Email service for authentication flows."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or get_config()
        self.smtp_host = self.config.get('smtp_host', 'localhost')
        self.smtp_port = self.config.get('smtp_port', 587)
        self.smtp_username = self.config.get('smtp_username', '')
        self.smtp_password = self.config.get('smtp_password', '')
        self.from_email = self.config.get('from_email', 'noreply@riskmanagement.com')
        self.enabled = self.config.get('email_enabled', False)
    
    def send_email(self, to_email: str, subject: str, body_text: str, body_html: str = None) -> bool:
        """Send email with text and optional HTML body."""
        if not self.enabled:
            logger.info(f"Email disabled - would send to {to_email}: {subject}")
            return True
        
        try:
            msg = MimeMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Add text part
            msg.attach(MimeText(body_text, 'plain'))
            
            # Add HTML part if provided
            if body_html:
                msg.attach(MimeText(body_html, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_username and self.smtp_password:
                    server.starttls()
                    server.login(self.smtp_username, self.smtp_password)
                
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    def send_password_reset_email(self, user: User, reset_token: str) -> bool:
        """Send password reset email."""
        reset_url = f"{self.config.get('frontend_url', 'http://localhost:3000')}/reset-password?token={reset_token}"
        
        subject = "Password Reset Request - Risk Management System"
        
        body_text = f"""
        Hello {user.first_name or user.username},
        
        You have requested to reset your password for the Risk Management System.
        
        To reset your password, please click the following link or copy it to your browser:
        {reset_url}
        
        This link will expire in 1 hour for security reasons.
        
        If you did not request this password reset, please ignore this email.
        
        Best regards,
        Risk Management System Team
        """
        
        body_html = f"""
        <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>Hello {user.first_name or user.username},</p>
            
            <p>You have requested to reset your password for the Risk Management System.</p>
            
            <p>To reset your password, please click the button below:</p>
            
            <p style="margin: 20px 0;">
                <a href="{reset_url}" 
                   style="background-color: #007bff; color: white; padding: 12px 24px; 
                          text-decoration: none; border-radius: 4px; display: inline-block;">
                    Reset Password
                </a>
            </p>
            
            <p>Or copy this link to your browser: <a href="{reset_url}">{reset_url}</a></p>
            
            <p><strong>This link will expire in 1 hour for security reasons.</strong></p>
            
            <p>If you did not request this password reset, please ignore this email.</p>
            
            <p>Best regards,<br>Risk Management System Team</p>
        </body>
        </html>
        """
        
        return self.send_email(user.email, subject, body_text, body_html)
    
    def send_verification_email(self, user: User, verification_token: str) -> bool:
        """Send email verification email."""
        verification_url = f"{self.config.get('frontend_url', 'http://localhost:3000')}/verify-email?token={verification_token}"
        
        subject = "Email Verification - Risk Management System"
        
        body_text = f"""
        Hello {user.first_name or user.username},
        
        Welcome to the Risk Management System!
        
        To complete your registration, please verify your email address by clicking the link below:
        {verification_url}
        
        This link will expire in 24 hours.
        
        If you did not create this account, please ignore this email.
        
        Best regards,
        Risk Management System Team
        """
        
        body_html = f"""
        <html>
        <body>
            <h2>Welcome to Risk Management System</h2>
            <p>Hello {user.first_name or user.username},</p>
            
            <p>Welcome to the Risk Management System!</p>
            
            <p>To complete your registration, please verify your email address by clicking the button below:</p>
            
            <p style="margin: 20px 0;">
                <a href="{verification_url}" 
                   style="background-color: #28a745; color: white; padding: 12px 24px; 
                          text-decoration: none; border-radius: 4px; display: inline-block;">
                    Verify Email
                </a>
            </p>
            
            <p>Or copy this link to your browser: <a href="{verification_url}">{verification_url}</a></p>
            
            <p><strong>This link will expire in 24 hours.</strong></p>
            
            <p>If you did not create this account, please ignore this email.</p>
            
            <p>Best regards,<br>Risk Management System Team</p>
        </body>
        </html>
        """
        
        return self.send_email(user.email, subject, body_text, body_html)
    
    def send_login_alert_email(self, user: User, ip_address: str, user_agent: str = None) -> bool:
        """Send login alert email for security notifications."""
        subject = "Security Alert - New Login to Risk Management System"
        
        body_text = f"""
        Hello {user.first_name or user.username},
        
        We detected a new login to your Risk Management System account:
        
        Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
        IP Address: {ip_address}
        {f'Device: {user_agent}' if user_agent else ''}
        
        If this was you, no action is needed.
        
        If you don't recognize this login, please:
        1. Change your password immediately
        2. Review your account activity
        3. Enable two-factor authentication if not already enabled
        
        Best regards,
        Risk Management System Team
        """
        
        body_html = f"""
        <html>
        <body>
            <h2>Security Alert</h2>
            <p>Hello {user.first_name or user.username},</p>
            
            <p>We detected a new login to your Risk Management System account:</p>
            
            <ul>
                <li><strong>Time:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</li>
                <li><strong>IP Address:</strong> {ip_address}</li>
                {f'<li><strong>Device:</strong> {user_agent}</li>' if user_agent else ''}
            </ul>
            
            <p>If this was you, no action is needed.</p>
            
            <p>If you don't recognize this login, please:</p>
            <ol>
                <li>Change your password immediately</li>
                <li>Review your account activity</li>
                <li>Enable two-factor authentication if not already enabled</li>
            </ol>
            
            <p>Best regards,<br>Risk Management System Team</p>
        </body>
        </html>
        """
        
        return self.send_email(user.email, subject, body_text, body_html)


class AuthenticationService:
    """Enhanced authentication service."""
    
    def __init__(self, cache_manager: Optional[CacheManager] = None):
        self.cache_manager = cache_manager or CacheManager() if CacheManager else None
        self.password_manager = PasswordManager()
        self.jwt_manager = JWTManager()
        self.security_validator = SecurityValidator()
        self.security_logger = SecurityEventLogger()
        self.mfa_manager = MFAManager()
        self.email_service = EmailService()
        
        # In-memory stores (would use database in production)
        self.users: Dict[str, User] = {}  # username -> User
        self.login_attempts: List[LoginAttempt] = []
        self.password_resets: Dict[str, PasswordResetRequest] = {}  # token -> request
        self.email_verifications: Dict[str, EmailVerification] = {}  # token -> verification
        
        # Create default admin user
        self._create_default_admin()
    
    def _create_default_admin(self):
        """Create default admin user for initial setup."""
        admin_username = "admin"
        if admin_username not in self.users:
            admin_password = os.getenv('ADMIN_PASSWORD', 'AdminPassword123!')
            
            admin_user = User(
                user_id=secrets.token_hex(16),
                username=admin_username,
                email="admin@riskmanagement.com",
                password_hash=self.password_manager.hash_password(admin_password),
                role=Role.SUPER_ADMIN,
                first_name="System",
                last_name="Administrator",
                is_active=True,
                is_verified=True
            )
            
            self.users[admin_username] = admin_user
            logger.info("Default admin user created")
    
    def register_user(self, username: str, email: str, password: str, 
                     first_name: str = "", last_name: str = "",
                     role: Role = Role.VIEWER) -> Dict[str, Any]:
        """Register new user."""
        try:
            # Validate inputs
            username_validation = self.security_validator.validate_username(username)
            if not username_validation['valid']:
                return {
                    'success': False,
                    'error': 'Invalid username',
                    'details': username_validation['errors']
                }
            
            if not self.security_validator.validate_email(email):
                return {
                    'success': False,
                    'error': 'Invalid email address'
                }
            
            password_validation = self.security_validator.validate_password(password)
            if not password_validation['valid']:
                return {
                    'success': False,
                    'error': 'Password does not meet requirements',
                    'details': password_validation['errors']
                }
            
            # Check if user already exists
            if username in self.users:
                return {
                    'success': False,
                    'error': 'Username already exists'
                }
            
            if any(user.email == email for user in self.users.values()):
                return {
                    'success': False,
                    'error': 'Email already registered'
                }
            
            # Create user
            user = User(
                user_id=secrets.token_hex(16),
                username=username,
                email=email,
                password_hash=self.password_manager.hash_password(password),
                role=role,
                first_name=first_name,
                last_name=last_name,
                is_active=True,
                is_verified=False  # Require email verification
            )
            
            self.users[username] = user
            
            # Send verification email
            verification_token = secrets.token_urlsafe(32)
            verification = EmailVerification(
                user_id=user.user_id,
                email=email,
                token=verification_token,
                expires_at=datetime.utcnow() + timedelta(minutes=EMAIL_VERIFICATION_EXPIRE_MINUTES)
            )
            
            self.email_verifications[verification_token] = verification
            
            if self.email_service.send_verification_email(user, verification_token):
                verification_sent = True
            else:
                verification_sent = False
            
            self.security_logger.log_security_event(
                'user_registered',
                user_id=user.user_id,
                details={
                    'username': username,
                    'email': email,
                    'role': role.value,
                    'verification_sent': verification_sent
                }
            )
            
            return {
                'success': True,
                'user_id': user.user_id,
                'verification_required': True,
                'verification_sent': verification_sent
            }
            
        except Exception as e:
            logger.error(f"User registration failed: {e}")
            return {
                'success': False,
                'error': 'Registration failed',
                'details': str(e)
            }
    
    def authenticate(self, username: str, password: str, 
                    ip_address: str = None, user_agent: str = None,
                    totp_token: str = None, backup_code: str = None) -> Dict[str, Any]:
        """Authenticate user with password and optional MFA."""
        
        attempt = LoginAttempt(
            username=username,
            ip_address=ip_address or '127.0.0.1',
            timestamp=datetime.utcnow(),
            success=False,
            user_agent=user_agent
        )
        
        try:
            # Check if user exists
            user = self.users.get(username)
            if not user:
                attempt.failure_reason = "Invalid credentials"
                self.login_attempts.append(attempt)
                self.security_logger.log_security_event(
                    'failed_login',
                    ip_address=ip_address,
                    details={'username': username, 'reason': 'user_not_found'}
                )
                return {
                    'success': False,
                    'error': 'Invalid credentials'
                }
            
            # Check if account is locked
            if user.is_account_locked():
                attempt.failure_reason = "Account locked"
                self.login_attempts.append(attempt)
                self.security_logger.log_security_event(
                    'failed_login',
                    user_id=user.user_id,
                    ip_address=ip_address,
                    details={'username': username, 'reason': 'account_locked'}
                )
                return {
                    'success': False,
                    'error': 'Account is locked. Please try again later.'
                }
            
            # Check if account is active
            if not user.is_active:
                attempt.failure_reason = "Account disabled"
                self.login_attempts.append(attempt)
                self.security_logger.log_security_event(
                    'failed_login',
                    user_id=user.user_id,
                    ip_address=ip_address,
                    details={'username': username, 'reason': 'account_disabled'}
                )
                return {
                    'success': False,
                    'error': 'Account is disabled'
                }
            
            # Verify password
            if not self.password_manager.verify_password(password, user.password_hash):
                user.failed_login_attempts += 1
                
                # Lock account after max attempts
                if user.failed_login_attempts >= MAX_LOGIN_ATTEMPTS:
                    user.account_locked_until = datetime.utcnow() + timedelta(minutes=ACCOUNT_LOCKOUT_DURATION_MINUTES)
                
                attempt.failure_reason = "Invalid password"
                self.login_attempts.append(attempt)
                self.security_logger.log_security_event(
                    'failed_login',
                    user_id=user.user_id,
                    ip_address=ip_address,
                    details={'username': username, 'reason': 'invalid_password', 'attempts': user.failed_login_attempts}
                )
                return {
                    'success': False,
                    'error': 'Invalid credentials'
                }
            
            # Check MFA if enabled
            if user.mfa_enabled:
                mfa_verified = False
                
                if totp_token:
                    mfa_verified = self.mfa_manager.verify_totp_token(user.mfa_secret, totp_token)
                elif backup_code:
                    # In production, backup codes would be stored securely
                    # For demo, assume backup codes are stored as user attribute
                    backup_codes = getattr(user, 'mfa_backup_codes', [])
                    is_valid, code_index = self.mfa_manager.verify_backup_code(backup_codes, backup_code)
                    if is_valid:
                        # Remove used backup code
                        backup_codes.pop(code_index)
                        mfa_verified = True
                
                if not mfa_verified:
                    attempt.failure_reason = "MFA required"
                    self.login_attempts.append(attempt)
                    return {
                        'success': False,
                        'error': 'MFA verification required',
                        'mfa_required': True
                    }
            
            # Successful authentication
            user.failed_login_attempts = 0
            user.account_locked_until = None
            user.last_login = datetime.utcnow()
            
            # Generate tokens
            access_token = self.jwt_manager.generate_token(user, 'access')
            refresh_token = self.jwt_manager.generate_token(user, 'refresh')
            
            attempt.success = True
            self.login_attempts.append(attempt)
            
            self.security_logger.log_security_event(
                'successful_login',
                user_id=user.user_id,
                ip_address=ip_address,
                details={
                    'username': username,
                    'mfa_used': user.mfa_enabled,
                    'user_agent': user_agent
                }
            )
            
            # Send login alert email for new IP addresses
            recent_logins = [
                la for la in self.login_attempts[-10:]  # Check last 10 attempts
                if la.username == username and la.success and la.ip_address != ip_address
            ]
            
            if ip_address and len(recent_logins) == 0:  # New IP
                self.email_service.send_login_alert_email(user, ip_address, user_agent)
            
            return {
                'success': True,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': 'bearer',
                'user': user.to_dict(),
                'mfa_enabled': user.mfa_enabled
            }
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            attempt.failure_reason = f"System error: {str(e)}"
            self.login_attempts.append(attempt)
            return {
                'success': False,
                'error': 'Authentication failed'
            }
    
    def setup_mfa(self, user_id: str) -> Dict[str, Any]:
        """Setup MFA for user."""
        try:
            user = next((u for u in self.users.values() if u.user_id == user_id), None)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            if user.mfa_enabled:
                return {
                    'success': False,
                    'error': 'MFA already enabled'
                }
            
            # Generate secret and QR code
            secret = self.mfa_manager.generate_secret()
            qr_code = self.mfa_manager.generate_qr_code(user, secret)
            
            # Generate backup codes
            backup_codes = self.mfa_manager.generate_backup_codes()
            hashed_backup_codes = self.mfa_manager.hash_backup_codes(backup_codes)
            
            # Store temporarily (user needs to verify before enabling)
            user.mfa_secret = secret
            setattr(user, 'mfa_backup_codes', hashed_backup_codes)
            
            return {
                'success': True,
                'secret': secret,
                'qr_code': qr_code.decode('utf-8'),
                'backup_codes': backup_codes
            }
            
        except Exception as e:
            logger.error(f"MFA setup failed: {e}")
            return {
                'success': False,
                'error': 'MFA setup failed'
            }
    
    def enable_mfa(self, user_id: str, totp_token: str) -> Dict[str, Any]:
        """Enable MFA after verification."""
        try:
            user = next((u for u in self.users.values() if u.user_id == user_id), None)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            if not user.mfa_secret:
                return {
                    'success': False,
                    'error': 'MFA not set up'
                }
            
            # Verify TOTP token
            if not self.mfa_manager.verify_totp_token(user.mfa_secret, totp_token):
                return {
                    'success': False,
                    'error': 'Invalid TOTP token'
                }
            
            user.mfa_enabled = True
            
            self.security_logger.log_security_event(
                'mfa_enabled',
                user_id=user.user_id,
                details={'username': user.username}
            )
            
            return {
                'success': True,
                'message': 'MFA enabled successfully'
            }
            
        except Exception as e:
            logger.error(f"MFA enable failed: {e}")
            return {
                'success': False,
                'error': 'Failed to enable MFA'
            }
    
    def request_password_reset(self, email: str) -> Dict[str, Any]:
        """Request password reset."""
        try:
            user = next((u for u in self.users.values() if u.email == email), None)
            if not user:
                # Don't reveal if email exists
                return {
                    'success': True,
                    'message': 'If email exists, reset instructions have been sent'
                }
            
            # Generate reset token
            reset_token = secrets.token_urlsafe(32)
            reset_request = PasswordResetRequest(
                user_id=user.user_id,
                token=reset_token,
                email=email,
                expires_at=datetime.utcnow() + timedelta(minutes=PASSWORD_RESET_EXPIRE_MINUTES)
            )
            
            self.password_resets[reset_token] = reset_request
            
            # Send reset email
            email_sent = self.email_service.send_password_reset_email(user, reset_token)
            
            self.security_logger.log_security_event(
                'password_reset_requested',
                user_id=user.user_id,
                details={'email': email, 'email_sent': email_sent}
            )
            
            return {
                'success': True,
                'message': 'If email exists, reset instructions have been sent'
            }
            
        except Exception as e:
            logger.error(f"Password reset request failed: {e}")
            return {
                'success': False,
                'error': 'Failed to process reset request'
            }
    
    def reset_password(self, token: str, new_password: str) -> Dict[str, Any]:
        """Reset password using token."""
        try:
            reset_request = self.password_resets.get(token)
            if not reset_request or not reset_request.is_valid():
                return {
                    'success': False,
                    'error': 'Invalid or expired reset token'
                }
            
            # Validate new password
            validation = self.security_validator.validate_password(new_password)
            if not validation['valid']:
                return {
                    'success': False,
                    'error': 'Password does not meet requirements',
                    'details': validation['errors']
                }
            
            user = next((u for u in self.users.values() if u.user_id == reset_request.user_id), None)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            # Update password
            user.password_hash = self.password_manager.hash_password(new_password)
            user.failed_login_attempts = 0
            user.account_locked_until = None
            
            # Mark reset as used
            reset_request.used = True
            
            self.security_logger.log_security_event(
                'password_reset_completed',
                user_id=user.user_id,
                details={'username': user.username}
            )
            
            return {
                'success': True,
                'message': 'Password reset successfully'
            }
            
        except Exception as e:
            logger.error(f"Password reset failed: {e}")
            return {
                'success': False,
                'error': 'Password reset failed'
            }
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return next((u for u in self.users.values() if u.user_id == user_id), None)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.users.get(username)
    
    def get_authentication_stats(self) -> Dict[str, Any]:
        """Get authentication statistics."""
        total_attempts = len(self.login_attempts)
        successful_attempts = sum(1 for attempt in self.login_attempts if attempt.success)
        failed_attempts = total_attempts - successful_attempts
        
        recent_attempts = [
            attempt for attempt in self.login_attempts
            if attempt.timestamp > datetime.utcnow() - timedelta(hours=24)
        ]
        
        return {
            'total_users': len(self.users),
            'active_users': sum(1 for user in self.users.values() if user.is_active),
            'verified_users': sum(1 for user in self.users.values() if user.is_verified),
            'mfa_enabled_users': sum(1 for user in self.users.values() if user.mfa_enabled),
            'total_login_attempts': total_attempts,
            'successful_logins': successful_attempts,
            'failed_logins': failed_attempts,
            'success_rate': (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0,
            'recent_attempts_24h': len(recent_attempts),
            'active_password_resets': sum(1 for reset in self.password_resets.values() if reset.is_valid()),
            'pending_verifications': sum(1 for verification in self.email_verifications.values() if verification.is_valid())
        }


# Global authentication service instance
_auth_service = None


def get_auth_service() -> AuthenticationService:
    """Get global authentication service instance."""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthenticationService()
    return _auth_service
"""
Authentication library for the mono-repo risk platform.
Provides JWT handling, user management, and password utilities.
"""

import jwt
import bcrypt
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Any, List
from pydantic import BaseModel
import os
import logging

logger = logging.getLogger(__name__)

# Configuration
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', '24'))

class User(BaseModel):
    """User model for authentication."""
    username: str
    email: str
    full_name: str
    role: str  # business_user, data_scientist, admin
    groups: List[str] = []
    is_active: bool = True
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

class TokenData(BaseModel):
    """Token payload data."""
    username: str
    role: str
    groups: List[str]
    exp: datetime
    iat: datetime

class AuthManager:
    """Main authentication manager class."""
    
    def __init__(self):
        self.secret_key = JWT_SECRET_KEY
        self.algorithm = JWT_ALGORITHM
        self.expiration_hours = JWT_EXPIRATION_HOURS
        
        if self.secret_key == 'your-secret-key-change-in-production':
            logger.warning("Using default JWT secret key. Please set JWT_SECRET_KEY environment variable.")
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        # Generate salt and hash password
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    def generate_token(self, user: User) -> str:
        """Generate JWT token for user."""
        now = datetime.now(timezone.utc)
        expire = now + timedelta(hours=self.expiration_hours)
        
        payload = {
            'username': user.username,
            'role': user.role,
            'groups': user.groups,
            'exp': expire,
            'iat': now,
            'sub': user.username  # Subject
        }
        
        try:
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            logger.info(f"Generated token for user: {user.username}")
            return token
        except Exception as e:
            logger.error(f"Token generation error: {e}")
            raise ValueError("Failed to generate token")
    
    def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Validate required fields
            username = payload.get('username')
            if not username:
                logger.warning("Token missing username")
                return None
            
            token_data = TokenData(
                username=username,
                role=payload.get('role', 'business_user'),
                groups=payload.get('groups', []),
                exp=datetime.fromtimestamp(payload['exp'], timezone.utc),
                iat=datetime.fromtimestamp(payload['iat'], timezone.utc)
            )
            
            logger.debug(f"Token verified for user: {username}")
            return token_data
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None
    
    def refresh_token(self, token: str) -> Optional[str]:
        """Refresh JWT token if valid and not expired."""
        token_data = self.verify_token(token)
        if not token_data:
            return None
        
        # Create user object for token generation
        user = User(
            username=token_data.username,
            email=f"{token_data.username}@company.com",  # Would come from database
            full_name=token_data.username.title(),
            role=token_data.role,
            groups=token_data.groups
        )
        
        return self.generate_token(user)

class RoleManager:
    """Manages user roles and permissions."""
    
    # Role hierarchy (higher number = more permissions)
    ROLE_HIERARCHY = {
        'business_user': 1,
        'data_scientist': 2,
        'admin': 3
    }
    
    # Permission mappings
    ROLE_PERMISSIONS = {
        'business_user': [
            'read_notebooks',
            'run_notebooks',
            'view_dashboards',
            'read_reports'
        ],
        'data_scientist': [
            'read_notebooks',
            'run_notebooks',
            'create_notebooks',
            'view_dashboards',
            'read_reports',
            'create_reports',
            'access_raw_data',
            'run_analytics'
        ],
        'admin': [
            'read_notebooks',
            'run_notebooks',
            'create_notebooks',
            'manage_notebooks',
            'view_dashboards',
            'manage_dashboards',
            'read_reports',
            'create_reports',
            'manage_reports',
            'access_raw_data',
            'run_analytics',
            'manage_users',
            'manage_system',
            'access_logs'
        ]
    }
    
    @classmethod
    def has_permission(cls, user_role: str, required_permission: str) -> bool:
        """Check if user role has required permission."""
        permissions = cls.ROLE_PERMISSIONS.get(user_role, [])
        return required_permission in permissions
    
    @classmethod
    def has_role_level(cls, user_role: str, required_role: str) -> bool:
        """Check if user role meets minimum required role level."""
        user_level = cls.ROLE_HIERARCHY.get(user_role, 0)
        required_level = cls.ROLE_HIERARCHY.get(required_role, 999)
        return user_level >= required_level
    
    @classmethod
    def get_permissions(cls, role: str) -> List[str]:
        """Get all permissions for a role."""
        return cls.ROLE_PERMISSIONS.get(role, [])

# Global auth manager instance
auth_manager = AuthManager()
role_manager = RoleManager()

# Utility functions for easy imports
def hash_password(password: str) -> str:
    """Hash a password."""
    return auth_manager.hash_password(password)

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password."""
    return auth_manager.verify_password(password, hashed_password)

def generate_token(user: User) -> str:
    """Generate JWT token."""
    return auth_manager.generate_token(user)

def verify_token(token: str) -> Optional[TokenData]:
    """Verify JWT token."""
    return auth_manager.verify_token(token)

def has_permission(user_role: str, permission: str) -> bool:
    """Check if user has permission."""
    return role_manager.has_permission(user_role, permission)

def has_role_level(user_role: str, required_role: str) -> bool:
    """Check if user meets role level."""
    return role_manager.has_role_level(user_role, required_role)
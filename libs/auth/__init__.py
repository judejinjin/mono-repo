"""
Authentication library initialization.
"""

from .auth import (
    User, TokenData, AuthManager, RoleManager,
    auth_manager, role_manager,
    hash_password, verify_password, generate_token, verify_token,
    has_permission, has_role_level
)

from .jwt_handler import (
    TokenType, JWTHandler, TokenBlacklist,
    get_jwt_handler, get_token_blacklist
)

from .password_utils import (
    PasswordValidator, PasswordHasher, PasswordGenerator,
    validate_password, get_password_strength,
    generate_password, generate_reset_token
)

__all__ = [
    # Core auth
    'User', 'TokenData', 'AuthManager', 'RoleManager',
    'auth_manager', 'role_manager',
    
    # JWT handling
    'TokenType', 'JWTHandler', 'TokenBlacklist',
    'get_jwt_handler', 'get_token_blacklist',
    
    # Password utilities
    'PasswordValidator', 'PasswordHasher', 'PasswordGenerator',
    
    # Utility functions
    'hash_password', 'verify_password', 'generate_token', 'verify_token',
    'has_permission', 'has_role_level', 'validate_password', 
    'get_password_strength', 'generate_password', 'generate_reset_token'
]
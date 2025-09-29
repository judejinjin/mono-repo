"""
JWT token handler utilities.
Provides specialized JWT operations and token management.
"""

import jwt
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Any, List
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class TokenType(Enum):
    """Token types for different purposes."""
    ACCESS = "access"
    REFRESH = "refresh"
    RESET_PASSWORD = "reset_password"
    EMAIL_VERIFICATION = "email_verification"

class JWTHandler:
    """Specialized JWT token handler."""
    
    def __init__(self, secret_key: str, algorithm: str = 'HS256'):
        self.secret_key = secret_key
        self.algorithm = algorithm
        
        # Different expiration times for different token types
        self.expiration_times = {
            TokenType.ACCESS: timedelta(hours=24),
            TokenType.REFRESH: timedelta(days=7),
            TokenType.RESET_PASSWORD: timedelta(hours=1),
            TokenType.EMAIL_VERIFICATION: timedelta(days=1)
        }
    
    def encode_token(self, payload: Dict[str, Any], token_type: TokenType = TokenType.ACCESS) -> str:
        """Encode a JWT token with specified type."""
        now = datetime.now(timezone.utc)
        
        # Add standard claims
        payload.update({
            'iat': now,  # Issued at
            'exp': now + self.expiration_times[token_type],  # Expiration
            'type': token_type.value,  # Token type
            'jti': self._generate_jti()  # JWT ID
        })
        
        try:
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            logger.debug(f"Encoded {token_type.value} token")
            return token
        except Exception as e:
            logger.error(f"Token encoding error: {e}")
            raise ValueError(f"Failed to encode {token_type.value} token")
    
    def decode_token(self, token: str, expected_type: TokenType = None) -> Optional[Dict[str, Any]]:
        """Decode and validate JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Validate token type if specified
            if expected_type and payload.get('type') != expected_type.value:
                logger.warning(f"Token type mismatch. Expected: {expected_type.value}, Got: {payload.get('type')}")
                return None
            
            logger.debug(f"Decoded {payload.get('type', 'unknown')} token")
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Token decoding error: {e}")
            return None
    
    def is_token_expired(self, token: str) -> bool:
        """Check if token is expired without raising exception."""
        try:
            jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return False
        except jwt.ExpiredSignatureError:
            return True
        except jwt.InvalidTokenError:
            return True
    
    def get_token_claims(self, token: str) -> Optional[Dict[str, Any]]:
        """Get token claims without verification (for expired tokens)."""
        try:
            # Decode without verification to get claims
            return jwt.decode(token, options={"verify_signature": False})
        except Exception as e:
            logger.error(f"Failed to get token claims: {e}")
            return None
    
    def create_access_token(self, user_id: str, username: str, role: str, groups: List[str] = None) -> str:
        """Create access token for user authentication."""
        payload = {
            'sub': user_id,
            'username': username,
            'role': role,
            'groups': groups or [],
            'scope': 'access'
        }
        return self.encode_token(payload, TokenType.ACCESS)
    
    def create_refresh_token(self, user_id: str, username: str) -> str:
        """Create refresh token for token renewal."""
        payload = {
            'sub': user_id,
            'username': username,
            'scope': 'refresh'
        }
        return self.encode_token(payload, TokenType.REFRESH)
    
    def create_reset_token(self, user_id: str, email: str) -> str:
        """Create password reset token."""
        payload = {
            'sub': user_id,
            'email': email,
            'scope': 'reset_password'
        }
        return self.encode_token(payload, TokenType.RESET_PASSWORD)
    
    def validate_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate access token and return user data."""
        payload = self.decode_token(token, TokenType.ACCESS)
        if not payload:
            return None
        
        # Validate required claims
        required_claims = ['sub', 'username', 'role']
        if not all(claim in payload for claim in required_claims):
            logger.warning("Access token missing required claims")
            return None
        
        return {
            'user_id': payload['sub'],
            'username': payload['username'],
            'role': payload['role'],
            'groups': payload.get('groups', [])
        }
    
    def validate_refresh_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate refresh token and return user data."""
        payload = self.decode_token(token, TokenType.REFRESH)
        if not payload:
            return None
        
        return {
            'user_id': payload['sub'],
            'username': payload['username']
        }
    
    def _generate_jti(self) -> str:
        """Generate unique JWT ID."""
        import uuid
        return str(uuid.uuid4())

class TokenBlacklist:
    """Manages blacklisted tokens (for logout functionality)."""
    
    def __init__(self):
        # In production, this should use Redis or database
        self._blacklisted_tokens = set()
        logger.warning("Using in-memory token blacklist. Use Redis in production.")
    
    def blacklist_token(self, token: str) -> None:
        """Add token to blacklist."""
        self._blacklisted_tokens.add(token)
        logger.info("Token blacklisted")
    
    def is_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted."""
        return token in self._blacklisted_tokens
    
    def cleanup_expired_tokens(self, jwt_handler: JWTHandler) -> int:
        """Remove expired tokens from blacklist."""
        expired_tokens = []
        for token in self._blacklisted_tokens:
            if jwt_handler.is_token_expired(token):
                expired_tokens.append(token)
        
        for token in expired_tokens:
            self._blacklisted_tokens.remove(token)
        
        logger.info(f"Cleaned up {len(expired_tokens)} expired tokens from blacklist")
        return len(expired_tokens)

# Global instances
_jwt_handler = None
_token_blacklist = None

def get_jwt_handler() -> JWTHandler:
    """Get global JWT handler instance."""
    global _jwt_handler
    if _jwt_handler is None:
        import os
        secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
        _jwt_handler = JWTHandler(secret_key)
    return _jwt_handler

def get_token_blacklist() -> TokenBlacklist:
    """Get global token blacklist instance."""
    global _token_blacklist
    if _token_blacklist is None:
        _token_blacklist = TokenBlacklist()
    return _token_blacklist
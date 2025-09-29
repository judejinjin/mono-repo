"""
Password utility functions for secure password handling.
Provides password validation, hashing, and security utilities.
"""

import bcrypt
import hashlib
import secrets
import string
import re
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class PasswordValidator:
    """Password validation utilities."""
    
    # Password policy configuration
    MIN_LENGTH = 8
    MAX_LENGTH = 128
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True  
    REQUIRE_DIGITS = True
    REQUIRE_SPECIAL = True
    SPECIAL_CHARACTERS = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    # Common weak passwords
    COMMON_PASSWORDS = {
        'password', '123456', '123456789', 'qwerty', 'abc123', 'password123',
        'admin', 'letmein', 'welcome', 'monkey', '1234567890', 'password1',
        'qwertyuiop', '123123', '000000', 'iloveyou', 'dragon', 'master'
    }
    
    @classmethod
    def validate_password(cls, password: str) -> Tuple[bool, List[str]]:
        """
        Validate password against security policy.
        Returns (is_valid, error_messages)
        """
        errors = []
        
        # Check length
        if len(password) < cls.MIN_LENGTH:
            errors.append(f"Password must be at least {cls.MIN_LENGTH} characters long")
        
        if len(password) > cls.MAX_LENGTH:
            errors.append(f"Password must be no more than {cls.MAX_LENGTH} characters long")
        
        # Check character requirements
        if cls.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if cls.REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if cls.REQUIRE_DIGITS and not re.search(r'[0-9]', password):
            errors.append("Password must contain at least one digit")
        
        if cls.REQUIRE_SPECIAL and not re.search(f'[{re.escape(cls.SPECIAL_CHARACTERS)}]', password):
            errors.append(f"Password must contain at least one special character: {cls.SPECIAL_CHARACTERS}")
        
        # Check for common passwords
        if password.lower() in cls.COMMON_PASSWORDS:
            errors.append("Password is too common and easily guessable")
        
        # Check for sequential patterns
        if cls._has_sequential_pattern(password):
            errors.append("Password contains sequential patterns")
        
        # Check for repeated characters
        if cls._has_repeated_characters(password):
            errors.append("Password has too many repeated characters")
        
        return len(errors) == 0, errors
    
    @classmethod
    def get_password_strength(cls, password: str) -> Dict[str, any]:
        """
        Analyze password strength and return detailed metrics.
        """
        strength = {
            'score': 0,
            'level': 'Very Weak',
            'feedback': [],
            'has_uppercase': bool(re.search(r'[A-Z]', password)),
            'has_lowercase': bool(re.search(r'[a-z]', password)),
            'has_digits': bool(re.search(r'[0-9]', password)),
            'has_special': bool(re.search(f'[{re.escape(cls.SPECIAL_CHARACTERS)}]', password)),
            'length': len(password),
            'entropy': cls._calculate_entropy(password)
        }
        
        # Calculate strength score (0-100)
        score = 0
        
        # Length scoring
        if len(password) >= 8:
            score += 20
        if len(password) >= 12:
            score += 10
        if len(password) >= 16:
            score += 10
        
        # Character variety scoring
        if strength['has_uppercase']:
            score += 15
        if strength['has_lowercase']:
            score += 15
        if strength['has_digits']:
            score += 15
        if strength['has_special']:
            score += 15
        
        # Entropy bonus
        if strength['entropy'] > 50:
            score += 10
        
        strength['score'] = min(score, 100)
        
        # Determine strength level
        if score < 30:
            strength['level'] = 'Very Weak'
            strength['feedback'].append('Password is very weak and easily crackable')
        elif score < 50:
            strength['level'] = 'Weak'
            strength['feedback'].append('Password is weak, consider adding more variety')
        elif score < 70:
            strength['level'] = 'Fair'
            strength['feedback'].append('Password is fair, but could be stronger')
        elif score < 85:
            strength['level'] = 'Good'
            strength['feedback'].append('Password is good and secure')
        else:
            strength['level'] = 'Excellent'
            strength['feedback'].append('Password is excellent and very secure')
        
        return strength
    
    @classmethod
    def _has_sequential_pattern(cls, password: str) -> bool:
        """Check for sequential patterns like 'abc' or '123'."""
        password_lower = password.lower()
        
        # Check for ascending sequences
        for i in range(len(password_lower) - 2):
            if (ord(password_lower[i+1]) == ord(password_lower[i]) + 1 and 
                ord(password_lower[i+2]) == ord(password_lower[i]) + 2):
                return True
        
        return False
    
    @classmethod
    def _has_repeated_characters(cls, password: str, max_repeats: int = 3) -> bool:
        """Check for excessive repeated characters."""
        char_count = {}
        for char in password:
            char_count[char] = char_count.get(char, 0) + 1
            if char_count[char] > max_repeats:
                return True
        return False
    
    @classmethod
    def _calculate_entropy(cls, password: str) -> float:
        """Calculate password entropy."""
        import math
        
        # Determine character space
        charset_size = 0
        if re.search(r'[a-z]', password):
            charset_size += 26
        if re.search(r'[A-Z]', password):
            charset_size += 26
        if re.search(r'[0-9]', password):
            charset_size += 10
        if re.search(f'[{re.escape(cls.SPECIAL_CHARACTERS)}]', password):
            charset_size += len(cls.SPECIAL_CHARACTERS)
        
        if charset_size == 0:
            return 0
        
        # Calculate entropy: log2(charset_size ^ length)
        entropy = len(password) * math.log2(charset_size)
        return entropy

class PasswordHasher:
    """Secure password hashing utilities using bcrypt."""
    
    DEFAULT_ROUNDS = 12  # bcrypt rounds (2^12 iterations)
    
    @classmethod
    def hash_password(cls, password: str, rounds: int = None) -> str:
        """
        Hash password using bcrypt with salt.
        Higher rounds = more secure but slower.
        """
        if rounds is None:
            rounds = cls.DEFAULT_ROUNDS
        
        try:
            # Generate salt and hash
            salt = bcrypt.gensalt(rounds=rounds)
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            
            logger.debug(f"Password hashed with {rounds} rounds")
            return hashed.decode('utf-8')
            
        except Exception as e:
            logger.error(f"Password hashing error: {e}")
            raise ValueError("Failed to hash password")
    
    @classmethod
    def verify_password(cls, password: str, hashed_password: str) -> bool:
        """Verify password against bcrypt hash."""
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'), 
                hashed_password.encode('utf-8')
            )
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    @classmethod
    def needs_rehash(cls, hashed_password: str, rounds: int = None) -> bool:
        """Check if password needs rehashing (due to updated rounds)."""
        if rounds is None:
            rounds = cls.DEFAULT_ROUNDS
        
        try:
            # Extract current rounds from hash
            current_rounds = cls._get_hash_rounds(hashed_password)
            return current_rounds < rounds
        except Exception:
            return True  # Rehash if we can't determine rounds
    
    @classmethod
    def _get_hash_rounds(cls, hashed_password: str) -> int:
        """Extract rounds from bcrypt hash."""
        # bcrypt hash format: $2b$rounds$salt+hash
        parts = hashed_password.split('$')
        if len(parts) >= 3:
            return int(parts[2])
        raise ValueError("Invalid bcrypt hash format")

class PasswordGenerator:
    """Generate secure passwords and tokens."""
    
    @classmethod
    def generate_password(cls, length: int = 16, 
                         include_uppercase: bool = True,
                         include_lowercase: bool = True,
                         include_digits: bool = True,
                         include_special: bool = True) -> str:
        """Generate a secure random password."""
        
        characters = ""
        if include_lowercase:
            characters += string.ascii_lowercase
        if include_uppercase:
            characters += string.ascii_uppercase
        if include_digits:
            characters += string.digits
        if include_special:
            characters += "!@#$%^&*()_+-="
        
        if not characters:
            raise ValueError("At least one character type must be included")
        
        # Ensure at least one character from each required type
        password = []
        
        if include_lowercase:
            password.append(secrets.choice(string.ascii_lowercase))
        if include_uppercase:
            password.append(secrets.choice(string.ascii_uppercase))
        if include_digits:
            password.append(secrets.choice(string.digits))
        if include_special:
            password.append(secrets.choice("!@#$%^&*()_+-="))
        
        # Fill remaining length with random characters
        remaining_length = length - len(password)
        for _ in range(remaining_length):
            password.append(secrets.choice(characters))
        
        # Shuffle the password
        secrets.SystemRandom().shuffle(password)
        
        return ''.join(password)
    
    @classmethod
    def generate_reset_token(cls, length: int = 32) -> str:
        """Generate secure reset token."""
        return secrets.token_urlsafe(length)
    
    @classmethod
    def generate_api_key(cls, length: int = 40) -> str:
        """Generate API key."""
        return secrets.token_hex(length)

# Utility functions for easy imports
validator = PasswordValidator()
hasher = PasswordHasher()
generator = PasswordGenerator()

def validate_password(password: str) -> Tuple[bool, List[str]]:
    """Validate password against security policy."""
    return validator.validate_password(password)

def get_password_strength(password: str) -> Dict[str, any]:
    """Get password strength analysis."""
    return validator.get_password_strength(password)

def hash_password(password: str, rounds: int = None) -> str:
    """Hash password securely."""
    return hasher.hash_password(password, rounds)

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return hasher.verify_password(password, hashed_password)

def generate_password(length: int = 16, **kwargs) -> str:
    """Generate secure password."""
    return generator.generate_password(length, **kwargs)

def generate_reset_token() -> str:
    """Generate password reset token."""
    return generator.generate_reset_token()
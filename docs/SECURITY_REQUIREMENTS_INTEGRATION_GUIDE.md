# Security Requirements Integration Guide

## 📅 Updated: September 29, 2025

## 🎯 **Overview**

Security requirements have been **fully integrated** into the main requirements structure. All security packages from `requirements-security.txt` are now included in the appropriate environment-specific requirements files.

## 🔐 **Security Packages Included**

### Core Security (Base Requirements)
All environments automatically include these security packages:

#### Authentication & Authorization
- **`bcrypt==4.1.2`** - Secure password hashing
- **`PyJWT==2.8.0`** - JWT token handling
- **`cryptography==41.0.8`** - Cryptographic functions
- **`passlib==1.7.4`** - Password utilities

#### Multi-Factor Authentication
- **`pyotp==2.9.0`** - TOTP (Time-based OTP) for MFA
- **`qrcode==7.4.2`** - QR code generation for MFA setup
- **`Pillow==10.1.0`** - Image processing for QR codes

#### Email Security
- **`aiosmtplib==3.0.1`** - Async SMTP client
- **`email-validator==2.1.0.post1`** - Email validation

#### Rate Limiting & Caching
- **`redis==5.0.1`** - Redis client for rate limiting
- **`hiredis==2.2.3`** - Fast Redis parser

#### Input Validation
- **`bleach==6.1.0`** - HTML sanitization
- **`python-multipart==0.0.6`** - Form data parsing

#### Monitoring & Logging
- **`structlog==23.2.0`** - Structured logging
- **`sentry-sdk==1.40.6`** - Error tracking and monitoring

#### Network Security
- **`httpx==0.25.2`** - HTTP client with security features
- **`certifi==2023.11.17`** - Certificate validation
- **`urllib3==2.1.0`** - HTTP library with security patches

### Production Security Tools
Production environments include additional security scanning:
- **`safety==2.3.5`** - Dependency vulnerability scanner
- **`bandit==1.7.5`** - Security linting for Python

### Development Security Tools
Development environments include security testing:
- **`pytest-security==0.1.0`** - Security testing for pytest
- **`faker==21.0.0`** - Updated version for security testing

## 📦 **Installation Instructions**

### Automatic Installation (Recommended)
Security requirements are now automatically installed with environment-specific files:

```bash
# Development (includes all security packages + dev tools)
pip install -r build/requirements/dev.txt

# UAT (includes all security packages + UAT-specific tools)
pip install -r build/requirements/uat.txt

# Production (includes all security packages + production tools)
pip install -r build/requirements/prod.txt
```

### Manual Security Package Installation (If Needed)
If you need only security packages:

```bash
# Core security packages
pip install bcrypt==4.1.2 PyJWT==2.8.0 cryptography==41.0.8 passlib==1.7.4

# MFA packages
pip install pyotp==2.9.0 qrcode==7.4.2 Pillow==10.1.0

# Email security
pip install aiosmtplib==3.0.1 email-validator==2.1.0.post1

# Rate limiting
pip install redis==5.0.1 hiredis==2.2.3

# Validation and monitoring
pip install bleach==6.1.0 python-multipart==0.0.6 structlog==23.2.0 sentry-sdk==1.40.6

# Network security
pip install httpx==0.25.2 certifi==2023.11.17 urllib3==2.1.0
```

## 🔧 **Usage Examples**

### Password Hashing with bcrypt
```python
from libs.security import get_password_manager

password_manager = get_password_manager()
hashed = password_manager.hash_password("user_password")
is_valid = password_manager.verify_password("user_password", hashed)
```

### JWT Token Handling
```python
from libs.security import get_jwt_manager

jwt_manager = get_jwt_manager()
token = jwt_manager.create_token({"user_id": 123}, expires_in=3600)
payload = jwt_manager.decode_token(token)
```

### Multi-Factor Authentication
```python
from libs.security.authentication import get_auth_service

auth_service = get_auth_service()
secret = auth_service.generate_mfa_secret()
qr_code = auth_service.generate_qr_code(secret, "user@example.com")
is_valid = auth_service.verify_totp_token(secret, "123456")
```

### Email Validation
```python
from email_validator import validate_email

try:
    validation = validate_email("user@example.com")
    email = validation.email
except EmailNotValidError:
    print("Invalid email")
```

### Rate Limiting with Redis
```python
from libs.security import get_rate_limiter

rate_limiter = get_rate_limiter()
is_allowed = rate_limiter.is_allowed("user_123", requests_per_minute=60)
```

## 🚀 **CI/CD Integration**

### Build Scripts
The security requirements are automatically included in all build processes:

```bash
# Dockerfile example
FROM python:3.11-slim
COPY build/requirements/prod.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
# Security packages automatically included
```

### Testing Pipeline
Security testing is now integrated into the testing pipeline:

```bash
# Run security tests
pytest tests/ --security

# Run security linting
bandit -r libs/ services/ -f json

# Check for vulnerabilities
safety check
```

## 📊 **Security Compliance**

### Vulnerability Scanning
Production deployments include automatic vulnerability scanning:
- **Safety** scans for known vulnerabilities in dependencies
- **Bandit** performs static security analysis of Python code
- **pytest-security** runs security-focused tests

### Security Headers
All web applications automatically include security headers:
- Content Security Policy (CSP)
- X-Frame-Options
- X-Content-Type-Options
- Strict-Transport-Security

### Audit Trail
Security events are automatically logged:
- Authentication attempts
- Authorization failures
- Rate limiting triggers
- Security scan results

## 🔍 **Migration from requirements-security.txt**

### What Changed
1. **Integrated packages** - All packages moved to main requirements files
2. **Environment-specific** - Security tools distributed appropriately
3. **Automatic installation** - No separate installation step needed
4. **Version consistency** - Locked versions for production stability

### Legacy File Status
- **`requirements-security.txt`** can now be safely removed
- All packages are included in main requirements structure
- No functionality is lost

### Verification
To verify security packages are installed:

```bash
# Check if security packages are available
python -c "import bcrypt, jwt, pyotp, qrcode; print('✅ Security packages installed')"

# Run security framework test
python -c "from libs.security import get_security_validator; print('✅ Security framework available')"
```

## 🎯 **Next Steps**

1. **Update deployment scripts** - Remove any references to requirements-security.txt
2. **Update documentation** - Security requirements are now in main requirements
3. **Test security features** - Verify all security functionality works
4. **Remove legacy file** - requirements-security.txt can be safely deleted

## 📞 **Support**

For questions about security requirements integration:
- Check the security framework documentation in `libs/security/`
- Review the updated requirements management guide
- Test security features using the provided examples
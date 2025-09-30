# Requirements Management Structure

# Requirements Management Structure

This document provides a comprehensive guide to the requirements management system used in this mono-repository project.

## 🔐 **SECURITY REQUIREMENTS INTEGRATION** ✨ **UPDATED**

**Security dependencies are now fully integrated into the main requirements structure.**

All security packages from `requirements-security.txt` have been incorporated into the appropriate environment files:
- **Core security packages** → `build/requirements/base.txt`
- **Production security tools** → `build/requirements/prod.txt`
- **Development security tools** → `build/requirements/dev.txt`

**Installation automatically includes security requirements when using environment-specific files.**

## 📁 Structure Overview

The project now uses environment-specific requirements files located in `build/requirements/`:

```
build/requirements/
├── base.txt     # Core dependencies for all environments
├── dev.txt      # Development environment (inherits base + dev tools)
├── uat.txt      # UAT environment (inherits base + testing tools)
└── prod.txt     # Production environment (inherits base + prod optimizations)
```

## 🔧 Installation Commands

### Development Environment
```bash
pip install -r build/requirements/dev.txt
```
**Includes:** All base dependencies + development tools (Jupyter, debugging, documentation)

### UAT Environment
```bash
pip install -r build/requirements/uat.txt
```
**Includes:** All base dependencies + testing tools (Locust, enhanced monitoring)

### Production Environment
```bash
pip install -r build/requirements/prod.txt
```
**Includes:** All base dependencies + production optimizations (Gunicorn, enhanced security)

## 📋 What Each Environment Contains

### Base Requirements (`base.txt`)
- **Web frameworks:** FastAPI, Flask, Uvicorn
- **Database:** SQLAlchemy, PostgreSQL, Snowflake drivers
- **Data processing:** Pandas, NumPy
- **Configuration:** Pydantic, Python-dotenv
- **Security:** ✨ **ENHANCED** - bcrypt, PyJWT, cryptography, passlib, pyotp, qrcode, Pillow, redis, structlog, sentry-sdk\n- **Email services:** aiosmtplib, email-validator\n- **Input validation:** bleach, python-multipart  \n- **Network security:** httpx, certifi, urllib3
- **Testing:** Pytest, basic testing tools
- **Code quality:** Black, Flake8, MyPy
- **Utilities:** Requests, Click
- **Orchestration:** Apache Airflow
- **Visualization:** Dash, Plotly
- **Kubernetes:** Basic K8s client

### Development Environment (`dev.txt`)
**Inherits base.txt plus:**
- **Jupyter ecosystem:** Jupyter, IPython, Notebook
- **Debugging tools:** IPDB, PDB++
- **Development server:** Watchdog for file monitoring
- **Enhanced testing:** Factory Boy, Faker (v21.0.0), HTTPX\n- **Security development:** pytest-security for security testing
- **Documentation:** Sphinx, RTD theme
- **AWS SDK:** Enabled for local development

### UAT Environment (`uat.txt`)
**Inherits base.txt plus:**
- **Load testing:** Locust for performance testing
- **Enhanced monitoring:** Prometheus client (specific version)
- **Enhanced database:** Snowflake with pandas support
- **Testing utilities:** HTTPX, Factory Boy, Faker
- **AWS SDK:** Enabled for cloud integration testing

### Production Environment (`prod.txt`)
**Inherits base.txt plus:**
- **Production server:** Gunicorn WSGI server
- **Optimized database:** Compiled psycopg2 (not binary)
- **Enhanced security:** All security packages from base.txt plus safety, bandit for vulnerability scanning
- **Production monitoring:** Prometheus client (locked version)
- **AWS SDK:** Enabled for production cloud operations

## 🚀 CI/CD Integration

The build system now automatically selects the appropriate requirements file based on the target environment:

```bash
# In CI/CD pipelines
if [[ "${ENVIRONMENT}" == "prod" ]]; then
  pip install -r build/requirements/prod.txt
elif [[ "${ENVIRONMENT}" == "uat" ]]; then
  pip install -r build/requirements/uat.txt
else
  pip install -r build/requirements/dev.txt
fi
```

## 📝 Migration from Root requirements.txt

The root `requirements.txt` file has been **removed** and its contents have been consolidated into the environment-specific files. All documentation and scripts have been updated to reference the new structure.

### Updated Documentation
- ✅ `DEPLOYMENT_GUIDE.md` - Now references `build/requirements/dev.txt`
- ✅ `UAT_DEPLOYMENT_GUIDE.md` - Now references `build/requirements/uat.txt`
- ✅ `PROD_DEPLOYMENT_GUIDE.md` - Now references `build/requirements/prod.txt`
- ✅ `docs/AWS_CREDENTIALS_SETUP.md` - Updated with environment-specific commands
- ✅ `docs/BAMBOO_BITBUCKET_CICD_CONFIGURATION.md` - Updated CI/CD scripts

## 🔒 Security Considerations

### Production Security
- **Locked versions:** Security-critical packages use specific versions in production
- **Compiled drivers:** Production uses compiled database drivers for performance
- **Minimal surface:** Production only includes necessary packages

### Development Flexibility
- **Latest compatible:** Development uses latest compatible versions for productivity
- **Full toolchain:** Includes all development and debugging tools
- **AWS enabled:** Local development has AWS SDK available

## 💡 Best Practices

1. **Always use environment-specific files** - Don't install dev.txt in production
2. **Test with UAT requirements** - UAT should mirror production dependency versions
3. **Keep base.txt minimal** - Only include dependencies needed across all environments
4. **Lock security versions** - Production security packages should have specific versions
5. **Document environment differences** - Keep this file updated when adding new dependencies

## 🚨 Important Notes

- **No more root requirements.txt** - The file has been removed
- **Inheritance structure** - All environment files inherit from base.txt
- **Environment isolation** - Each environment gets exactly what it needs
- **CI/CD ready** - Files are optimized for automated deployment pipelines

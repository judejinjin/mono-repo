# Parameter Store Configuration Management

This directory contains the refactored configuration system that uses AWS Systems Manager Parameter Store for environment-specific configuration management.

## 🔄 Migration from .env to Parameter Store

### Overview
The configuration system has been refactored to use AWS Parameter Store as the primary source of configuration, with config/.env files as fallback. This provides:

- **Centralized Configuration**: All environments managed in AWS Parameter Store
- **Security**: Sensitive values stored as SecureString parameters
- **Environment Isolation**: Clear separation between dev/uat/prod configurations
- **Runtime Updates**: Configuration can be updated without redeployment
- **Audit Trail**: All parameter changes are logged in CloudTrail

### Parameter Store Structure

Parameters follow the hierarchical naming convention:
```
/{environment}/{app_name}/{parameter_name}
```

#### Examples:
```
/dev/terraform/aws_account_id
/dev/fastapi/port
/dev/rds/password (SecureString)
/prod/security/jwt_secret_key (SecureString)
```

## 📁 Files

### Core Configuration
- **`__init__.py`**: Main configuration module with Parameter Store integration
- **`parameter_store_design.md`**: Design document and migration strategy
- **`base.yaml`**: Base configuration (fallback)
- **`{env}.yaml`**: Environment-specific YAML files (fallback)

### Parameter Store Utilities
- **`../libs/cloud/parameter_store.py`**: Parameter Store management utilities
- **`../scripts/setup_environment_config.py`**: Setup configuration during deployment
- **`../scripts/migrate_to_parameter_store.py`**: Migrate from config/.env to Parameter Store
- **`../scripts/validate_parameter_store.py`**: Validate Parameter Store configuration

## 🚀 Usage

### 1. Configuration Loading (Automatic)

The configuration system automatically loads from Parameter Store when `USE_PARAMETER_STORE=true`:

```python
from config import get_config, get_parameter_store_value

# Get configuration (Parameter Store + YAML fallback)
config = get_config()

# Get specific parameter from Parameter Store
port = get_parameter_store_value('fastapi', 'port', default='8000')
```

### 2. Migration from config/.env

```bash
# Migrate existing config/.env to Parameter Store
python scripts/migrate_to_parameter_store.py --environment=dev

# Dry run to see what would be migrated
python scripts/migrate_to_parameter_store.py --environment dev --dry-run

# Generate migration report
python scripts/migrate_to_parameter_store.py --environment dev --report migration_report.txt
```

### 3. Setup Environment Configuration

```bash
# Setup Parameter Store configuration for deployment
python scripts/setup_environment_config.py --environment dev

# Setup specific category only
python scripts/setup_environment_config.py --environment prod --category security

# Validate Parameter Store access
python scripts/setup_environment_config.py --environment uat --validate-only
```

### 4. Validation

```bash
# Validate Parameter Store configuration
python scripts/validate_parameter_store.py --environment dev

# Generate validation report
python scripts/validate_parameter_store.py --environment prod --output validation_report.txt

# JSON output for automation
python scripts/validate_parameter_store.py --environment dev --json
```

## 🔧 Configuration Priority

The system uses the following priority order:

1. **Parameter Store** (if `USE_PARAMETER_STORE=true`)
2. **Environment Variables** (for AWS credentials)
3. **YAML Configuration Files** (fallback)

## 🔒 Security Features

### Secure Parameter Types
- **SecureString**: Encrypted parameters for sensitive data
  - Passwords (`/dev/rds/password`)
  - API Keys (`/dev/security/jwt_secret_key`)
  - Encryption Keys (`/dev/security/encryption_key`)

### IAM Permissions Required
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ssm:GetParameter",
        "ssm:GetParameters",
        "ssm:GetParametersByPath",
        "ssm:PutParameter",
        "ssm:DeleteParameter",
        "ssm:DescribeParameters"
      ],
      "Resource": [
        "arn:aws:ssm:*:*:parameter/dev/*",
        "arn:aws:ssm:*:*:parameter/uat/*", 
        "arn:aws:ssm:*:*:parameter/prod/*"
      ]
    }
  ]
}
```

## 🎯 Environment Variables

### Control Parameter Store Usage
```bash
# Enable Parameter Store (default: true)
export USE_PARAMETER_STORE=true

# Set environment
export ENVIRONMENT=dev
export AWS_DEFAULT_REGION=us-east-1
```

### AWS Credentials (fallback)
```bash
# For development environments
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

## 📊 Parameter Categories

### Infrastructure Parameters
- **terraform**: AWS account, region, project name, VPC CIDR
- **eks**: Cluster name, node group sizes, Kubernetes version
- **rds**: Database name, username, password, instance class
- **ecr**: Registry URL, repository prefix
- **s3**: Bucket prefixes, Terraform state bucket

### Application Parameters
- **fastapi**: Port, debug mode, workers, host
- **web**: Port, debug mode, build environment
- **dash**: Port, debug mode, hot reload
- **airflow**: Webserver port, executor, namespace

### Security Parameters
- **security**: JWT secret key, encryption key (SecureString)
- **aws**: Access key, secret key (SecureString, dev only)

### Monitoring Parameters
- **monitoring**: CloudWatch log group, metrics namespace, log level

## 🔄 Integration with Deployment

### Automatic Setup During Deployment

The deployment system automatically populates Parameter Store:

```python
# In deploy/deploy.py
def deploy_infrastructure(self):
    # Setup Parameter Store configuration
    if not self._setup_environment_config():
        logger.warning("Parameter Store setup failed, continuing with deployment")
    
    # Continue with Terraform deployment
    # ...
```

### Manual Setup

```bash
# Setup configuration before deployment
python scripts/setup_environment_config.py --environment prod

# Deploy infrastructure
python deploy/deploy.py --environment prod --target infrastructure
```

## 🧪 Testing and Validation

### Pre-deployment Validation
```bash
# Validate Parameter Store access and structure
python scripts/validate_parameter_store.py --environment dev

# Check specific parameter values
python -c "
from libs.cloud.parameter_store import get_environment_config
config = get_environment_config('dev', 'fastapi')
print(config)
"
```

### Runtime Configuration Testing
```bash
# Test configuration loading
python -c "
from config import get_config
config = get_config()
print(f'FastAPI port: {config.get(\"fastapi\", {}).get(\"port\", \"default\")}')
"
```

## 📈 Migration Path

### Phase 1: Parallel Operation (Current)
- Parameter Store enabled with config/.env fallback
- Gradual migration of parameters
- Validation and testing

### Phase 2: Parameter Store Primary
- All parameters migrated to Parameter Store
- config/.env files used only for local development
- Production relies entirely on Parameter Store

### Phase 3: Complete Migration
- Remove config/.env dependency
- All configuration from Parameter Store
- Enhanced security and compliance

## 🔍 Troubleshooting

### Common Issues

#### Parameter Store Access Denied
```bash
# Check IAM permissions
aws sts get-caller-identity
aws ssm describe-parameters --path-prefix="/dev/"
```

#### Configuration Not Loading
```bash
# Check Parameter Store configuration
python scripts/validate_parameter_store.py --environment dev --access-only

# Force cache refresh
python -c "
from config import refresh_config_cache
refresh_config_cache()
"
```

#### Migration Issues
```bash
# Validate migration with dry run
python scripts/migrate_to_parameter_store.py --environment dev --dry-run

# Check for unmapped variables
python scripts/migrate_to_parameter_store.py --environment dev --validate
```

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Test Parameter Store connection
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from libs.cloud.parameter_store import ParameterStoreManager
manager = ParameterStoreManager()
print(manager.validate_parameter_access('dev'))
"
```

## 📋 Checklist for New Environments

### Setting up a New Environment

1. **Create Parameter Structure**
   ```bash
   python scripts/setup_environment_config.py --environment new_env
   ```

2. **Migrate Existing Configuration**
   ```bash
   python scripts/migrate_to_parameter_store.py --environment new_env
   ```

3. **Validate Configuration**
   ```bash
   python scripts/validate_parameter_store.py --environment new_env
   ```

4. **Test Application Loading**
   ```bash
   ENVIRONMENT=new_env python -c "from config import get_config; print(get_config())"
   ```

5. **Deploy Infrastructure**
   ```bash
   python deploy/deploy.py --environment new_env --target infrastructure
   ```

---

**Note**: This refactored configuration system maintains backward compatibility while providing enhanced security, centralized management, and environment isolation through AWS Parameter Store.
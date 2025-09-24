# AWS Parameter Store Configuration Management

## Current .env Structure Analysis

Based on the existing `.env` file, the following categories of configuration need to be migrated:

### Environment Variables Categories:
1. **AWS Credentials**: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION
2. **Terraform Variables**: TF_VAR_*, AWS_ACCOUNT_ID  
3. **Infrastructure**: EKS_CLUSTER_NAME, ECR_REGISTRY_URL, S3_BUCKET_PREFIX
4. **Database**: RDS_DB_NAME, RDS_USERNAME, RDS_PASSWORD
5. **Application**: FASTAPI_PORT, WEB_PORT, DASH_PORT, AIRFLOW_WEBSERVER_PORT
6. **Security**: JWT_SECRET_KEY, ENCRYPTION_KEY
7. **Monitoring**: CLOUDWATCH_LOG_GROUP, METRICS_NAMESPACE

## Parameter Store Naming Convention

### Hierarchical Structure: `/{environment}/{app_name}/{variable_name}`

### Examples:
```
# Infrastructure Parameters
/dev/terraform/aws_account_id
/dev/terraform/project_name
/dev/terraform/vpc_cidr

# EKS Configuration
/dev/eks/cluster_name
/dev/eks/node_group_min_size
/dev/eks/node_group_max_size

# Database Configuration
/dev/rds/db_name
/dev/rds/username
/dev/rds/password (SecureString)

# Application Configuration
/dev/fastapi/port
/dev/fastapi/debug
/dev/fastapi/workers

# Web Application
/dev/web/port
/dev/web/debug

# Dash Application
/dev/dash/port
/dev/dash/debug

# Airflow
/dev/airflow/webserver_port
/dev/airflow/executor
/dev/airflow/namespace

# Security (SecureString parameters)
/dev/security/jwt_secret_key
/dev/security/encryption_key

# Monitoring
/dev/monitoring/cloudwatch_log_group
/dev/monitoring/metrics_namespace

# ECR
/dev/ecr/registry_url
/dev/ecr/repository_prefix

# S3
/dev/s3/bucket_prefix
/dev/s3/terraform_state_bucket
```

### Parameter Types:
- **String**: Regular configuration values
- **SecureString**: Sensitive values (passwords, keys, secrets)
- **StringList**: Comma-separated values (when applicable)

### Environment Separation:
- `/dev/*` - Development environment
- `/uat/*` - UAT environment  
- `/prod/*` - Production environment

## Migration Strategy

### Phase 1: Create Parameter Store utilities
1. Create utilities for reading/writing parameters
2. Support for bulk operations
3. Environment-based parameter filtering

### Phase 2: Refactor configuration loading
1. Update `config/__init__.py` to use Parameter Store
2. Maintain backward compatibility with .env during transition
3. Cache parameters for performance

### Phase 3: Update deployment scripts
1. Modify deployment scripts to populate Parameter Store
2. Update build scripts to use Parameter Store values
3. Update Terraform to read from Parameter Store

### Phase 4: Migration and validation
1. Create migration script from .env to Parameter Store
2. Validate parameter access across all environments
3. Remove .env dependency

## Benefits

### Security
- Sensitive values stored as SecureString in Parameter Store
- AWS IAM-based access control
- Audit trail for parameter access
- No sensitive values in code or .env files

### Environment Management
- Clear separation between dev/uat/prod configurations
- Centralized configuration management
- Easy environment-specific deployments
- No need to manage multiple .env files

### Scalability
- Support for parameter hierarchies
- Bulk parameter operations
- Parameter versioning
- Integration with AWS services

### Operational
- Runtime configuration changes without redeployment
- Configuration drift detection
- Automated configuration validation
- Integration with CI/CD pipelines
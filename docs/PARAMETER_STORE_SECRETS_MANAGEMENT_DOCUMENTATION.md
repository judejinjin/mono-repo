# Parameter Store and Secrets Management Diagrams Documentation

Generated: 2025-09-25 13:52:15

## Overview

This document accompanies the visual diagrams created to illustrate the comprehensive secrets and configuration management architecture, including AWS Parameter Store, Secrets Manager integration, application workflows, and security compliance controls.

## Generated Diagrams

### 1. Parameter Store Hierarchy & Access Patterns (`parameter_store_hierarchy`)
**Purpose**: Complete parameter organization and retrieval patterns for configuration management

**Hierarchical Organization**:
- **Environment-based**: `/mono-repo/dev/`, `/mono-repo/uat/`, `/mono-repo/prod/`
- **Application Categories**: Database config, API keys, feature flags, service URLs
- **Parameter Types**: String, StringList, SecureString (KMS encrypted)

**Access Patterns**:
- **Startup**: Bulk parameter retrieval by path
- **Runtime**: Dynamic configuration updates
- **Security**: IAM policy-based access control

### 2. Secrets Manager Integration & Lifecycle (`secrets_manager_integration`)
**Purpose**: Automated secrets rotation and secure secrets management

**Secrets Categories**:
- **Database Secrets**: RDS master password, read replica credentials
- **Application Secrets**: API keys, JWT signing keys, encryption keys
- **Rotation Lifecycle**: Create → Test → Update → Finalize → Delete

**Integration Features**:
- **Automated Rotation**: 30-90 day intervals
- **Lambda Functions**: Custom rotation logic
- **Version Management**: Multiple active secret versions

### 3. Application Secrets Workflow & Retrieval (`application_secrets_workflow`)
**Purpose**: Runtime secrets management and application integration patterns

**Services Integration**:
- **Web App**: React frontend with environment configuration
- **Risk API**: FastAPI backend with database and API secrets
- **Dash Analytics**: Python dashboard with data source credentials
- **Airflow**: Workflow engine with service integrations

**Retrieval Workflow**:
- **Startup**: Load environment-specific configuration
- **Runtime**: Cached access with TTL
- **Rotation**: Automatic secret refresh

### 4. Security & Compliance Controls (`security_compliance_controls`)
**Purpose**: Comprehensive data protection and regulatory compliance

**Defense in Depth**:
1. **Data at Rest Encryption** (KMS)
2. **Data in Transit** (TLS 1.3)
3. **IAM Access Control** (RBAC)
4. **Application Security** (Authentication)

**Compliance Framework**:
- **SOC 2 Type II** compliance
- **ISO 27001** information security
- **GDPR** data protection
- **Custom** industry requirements

## Secrets Management Architecture

### Parameter Store Structure
```
/mono-repo/
├── dev/
│   ├── database/
│   │   ├── host              # String
│   │   ├── port              # String  
│   │   └── name              # String
│   ├── api/
│   │   ├── external-url      # String
│   │   └── rate-limit        # String
│   └── features/
│       ├── risk-analysis-v2  # String
│       └── dashboard-beta    # String
├── uat/
│   └── [same structure as dev]
└── prod/
    ├── database/
    │   ├── host              # String
    │   ├── port              # String
    │   ├── password          # SecureString (KMS)
    │   └── connection-string # SecureString (KMS)
    ├── api/
    │   ├── jwt-signing-key   # SecureString (KMS)
    │   └── external-api-key  # SecureString (KMS)
    └── services/
        ├── allowed-origins   # StringList
        └── notification-emails # StringList
```

### Secrets Manager Secrets
```
Database Secrets:
├── mono-repo/prod/rds/master-password
├── mono-repo/prod/rds/readonly-user
└── mono-repo/prod/rds/app-user

Application Secrets:
├── mono-repo/prod/api/jwt-signing-key
├── mono-repo/prod/api/external-service-key
└── mono-repo/prod/encryption/data-key

Service Secrets:
├── mono-repo/prod/airflow/fernet-key
├── mono-repo/prod/dash/session-key
└── mono-repo/prod/monitoring/api-key
```

## Security Implementation

### Encryption Strategy
```
KMS Key Management:
├── Customer Managed Keys (CMK)
│   ├── mono-repo-parameter-store-key
│   ├── mono-repo-secrets-manager-key
│   └── mono-repo-database-key
├── Automatic Key Rotation: Annual
├── Cross-Region Replication: Enabled
└── HSM Backing: FIPS 140-2 Level 3

SecureString Parameters:
├── Encryption: AES-256-GCM
├── Key Derivation: PBKDF2
└── Access Logging: CloudTrail
```

### Access Control Framework
```
IAM Policies:
├── ParameterStoreReadOnly
│   ├── GetParameter
│   ├── GetParameters
│   └── GetParametersByPath
├── SecretsManagerReadOnly
│   ├── GetSecretValue
│   ├── DescribeSecret
│   └── ListSecretVersionIds
└── SecretsManagerRotation
    ├── UpdateSecretVersionStage
    ├── PutSecretValue
    └── CreateNewVersion

Service Roles:
├── EKS Pod Identity (IRSA)
├── Lambda Execution Roles
├── EC2 Instance Profiles
└── Cross-Account Access
```

## Application Integration

### Secrets Retrieval Patterns
```python
# Parameter Store Access
import boto3

ssm = boto3.client('ssm')

# Get single parameter
response = ssm.get_parameter(
    Name='/mono-repo/prod/database/host'
)

# Get parameters by path
response = ssm.get_parameters_by_path(
    Path='/mono-repo/prod/',
    Recursive=True,
    WithDecryption=True
)

# Secrets Manager Access
secrets = boto3.client('secretsmanager')

# Get secret value
response = secrets.get_secret_value(
    SecretId='mono-repo/prod/rds/master-password'
)
```

### Caching Implementation
```python
# Local Cache with TTL
import time
from typing import Dict, Any, Optional

class SecretCache:
    def __init__(self, ttl: int = 900):  # 15 minutes
        self._cache: Dict[str, tuple] = {}
        self._ttl = ttl
    
    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp < self._ttl:
                return value
            del self._cache[key]
        return None
    
    def set(self, key: str, value: Any):
        self._cache[key] = (value, time.time())
```

## Monitoring & Compliance

### CloudTrail Events
```json
{
    "eventSource": "ssm.amazonaws.com",
    "eventName": "GetParameter",
    "sourceIPAddress": "10.0.101.45",
    "userIdentity": {
        "type": "AssumedRole",
        "principalId": "AROA...:risk-api-pod",
        "arn": "arn:aws:sts::123456789012:assumed-role/risk-api-role/risk-api-pod"
    },
    "requestParameters": {
        "name": "/mono-repo/prod/database/password",
        "withDecryption": true
    }
}
```

### CloudWatch Metrics
- **ParameterStore.GetParameter.Count**: API call volume
- **SecretsManager.GetSecretValue.Latency**: Retrieval performance
- **KMS.Decrypt.Count**: Decryption operations
- **Custom.SecretCacheHitRate**: Caching effectiveness

### Compliance Reporting
- **SOC 2**: Automated control testing
- **ISO 27001**: Security control validation
- **GDPR**: Data protection compliance
- **Audit Reports**: Quarterly compliance review

## Cost Optimization

### Pricing Structure
```
Parameter Store:
├── Standard Parameters: Free (up to 10,000)
├── Advanced Parameters: $0.05/parameter/month
└── API Calls: Free (standard tier)

Secrets Manager:
├── Secret Storage: $0.40/secret/month
├── API Calls: $0.05/10,000 requests
└── Rotation: No additional charge

Estimated Monthly Cost:
├── Parameter Store: $0 (using standard tier)
├── Secrets Manager: $6 (15 secrets × $0.40)
├── KMS: $1/key/month (3 keys = $3)
└── Total: ~$9/month
```

### Optimization Strategies
- **Consolidate Secrets**: JSON values in single secret
- **Cache Configuration**: Reduce API call frequency
- **Parameter Store First**: Use for non-sensitive config
- **Batch Retrieval**: GetParametersByPath for efficiency

## Operational Procedures

### Secret Rotation Process
```
1. Pre-rotation:
   ├── Validate rotation schedule
   ├── Check application health
   └── Prepare rollback plan

2. Rotation Execution:
   ├── Create new secret version
   ├── Test new credentials
   ├── Update application references
   └── Finalize rotation

3. Post-rotation:
   ├── Verify application functionality
   ├── Monitor error rates
   └── Clean up old versions
```

### Emergency Procedures
- **Credential Compromise**: Immediate rotation
- **Access Revocation**: IAM policy updates
- **Service Recovery**: Cached credential fallback
- **Incident Documentation**: Complete audit trail

## Troubleshooting Guide

### Common Issues
```
Issue: Access Denied
├── Check: IAM policy permissions
├── Check: Resource-based policies
├── Check: KMS key permissions
└── Verify: Service role assumption

Issue: Rotation Failures
├── Check: Lambda function logs
├── Check: Network connectivity
├── Check: Database permissions
└── Verify: Secret format

Issue: Performance Problems
├── Check: Cache hit rates
├── Check: API call patterns
├── Check: Network latency
└── Optimize: Batch retrieval
```

## File Structure
```
docs/architecture/
├── parameter_store_hierarchy.png               # Parameter organization
├── parameter_store_hierarchy.svg               # Vector format
├── secrets_manager_integration.png             # Secrets lifecycle
├── secrets_manager_integration.svg             # Vector format
├── application_secrets_workflow.png            # App integration
├── application_secrets_workflow.svg            # Vector format
├── security_compliance_controls.png            # Security framework
└── security_compliance_controls.svg            # Vector format
```

Created: September 25, 2025
Generated by: create_secrets_management_diagrams.py

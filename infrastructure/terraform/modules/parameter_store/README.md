# Parameter Store Terraform Module

This module manages AWS Systems Manager Parameter Store parameters with a hierarchical naming structure and appropriate security controls.

## Features

- **Hierarchical Parameter Structure**: Uses `/{environment}/{app_name}/{parameter_name}` naming convention
- **Security Classifications**: Supports both regular (String) and secure (SecureString) parameters
- **KMS Encryption**: Optional KMS key creation for SecureString parameter encryption
- **IAM Access Control**: Creates IAM roles and policies for parameter access
- **Cross-Account Access**: Supports cross-account parameter sharing
- **CloudWatch Logging**: Optional access logging for audit trails
- **Comprehensive Outputs**: Returns parameter names, ARNs, and access credentials

## Usage

### Basic Usage

```hcl
module "parameter_store" {
  source = "./modules/parameter_store"
  
  environment = "dev"
  app_name    = "mono-repo"
  
  regular_parameters = {
    "database/host"     = "db.dev.example.com"
    "database/port"     = "5432"
    "database/name"     = "mono_repo_dev"
    "api/base_url"      = "https://api.dev.example.com"
    "app/environment"   = "development"
  }
  
  secure_parameters = {
    "database/username" = "admin"
    "database/password" = "secure-password-123"
    "api/secret_key"    = "super-secret-api-key"
    "jwt/secret"        = "jwt-signing-secret"
  }
  
  create_access_role = true
  allow_write_access = false
}
```

### Advanced Usage with Custom KMS Key

```hcl
module "parameter_store" {
  source = "./modules/parameter_store"
  
  environment      = "prod"
  app_name         = "mono-repo"
  create_kms_key   = true
  allow_write_access = true
  
  regular_parameters = {
    # ... your regular parameters
  }
  
  secure_parameters = {
    # ... your secure parameters
  }
  
  assume_role_arns = [
    "arn:aws:iam::123456789012:role/AdminRole",
    "arn:aws:iam::123456789012:user/DeployUser"
  ]
  
  enable_access_logging = true
  log_retention_days    = 90
  
  common_tags = {
    Project     = "mono-repo"
    Environment = "prod"
    Team        = "platform"
    Owner       = "devops@company.com"
  }
}
```

## Requirements

| Name | Version |
|------|---------|
| terraform | >= 1.0 |
| aws | ~> 5.0 |

## Providers

| Name | Version |
|------|---------|
| aws | ~> 5.0 |

## Resources Created

- `aws_ssm_parameter` - Parameter Store parameters (String and SecureString)
- `aws_kms_key` - KMS key for parameter encryption (optional)
- `aws_kms_alias` - KMS key alias (optional)
- `aws_iam_role` - IAM role for parameter access (optional)
- `aws_iam_role_policy` - IAM policies for read/write access (optional)
- `aws_iam_instance_profile` - Instance profile for EC2 access (optional)
- `aws_cloudwatch_log_group` - CloudWatch log group for access logging (optional)

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| environment | Environment name (dev, uat, prod) | `string` | n/a | yes |
| app_name | Application name for parameter namespacing | `string` | `"mono-repo"` | no |
| regular_parameters | Map of regular (non-sensitive) parameters | `map(string)` | `{}` | no |
| secure_parameters | Map of secure (sensitive) parameters | `map(string)` | `{}` | no |
| create_kms_key | Whether to create a new KMS key | `bool` | `true` | no |
| kms_key_id | Existing KMS key ID to use | `string` | `null` | no |
| create_access_role | Whether to create IAM role for access | `bool` | `true` | no |
| allow_write_access | Whether to allow write access | `bool` | `false` | no |
| create_instance_profile | Whether to create instance profile | `bool` | `false` | no |
| assume_role_services | Services that can assume the role | `list(string)` | `["ec2.amazonaws.com", "ecs-tasks.amazonaws.com", "lambda.amazonaws.com"]` | no |
| assume_role_arns | ARNs that can assume the role | `list(string)` | `[]` | no |
| cross_account_access_arns | Cross-account ARNs for access | `list(string)` | `[]` | no |
| enable_access_logging | Whether to enable access logging | `bool` | `false` | no |
| log_retention_days | CloudWatch log retention days | `number` | `30` | no |
| common_tags | Common tags for all resources | `map(string)` | `{"Project": "mono-repo", "ManagedBy": "Terraform"}` | no |

## Outputs

| Name | Description |
|------|-------------|
| parameter_prefix | The prefix used for all parameters |
| parameters | Map of all created parameters with details |
| regular_parameter_names | List of regular parameter names |
| secure_parameter_names | List of secure parameter names |
| regular_parameter_arns | List of regular parameter ARNs |
| secure_parameter_arns | List of secure parameter ARNs |
| kms_key_id | KMS key ID for encryption |
| kms_key_arn | KMS key ARN |
| access_role_arn | IAM role ARN for access |
| access_role_name | IAM role name for access |
| instance_profile_arn | Instance profile ARN |
| instance_profile_name | Instance profile name |
| parameter_count | Summary of parameter counts |

## Parameter Naming Convention

All parameters follow the hierarchical structure:
```
/{environment}/{app_name}/{parameter_name}
```

Examples:
- `/dev/mono-repo/database/host`
- `/dev/mono-repo/database/password` (SecureString)
- `/prod/mono-repo/api/secret_key` (SecureString)

## Security Considerations

1. **SecureString Parameters**: Automatically encrypted using KMS
2. **IAM Policies**: Least privilege access with path-based restrictions
3. **KMS Permissions**: Scoped to SSM service usage only
4. **Cross-Account Access**: Optional and explicitly configured
5. **Access Logging**: Optional CloudWatch logging for audit trails

## Integration with Application

The created parameters can be accessed by applications using the AWS SDK or CLI:

```python
import boto3

ssm = boto3.client('ssm')

# Get a single parameter
response = ssm.get_parameter(
    Name='/dev/mono-repo/database/host',
    WithDecryption=True
)

# Get parameters by path
response = ssm.get_parameters_by_path(
    Path='/dev/mono-repo/',
    Recursive=True,
    WithDecryption=True
)
```
# Terraform Bootstrap - README

This directory contains the bootstrap Terraform configuration that creates the foundational infrastructure required for the main Terraform deployment.

## What This Creates

### Core State Management
- **S3 Bucket**: Encrypted bucket for Terraform remote state storage
- **DynamoDB Table**: Table for Terraform state locking to prevent concurrent modifications
- **ECR Repositories**: Container registries for application images (optional)

### Security Features
- Server-side encryption on S3 bucket
- Versioning enabled for state recovery
- Public access blocked on S3 bucket
- DynamoDB table with pay-per-request billing

## Prerequisites

1. **AWS Credentials**: Configure your AWS credentials (access key, secret key, region)
2. **Terraform Installed**: Ensure Terraform is installed and in your PATH
3. **Proper IAM Permissions**: Your AWS user needs permissions for S3, DynamoDB, and ECR

## Required AWS Permissions

Your AWS user/role needs these permissions:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:CreateBucket",
        "s3:DeleteBucket",
        "s3:GetBucketVersioning",
        "s3:PutBucketVersioning",
        "s3:GetBucketEncryption",
        "s3:PutBucketEncryption",
        "s3:GetBucketPublicAccessBlock",
        "s3:PutBucketPublicAccessBlock",
        "s3:ListBucket",
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:CreateTable",
        "dynamodb:DeleteTable",
        "dynamodb:DescribeTable",
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:DeleteItem"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ecr:CreateRepository",
        "ecr:DeleteRepository",
        "ecr:DescribeRepositories",
        "ecr:PutLifecyclePolicy",
        "ecr:PutImageScanningConfiguration"
      ],
      "Resource": "*"
    }
  ]
}
```

## Usage

### Step 1: Navigate to Bootstrap Directory
```bash
cd infrastructure/bootstrap
```

### Step 2: Initialize Terraform
```bash
terraform init
```

### Step 3: Plan the Deployment
```bash
terraform plan -var-file="dev.tfvars"
```

### Step 4: Apply the Configuration
```bash
terraform apply -var-file="dev.tfvars"
```

### Step 5: Note the Outputs
After successful deployment, Terraform will output:
- `terraform_state_bucket`: S3 bucket name for remote state
- `dynamodb_table_name`: DynamoDB table name for state locking
- `ecr_repository_urls`: URLs of created ECR repositories

## Important Outputs

The bootstrap creates these resources that you'll need for the main infrastructure:

```bash
# Example outputs (actual values will be different)
terraform_state_bucket = "mono-repo-test-terraform-state-a1b2c3d4"
dynamodb_table_name = "mono-repo-test-terraform-state-lock"
ecr_repository_urls = {
  "api-service" = "123456789012.dkr.ecr.us-east-1.amazonaws.com/mono-repo-test-api-service"
  "web-app" = "123456789012.dkr.ecr.us-east-1.amazonaws.com/mono-repo-test-web-app"
  # ... more repositories
}
```

## Next Steps

After bootstrap completion:

1. **Update Main Terraform Backend**: Copy the S3 bucket name and DynamoDB table name to update the backend configuration in `../terraform/main.tf`

2. **Update Environment Variables**: Add the ECR repository URLs to your `.env` file

3. **Deploy Main Infrastructure**: Run the main Terraform configuration in `../terraform/`

## Configuration Files

- `main.tf`: Core bootstrap resources
- `variables.tf`: Input variables and validation
- `dev.tfvars`: Development environment values
- `terraform.tfstate`: Local state file for bootstrap (keep this safe!)

## Cleanup

To destroy the bootstrap infrastructure (use with extreme caution):

```bash
terraform destroy -var-file="dev.tfvars"
```

⚠️ **Warning**: Destroying the bootstrap will delete your Terraform state bucket and may cause data loss for your main infrastructure state.

## Troubleshooting

### Common Issues

1. **Bucket Already Exists**: S3 bucket names are globally unique. The configuration uses a random suffix to avoid conflicts.

2. **Permission Denied**: Ensure your AWS credentials have the required permissions listed above.

3. **Region Mismatch**: Ensure your AWS credentials are configured for the same region specified in the variables.

### Validation

After deployment, verify resources were created:

```bash
# Check S3 bucket
aws s3 ls | grep terraform-state

# Check DynamoDB table  
aws dynamodb list-tables | grep terraform-state-lock

# Check ECR repositories
aws ecr describe-repositories
```

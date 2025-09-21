# AWS UAT Infrastructure Deployment Guide

This guide walks you through deploying the VPC infrastructure to your UAT environment.

## 🚀 Quick Start - UAT Environment

### Step 1: Install Dependencies ✅ COMPLETED
```bash
# Install UAT-specific requirements (includes testing and monitoring tools)
pip install -r build/requirements/uat.txt
```

### Step 2: Configure AWS Credentials for UAT
```bash
# Update .env file with UAT-specific values
TF_VAR_environment=uat
TF_VAR_project_name=mono-repo-uat
```

### Step 3: Deploy UAT Bootstrap Infrastructure
```bash
cd infrastructure/bootstrap
python deploy_bootstrap.py --environment=uat
```

### Step 4: Deploy UAT Main Infrastructure
```bash
cd ../terraform
terraform init
terraform plan -var-file="uat.tfvars"
terraform apply -var-file="uat.tfvars"
```

## 📋 UAT Environment Specifications

### ✅ **UAT-Specific Configuration**
- **Project Name**: `mono-repo-uat`
- **Environment**: `uat`
- **VPC CIDR**: `10.1.0.0/16` (defined in uat.tfvars)
- **Region**: `us-east-1`
- **Availability Zones**: 2 AZs for redundancy

### ✅ **Bootstrap Infrastructure for UAT**
The bootstrap will create:
- **S3 Bucket**: `mono-repo-uat-terraform-state-{random}` for remote state
- **DynamoDB Table**: `mono-repo-uat-terraform-state-lock` for state locking
- **ECR Repositories**: Container registries with `-uat` suffix

### ✅ **UAT Resource Naming Convention**
```bash
# S3 Bucket for Terraform State
mono-repo-uat-terraform-state-{random-id}
  ├── Versioning: Enabled
  ├── Encryption: AES256
  └── Public Access: Blocked

# DynamoDB Table for State Locking  
mono-repo-uat-terraform-state-lock
  └── Billing: Pay-per-request

# ECR Repositories (7 repositories)
├── mono-repo-uat-web-app
├── mono-repo-uat-api-service
├── mono-repo-uat-airflow-worker
├── mono-repo-uat-airflow-scheduler
├── mono-repo-uat-dash-app
├── mono-repo-uat-data-processor
└── mono-repo-uat-risk-calculator
```

## 🔧 UAT Environment Differences

### **Network Configuration**
- **VPC CIDR**: `10.1.0.0/16` (different from DEV: `10.0.0.0/16`)
- **Subnets**: Automatically calculated from VPC CIDR
- **Availability Zones**: 2 AZs for high availability testing

### **Scaling Configuration**
- **EKS Node Groups**: Moderate sizing for UAT workloads
- **RDS Instance**: Multi-AZ for availability testing
- **Load Balancers**: Internal ALB for corporate access

### **Security Configuration**
- **Enhanced monitoring**: CloudTrail and CloudWatch enabled
- **Backup policies**: Automated snapshots for data protection
- **Network ACLs**: More restrictive than DEV, less than PROD

## ⚠️ UAT Prerequisites

### AWS Account Requirements
Your UAT AWS account/region needs:

1. **UAT-specific IAM Permissions**
2. **Network Isolation**: Separate VPC from DEV/PROD
3. **Resource Limits**: Sufficient limits for UAT workloads

### Recommended IAM Policy for UAT
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:*",
        "eks:*",
        "ecr:*",
        "s3:*",
        "dynamodb:*",
        "iam:*",
        "route53:*",
        "elasticloadbalancing:*",
        "cloudwatch:*",
        "logs:*"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "aws:RequestedRegion": "us-east-1"
        }
      }
    }
  ]
}
```

## 🎯 UAT Deployment Steps

### 1. Update Environment Configuration
```bash
# Update .env file for UAT
cat >> .env << EOF

# UAT Environment Overrides
TF_VAR_environment=uat
TF_VAR_project_name=mono-repo-uat
TF_VAR_vpc_cidr=10.1.0.0/16

# UAT EKS Configuration
EKS_CLUSTER_NAME=mono-repo-uat-eks-uat

# UAT ECR Configuration
ECR_REGISTRY_URL=your_account_id.dkr.ecr.us-east-1.amazonaws.com
ECR_REPOSITORY_PREFIX=mono-repo-uat
EOF
```

### 2. Deploy UAT Bootstrap
```bash
cd infrastructure/bootstrap

# Plan UAT bootstrap
terraform plan -var-file="uat.tfvars" -out="uat.tfplan"

# Apply UAT bootstrap
terraform apply "uat.tfplan"

# Get outputs for main terraform configuration
terraform output -json > uat-outputs.json
```

### 3. Update Main Terraform Backend for UAT
```bash
# Update main terraform with UAT S3 backend
python update_main_backend.py --environment=uat

# Or manually update infrastructure/terraform/main.tf with UAT bucket name
```

### 4. Deploy UAT Main Infrastructure
```bash
cd ../terraform

# Initialize with UAT backend
terraform init

# Plan UAT infrastructure
terraform plan -var-file="uat.tfvars" -out="uat-main.tfplan"

# Apply UAT infrastructure
terraform apply "uat-main.tfplan"
```

## 🔍 UAT Verification Steps

### After Bootstrap
```bash
# Verify UAT S3 bucket exists
aws s3 ls | grep mono-repo-uat-terraform-state

# Verify UAT DynamoDB table exists  
aws dynamodb list-tables | grep mono-repo-uat-terraform-state-lock

# Verify UAT ECR repositories
aws ecr describe-repositories --region us-east-1 | grep mono-repo-uat
```

### After Main Infrastructure
```bash
# Check UAT VPC creation
aws ec2 describe-vpcs --filters "Name=tag:Project,Values=mono-repo-uat" "Name=tag:Environment,Values=uat"

# Check UAT EKS cluster
aws eks list-clusters --region us-east-1 | grep uat

# Check all UAT resources
aws resourcegroups search-resources --resource-query '{"Type":"TAG_FILTERS_1_0","Query":"{\"ResourceTypeFilters\":[\"AWS::AllSupported\"],\"TagFilters\":[{\"Key\":\"Project\",\"Values\":[\"mono-repo-uat\"]},{\"Key\":\"Environment\",\"Values\":[\"uat\"]}]}"}'
```

## 💰 UAT Cost Estimates

### Bootstrap Infrastructure
- **S3 Bucket**: ~$1-5/month (state storage)
- **DynamoDB**: ~$1/month (state locking)
- **ECR Repositories**: $0.10/GB/month (container images)

### Main Infrastructure
- **VPC**: Free (AWS VPC is free)
- **EKS Cluster**: ~$73/month (control plane)
- **EKS Node Groups**: ~$50-200/month (depending on instance types)
- **Load Balancers**: ~$25/month (ALB)
- **RDS Instance**: ~$15-100/month (depending on instance size)

**Total UAT Monthly Cost**: ~$165-405/month

## 🔥 UAT Troubleshooting

### Common UAT Issues

1. **CIDR Conflicts**
   - UAT uses `10.1.0.0/16` to avoid conflicts with DEV (`10.0.0.0/16`)
   - Ensure no overlapping networks with existing infrastructure

2. **Resource Naming Conflicts**
   - All UAT resources are prefixed with `mono-repo-uat`
   - S3 buckets include random suffix for global uniqueness

3. **Permission Issues**
   - UAT may require different IAM policies than DEV
   - Ensure cross-account access is properly configured if using separate AWS accounts

### UAT-Specific Considerations

1. **Data Seeding**: UAT often requires test data
2. **Integration Testing**: UAT is for integration and user acceptance testing
3. **Performance Testing**: UAT may need performance testing resources
4. **Monitoring**: Enhanced monitoring for test validation

## 🎉 UAT Success Indicators

You'll know UAT deployment is successful when:

- ✅ UAT bootstrap completes without errors
- ✅ UAT S3 bucket and DynamoDB table are created with `uat` naming
- ✅ UAT ECR repositories are visible with proper naming
- ✅ UAT main Terraform initializes with correct S3 backend
- ✅ UAT VPC is created with `10.1.0.0/16` CIDR
- ✅ UAT EKS cluster is accessible and ready for deployments
- ✅ UAT applications can be deployed and tested

## 📈 UAT Best Practices

1. **Environment Isolation**: Keep UAT completely separate from DEV/PROD
2. **Test Data Management**: Use anonymized production-like data
3. **Automated Testing**: Set up CI/CD pipelines for UAT deployments
4. **Monitoring**: Implement comprehensive monitoring for test validation
5. **Cost Control**: Monitor UAT costs and clean up unused resources
6. **Security Testing**: Use UAT for security testing and validation

UAT environment provides a production-like environment for comprehensive testing before production deployment!

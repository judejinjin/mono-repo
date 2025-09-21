# AWS DEV VPC Infrastructure Deployment Guide

This guide walks you through deploying the VPC infrastructure to your personal AWS account.

## 🚀 Quick Start

### Step 1: Install Dependencies ✅ COMPLETED
```bash
# For development environment (recommended for initial setup)
pip install -r build/requirements/dev.txt
```

### Step 2: Configure AWS Credentials (You'll do this)
```bash
python setup_aws_credentials.py
```

### Step 3: Deploy Bootstrap Infrastructure ✅ READY
```bash
cd infrastructure/bootstrap
python deploy_bootstrap.py
```

### Step 4: Deploy Main Infrastructure
```bash
cd ../terraform
terraform init
terraform plan -var-file="dev.tfvars"
terraform apply -var-file="dev.tfvars"
```

## 📋 What's Been Prepared

### ✅ **Dependencies Installed**
All required Python packages are now installed:
- `boto3` - AWS SDK for Python
- `python-dotenv` - Environment variable management
- `PyYAML` - Configuration file parsing
- `fastapi`, `pandas`, `kubernetes` - Application dependencies

### ✅ **Bootstrap Infrastructure Created**
Created in `infrastructure/bootstrap/`:
- **main.tf** - Creates S3 bucket and DynamoDB table for Terraform state
- **variables.tf** - Configuration variables
- **dev.tfvars** - Development environment settings
- **deploy_bootstrap.py** - Automated deployment script
- **update_main_backend.py** - Updates main Terraform backend
- **README.md** - Detailed documentation

### ✅ **Terraform State Management**
The bootstrap will create:
- **S3 Bucket**: `mono-repo-test-terraform-state-{random}` for remote state
- **DynamoDB Table**: `mono-repo-test-terraform-state-lock` for state locking
- **ECR Repositories**: Container registries for your applications

## 🔧 Bootstrap Infrastructure Details

### Resources Created
```bash
# S3 Bucket for Terraform State
mono-repo-test-terraform-state-{random-id}
  ├── Versioning: Enabled
  ├── Encryption: AES256
  └── Public Access: Blocked

# DynamoDB Table for State Locking  
mono-repo-test-terraform-state-lock
  └── Billing: Pay-per-request

# ECR Repositories (7 repositories)
├── mono-repo-test-web-app
├── mono-repo-test-api-service
├── mono-repo-test-airflow-worker
├── mono-repo-test-airflow-scheduler
├── mono-repo-test-dash-app
├── mono-repo-test-data-processor
└── mono-repo-test-risk-calculator
```

### Estimated Costs
- **S3 Bucket**: ~$1-5/month (depending on state file size)
- **DynamoDB**: ~$1/month (minimal usage for locking)
- **ECR Repositories**: $0.10/GB/month for stored images
- **Total Bootstrap Cost**: ~$2-10/month

## ⚠️ Prerequisites for Bootstrap Deployment

### AWS Account Requirements
Your personal AWS account needs:

1. **Valid AWS Credentials** (Access Key + Secret Key)
2. **Sufficient IAM Permissions**:
   - S3: CreateBucket, PutBucketVersioning, PutBucketEncryption
   - DynamoDB: CreateTable, DescribeTable
   - ECR: CreateRepository, DescribeRepositories

3. **Available Resources**:
   - S3 bucket limit not exceeded
   - DynamoDB table limit not exceeded
   - ECR repository limit not exceeded (default: 10,000)

### Recommended IAM Policy
Attach these AWS managed policies to your user:
- `AmazonS3FullAccess`
- `AmazonDynamoDBFullAccess` 
- `AmazonEC2ContainerRegistryFullAccess`

## 🎯 Next Steps After You Configure Credentials

### 1. Run Bootstrap Deployment
```bash
cd infrastructure/bootstrap
python deploy_bootstrap.py
```

This will:
- ✅ Check Terraform installation
- ✅ Verify AWS credentials  
- ✅ Create S3 bucket for state
- ✅ Create DynamoDB table for locking
- ✅ Create ECR repositories
- ✅ Output configuration for main Terraform

### 2. Update Main Terraform Backend
```bash
python update_main_backend.py
```

This automatically updates `../terraform/main.tf` with the correct S3 bucket name.

### 3. Deploy Main Infrastructure
```bash
cd ../terraform
terraform init
terraform plan -var-file="dev.tfvars" 
terraform apply -var-file="dev.tfvars"
```

## 🔍 Verification Steps

### After Bootstrap
```bash
# Verify S3 bucket exists
aws s3 ls | grep terraform-state

# Verify DynamoDB table exists  
aws dynamodb list-tables | grep terraform-state-lock

# Verify ECR repositories
aws ecr describe-repositories --region us-east-1
```

### After Main Infrastructure
```bash
# Check VPC creation
aws ec2 describe-vpcs --filters "Name=tag:Project,Values=mono-repo-test"

# Check EKS cluster (if created)  
aws eks list-clusters --region us-east-1

# Check all resources
aws resourcegroups search-resources --resource-query '{"Type":"TAG_FILTERS_1_0","Query":"{\"ResourceTypeFilters\":[\"AWS::AllSupported\"],\"TagFilters\":[{\"Key\":\"Project\",\"Values\":[\"mono-repo-test\"]}]}"}'
```

## 🔥 Troubleshooting

### Common Bootstrap Issues

1. **"Bucket already exists"**
   - S3 bucket names are globally unique
   - The bootstrap uses random suffixes to avoid conflicts
   - If it still fails, change `project_name` in `dev.tfvars`

2. **"Access Denied"**
   - Check your AWS credentials are valid
   - Verify IAM permissions for S3, DynamoDB, ECR
   - Ensure region matches your credentials

3. **"Terraform not found"**
   - Install Terraform from: https://www.terraform.io/downloads.html
   - Ensure it's in your system PATH

### Getting Help

If you encounter issues:

1. **Check Prerequisites**: Verify AWS credentials and permissions
2. **Review Logs**: Look at Terraform output for specific errors
3. **Validate Resources**: Use AWS CLI to check if resources were created
4. **Clean Up**: If needed, run `terraform destroy` in bootstrap directory

## 💡 Pro Tips

1. **Keep Bootstrap State Safe**: The `terraform.tfstate` file in bootstrap directory is critical
2. **Use Consistent Naming**: Keep `project_name` consistent across environments
3. **Monitor Costs**: Set up AWS billing alerts for your account
4. **Backup Strategy**: S3 versioning is enabled for state recovery

## 🎉 Success Indicators

You'll know everything is working when:

- ✅ Bootstrap completes without errors
- ✅ S3 bucket and DynamoDB table are created
- ✅ ECR repositories are visible in AWS Console
- ✅ Main Terraform initializes with S3 backend
- ✅ Main Terraform plan shows infrastructure to be created

The infrastructure is well-architected and ready for deployment once you provide your AWS credentials!

## 🗑️ Infrastructure Teardown

When you want to completely remove all infrastructure and clean up your AWS account, follow these steps **in reverse order**:

### ⚠️ **IMPORTANT: Data Loss Warning**
Tearing down infrastructure will **permanently delete**:
- All EKS clusters and applications
- VPC and networking components
- ECR container images
- S3 buckets and stored data
- DynamoDB tables and data
- **This action cannot be undone!**

### **Step 1: Destroy Main Infrastructure** 🏗️
```bash
cd infrastructure/terraform

# Review what will be destroyed
terraform plan -destroy -var-file="dev.tfvars"

# Destroy main infrastructure (VPC, EKS, etc.)
terraform destroy -var-file="dev.tfvars"
```

**Expected resources to be destroyed:**
- VPC and all networking (subnets, route tables, gateways)
- EKS cluster and node groups
- Load balancers (ALB/NLB)
- Security groups and NACLs
- IAM roles and policies (from main terraform)
- Route53 hosted zones (if created)

### **Step 2: Clean Up Container Images** 📦
Before destroying ECR repositories, optionally clean up images:
```bash
# List all ECR repositories
aws ecr describe-repositories --region us-east-1

# Delete all images in a repository (optional - they'll be deleted with repository)
aws ecr batch-delete-image \
    --repository-name mono-repo-test-web-app \
    --image-ids imageTag=latest \
    --region us-east-1

# Or delete all images in all repositories
for repo in $(aws ecr describe-repositories --query 'repositories[].repositoryName' --output text --region us-east-1); do
    aws ecr batch-delete-image \
        --repository-name $repo \
        --image-ids $(aws ecr list-images --repository-name $repo --query 'imageIds[].imageDigest' --output text --region us-east-1 | tr '\t' '\n' | sed 's/^/imageDigest=/') \
        --region us-east-1 2>/dev/null || echo "No images in $repo"
done
```

### **Step 3: Destroy Bootstrap Infrastructure** 🔧
```bash
cd infrastructure/bootstrap

# Review bootstrap resources that will be destroyed
terraform plan -destroy -var-file="dev.tfvars"

# Destroy bootstrap infrastructure
terraform destroy -var-file="dev.tfvars"
```

**Expected resources to be destroyed:**
- S3 bucket for Terraform state (including all state files)
- DynamoDB table for state locking
- ECR repositories (all 7 repositories)
- All stored container images

### **Step 4: Manual Cleanup (If Needed)** 🧹

Sometimes resources might remain due to dependencies or protection. Check and manually delete:

#### **Check for Remaining S3 Buckets:**
```bash
aws s3 ls | grep mono-repo
```

#### **Force Delete S3 Buckets (if needed):**
```bash
# List bucket contents
aws s3 ls s3://mono-repo-test-terraform-state-{random-id} --recursive

# Delete all objects first
aws s3 rm s3://mono-repo-test-terraform-state-{random-id} --recursive

# Delete bucket
aws s3 rb s3://mono-repo-test-terraform-state-{random-id}
```

#### **Check for Remaining ECR Repositories:**
```bash
aws ecr describe-repositories --region us-east-1 | grep mono-repo
```

#### **Check for Remaining DynamoDB Tables:**
```bash
aws dynamodb list-tables | grep mono-repo
```

#### **Check for Any Remaining Resources:**
```bash
# Search all resources with project tag
aws resourcegroups search-resources \
    --resource-query '{"Type":"TAG_FILTERS_1_0","Query":"{\"ResourceTypeFilters\":[\"AWS::AllSupported\"],\"TagFilters\":[{\"Key\":\"Project\",\"Values\":[\"mono-repo-test\"]}]}"}'
```

### **Step 5: Clean Up Local Files** 🗂️
Remove local Terraform state and cache files:
```bash
# Remove main Terraform state and cache
cd infrastructure/terraform
rm -rf .terraform/
rm -f .terraform.lock.hcl
rm -f terraform.tfstate*

# Remove bootstrap Terraform state and cache  
cd ../bootstrap
rm -rf .terraform/
rm -f .terraform.lock.hcl
rm -f terraform.tfstate*

# Optional: Reset main.tf backend to original hardcoded values
python update_main_backend.py --reset
```

## 🔄 **Teardown Automation Script**

For convenience, here's an automated teardown script:

```bash
#!/bin/bash
# infrastructure/teardown_all.sh

set -e

echo "🗑️ Starting complete infrastructure teardown..."
echo "⚠️  This will destroy ALL infrastructure and data!"
read -p "Are you sure? Type 'YES' to continue: " confirm

if [ "$confirm" != "YES" ]; then
    echo "❌ Teardown cancelled"
    exit 0
fi

echo "📍 Step 1: Destroying main infrastructure..."
cd infrastructure/terraform
terraform destroy -var-file="dev.tfvars" -auto-approve

echo "📍 Step 2: Destroying bootstrap infrastructure..."
cd ../bootstrap  
terraform destroy -var-file="dev.tfvars" -auto-approve

echo "📍 Step 3: Cleaning up local files..."
cd ../terraform
rm -rf .terraform/ .terraform.lock.hcl terraform.tfstate*
cd ../bootstrap
rm -rf .terraform/ .terraform.lock.hcl terraform.tfstate*

echo "✅ Teardown complete!"
echo "💡 Check AWS Console to verify all resources are deleted"
```

## 💰 **Cost Monitoring During Teardown**

### **Before Teardown - Check Current Costs:**
```bash
# Get current month's costs (requires AWS CLI with billing permissions)
aws ce get-cost-and-usage \
    --time-period Start=2025-09-01,End=2025-09-21 \
    --granularity MONTHLY \
    --metrics BlendedCost \
    --group-by Type=DIMENSION,Key=SERVICE

# Check resources that might incur costs
aws ec2 describe-instances --query 'Reservations[].Instances[?State.Name==`running`]'
aws elbv2 describe-load-balancers --query 'LoadBalancers[?State.Code==`active`]'
aws eks list-clusters
```

### **After Teardown - Verify No Ongoing Costs:**
```bash
# Wait 24 hours, then check for any remaining billable resources
aws support describe-cases --include-resolved-cases false
```

## ⚡ **Quick Teardown Checklist**

- [ ] **Backup Important Data**: Export any data you want to keep
- [ ] **Stop Applications**: Ensure no critical workloads are running
- [ ] **Check Dependencies**: Verify no other projects depend on this infrastructure
- [ ] **Run Main Destroy**: `cd infrastructure/terraform && terraform destroy`
- [ ] **Run Bootstrap Destroy**: `cd ../bootstrap && terraform destroy`
- [ ] **Manual Cleanup**: Check AWS Console for any remaining resources
- [ ] **Cost Verification**: Confirm no unexpected charges after 24-48 hours
- [ ] **Local Cleanup**: Remove `.terraform` directories and state files

## 🆘 **Teardown Troubleshooting**

### **Common Issues:**

1. **"Resource still has dependencies"**
   - Some resources may have dependencies that prevent deletion
   - Check for ENIs, security group rules, or load balancer targets
   - Manually delete blocking resources first

2. **"Access Denied during destroy"**  
   - Ensure your AWS credentials still have deletion permissions
   - Some resources require additional permissions to delete

3. **"S3 bucket not empty"**
   - Empty the bucket contents first: `aws s3 rm s3://bucket-name --recursive`
   - Then delete the bucket: `aws s3 rb s3://bucket-name`

4. **"State file corrupted"**
   - If Terraform state is corrupted, you may need to manually delete resources via AWS Console
   - Use the resource search query above to find all tagged resources

### **Emergency Manual Cleanup:**
If Terraform destroy fails completely, manually delete resources in this order:
1. EKS clusters and node groups
2. Load balancers and target groups  
3. EC2 instances and security groups
4. VPC and networking components
5. IAM roles and policies
6. S3 buckets (empty first)
7. DynamoDB tables
8. ECR repositories

Remember: **Always verify in AWS Console that resources are actually deleted** to avoid unexpected charges!

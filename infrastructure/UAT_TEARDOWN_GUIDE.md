# AWS UAT Infrastructure Teardown Guide

This guide walks you through safely tearing down the UAT VPC infrastructure.

## 🗑️ UAT Infrastructure Teardown

When you want to completely remove UAT infrastructure and clean up your AWS account, follow these steps **in reverse order**:

### ⚠️ **IMPORTANT: UAT Data Loss Warning**
Tearing down UAT infrastructure will **permanently delete**:
- All UAT EKS clusters and test applications
- UAT VPC and networking components
- UAT ECR container images and test data
- UAT S3 buckets and stored test results
- UAT DynamoDB tables and test data
- **This action cannot be undone!**

### **Step 1: Destroy UAT Main Infrastructure** 🏗️
```bash
cd infrastructure/terraform

# Review what will be destroyed in UAT
terraform plan -destroy -var-file="uat.tfvars"

# Destroy UAT main infrastructure
terraform destroy -var-file="uat.tfvars" -auto-approve
```

**Expected UAT resources to be destroyed:**
- UAT VPC (`10.1.0.0/16`) and all networking
- UAT EKS cluster: `mono-repo-uat-eks-uat`
- UAT Load balancers with `uat` tags
- UAT Security groups and NACLs
- UAT IAM roles and policies
- UAT Route53 hosted zones (if created)

### **Step 2: Clean Up UAT Container Images** 📦
```bash
# List UAT ECR repositories
aws ecr describe-repositories --region us-east-1 | grep mono-repo-uat

# Delete all images in UAT repositories
for repo in $(aws ecr describe-repositories --query 'repositories[?contains(repositoryName, `mono-repo-uat`)].repositoryName' --output text --region us-east-1); do
    echo "Cleaning repository: $repo"
    aws ecr batch-delete-image \
        --repository-name $repo \
        --image-ids $(aws ecr list-images --repository-name $repo --query 'imageIds[].imageDigest' --output text --region us-east-1 | tr '\t' '\n' | sed 's/^/imageDigest=/') \
        --region us-east-1 2>/dev/null || echo "No images in $repo"
done
```

### **Step 3: Destroy UAT Bootstrap Infrastructure** 🔧
```bash
cd infrastructure/bootstrap

# Review UAT bootstrap resources that will be destroyed
terraform plan -destroy -var-file="uat.tfvars"

# Destroy UAT bootstrap infrastructure
terraform destroy -var-file="uat.tfvars" -auto-approve
```

**Expected UAT bootstrap resources to be destroyed:**
- S3 bucket: `mono-repo-uat-terraform-state-{random}` (including all UAT state files)
- DynamoDB table: `mono-repo-uat-terraform-state-lock`
- UAT ECR repositories: All 7 repositories with `mono-repo-uat` prefix

### **Step 4: UAT Manual Cleanup (If Needed)** 🧹

#### **Check for Remaining UAT S3 Buckets:**
```bash
aws s3 ls | grep mono-repo-uat
```

#### **Force Delete UAT S3 Buckets:**
```bash
# Find UAT state bucket
UAT_BUCKET=$(aws s3 ls | grep mono-repo-uat-terraform-state | awk '{print $3}')

if [ ! -z "$UAT_BUCKET" ]; then
    echo "Found UAT bucket: $UAT_BUCKET"
    
    # List bucket contents
    aws s3 ls s3://$UAT_BUCKET --recursive
    
    # Delete all objects first
    aws s3 rm s3://$UAT_BUCKET --recursive
    
    # Delete bucket
    aws s3 rb s3://$UAT_BUCKET
    
    echo "UAT bucket $UAT_BUCKET deleted"
fi
```

#### **Check for Remaining UAT Resources:**
```bash
# Search UAT resources with environment tag
aws resourcegroups search-resources \
    --resource-query '{"Type":"TAG_FILTERS_1_0","Query":"{\"ResourceTypeFilters\":[\"AWS::AllSupported\"],\"TagFilters\":[{\"Key\":\"Project\",\"Values\":[\"mono-repo-uat\"]},{\"Key\":\"Environment\",\"Values\":[\"uat\"]}]}"}'

# Check UAT-specific resources
aws ec2 describe-vpcs --filters "Name=tag:Environment,Values=uat"
aws eks list-clusters | grep uat
aws dynamodb list-tables | grep uat
aws ecr describe-repositories --region us-east-1 | grep uat
```

### **Step 5: Clean Up UAT Local Files** 🗂️
```bash
# Remove UAT Terraform state and cache
cd infrastructure/terraform
rm -rf .terraform/
rm -f .terraform.lock.hcl
rm -f terraform.tfstate*
rm -f uat.tfplan
rm -f uat-main.tfplan

# Remove UAT bootstrap state and cache  
cd ../bootstrap
rm -rf .terraform/
rm -f .terraform.lock.hcl
rm -f terraform.tfstate*
rm -f uat.tfplan
rm -f uat-outputs.json
```

## 🔄 **UAT Teardown Automation Script**

Create an automated UAT teardown script:

```bash
#!/bin/bash
# infrastructure/teardown_uat.sh

set -e

echo "🗑️ Starting UAT infrastructure teardown..."
echo "⚠️  This will destroy ALL UAT infrastructure and test data!"
read -p "Are you sure? Type 'UAT-DESTROY' to continue: " confirm

if [ "$confirm" != "UAT-DESTROY" ]; then
    echo "❌ UAT teardown cancelled"
    exit 0
fi

echo "📍 Step 1: Destroying UAT main infrastructure..."
cd infrastructure/terraform
terraform destroy -var-file="uat.tfvars" -auto-approve

echo "📍 Step 2: Cleaning UAT container images..."
for repo in $(aws ecr describe-repositories --query 'repositories[?contains(repositoryName, `mono-repo-uat`)].repositoryName' --output text --region us-east-1); do
    echo "Cleaning UAT repository: $repo"
    aws ecr batch-delete-image \
        --repository-name $repo \
        --image-ids $(aws ecr list-images --repository-name $repo --query 'imageIds[].imageDigest' --output text --region us-east-1 | tr '\t' '\n' | sed 's/^/imageDigest=/') \
        --region us-east-1 2>/dev/null || echo "No images in $repo"
done

echo "📍 Step 3: Destroying UAT bootstrap infrastructure..."
cd ../bootstrap  
terraform destroy -var-file="uat.tfvars" -auto-approve

echo "📍 Step 4: Cleaning up UAT local files..."
cd ../terraform
rm -rf .terraform/ .terraform.lock.hcl terraform.tfstate* uat*.tfplan
cd ../bootstrap
rm -rf .terraform/ .terraform.lock.hcl terraform.tfstate* uat*.tfplan uat-outputs.json

echo "✅ UAT teardown complete!"
echo "💡 Check AWS Console to verify all UAT resources are deleted"
```

## 💰 **UAT Cost Verification After Teardown**

### **Verify No UAT Costs Remain:**
```bash
# Check for UAT resources that might incur costs
aws ec2 describe-instances --filters "Name=tag:Environment,Values=uat" --query 'Reservations[].Instances[?State.Name==`running`]'
aws elbv2 describe-load-balancers --query 'LoadBalancers[?contains(LoadBalancerName, `uat`) && State.Code==`active`]'
aws rds describe-db-instances --query 'DBInstances[?contains(DBInstanceIdentifier, `uat`)]'

# Wait 24 hours and check AWS billing for any remaining UAT charges
aws ce get-cost-and-usage \
    --time-period Start=2025-09-01,End=2025-09-21 \
    --granularity DAILY \
    --metrics BlendedCost \
    --group-by Type=DIMENSION,Key=SERVICE \
    --filter file://uat-cost-filter.json
```

## ⚡ **Quick UAT Teardown Checklist**

- [ ] **Backup UAT Test Results**: Export any important test data
- [ ] **Notify UAT Users**: Inform testing teams about planned teardown
- [ ] **Check UAT Dependencies**: Ensure no other environments depend on UAT
- [ ] **Run UAT Main Destroy**: `cd infrastructure/terraform && terraform destroy -var-file="uat.tfvars"`
- [ ] **Clean UAT Images**: Remove container images from UAT ECR repositories
- [ ] **Run UAT Bootstrap Destroy**: `cd ../bootstrap && terraform destroy -var-file="uat.tfvars"`
- [ ] **Manual UAT Cleanup**: Check AWS Console for remaining UAT resources
- [ ] **Cost Verification**: Confirm no UAT charges after 24-48 hours
- [ ] **Local UAT Cleanup**: Remove UAT `.terraform` directories and state files

## 🆘 **UAT Teardown Troubleshooting**

### **UAT-Specific Issues:**

1. **UAT EKS Cluster Dependencies**
   - UAT might have persistent volumes that prevent deletion
   - Check for UAT LoadBalancer services that create ELBs
   ```bash
   kubectl --context=mono-repo-uat-eks-uat get pv
   kubectl --context=mono-repo-uat-eks-uat get svc --all-namespaces -o wide
   ```

2. **UAT RDS Snapshots**
   - UAT RDS might have final snapshots enabled
   - Delete snapshots manually if needed
   ```bash
   aws rds describe-db-snapshots --query 'DBSnapshots[?contains(DBSnapshotIdentifier, `uat`)]'
   aws rds delete-db-snapshot --db-snapshot-identifier uat-final-snapshot
   ```

3. **UAT VPC Dependencies**
   - UAT VPC might have dependencies preventing deletion
   - Check for ENIs, NAT Gateways, VPC Endpoints
   ```bash
   aws ec2 describe-network-interfaces --filters "Name=vpc-id,Values=vpc-uat-xxxxx"
   aws ec2 describe-nat-gateways --filter "Name=vpc-id,Values=vpc-uat-xxxxx"
   aws ec2 describe-vpc-endpoints --filters "Name=vpc-id,Values=vpc-uat-xxxxx"
   ```

### **Emergency UAT Manual Cleanup:**
If Terraform destroy fails for UAT, manually delete in this order:
1. UAT EKS clusters and node groups
2. UAT Load balancers and target groups  
3. UAT RDS instances and snapshots
4. UAT EC2 instances and security groups
5. UAT VPC endpoints and NAT gateways
6. UAT VPC and networking components
7. UAT IAM roles and policies
8. UAT S3 buckets (empty first)
9. UAT DynamoDB tables
10. UAT ECR repositories

## 🔄 **UAT Environment Recreation**

After UAT teardown, to recreate UAT environment:

```bash
# Recreate UAT bootstrap
cd infrastructure/bootstrap
terraform apply -var-file="uat.tfvars"

# Update UAT backend configuration
python update_main_backend.py --environment=uat

# Recreate UAT main infrastructure
cd ../terraform
terraform init
terraform apply -var-file="uat.tfvars"
```

## 📋 **UAT Teardown Verification**

After teardown, verify UAT cleanup:

```bash
# Verify no UAT VPCs remain
aws ec2 describe-vpcs --filters "Name=tag:Environment,Values=uat" --query 'Vpcs[].VpcId'

# Verify no UAT EKS clusters remain
aws eks list-clusters --query 'clusters[?contains(@, `uat`)]'

# Verify no UAT S3 buckets remain
aws s3 ls | grep -i uat

# Verify no UAT DynamoDB tables remain
aws dynamodb list-tables --query 'TableNames[?contains(@, `uat`)]'

# Verify no UAT ECR repositories remain
aws ecr describe-repositories --query 'repositories[?contains(repositoryName, `uat`)].repositoryName'

# Final verification - no UAT resources with tags
aws resourcegroups search-resources \
    --resource-query '{"Type":"TAG_FILTERS_1_0","Query":"{\"ResourceTypeFilters\":[\"AWS::AllSupported\"],\"TagFilters\":[{\"Key\":\"Environment\",\"Values\":[\"uat\"]}]}"}'
```

✅ **UAT teardown is complete when all verification commands return empty results!**

Remember: UAT environments are typically recreated frequently for testing, so teardown and recreation should be a smooth, well-tested process.

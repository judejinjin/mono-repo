# Infrastructure Teardown and Cleanup Guide

## ⚠️ **IMPORTANT: READ BEFORE DESTROYING INFRASTRUCTURE**

This guide helps you safely tear down the entire AWS infrastructure to avoid ongoing charges after testing.

## 🛡️ **Safety Checklist**

Before running teardown scripts, ensure:

- [ ] **Backup any important data** from databases and S3 buckets
- [ ] **Export configurations** you want to keep
- [ ] **Document any custom changes** made during testing
- [ ] **Verify you're in the correct AWS account**
- [ ] **Check you're targeting the right environment** (dev/uat/prod)

## 🚨 **Pre-Teardown Data Backup**

### 1. Database Backup
```bash
# Export PostgreSQL data (if needed)
kubectl exec -it postgres-pod -- pg_dump -U postgres dbname > backup.sql

# Export Snowflake data (if needed)
# Use Snowflake web console or SnowSQL to export important data
```

### 2. S3 Data Backup
```bash
# Download important S3 data
aws s3 sync s3://your-bucket-name ./local-backup/
```

### 3. Configuration Backup
```bash
# Backup Kubernetes configurations
kubectl get all --all-namespaces -o yaml > k8s-backup.yaml

# Backup Terraform state (if needed)
cp terraform.tfstate terraform.tfstate.backup
```

## 🔥 **Teardown Methods**

### Option 1: Automated Teardown (Recommended)
```bash
# Windows
scripts\teardown-infrastructure.bat

# Linux/macOS
./scripts/teardown-infrastructure.sh

# Python (cross-platform)
python scripts/teardown_infrastructure.py
```

### Option 2: Manual Terraform Destroy
```bash
cd infrastructure/terraform

# Destroy specific environment
terraform destroy -var-file=dev.tfvars -auto-approve

# Or destroy all (be very careful!)
terraform destroy -auto-approve
```

### Option 3: Selective Teardown
```bash
# Destroy only non-persistent resources
terraform destroy -target=aws_eks_cluster.main -auto-approve
terraform destroy -target=aws_instance.dev_server -auto-approve

# Keep databases and S3 for later manual cleanup
```

## 🧹 **Complete Cleanup Process**

### 1. Application Layer
- Stop all running pods and services
- Remove Helm deployments
- Clean up persistent volumes

### 2. Kubernetes Layer
- Destroy EKS cluster
- Remove node groups
- Clean up security groups

### 3. Database Layer
- Destroy RDS instances
- Remove DB snapshots (optional)
- Clean up parameter groups

### 4. Storage Layer
- Empty S3 buckets
- Delete S3 buckets
- Remove EBS volumes

### 5. Network Layer
- Destroy load balancers
- Remove NAT gateways
- Delete VPC and subnets

### 6. Security Layer
- Remove IAM roles and policies
- Delete security groups
- Clean up access keys

## ⏱️ **Estimated Teardown Time**

- **Small environment (dev)**: 5-10 minutes
- **Medium environment (uat)**: 10-15 minutes
- **Large environment (prod)**: 15-30 minutes

## 💰 **Cost Verification**

After teardown, verify no charges are incurring:

1. **AWS Cost Explorer**: Check for ongoing charges
2. **AWS Billing Dashboard**: Review current month usage
3. **Resource Groups**: Ensure all tagged resources are deleted
4. **CloudWatch**: Check for remaining log groups (they cost money)

## 🔍 **Verification Commands**

```bash
# Verify no EC2 instances
aws ec2 describe-instances --query 'Reservations[].Instances[?State.Name!=`terminated`]'

# Verify no RDS instances
aws rds describe-db-instances

# Verify no EKS clusters
aws eks list-clusters

# Verify no load balancers
aws elbv2 describe-load-balancers

# Verify no NAT gateways
aws ec2 describe-nat-gateways --filter Name=state,Values=available

# Check S3 buckets
aws s3 ls
```

## 🚨 **Emergency Stop**

If you need to immediately stop all compute resources:

```bash
# Stop all EC2 instances (doesn't delete, just stops)
aws ec2 stop-instances --instance-ids $(aws ec2 describe-instances --query 'Reservations[].Instances[?State.Name==`running`].InstanceId' --output text)

# Delete EKS cluster immediately
aws eks delete-cluster --name mono-repo-cluster
```

## 📋 **Teardown Checklist**

- [ ] Data backed up
- [ ] Correct AWS account verified
- [ ] Environment specified (dev/uat/prod)
- [ ] Teardown script executed
- [ ] Resources verified as deleted
- [ ] AWS billing checked
- [ ] No unexpected charges
- [ ] Terraform state cleaned up

## 🔄 **Re-deployment**

To redeploy after teardown:

```bash
# Re-initialize Terraform
cd infrastructure/terraform
terraform init

# Deploy fresh environment
terraform plan -var-file=dev.tfvars
terraform apply -var-file=dev.tfvars -auto-approve
```

## 📞 **Support**

If teardown fails or you see unexpected charges:

1. Check AWS CloudTrail for failed deletions
2. Review AWS Support center
3. Use AWS Cost Anomaly Detection
4. Contact AWS support if needed

## ⚡ **Quick Reference**

| Action | Command |
|--------|---------|
| Full teardown | `scripts/teardown-infrastructure.sh` |
| Verify deletion | `aws ec2 describe-instances` |
| Check costs | AWS Billing Dashboard |
| Emergency stop | `aws ec2 stop-instances --instance-ids $(...)` |
| Re-deploy | `terraform apply -var-file=dev.tfvars` |

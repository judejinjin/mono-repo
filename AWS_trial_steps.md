# AWS Free Trial Deployment Steps - GenAI Mono-Repo

## Overview

This guide provides step-by-step instructions to deploy the GenAI mono-repo infrastructure in your AWS Free Trial account. The deployment creates a complete development environment with FastAPI services, React web applications, Dash analytics dashboards, Airflow data pipelines, and supporting infrastructure.

## ⚠️ Important Free Trial Considerations

### AWS Free Trial Limits
- **EC2**: 750 hours per month of t2.micro instances (12 months)
- **RDS**: 750 hours per month of t2.micro database instances (12 months)
- **S3**: 5 GB of standard storage (12 months)
- **CloudWatch**: 10 custom metrics and 10 alarms (always free)
- **NAT Gateway**: **NOT FREE** - Will incur charges (~$45/month)

### Cost Optimization for Free Trial
This deployment has been configured to stay within free tier limits:
- Uses t3.micro instances instead of larger sizes
- Minimal RDS storage allocation
- Disabled VPC Flow Logs to reduce CloudWatch costs
- Limited EKS node capacity

**Expected Monthly Costs**: $5-15 (mostly NAT Gateway and minimal EKS charges)

## 🚀 Prerequisites

### 1. AWS Account Setup
1. **Create AWS Free Trial Account**: [aws.amazon.com/free](https://aws.amazon.com/free)
2. **Verify Email and Phone Number**
3. **Add Payment Method** (required even for free tier)
4. **Wait for Account Activation** (usually 10-15 minutes)

### 2. Create IAM User (Security Best Practice)
Instead of using root credentials:

1. **Sign in to AWS Console** with root account
2. **Navigate to IAM Service**
3. **Create New User**:
   - Username: `mono-repo-admin`
   - Access type: ✅ Programmatic access
   - Attach policies: 
     - `AdministratorAccess` (for initial setup)
     - `IAMFullAccess`
4. **Download Credentials CSV** - Save the Access Key ID and Secret Access Key

### 3. Local Development Environment Setup

#### Required Software Installation:

**Windows/Linux/macOS**:
```bash
# Install Python 3.11+ (if not installed)
# Download from: https://www.python.org/downloads/

# Install Terraform
# Download from: https://www.terraform.io/downloads
# Add to system PATH

# Install AWS CLI
# Download from: https://aws.amazon.com/cli/
```

**Verification**:
```bash
python --version        # Should be 3.11+
terraform --version     # Should be 1.0+
aws --version          # Should be 2.x
```

### 4. Clone and Setup Repository

```bash
# Clone the repository
git clone <your-repo-url>
cd mono-repo

# Install Python dependencies
pip install -r build/requirements/dev.txt

# Alternative: Use virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r build/requirements/dev.txt
```

## 🔧 Step-by-Step Deployment

### Step 1: Configure AWS Credentials

Run the interactive AWS credentials setup:

```bash
python setup_aws_credentials.py
```

**When prompted, enter**:
- **AWS Access Key ID**: Your IAM user access key
- **AWS Secret Access Key**: Your IAM user secret key  
- **AWS Region**: `us-east-1` (recommended for free tier)
- **AWS Session Token**: Leave blank (press Enter)

**Verification**:
```bash
# Test AWS connectivity
aws sts get-caller-identity
```

You should see your account ID and user ARN.

### Step 2: Review and Customize Configuration

**Important**: Review the development configuration to ensure it fits your needs:

```bash
# Review development configuration
cat infrastructure/terraform/dev.tfvars
```

**🆓 Free Trial Optimization Enabled**:

This infrastructure includes a `free_trial = true` flag in dev.tfvars that automatically configures AWS Free Tier eligible resources:

- `eks_node_instance_types = ["t3.micro"]` - Free tier eligible
- `rds_instance_class = "db.t3.micro"` - Free tier eligible  
- `rds_allocated_storage = 20` - Within free tier limit (20GB)
- `dev_server_instance_type = "t3.micro"` - Free tier eligible
- Single AZ deployment to minimize costs
- Monitoring disabled to reduce CloudWatch charges

**Key Free Tier Benefits**:
- **No charges** for first 12 months on eligible resources
- **750 hours/month** of t3.micro EC2 instances
- **20GB** of RDS storage and backup
- **Limited CloudWatch** to stay within free tier

**Optional Customization**:
```bash
# Edit if you want to change project name or region
nano infrastructure/terraform/dev.tfvars

# Key variables you might want to change:
# - project_name = "mono-repo-test"  # Change if you prefer different name
# - aws_region = "us-east-1"         # Change if you prefer different region
```

### Step 3: Deploy Bootstrap Infrastructure

The bootstrap creates S3 bucket for Terraform state and ECR repositories:

```bash
cd infrastructure/bootstrap

# Run automated bootstrap deployment
python deploy_bootstrap.py
```

**Expected Output**:
```
🔧 Terraform Bootstrap Deployment
==================================================

🔍 Pre-flight checks...
✅ Terraform found: v1.6.0
✅ AWS credentials found for region: us-east-1
✅ All pre-flight checks passed!

📦 Initializing Terraform...
✅ Terraform initialized successfully

📋 Planning infrastructure changes...
✅ Terraform planning completed

🚀 Applying Terraform configuration...
✅ Bootstrap infrastructure created successfully!

📄 Important Outputs:
S3 Bucket: mono-repo-test-terraform-state-abc123
DynamoDB Table: mono-repo-test-terraform-locks
ECR Repositories: 7 repositories created
```

**If deployment fails**, see [Troubleshooting](#troubleshooting) section.

### Step 4: Update Main Terraform Backend

Configure main Terraform to use the S3 backend created in bootstrap:

```bash
# Update backend configuration automatically
python update_main_backend.py
```

**Verification**:
```bash
# Check that main.tf was updated with correct S3 bucket
grep -A 5 'backend "s3"' ../terraform/main.tf
```

### Step 5: Deploy Main Infrastructure

Deploy the complete infrastructure including VPC, EKS, RDS, and applications:

```bash
cd ../terraform

# Initialize Terraform with S3 backend
terraform init

# 🆓 FREE TRIAL OPTIMIZATION
# The dev.tfvars is already configured with free_trial=true for AWS Free Tier compliance
# This automatically uses:
# - t3.micro instances for EKS nodes and dev server
# - db.t3.micro for RDS (free tier eligible)
# - Minimal storage sizes (20GB)
# - Single AZ deployment
# - Disabled monitoring to reduce CloudWatch costs

# Review planned infrastructure changes
terraform plan -var-file="dev.tfvars"
```

**Review the plan carefully**. You should see:
- ✅ VPC with subnets and routing
- ✅ EKS cluster with node groups  
- ✅ RDS PostgreSQL instance (t3.micro)
- ✅ Security groups and load balancers
- ✅ Development server (optional)

```bash
# Apply infrastructure (this takes 15-30 minutes)
terraform apply -var-file="dev.tfvars"
```

**Expected Timeline**:
- **Minutes 0-5**: VPC and networking components
- **Minutes 5-20**: EKS cluster creation (longest step)
- **Minutes 20-25**: RDS database and other services
- **Minutes 25-30**: Final configuration and outputs

### Step 6: Configure kubectl and Verify Deployment

Connect to your EKS cluster and verify deployment:

```bash
# Configure kubectl to connect to your EKS cluster
aws eks update-kubeconfig --region us-east-1 --name mono-repo-test-eks-dev

# Verify cluster connection
kubectl get nodes
kubectl get namespaces
```

**Expected Output**:
```
NAME                         STATUS   ROLES    AGE   VERSION
ip-10-0-1-100.ec2.internal   Ready    <none>   5m    v1.28.x
ip-10-0-2-101.ec2.internal   Ready    <none>   5m    v1.28.x
```

### Step 7: Deploy Applications to Kubernetes

Deploy the FastAPI, Web, and Dash applications:

```bash
# Navigate to deployment directory
cd ../../deploy

# Deploy applications
python deploy.py --target applications --environment dev
```

**Verification**:
```bash
# Check application deployments
kubectl get deployments -n mono-repo-dev
kubectl get services -n mono-repo-dev
kubectl get pods -n mono-repo-dev
```

### Step 8: Access Your Applications

Get the URLs for your deployed applications:

```bash
# Get load balancer URLs
kubectl get ingress -n mono-repo-dev
kubectl get svc -n mono-repo-dev --field-selector spec.type=LoadBalancer
```

**Access Applications**:
- **FastAPI Service**: `http://<alb-url>/api/docs` - API documentation
- **Web Dashboard**: `http://<alb-url>/` - React application  
- **Dash Analytics**: `http://<alb-url>/dash/` - Analytics dashboard
- **Airflow**: `http://<alb-url>/airflow/` - Data pipeline UI

## 🔍 Verification Checklist

### Infrastructure Verification
- [ ] **S3 Bucket Created**: Check AWS Console → S3
- [ ] **ECR Repositories**: Check AWS Console → ECR (7 repositories)
- [ ] **VPC Created**: Check AWS Console → VPC
- [ ] **EKS Cluster Running**: Check AWS Console → EKS
- [ ] **RDS Database**: Check AWS Console → RDS
- [ ] **Load Balancer**: Check AWS Console → EC2 → Load Balancers

### Application Verification
- [ ] **Kubernetes Pods Running**: `kubectl get pods -n mono-repo-dev`
- [ ] **Services Accessible**: `kubectl get svc -n mono-repo-dev`
- [ ] **FastAPI Health Check**: `curl http://<api-url>/health`
- [ ] **Web Application Loads**: Open web browser to ALB URL
- [ ] **Dash Dashboard Loads**: Open `http://<alb-url>/dash/`

### Cost Monitoring
- [ ] **AWS Billing Dashboard**: Monitor daily costs
- [ ] **Set Billing Alerts**: Create alerts for $10, $20, $50
- [ ] **Resource Usage**: Monitor EC2, RDS, and data transfer

## 💰 Cost Management for Free Trial

### Monitor Your Costs Daily

1. **AWS Billing Dashboard**:
   - Go to AWS Console → Billing → Bills
   - Check daily usage and costs
   - Set up billing alerts

2. **Create Cost Alerts**:
```bash
# Create billing alert for $10
aws budgets create-budget --account-id <your-account-id> --budget file://billing-alert.json
```

### Stop/Start Infrastructure to Save Costs

**Stop Everything** (when not in use):
```bash
# Stop EKS node groups
aws eks update-nodegroup-config --cluster-name mono-repo-test-eks-dev --nodegroup-name <nodegroup-name> --scaling-config minSize=0,maxSize=0,desiredSize=0

# Stop RDS instance  
aws rds stop-db-instance --db-instance-identifier mono-repo-test-dev-db
```

**Restart When Needed**:
```bash
# Restart RDS instance
aws rds start-db-instance --db-instance-identifier mono-repo-test-dev-db

# Scale up node groups
aws eks update-nodegroup-config --cluster-name mono-repo-test-eks-dev --nodegroup-name <nodegroup-name> --scaling-config minSize=1,maxSize=3,desiredSize=2
```

## 🔥 Troubleshooting

### Common Bootstrap Issues

**1. "Access Denied" Errors**:
```bash
# Check IAM permissions
aws iam get-user
aws sts get-caller-identity

# Verify IAM policies attached
aws iam list-attached-user-policies --user-name mono-repo-admin
```

**2. "Bucket Already Exists"**:
```bash
# Change project name in bootstrap/dev.tfvars
nano infrastructure/bootstrap/dev.tfvars
# Change: project_name = "mono-repo-test-2"  # Make it unique
```

**3. "Terraform Not Found"**:
```bash
# Install Terraform (Ubuntu/Debian)
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform
```

### Common Infrastructure Issues

**1. EKS Cluster Creation Fails**:
- **Cause**: Insufficient permissions or region limits
- **Solution**: Check IAM permissions, try different region

**2. "Instance Limit Exceeded"**:
- **Cause**: Free tier instance limits reached
- **Solution**: Request limit increase or use smaller instances

**3. RDS Creation Fails**:
- **Cause**: Free tier database limit exceeded  
- **Solution**: Delete unused databases or use different instance class

### Application Deployment Issues

**1. Pods Not Starting**:
```bash
# Check pod status and logs
kubectl describe pod <pod-name> -n mono-repo-dev
kubectl logs <pod-name> -n mono-repo-dev
```

**2. Load Balancer Not Accessible**:
```bash
# Check security groups
aws ec2 describe-security-groups --group-names default
```

### Getting Help

**1. Check AWS Service Health**:
- AWS Service Health Dashboard: [status.aws.amazon.com](https://status.aws.amazon.com)

**2. AWS Support** (Free tier includes basic support):
- AWS Console → Support → Create Case

**3. Community Resources**:
- AWS Reddit: [r/aws](https://reddit.com/r/aws)
- Stack Overflow: Tag `amazon-web-services`

## 🗑️ Complete Cleanup (When Done)

### Quick Cleanup Script

```bash
#!/bin/bash
# cleanup_aws.sh - Complete infrastructure teardown

echo "🧹 Starting complete AWS infrastructure cleanup..."

# Navigate to terraform directory  
cd infrastructure/terraform

# Destroy main infrastructure
echo "Destroying main infrastructure..."
terraform destroy -var-file="dev.tfvars" -auto-approve

# Navigate to bootstrap directory
cd ../bootstrap

# Destroy bootstrap infrastructure  
echo "Destroying bootstrap infrastructure..."
terraform destroy -var-file="dev.tfvars" -auto-approve

echo "✅ Infrastructure cleanup complete!"
echo "⚠️  Verify in AWS Console that all resources are deleted"
```

### Manual Cleanup Steps

If automated cleanup fails:

1. **Delete EKS Cluster**:
   ```bash
   aws eks delete-cluster --name mono-repo-test-eks-dev
   ```

2. **Delete RDS Instances**:
   ```bash
   aws rds delete-db-instance --db-instance-identifier mono-repo-test-dev-db --skip-final-snapshot
   ```

3. **Delete Load Balancers**:
   - AWS Console → EC2 → Load Balancers → Delete

4. **Delete VPC** (after other resources):
   - AWS Console → VPC → Delete VPC

5. **Empty and Delete S3 Buckets**:
   ```bash
   aws s3 rm s3://mono-repo-test-terraform-state-abc123 --recursive
   aws s3 rb s3://mono-repo-test-terraform-state-abc123
   ```

6. **Delete ECR Repositories**:
   ```bash
   aws ecr delete-repository --repository-name mono-repo-test/web-app --force
   # Repeat for all repositories
   ```

### Cost Verification After Cleanup

**Important**: After cleanup, verify no charges are accumulating:

1. **Check AWS Billing** daily for 3-5 days
2. **Look for unexpected charges** (especially data transfer, NAT Gateway)
3. **Contact AWS Support** if unexpected charges appear

## 📋 Summary Checklist

### Pre-Deployment
- [ ] AWS Free Trial account created and activated
- [ ] IAM user created with AdministratorAccess
- [ ] Local development environment set up (Python, Terraform, AWS CLI)
- [ ] Repository cloned and dependencies installed
- [ ] AWS credentials configured via `setup_aws_credentials.py`

### Deployment Steps
- [ ] Bootstrap infrastructure deployed (`deploy_bootstrap.py`)
- [ ] Main Terraform backend updated (`update_main_backend.py`)
- [ ] Main infrastructure deployed (`terraform apply`)
- [ ] kubectl configured for EKS cluster
- [ ] Applications deployed to Kubernetes

### Verification
- [ ] All AWS resources created and accessible
- [ ] Applications responding to health checks
- [ ] Load balancer URLs working
- [ ] Billing alerts configured
- [ ] Daily cost monitoring set up

### Post-Deployment
- [ ] Applications tested and working
- [ ] Monitoring and alerting configured
- [ ] Backup strategy implemented (optional)
- [ ] Documentation updated with your specific URLs/endpoints

## 🎉 Success Metrics

You'll know everything is working correctly when:

- ✅ **Infrastructure**: All Terraform applies complete without errors
- ✅ **Connectivity**: `kubectl get nodes` shows healthy nodes  
- ✅ **Applications**: All pods are Running status
- ✅ **URLs**: FastAPI `/docs`, Web dashboard, and Dash analytics all load
- ✅ **Costs**: Daily AWS costs remain under $1-2 per day
- ✅ **Monitoring**: CloudWatch shows metrics for all services

## 🚀 Next Steps

After successful deployment:

1. **Explore the Applications**:
   - Test the FastAPI endpoints at `/docs`
   - Create sample portfolios and risk calculations
   - View analytics in the Dash dashboard

2. **Development Workflow**:
   - Make code changes locally
   - Build and deploy using `deploy.py`
   - Monitor applications with Kubernetes tools

3. **Scale and Enhance**:
   - Add new services to the mono-repo
   - Implement CI/CD pipelines
   - Add monitoring and alerting

4. **Production Readiness** (later):
   - Review security configurations
   - Implement proper secret management
   - Set up production environments

---

## 📞 Support and Resources

**Repository Documentation**:
- `infrastructure/DEPLOYMENT_GUIDE.md` - Detailed infrastructure guide
- `devops/port_management.md` - Service port configurations
- `docs/` - Application-specific documentation

**AWS Resources**:
- [AWS Free Tier Guide](https://aws.amazon.com/free/)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)

**Emergency Contacts**:
- AWS Support (Basic): Available through AWS Console
- Community Support: Stack Overflow, Reddit r/aws

---

**Document Version**: 1.0  
**Last Updated**: September 23, 2025  
**Estimated Deployment Time**: 45-60 minutes  
**Estimated Monthly Cost**: $5-15 USD (mostly NAT Gateway)

Good luck with your deployment! 🎯
# AWS Production Infrastructure Deployment Guide

This guide walks you through deploying the VPC infrastructure to your Production environment.

## 🚀 Quick Start - Production Environment

### Step 1: Install Dependencies ✅ COMPLETED
```bash
# Install production-optimized requirements
pip install -r build/requirements/prod.txt
```

### Step 2: Configure AWS Credentials for Production
```bash
# Update .env file with Production-specific values
TF_VAR_environment=prod
TF_VAR_project_name=mono-repo-prod
```

### Step 3: Deploy Production Bootstrap Infrastructure
```bash
cd infrastructure/bootstrap
python deploy_bootstrap.py --environment=prod
```

### Step 4: Deploy Production Main Infrastructure
```bash
cd ../terraform
terraform init
terraform plan -var-file="prod.tfvars"
terraform apply -var-file="prod.tfvars"
```

## 📋 Production Environment Specifications

### ✅ **Production-Specific Configuration**
- **Project Name**: `mono-repo-prod`
- **Environment**: `prod`
- **VPC CIDR**: `10.2.0.0/16` (defined in prod.tfvars)
- **Region**: `us-east-1`
- **Availability Zones**: 3 AZs for maximum availability
- **Multi-Region**: Consider multi-region deployment for DR

### ✅ **Bootstrap Infrastructure for Production**
The bootstrap will create:
- **S3 Bucket**: `mono-repo-prod-terraform-state-{random}` for remote state
- **DynamoDB Table**: `mono-repo-prod-terraform-state-lock` for state locking
- **ECR Repositories**: Container registries with `-prod` suffix

### ✅ **Production Resource Naming Convention**
```bash
# S3 Bucket for Terraform State
mono-repo-prod-terraform-state-{random-id}
  ├── Versioning: Enabled
  ├── Encryption: AES256
  ├── Lifecycle Policies: Long-term retention
  └── Public Access: Blocked

# DynamoDB Table for State Locking  
mono-repo-prod-terraform-state-lock
  ├── Billing: Pay-per-request
  ├── Point-in-time Recovery: Enabled
  └── Backup: Automated

# ECR Repositories (7 repositories)
├── mono-repo-prod-web-app
├── mono-repo-prod-api-service
├── mono-repo-prod-airflow-worker
├── mono-repo-prod-airflow-scheduler
├── mono-repo-prod-dash-app
├── mono-repo-prod-data-processor
└── mono-repo-prod-risk-calculator
```

## 🔧 Production Environment Features

### **High Availability Configuration**
- **VPC CIDR**: `10.2.0.0/16` (isolated from DEV/UAT)
- **Availability Zones**: 3 AZs for maximum redundancy
- **Multi-AZ Deployments**: RDS, EKS across multiple AZs
- **Auto Scaling**: Enabled for all components

### **Security Configuration**
- **Enhanced Security**: WAF, GuardDuty, Security Hub
- **Network Security**: NACLs, Security Groups, VPC Flow Logs
- **Encryption**: All data encrypted at rest and in transit
- **Access Control**: Strict IAM policies and MFA requirements

### **Monitoring & Logging**
- **CloudTrail**: Full API logging and monitoring
- **CloudWatch**: Comprehensive metrics and alerting
- **VPC Flow Logs**: Network traffic analysis
- **Application Monitoring**: APM and performance monitoring

### **Backup & Disaster Recovery**
- **Automated Backups**: RDS, EBS snapshots
- **Cross-Region Replication**: S3, RDS backups
- **Point-in-Time Recovery**: Database PITR enabled
- **Disaster Recovery**: Multi-region failover capability

## ⚠️ Production Prerequisites

### AWS Account Requirements
Your Production AWS account needs:

1. **Production-Grade IAM Permissions**
2. **Compliance Requirements**: SOC2, HIPAA, etc. if applicable
3. **Resource Limits**: Sufficient limits for production workloads
4. **Support Plan**: Business or Enterprise AWS support

### Required Production IAM Permissions
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
        "logs:*",
        "wafv2:*",
        "guardduty:*",
        "securityhub:*",
        "config:*",
        "cloudtrail:*"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "aws:RequestedRegion": ["us-east-1", "us-west-2"]
        }
      }
    }
  ]
}
```

### Production Compliance Checklist
- [ ] **Security Review**: Security team approval
- [ ] **Compliance Audit**: SOX, SOC2, HIPAA compliance if required
- [ ] **Change Management**: Formal change control process
- [ ] **Backup Strategy**: Tested backup and recovery procedures
- [ ] **Monitoring Setup**: 24/7 monitoring and alerting
- [ ] **Incident Response**: On-call procedures and runbooks

## 🎯 Production Deployment Steps

### 1. Pre-Production Validation
```bash
# Ensure UAT environment is stable and tested
cd infrastructure/terraform
terraform plan -var-file="uat.tfvars" -detailed-exitcode

# Run infrastructure tests
python -m pytest tests/infrastructure/ -v

# Security scan
terraform plan -var-file="prod.tfvars" | tfsec
```

### 2. Production Environment Configuration
```bash
# Update .env file for Production
cat >> .env << EOF

# Production Environment Configuration
TF_VAR_environment=prod
TF_VAR_project_name=mono-repo-prod
TF_VAR_vpc_cidr=10.2.0.0/16

# Production EKS Configuration
EKS_CLUSTER_NAME=mono-repo-prod-eks-prod
EKS_NODE_GROUP_MIN_SIZE=3
EKS_NODE_GROUP_MAX_SIZE=10
EKS_NODE_GROUP_DESIRED_SIZE=5

# Production ECR Configuration
ECR_REGISTRY_URL=your_account_id.dkr.ecr.us-east-1.amazonaws.com
ECR_REPOSITORY_PREFIX=mono-repo-prod

# Production Database Configuration
RDS_INSTANCE_CLASS=db.r5.xlarge
RDS_MULTI_AZ=true
RDS_BACKUP_RETENTION=30
RDS_BACKUP_WINDOW=03:00-04:00
RDS_MAINTENANCE_WINDOW=sun:04:00-sun:05:00
EOF
```

### 3. Deploy Production Bootstrap (With Approval)
```bash
cd infrastructure/bootstrap

# Plan production bootstrap with detailed output
terraform plan -var-file="prod.tfvars" -out="prod.tfplan" -detailed-exitcode

# IMPORTANT: Get approval before applying in production
echo "⚠️  PRODUCTION DEPLOYMENT - REQUIRES APPROVAL"
echo "Please review the terraform plan and get necessary approvals"
read -p "Do you have approval to deploy to production? (yes/no): " approval

if [ "$approval" = "yes" ]; then
    terraform apply "prod.tfplan"
else
    echo "Production deployment cancelled - approval required"
    exit 1
fi
```

### 4. Deploy Production Main Infrastructure (Staged)
```bash
cd ../terraform

# Initialize with production backend
terraform init

# Plan production infrastructure
terraform plan -var-file="prod.tfvars" -out="prod-main.tfplan"

# Apply in stages for production safety
echo "Deploying production infrastructure in stages..."

# Stage 1: Core networking
terraform apply -target=module.vpc -target=module.security_groups "prod-main.tfplan"

# Stage 2: EKS cluster
terraform apply -target=module.eks "prod-main.tfplan"

# Stage 3: Databases and storage
terraform apply -target=module.rds -target=module.elasticache "prod-main.tfplan"

# Stage 4: Load balancers and networking
terraform apply -target=module.alb -target=module.route53 "prod-main.tfplan"

# Stage 5: Complete deployment
terraform apply "prod-main.tfplan"
```

## 🔍 Production Verification Steps

### Comprehensive Production Verification
```bash
# Verify production S3 bucket exists with proper configuration
aws s3api get-bucket-versioning --bucket mono-repo-prod-terraform-state-xxxxx
aws s3api get-bucket-encryption --bucket mono-repo-prod-terraform-state-xxxxx

# Verify production DynamoDB table with backup enabled
aws dynamodb describe-table --table-name mono-repo-prod-terraform-state-lock
aws dynamodb describe-continuous-backups --table-name mono-repo-prod-terraform-state-lock

# Verify production VPC with proper CIDR and 3 AZs
aws ec2 describe-vpcs --filters "Name=tag:Project,Values=mono-repo-prod" "Name=tag:Environment,Values=prod"
aws ec2 describe-subnets --filters "Name=tag:Project,Values=mono-repo-prod" | jq '.Subnets | length'

# Verify production EKS cluster health
aws eks describe-cluster --name mono-repo-prod-eks-prod
aws eks list-nodegroups --cluster-name mono-repo-prod-eks-prod

# Verify production security configuration
aws wafv2 list-web-acls --scope CLOUDFRONT
aws guardduty list-detectors
aws securityhub get-enabled-standards

# Test production connectivity and health
kubectl --context=mono-repo-prod-eks-prod get nodes
kubectl --context=mono-repo-prod-eks-prod get namespaces
```

### Production Health Checks
```bash
# Application health checks
curl -f https://prod-api.yourcompany.com/health || echo "API health check failed"

# Database connectivity
psql -h prod-db.yourcompany.com -U dbadmin -d monorepodb -c "SELECT 1;" || echo "DB connection failed"

# Load balancer health
aws elbv2 describe-target-health --target-group-arn arn:aws:elasticloadbalancing:us-east-1:xxx:targetgroup/prod-api/xxx
```

## 💰 Production Cost Estimates

### Bootstrap Infrastructure
- **S3 Bucket**: ~$5-15/month (state storage + versioning)
- **DynamoDB**: ~$5/month (state locking + backups)
- **ECR Repositories**: $0.10/GB/month (container images)

### Production Infrastructure
- **VPC**: Free (AWS VPC is free)
- **EKS Cluster**: ~$73/month (control plane)
- **EKS Node Groups**: ~$500-2000/month (production sizing)
- **Load Balancers**: ~$25-50/month (ALB + NLB)
- **RDS Multi-AZ**: ~$200-1000/month (production database)
- **ElastiCache**: ~$100-500/month (Redis cluster)
- **CloudWatch**: ~$50-200/month (monitoring + logs)
- **Security Services**: ~$100-300/month (WAF, GuardDuty, etc.)

**Total Production Monthly Cost**: ~$1,055-4,145/month

### Cost Optimization Recommendations
1. **Reserved Instances**: Use RIs for predictable workloads (30-60% savings)
2. **Spot Instances**: Use spot for non-critical EKS nodes (up to 90% savings)
3. **S3 Lifecycle**: Implement intelligent tiering for long-term storage
4. **CloudWatch**: Optimize log retention and metric collection
5. **Right-sizing**: Regular review of instance sizes and utilization

## 🔥 Production Troubleshooting

### Critical Production Issues

1. **EKS Cluster Not Accessible**
   ```bash
   # Check cluster status
   aws eks describe-cluster --name mono-repo-prod-eks-prod
   
   # Update kubeconfig
   aws eks update-kubeconfig --name mono-repo-prod-eks-prod --region us-east-1
   
   # Check node group health
   kubectl get nodes -o wide
   ```

2. **RDS Connection Issues**
   ```bash
   # Check RDS instance status
   aws rds describe-db-instances --db-instance-identifier mono-repo-prod-db
   
   # Check security groups
   aws ec2 describe-security-groups --filters "Name=group-name,Values=*rds*"
   
   # Test connectivity from EKS
   kubectl run -it --rm debug --image=postgres:13 --restart=Never -- psql -h prod-db-endpoint -U dbadmin
   ```

3. **Load Balancer Health Check Failures**
   ```bash
   # Check target group health
   aws elbv2 describe-target-health --target-group-arn YOUR_TARGET_GROUP_ARN
   
   # Check application logs
   kubectl logs -f deployment/api-service -n production
   
   # Check security group rules
   aws ec2 describe-security-groups --group-ids sg-xxxxxxxxx
   ```

### Production Monitoring Commands
```bash
# Check cluster resource usage
kubectl top nodes
kubectl top pods --all-namespaces

# Check application health
kubectl get pods -n production -o wide
kubectl get services -n production

# Check recent events
kubectl get events --sort-by=.metadata.creationTimestamp
```

## 🚨 Production Incident Response

### Immediate Response Checklist
1. **Assess Impact**: Determine scope and severity
2. **Check Monitoring**: Review CloudWatch, application metrics
3. **Check Recent Changes**: Review recent deployments/changes
4. **Communicate**: Notify stakeholders via incident management system
5. **Document**: Log all actions taken during incident

### Emergency Contacts
- **On-Call Engineer**: [Your on-call system]
- **Platform Team**: [Platform team contact]
- **AWS Support**: [AWS support case system]
- **Management**: [Management escalation]

## 🎉 Production Success Indicators

Production deployment is successful when:

- ✅ All production infrastructure deploys without errors
- ✅ Production applications are accessible and healthy
- ✅ Monitoring and alerting are functional
- ✅ Security services are active and monitoring
- ✅ Backup and disaster recovery procedures are tested
- ✅ Performance metrics meet SLA requirements
- ✅ Security scans pass all requirements
- ✅ Compliance requirements are met

## 📈 Production Best Practices

### Operational Excellence
1. **Infrastructure as Code**: All changes via Terraform
2. **GitOps**: All deployments via Git workflows
3. **Monitoring**: Comprehensive observability stack
4. **Automation**: Automated deployments and rollbacks
5. **Documentation**: Keep runbooks and procedures updated

### Security Best Practices
1. **Least Privilege**: Minimal required permissions
2. **Network Segmentation**: Proper subnet and security group design
3. **Encryption**: All data encrypted at rest and in transit
4. **Audit Logging**: Comprehensive audit trail
5. **Regular Updates**: Keep all components updated

### Cost Management
1. **Resource Tagging**: Consistent tagging for cost allocation
2. **Cost Monitoring**: Regular cost review and optimization
3. **Reserved Capacity**: Use reserved instances for predictable workloads
4. **Auto Scaling**: Implement proper scaling policies
5. **Unused Resources**: Regular cleanup of unused resources

Production environment provides enterprise-grade infrastructure for your critical applications! 🚀

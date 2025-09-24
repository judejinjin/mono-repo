# DevOps Procedures for Infrastructure and User Management

This document provides comprehensive procedures for DevOps teams to maintain the mono-repo infrastructure and manage user privileges across all environments.

## Table of Contents

1. [Infrastructure Deployment Procedures](#infrastructure-deployment-procedures)
2. [User and Privilege Management](#user-and-privilege-management)
3. [Monitoring and Maintenance](#monitoring-and-maintenance)
4. [Emergency and Recovery Procedures](#emergency-and-recovery-procedures)
5. [CI/CD and Automation](#ci-cd-and-automation)
6. [Daily Operations](#daily-operations)

---

## Parameter Store Management

### 1. Parameter Store Overview

The mono-repo application uses AWS Systems Manager Parameter Store for centralized configuration management across all environments (dev, uat, prod). Parameters follow a hierarchical naming convention:

```
/{environment}/{app_name}/{parameter_name}
```

**Examples:**
- `/dev/mono-repo/database/host`
- `/prod/mono-repo/api/secret_key` (SecureString)
- `/uat/mono-repo/redis/port`

### 2. Parameter Types and Security

**Regular Parameters (String type):**
- Non-sensitive configuration values
- Database hosts, ports, URLs
- Application settings, feature flags
- Environment identifiers

**Secure Parameters (SecureString type):**
- Passwords, API keys, secrets
- JWT signing keys, encryption keys
- OAuth client secrets
- Database credentials

### 3. Parameter Store Deployment

#### **Initial Parameter Store Setup (Terraform)**

The Parameter Store infrastructure is managed via Terraform and deployed automatically with the main infrastructure:

```bash
cd infrastructure/terraform

# Initialize and deploy Parameter Store with infrastructure
terraform init
terraform plan -var-file="dev.tfvars"
terraform apply -var-file="dev.tfvars"
```

**Resources Created:**
- SSM Parameters (String and SecureString types)
- KMS key for parameter encryption
- IAM roles and policies for access control
- CloudWatch log groups for access logging
- Instance profiles (if required)

#### **Manual Parameter Management**

Use the provided utility scripts for parameter management:

```bash
# Populate Parameter Store from configuration
python scripts/setup_environment_config.py --environment=dev

# Migrate existing .env to Parameter Store
python scripts/migrate_to_parameter_store.py --environment=dev --env-file=config/.env

# Validate Parameter Store configuration
python scripts/validate_parameter_store.py --environment=dev --output=json
```

### 4. Parameter Store Operations

#### **Reading Parameters**

**Single Parameter:**
```bash
aws ssm get-parameter --name "/dev/mono-repo/database/host" --region us-east-1

# For SecureString parameters
aws ssm get-parameter --name "/dev/mono-repo/database/password" --with-decryption --region us-east-1
```

**Multiple Parameters by Path:**
```bash
aws ssm get-parameters-by-path --path "/dev/mono-repo/" --recursive --with-decryption --region us-east-1
```

**Using Python SDK:**
```python
import boto3

ssm = boto3.client('ssm', region_name='us-east-1')

# Get single parameter
response = ssm.get_parameter(
    Name='/dev/mono-repo/database/host',
    WithDecryption=True
)

# Get all parameters for environment
response = ssm.get_parameters_by_path(
    Path='/dev/mono-repo/',
    Recursive=True,
    WithDecryption=True
)
```

#### **Updating Parameters**

**Individual Parameter Update:**
```bash
aws ssm put-parameter \
    --name "/dev/mono-repo/api/version" \
    --value "v2" \
    --overwrite \
    --region us-east-1

# For SecureString parameters
aws ssm put-parameter \
    --name "/dev/mono-repo/database/password" \
    --value "new-secure-password" \
    --type "SecureString" \
    --overwrite \
    --region us-east-1
```

**Bulk Parameter Update:**
```bash
# Use the setup script to update multiple parameters
python scripts/setup_environment_config.py --environment=prod --update-existing
```

#### **Parameter Rotation and Security**

**Password Rotation:**
```bash
# Generate new secure password
NEW_PASSWORD=$(openssl rand -base64 32)

# Update parameter
aws ssm put-parameter \
    --name "/prod/mono-repo/database/password" \
    --value "$NEW_PASSWORD" \
    --type "SecureString" \
    --overwrite \
    --region us-east-1

# Update application configuration (restart required)
kubectl rollout restart deployment/mono-repo-api -n mono-repo-prod
```

**API Key Rotation:**
```bash
# Update API keys across environments
for env in dev uat prod; do
    NEW_KEY=$(uuidgen)
    aws ssm put-parameter \
        --name "/$env/mono-repo/api/secret_key" \
        --value "$NEW_KEY" \
        --type "SecureString" \
        --overwrite \
        --region us-east-1
done
```

### 5. Access Control and Permissions

#### **IAM Roles for Parameter Access**

The Terraform module creates environment-specific IAM roles:
- `mono-repo-parameter-store-access-{environment}`
- Provides read access to `/{environment}/mono-repo/*` parameters
- Write access controlled by `allow_write_access` variable

#### **Cross-Account Access**

For cross-account parameter sharing:
```bash
# Add cross-account access ARNs in tfvars
parameter_store_assume_role_arns = [
    "arn:aws:iam::ACCOUNT-ID:role/CrossAccountRole"
]
```

#### **Application Integration**

Applications automatically load parameters using the configuration system:

```python
from config import ConfigManager

config = ConfigManager()
db_host = config.get('database.host')  # Loads from Parameter Store
api_key = config.get('api.secret_key')  # SecureString parameter
```

### 6. Monitoring and Auditing

#### **CloudWatch Logs**

Parameter Store access is logged to CloudWatch (when enabled):
- Log Group: `/aws/ssm/parameter-store/{environment}/{app_name}`
- Retention: 7-90 days depending on environment
- Includes parameter access events and errors

#### **Parameter Store Validation**

Regular validation ensures parameter integrity:
```bash
# Validate all parameters for environment
python scripts/validate_parameter_store.py --environment=prod --report

# Check specific parameter categories
python scripts/validate_parameter_store.py --environment=uat --category=database
```

#### **Cost Monitoring**

Parameter Store costs are tracked via AWS Cost Explorer:
- Standard parameters: Free tier (10,000 parameters)
- Advanced parameters: $0.05 per 10,000 requests
- SecureString parameters: KMS usage charges apply

### 7. Disaster Recovery and Backup

#### **Parameter Export**

Export parameters for backup:
```bash
# Export all parameters for environment
python scripts/validate_parameter_store.py --environment=prod --export --output=backup-prod.json
```

#### **Cross-Region Replication**

For disaster recovery, replicate critical parameters:
```bash
# Replicate to secondary region
aws ssm get-parameters-by-path --path "/prod/mono-repo/" --recursive --with-decryption --region us-east-1 | \
jq -r '.Parameters[] | [.Name, .Value, .Type] | @csv' | \
while IFS=, read -r name value type; do
    aws ssm put-parameter --name "$name" --value "$value" --type "$type" --region us-west-2
done
```

#### **Parameter Restoration**

Restore from backup:
```bash
# Restore from exported JSON
python scripts/setup_environment_config.py --environment=prod --import-file=backup-prod.json
```

---

## Infrastructure Deployment Procedures

### 1. Environment Setup and Prerequisites

#### **Initial Development Environment Setup**
```bash
# 1. Install dependencies
pip install -r build/requirements/dev.txt

# 2. Configure AWS credentials
python setup_aws_credentials.py

# 3. Set environment variables
export TF_VAR_environment=dev
export TF_VAR_project_name=mono-repo-test
```

#### **Production Environment Setup**
```bash
# 1. Install production dependencies
pip install -r build/requirements/prod.txt

# 2. Set production environment variables
export TF_VAR_environment=prod
export TF_VAR_project_name=mono-repo-prod
export TF_VAR_vpc_cidr=10.2.0.0/16
```

### 2. Bootstrap Infrastructure Deployment

#### **Deploy Bootstrap (S3, DynamoDB, ECR)**
```bash
cd infrastructure/bootstrap

# Development
python deploy_bootstrap.py

# UAT
python deploy_bootstrap.py --environment=uat

# Production (requires approval)
python deploy_bootstrap.py --environment=prod
```

**Bootstrap Creates:**
- S3 bucket for Terraform state (`mono-repo-{env}-terraform-state-{random}`)
- DynamoDB table for state locking (`mono-repo-{env}-terraform-state-lock`)
- ECR repositories (7 repositories for applications)

### 3. Main Infrastructure Deployment

#### **Terraform Infrastructure Deployment**
```bash
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Development environment
terraform plan -var-file="dev.tfvars"
terraform apply -var-file="dev.tfvars"

# UAT environment
terraform plan -var-file="uat.tfvars"
terraform apply -var-file="uat.tfvars"

# Production environment (requires approval)
terraform plan -var-file="prod.tfvars"
terraform apply -var-file="prod.tfvars"
```

**Infrastructure Components Deployed:**
- VPC with public/private subnets across 3 AZs
- EKS cluster with managed node groups
- RDS PostgreSQL databases
- Application Load Balancers
- NAT Gateways and Internet Gateways
- Security Groups and NACLs
- **Parameter Store with KMS encryption**
- **IAM roles for Parameter Store access**
- **CloudWatch log groups for parameter auditing**

#### **Parameter Store Validation Post-Deployment**

After Terraform deployment, validate Parameter Store setup:
```bash
# Validate Parameter Store infrastructure
python scripts/validate_parameter_store.py --environment=dev --verbose

# Check parameter access permissions
aws sts get-caller-identity
aws ssm get-parameters-by-path --path "/dev/mono-repo/" --max-items 5

# Verify KMS key access
aws kms describe-key --key-id alias/mono-repo-parameter-store-dev
```

#### **Environment-Specific Parameter Store Configuration**

**Development Environment:**
- Write access enabled for easier testing
- 7-day log retention
- Instance profile created for EC2 access
- All parameters populated automatically

**UAT Environment:**
- Read-only access for stability
- 30-day log retention
- Instance profile created
- Production-like parameter values

**Production Environment:**
- Read-only access for security
- 90-day log retention
- No instance profile (uses IRSA for EKS)
- Secure parameter values (change defaults immediately)

### 4. Application Deployment

#### **Deploy All Components**
```bash
cd deploy

# Deploy infrastructure and applications
python deploy.py --environment=dev --target=all

# Deploy specific component
python deploy.py --environment=dev --target=services
python deploy.py --environment=dev --target=web
python deploy.py --environment=dev --target=airflow
```

#### **Build and Deploy Applications**
```bash
cd build

# Build all components
python build.py --environment=dev

# Deploy to Kubernetes
cd ../deploy
python deploy.py --environment=dev --target=kubernetes
```

---

## User and Privilege Management

### 1. IAM User Management

#### **Create Developer Users**
```bash
cd infrastructure/iam

# Deploy IAM infrastructure
terraform init
terraform plan -var-file="../terraform/dev.tfvars"
terraform apply -var-file="../terraform/dev.tfvars"
```

#### **Add New Developer User**
Edit `infrastructure/iam/users/developers.tf`:
```hcl
# Add to developer_users variable in dev.tfvars
developer_users = [
  {
    name  = "john-smith"
    email = "john.smith@company.com"
    team  = "backend"
  },
  {
    name  = "jane-doe" 
    email = "jane.doe@company.com"
    team  = "frontend"
  }
]
```

Then apply changes:
```bash
terraform plan -var-file="../terraform/dev.tfvars"
terraform apply -var-file="../terraform/dev.tfvars"
```

#### **Developer Access Keys Management**
```bash
# Retrieve access keys from Secrets Manager
aws secretsmanager get-secret-value \
  --secret-id "mono-repo-dev-access-keys-john-smith" \
  --query SecretString --output text

# Rotate access keys
aws iam create-access-key --user-name mono-repo-dev-john-smith
aws iam delete-access-key --user-name mono-repo-dev-john-smith --access-key-id OLD_KEY_ID
```

### 2. User Groups and Permissions

#### **Operations Groups Management**
- **Operations Group**: General ops permissions (CloudWatch, EC2 describe, SSM parameters)
- **DevOps Engineers**: Infrastructure management permissions
- **SRE Team**: System reliability and monitoring permissions
- **Security Team**: Security monitoring and audit permissions

#### **Assign Users to Groups**
```bash
# Add user to operations group
aws iam add-user-to-group \
  --group-name mono-repo-dev-operations \
  --user-name mono-repo-dev-john-smith

# Remove user from group
aws iam remove-user-from-group \
  --group-name mono-repo-dev-operations \
  --user-name mono-repo-dev-john-smith
```

### 3. Service Account Management

#### **Create Service Accounts**
Service accounts are managed through Terraform in `infrastructure/iam/users/service-accounts.tf`:
- **CI/CD Service Account**: For automated deployments
- **Monitoring Service Account**: For CloudWatch and logging
- **Backup Service Account**: For automated backups
- **Logging Service Account**: For centralized logging

#### **Rotate Service Account Credentials**
```bash
# Generate new access key
aws iam create-access-key --user-name mono-repo-dev-cicd-service

# Update in CI/CD system (GitHub Secrets, etc.)
# Delete old access key
aws iam delete-access-key --user-name mono-repo-dev-cicd-service --access-key-id OLD_KEY
```

### 4. Kubernetes RBAC Management

#### **Create Kubernetes Service Accounts**
```bash
# Create service account
kubectl create serviceaccount airflow-scheduler -n airflow

# Create role binding
kubectl create clusterrolebinding airflow-scheduler \
  --clusterrole=cluster-admin \
  --serviceaccount=airflow:airflow-scheduler
```

#### **Manage User Access to EKS**
```bash
# Add user to EKS cluster access
aws eks update-kubeconfig --region us-east-1 --name mono-repo-dev-eks-dev

# Create RBAC for user
kubectl apply -f - <<EOF
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: john-smith-admin
subjects:
- kind: User
  name: john-smith
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: cluster-admin
  apiGroup: rbac.authorization.k8s.io
EOF
```

---

## Monitoring and Maintenance

### 1. Cost Monitoring

#### **Daily Cost Monitoring**
```bash
cd devops

# Run cost monitoring script
python cost_monitor.py --days=30

# Check current month costs
python cost_monitor.py --current-month

# Get detailed cost breakdown
python cost_monitor.py --detailed --service=EC2
```

#### **Set Up Cost Alerts**
```bash
# Create cost budget alert
aws budgets create-budget --account-id ACCOUNT_ID --budget '{
  "BudgetName": "MonoRepo-Monthly-Budget",
  "BudgetLimit": {"Amount": "100", "Unit": "USD"},
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST"
}'
```

### 2. Infrastructure Health Monitoring

#### **Check Infrastructure Status**
```bash
# Check EKS cluster status
kubectl get nodes
kubectl get pods --all-namespaces

# Check RDS database status
aws rds describe-db-instances \
  --query 'DBInstances[?DBInstanceStatus!=`available`]'

# Check EC2 instances
aws ec2 describe-instances \
  --query 'Reservations[].Instances[?State.Name!=`running`]'
```

#### **Application Health Checks**
```bash
# Check service endpoints
curl -f http://api-service.mono-repo.internal/health
curl -f http://web-app.mono-repo.internal/health
curl -f http://dash-app.mono-repo.internal/health

# Check Airflow status
kubectl get pods -n airflow
curl -f http://airflow.mono-repo.internal/health
```

### 3. Log Management

#### **Access Application Logs**
```bash
# View Kubernetes logs
kubectl logs -f deployment/api-service -n services
kubectl logs -f deployment/web-app -n web
kubectl logs -f deployment/airflow-scheduler -n airflow

# View CloudWatch logs
aws logs tail /aws/eks/mono-repo-dev/cluster --follow
```

#### **Log Analysis and Troubleshooting**
```bash
# Search for errors in logs
kubectl logs deployment/api-service -n services | grep -i error

# Check application metrics
kubectl top nodes
kubectl top pods --all-namespaces
```

### 4. Security Monitoring

#### **Security Audit Procedures**
```bash
# Check IAM users and their last access
aws iam generate-credential-report
aws iam get-credential-report

# Review security groups
aws ec2 describe-security-groups \
  --query 'SecurityGroups[?IpPermissions[?FromPort==`22`]]'

# Check for unused access keys
aws iam list-access-keys --user-name USERNAME
aws iam get-access-key-last-used --access-key-id ACCESS_KEY_ID
```

---

## Emergency and Recovery Procedures

### 1. Emergency Stop Procedures

#### **Emergency Infrastructure Stop (Without Destruction)**
```bash
cd devops

# Stop all compute resources immediately
./emergency-stop.sh

# Or use Python script
python teardown_infrastructure.py --emergency-stop --environment=dev
```

**What Emergency Stop Does:**
- Stops all EC2 instances
- Scales EKS node groups to 0
- Stops RDS instances (if configured)
- Maintains data and configuration

### 2. Full Infrastructure Teardown

#### **Complete Infrastructure Destruction**
```bash
cd devops

# Interactive teardown with confirmation
./teardown-infrastructure.sh --environment=dev

# Automated teardown (use with caution)
python teardown_infrastructure.py --environment=dev --auto-approve
```

#### **Teardown Order:**
1. **Backup Creation**: Terraform state, Kubernetes resources
2. **Kubernetes Cleanup**: Delete applications and services
3. **Terraform Destroy**: Destroy infrastructure components
4. **Bootstrap Cleanup**: Remove S3 bucket and DynamoDB table
5. **Verification**: Confirm all resources are deleted

### 3. Disaster Recovery Procedures

#### **Restore from Backup**
```bash
# Restore Terraform state
cd infrastructure/terraform
cp backups/TIMESTAMP_dev/terraform.tfstate.backup terraform.tfstate

# Restore Kubernetes resources
kubectl apply -f backups/TIMESTAMP_dev/kubernetes/

# Re-deploy applications
cd ../../deploy
python deploy.py --environment=dev --target=applications
```

#### **Database Recovery**
```bash
# Restore RDS from snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier mono-repo-dev-restored \
  --db-snapshot-identifier mono-repo-dev-snapshot-TIMESTAMP
```

### 4. Incident Response

#### **Security Incident Response**
```bash
# 1. Immediately rotate compromised credentials
aws iam delete-access-key --user-name COMPROMISED_USER --access-key-id COMPROMISED_KEY

# 2. Check CloudTrail logs for suspicious activity
aws logs filter-log-events \
  --log-group-name CloudTrail/MonoRepoAuditLogs \
  --start-time 1640995200000 \
  --filter-pattern "{ $.userIdentity.type = \"IAMUser\" && $.userIdentity.userName = \"COMPROMISED_USER\" }"

# 3. Apply temporary security restrictions
# 4. Conduct security audit
# 5. Update security policies
```

#### **Performance Incident Response**
```bash
# 1. Check resource utilization
kubectl top nodes
kubectl top pods --all-namespaces

# 2. Scale applications if needed
kubectl scale deployment api-service --replicas=5 -n services

# 3. Check database performance
aws rds describe-db-instances --query 'DBInstances[].CPUUtilization'

# 4. Review CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/EKS \
  --metric-name CPUUtilization \
  --start-time 2025-01-01T00:00:00Z \
  --end-time 2025-01-01T23:59:59Z \
  --period 300 \
  --statistics Average
```

---

## CI/CD and Automation

### 1. Airflow DAG Management

#### **Deploy and Manage DAGs**
```bash
# Check DAG status
kubectl exec -it deployment/airflow-scheduler -n airflow -- \
  airflow dags list

# Trigger DAG manually
kubectl exec -it deployment/airflow-scheduler -n airflow -- \
  airflow dags trigger daily_risk_processing

# Check DAG run status
kubectl exec -it deployment/airflow-scheduler -n airflow -- \
  airflow dags state daily_risk_processing 2025-01-01
```

#### **Update DAG Configuration**
```bash
# Update DAG files
cp dags/*.py /path/to/airflow/dags/

# Restart Airflow scheduler
kubectl rollout restart deployment/airflow-scheduler -n airflow

# Verify DAGs are loaded
kubectl exec -it deployment/airflow-scheduler -n airflow -- \
  airflow dags list-import-errors
```

### 2. Container Image Management

#### **Build and Push Images**
```bash
# Build application images
cd build
python build.py --environment=dev --target=all

# Push to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/mono-repo-dev-api-service:latest
```

#### **Update Kubernetes Deployments**
```bash
# Update deployment with new image
kubectl set image deployment/api-service \
  api-service=ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/mono-repo-dev-api-service:v1.2.3 \
  -n services

# Check rollout status
kubectl rollout status deployment/api-service -n services
```

### 3. Automated Testing and Validation

#### **Run Infrastructure Tests**
```bash
# Test Terraform configuration
cd infrastructure/terraform
terraform validate
terraform plan -var-file="dev.tfvars" -detailed-exitcode

# Run infrastructure tests
python -m pytest tests/infrastructure/ -v
```

#### **Application Testing**
```bash
# Run unit tests
cd services
python -m pytest tests/ -v

# Run integration tests
python -m pytest tests/integration/ -v

# Run load tests
cd tests/load
python -m locust -f locustfile.py --host=http://api-service.mono-repo.internal
```

---

## Daily Operations

### 1. Daily Health Checks

#### **Morning Health Check Routine**
```bash
#!/bin/bash
# daily-health-check.sh

echo "🏥 Daily Infrastructure Health Check"
echo "=================================="

# Check EKS cluster
echo "1. Checking EKS cluster..."
kubectl get nodes
kubectl get pods --all-namespaces | grep -v Running

# Check RDS databases
echo "2. Checking RDS databases..."
aws rds describe-db-instances \
  --query 'DBInstances[?DBInstanceStatus!=`available`].{ID:DBInstanceIdentifier,Status:DBInstanceStatus}'

# Check application endpoints
echo "3. Checking application endpoints..."
curl -f -s http://api-service.mono-repo.internal/health || echo "❌ API service unhealthy"
curl -f -s http://web-app.mono-repo.internal/health || echo "❌ Web app unhealthy"
curl -f -s http://dash-app.mono-repo.internal/health || echo "❌ Dash app unhealthy"

# Check costs
echo "4. Checking daily costs..."
cd devops && python cost_monitor.py --current-month

# Check for failed DAGs
echo "5. Checking Airflow DAGs..."
kubectl exec -it deployment/airflow-scheduler -n airflow -- \
  airflow dags list-import-errors

# Check Parameter Store health
echo "6. Checking Parameter Store..."
python scripts/validate_parameter_store.py --environment=prod --quick-check

echo "✅ Health check complete"
```

### 2. Weekly Maintenance Tasks

#### **Weekly Infrastructure Review**
```bash
#!/bin/bash
# weekly-maintenance.sh

echo "🔧 Weekly Infrastructure Maintenance"
echo "==================================="

# 1. Update system packages in worker nodes
kubectl drain NODE_NAME --ignore-daemonsets --delete-emptydir-data
# Update AMI and restart node group

# 2. Check for security updates
aws inspector create-assessment-run \
  --assessment-template-arn TEMPLATE_ARN

# 3. Review and cleanup unused resources
aws ec2 describe-volumes --filters Name=status,Values=available
aws ec2 describe-snapshots --owner-ids self \
  --query 'Snapshots[?StartTime<=`2024-01-01`]'

# 4. Backup verification
aws rds describe-db-snapshots \
  --query 'DBSnapshots[?SnapshotCreateTime>=`2025-01-01`]'

# 5. Cost optimization review
python cost_monitor.py --detailed --days=7

# 6. Parameter Store maintenance
echo "6. Parameter Store Weekly Maintenance..."
# Validate parameters across all environments
for env in dev uat prod; do
    echo "Validating $env environment parameters..."
    python scripts/validate_parameter_store.py --environment=$env --report
done

# Check for parameter drift
python scripts/validate_parameter_store.py --environment=prod --check-drift

# Review Parameter Store access logs
aws logs filter-log-events \
  --log-group-name /aws/ssm/parameter-store/prod/mono-repo \
  --start-time $(date -d "7 days ago" +%s)000 \
  --query 'events[?message contains `ERROR` || message contains `WARN`]'
```

### 3. Monthly Administrative Tasks

#### **Monthly Security and Compliance Review**
```bash
# 1. Access review
aws iam generate-credential-report
aws iam get-credential-report

# 2. Rotate service account credentials
aws iam create-access-key --user-name mono-repo-dev-cicd-service

# 3. Review CloudTrail logs
aws logs filter-log-events \
  --log-group-name CloudTrail/MonoRepoAuditLogs \
  --start-time $(date -d "1 month ago" +%s)000

# 4. Update security policies
cd infrastructure/iam
terraform plan -var-file="../terraform/dev.tfvars"

# 5. Parameter Store security review
echo "5. Parameter Store Security Review..."
# Check for unused parameters
python scripts/validate_parameter_store.py --environment=prod --check-unused

# Review parameter access patterns
aws logs insights start-query \
  --log-group-name /aws/ssm/parameter-store/prod/mono-repo \
  --start-time $(date -d "1 month ago" +%s) \
  --end-time $(date +%s) \
  --query-string 'fields @timestamp, sourceIPAddress, userIdentity.type | filter @message like /GetParameter/ | stats count() by sourceIPAddress'

# Rotate sensitive parameters (quarterly)
if [ "$(date +%m)" -eq "03" ] || [ "$(date +%m)" -eq "06" ] || [ "$(date +%m)" -eq "09" ] || [ "$(date +%m)" -eq "12" ]; then
    echo "Quarterly parameter rotation due - scheduling rotation tasks"
    # Schedule parameter rotation for next maintenance window
fi

# 6. Compliance reporting
python generate_compliance_report.py --month=$(date +%Y-%m)
```

### 4. Documentation and Knowledge Management

#### **Keep Documentation Updated**
```bash
# Update infrastructure documentation
cd docs
python generate_infrastructure_docs.py

# Update API documentation
cd services
python generate_api_docs.py

# Update operational runbooks
cd devops
# Update this procedures.md file with any new procedures
```

---

## Troubleshooting Guide

### Common Issues and Solutions

#### **EKS Node Not Ready**
```bash
# Check node status
kubectl describe node NODE_NAME

# Check system pods
kubectl get pods -n kube-system

# Restart kubelet
kubectl drain NODE_NAME --ignore-daemonsets
# Replace node in node group
```

#### **Application Pod CrashLoopBackOff**
```bash
# Check pod logs
kubectl logs POD_NAME -n NAMESPACE --previous

# Check resource limits
kubectl describe pod POD_NAME -n NAMESPACE

# Check secrets and config maps
kubectl get secrets -n NAMESPACE
kubectl get configmaps -n NAMESPACE
```

#### **Database Connection Issues**
```bash
# Check RDS status
aws rds describe-db-instances

# Check security groups
aws ec2 describe-security-groups --group-ids sg-XXXXXX

# Test connectivity from pod
kubectl exec -it POD_NAME -n NAMESPACE -- \
  telnet RDS_ENDPOINT 5432
```

#### **High AWS Costs**
```bash
# Identify cost drivers
python cost_monitor.py --detailed --service=all

# Check for forgotten resources
aws ec2 describe-instances --query 'Reservations[].Instances[?State.Name==`running`]'
aws rds describe-db-instances --query 'DBInstances[?DBInstanceStatus==`available`]'
```

### Parameter Store Troubleshooting

#### **Parameter Not Found Error**
```bash
# Check if parameter exists
aws ssm get-parameter --name "/dev/mono-repo/database/host" --region us-east-1

# List parameters by path
aws ssm get-parameters-by-path --path "/dev/mono-repo/" --region us-east-1

# Check parameter naming convention
python scripts/validate_parameter_store.py --environment=dev --check-naming

# Verify application configuration
python -c "from config import ConfigManager; c = ConfigManager(); print(c.get('database.host'))"
```

#### **Access Denied to Parameter Store**
```bash
# Check current AWS identity
aws sts get-caller-identity

# Test parameter access
aws ssm get-parameter --name "/dev/mono-repo/database/host" --region us-east-1

# Check IAM permissions
aws iam get-role-policy --role-name mono-repo-parameter-store-access-dev --policy-name parameter-store-read-policy

# Verify KMS key access
aws kms describe-key --key-id alias/mono-repo-parameter-store-dev

# Check assume role permissions
aws sts assume-role --role-arn arn:aws:iam::ACCOUNT:role/mono-repo-parameter-store-access-dev --role-session-name test
```

#### **KMS Decryption Errors**
```bash
# Check KMS key status
aws kms describe-key --key-id alias/mono-repo-parameter-store-prod

# Test KMS access
aws kms decrypt --ciphertext-blob fileb://test-encrypted-data --region us-east-1

# Verify KMS key policy
aws kms get-key-policy --key-id alias/mono-repo-parameter-store-prod --policy-name default

# Check KMS usage in Parameter Store
aws ssm get-parameter --name "/prod/mono-repo/database/password" --with-decryption --region us-east-1
```

#### **Parameter Store Performance Issues**
```bash
# Check parameter access patterns
aws logs filter-log-events \
  --log-group-name /aws/ssm/parameter-store/prod/mono-repo \
  --start-time $(date -d "1 hour ago" +%s)000 \
  --filter-pattern "ERROR"

# Monitor API throttling
aws cloudwatch get-metric-statistics \
  --namespace AWS/SSM \
  --metric-name ThrottledRequests \
  --start-time $(date -d "1 hour ago" -u +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum

# Check parameter caching in application
python -c "
from libs.cloud.parameter_store import ParameterStoreManager
pm = ParameterStoreManager('dev', 'mono-repo')
print(f'Cache hits: {pm._cache_hits}, Cache misses: {pm._cache_misses}')
"
```

#### **Parameter Drift Detection**
```bash
# Check for configuration drift
python scripts/validate_parameter_store.py --environment=prod --check-drift

# Compare parameters between environments
python scripts/validate_parameter_store.py --compare-environments=dev,uat,prod

# Validate parameter values against expected patterns
python scripts/validate_parameter_store.py --environment=prod --validate-values

# Check for orphaned parameters
python scripts/validate_parameter_store.py --environment=prod --check-unused
```

#### **Emergency Parameter Recovery**
```bash
# Export current parameters for backup
python scripts/validate_parameter_store.py --environment=prod --export --output=/tmp/backup-$(date +%Y%m%d).json

# Restore from previous backup
python scripts/setup_environment_config.py --environment=prod --import-file=/tmp/backup-20241201.json

# Restore from Terraform state
cd infrastructure/terraform
terraform refresh -var-file="prod.tfvars"
terraform apply -var-file="prod.tfvars"

# Manual parameter restoration
aws ssm put-parameter \
  --name "/prod/mono-repo/database/password" \
  --value "$(aws ssm get-parameter --name '/prod/mono-repo/database/password' --with-decryption --query 'Parameter.Value' --output text)" \
  --type "SecureString" \
  --overwrite \
  --region us-east-1
```

#### **Cross-Region Parameter Sync Issues**
```bash
# Check parameter consistency across regions
for region in us-east-1 us-west-2; do
    echo "Checking region: $region"
    aws ssm get-parameters-by-path --path "/prod/mono-repo/" --region $region --query 'Parameters[].Name' --output table
done

# Sync parameters to secondary region
python scripts/sync_parameters_cross_region.py --source=us-east-1 --target=us-west-2 --environment=prod

# Verify replication
aws ssm get-parameter --name "/prod/mono-repo/database/host" --region us-west-2
```

# Scale down non-production environments
kubectl scale deployment --replicas=0 --all -n services
```

---

## Security Checklist

### Daily Security Tasks
- [ ] Review CloudTrail logs for suspicious activity
- [ ] Check for failed authentication attempts
- [ ] Verify backup completion
- [ ] Monitor security group changes

### Weekly Security Tasks
- [ ] Review IAM user access and permissions
- [ ] Check for unused access keys
- [ ] Review security patches and updates
- [ ] Validate SSL certificate expiry dates

### Monthly Security Tasks
- [ ] Rotate service account credentials
- [ ] Conduct access review and cleanup
- [ ] Update security policies and procedures
- [ ] Generate compliance reports

---

**Document Information:**
- **Last Updated**: September 23, 2025
- **Version**: 1.0
- **Owner**: DevOps Team
- **Review Cycle**: Monthly
- **Next Review**: October 23, 2025

**Emergency Contact:**
- **DevOps On-Call**: [Contact Information]
- **Security Team**: [Contact Information]
- **Infrastructure Lead**: [Contact Information]
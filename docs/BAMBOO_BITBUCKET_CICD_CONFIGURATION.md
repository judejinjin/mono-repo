# Bamboo CI/CD Configuration for Corporate Intranet

## Overview
This guide explains how to configure Atlassian Bamboo to access Bitbucket Server within a corporate intranet environment for automated CI/CD pipelines.

## Architecture Context

### Corporate Intranet Setup
```
Corporate Network
        ↓
   Bitbucket Server (Source Control)
        ↓
   Bamboo Server (CI/CD)
        ↓
   AWS VPN Connection
        ↓
   EKS Cluster (Deployment Target)
```

## Bamboo-Bitbucket Integration

### 1. Repository Configuration

#### Adding Bitbucket Repository to Bamboo
1. **Navigate to Bamboo Admin**:
   - Go to `Administration` → `Linked Repositories`
   - Click `Add Repository`

2. **Repository Details**:
   ```yaml
   Repository Type: Bitbucket Server
   Display Name: mono-repo-main
   Repository URL: https://bitbucket.corporate.com/projects/GENAI/repos/mono-repo
   Branch: main (or your default branch)
   ```

3. **Authentication Methods**:

   **Option A: SSH Key Authentication (Recommended)**
   ```bash
   # Generate SSH key on Bamboo server
   ssh-keygen -t rsa -b 4096 -C "bamboo@corporate.com"
   
   # Add public key to Bitbucket user/project
   # Copy private key to Bamboo configuration
   ```

   **Option B: Username/Password**
   ```yaml
   Authentication Type: Username/password
   Username: bamboo-service-account
   Password: [service account password]
   ```

   **Option C: Personal Access Token (Preferred)**
   ```yaml
   Authentication Type: Username/password
   Username: bamboo-service-account
   Password: [Bitbucket Personal Access Token]
   ```

### 2. Webhook Configuration

#### Bitbucket Webhook Setup
1. **In Bitbucket Repository Settings**:
   - Go to `Repository Settings` → `Webhooks`
   - Add webhook: `http://bamboo.corporate.com:8085/rest/api/latest/repository/PROJECT/REPO/webhook`

2. **Webhook Configuration**:
   ```json
   {
     "url": "http://bamboo.corporate.com:8085/rest/api/latest/repository/PROJECT/REPO/webhook",
     "events": [
       "repo:push",
       "pullrequest:created",
       "pullrequest:updated",
       "pullrequest:approved"
     ],
     "active": true
   }
   ```

#### Bamboo Trigger Configuration
```yaml
Trigger Type: Repository polling / Webhook
Repository: mono-repo-main
Trigger Conditions:
  - Push to branch: main, develop, feature/*
  - Pull request events
Polling Interval: 180 seconds (backup to webhooks)
```

## CI/CD Pipeline Configuration

### 3. Build Plan Structure

#### Plan Configuration
```yaml
Plan Name: GenAI MonoRepo CI/CD
Project: GENAI
Plan Key: GENAI-MONO

Stages:
  1. Build & Test
  2. Security Scan
  3. Package & Push
  4. Deploy to Dev
  5. Deploy to UAT (Manual)
  6. Deploy to Prod (Manual)
```

#### Stage 1: Build & Test
```yaml
Jobs:
  - Build FastAPI Services
  - Build Web Applications
  - Build Dash Applications
  - Run Unit Tests
  - Run Integration Tests
  - Generate Test Reports

Tasks per Job:
  1. Source Code Checkout
  2. Python Environment Setup
  3. Install Dependencies
  4. Run Tests
  5. Generate Artifacts
```

#### Stage 2: Security Scan
```yaml
Jobs:
  - SAST (Static Analysis)
  - Dependency Vulnerability Scan
  - Container Image Scan
  - Terraform Security Scan

Tasks:
  1. SonarQube Analysis
  2. OWASP Dependency Check
  3. Trivy Container Scan
  4. Checkov Terraform Scan
```

### 4. Bamboo Task Configuration

#### Python Build Tasks
```yaml
Task Type: Script
Working Directory: services/
Script Body: |
  #!/bin/bash
  python -m venv venv
  source venv/bin/activate
  # Install environment-specific requirements
  if [[ "${bamboo.deploy.environment}" == "prod" ]]; then
    pip install -r build/requirements/prod.txt
  elif [[ "${bamboo.deploy.environment}" == "uat" ]]; then
    pip install -r build/requirements/uat.txt
  else
    pip install -r build/requirements/dev.txt
  fi
  python -m pytest tests/ --junitxml=test-reports/junit.xml
  
Artifact Definition:
  Name: test-reports
  Location: test-reports/
  Copy Pattern: "**/*"
```

#### Docker Build Tasks
```yaml
Task Type: Docker
Working Directory: services/risk_api/
Docker Command: build
Arguments: |
  -t ${bamboo.ECR_REPOSITORY}:${bamboo.buildNumber}
  -t ${bamboo.ECR_REPOSITORY}:latest
  .

Post-Build Tasks:
  - ECR Login
  - Docker Push
```

#### Terraform Deployment Tasks
```yaml
Task Type: Script
Working Directory: infrastructure/terraform/
Script Body: |
  #!/bin/bash
  terraform init
  terraform plan -var-file="environments/${bamboo.deploy.environment}.tfvars"
  terraform apply -auto-approve -var-file="environments/${bamboo.deploy.environment}.tfvars"

Environment Variables:
  AWS_REGION: us-east-1
  TF_VAR_environment: ${bamboo.deploy.environment}
```

## Corporate Network Considerations

### 5. Network Access Configuration

#### Bamboo Server Requirements
```yaml
Network Access:
  - Bitbucket Server: https://bitbucket.corporate.com (port 443/7990)
  - AWS API: https://api.aws.amazonaws.com (port 443)
  - ECR Registry: https://123456789.dkr.ecr.us-east-1.amazonaws.com (port 443)
  - EKS Cluster: via VPN connection

Firewall Rules:
  Source: Bamboo Server IP
  Destinations:
    - Bitbucket: 10.0.1.100:7990,443
    - AWS APIs: 0.0.0.0/0:443 (or specific AWS IP ranges)
    - EKS: via corporate VPN
```

#### VPN Configuration for AWS Access
```yaml
VPN Connection:
  Type: Site-to-Site VPN
  Corporate Gateway: Bamboo subnet gateway
  AWS VPN Gateway: Attached to VPC
  
Routes:
  - Corporate to AWS: 10.0.0.0/16 → AWS VPC CIDR
  - AWS to Corporate: AWS VPC CIDR → 10.0.0.0/8
```

### 6. Service Account Configuration

#### Bitbucket Service Account
```yaml
Username: bamboo-cicd
Permissions:
  - Repository: Read, Clone
  - Project: Repository Admin (for webhooks)
  - Global: Personal Access Token creation

Personal Access Token Scopes:
  - Repositories: Read, Admin
  - Projects: Read
  - Webhooks: Read, Write
```

#### AWS Service Account (IAM)
```yaml
IAM User: bamboo-deployment
Policies:
  - ECR: Push/Pull images
  - EKS: Cluster access
  - S3: Terraform state access
  - IAM: Limited role assumption

Access Keys:
  - Access Key ID: [stored in Bamboo variables]
  - Secret Access Key: [stored in Bamboo variables]
```

## Deployment Strategies

### 7. Environment-Specific Deployments

#### Development Environment
```yaml
Trigger: Automatic on main branch push
Deployment Method: Direct kubectl apply
Rollback: Automatic on failure
Notifications: Slack channel

Bamboo Variables:
  KUBE_CONFIG: ${bamboo.dev.kubeconfig}
  ECR_REPOSITORY: 123456789.dkr.ecr.us-east-1.amazonaws.com/genai-dev
  ENVIRONMENT: dev
```

#### UAT Environment
```yaml
Trigger: Manual approval
Deployment Method: Helm upgrade
Rollback: Manual
Notifications: Email + Slack

Pre-deployment Tasks:
  - Database migration check
  - Smoke tests
  - Security validation
```

#### Production Environment
```yaml
Trigger: Manual approval + Multiple approvers
Deployment Method: Blue/Green via Helm
Rollback: Automated rollback capability
Notifications: Email + Slack + PagerDuty

Pre-deployment Requirements:
  - UAT sign-off
  - Security review
  - Performance testing results
  - Backup verification
```

### 8. Pipeline Automation Scripts

#### Bamboo Build Script
```bash
#!/bin/bash
# File: bamboo-build.sh

set -e

echo "🔧 Setting up build environment..."
export ENVIRONMENT=${bamboo.deploy.environment:-dev}
export BUILD_NUMBER=${bamboo.buildNumber}
export ECR_REPOSITORY=${bamboo.ECR_REPOSITORY}

echo "📦 Building applications..."
# Build each service
for service in risk_api web_app dash_app; do
    echo "Building $service..."
    cd services/$service
    docker build -t $ECR_REPOSITORY/$service:$BUILD_NUMBER .
    docker tag $ECR_REPOSITORY/$service:$BUILD_NUMBER $ECR_REPOSITORY/$service:latest
    cd ../../
done

echo "🚀 Pushing to ECR..."
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ECR_REPOSITORY
for service in risk_api web_app dash_app; do
    docker push $ECR_REPOSITORY/$service:$BUILD_NUMBER
    docker push $ECR_REPOSITORY/$service:latest
done

echo "✅ Build completed successfully!"
```

#### Deployment Script
```bash
#!/bin/bash
# File: bamboo-deploy.sh

set -e

ENVIRONMENT=${bamboo.deploy.environment}
BUILD_NUMBER=${bamboo.buildNumber}
ALB_ENDPOINT=${bamboo.INTERNAL_ALB_ENDPOINT}

echo "🚀 Deploying to $ENVIRONMENT environment..."

# Update Kubernetes manifests
cd deploy/kubernetes
sed -i "s/{{BUILD_NUMBER}}/$BUILD_NUMBER/g" */deployment.yaml

# Deploy via kubectl (Direct EKS API - bypasses ALB)
kubectl apply -f . --namespace=genai-$ENVIRONMENT

# Wait for rollout
kubectl rollout status deployment/risk-api --namespace=genai-$ENVIRONMENT
kubectl rollout status deployment/web-app --namespace=genai-$ENVIRONMENT
kubectl rollout status deployment/dash-app --namespace=genai-$ENVIRONMENT

echo "✅ Deployment to $ENVIRONMENT completed!"

# Post-deployment verification via Internal ALB
echo "🔍 Verifying services via Internal ALB..."
sleep 30  # Allow ALB target groups to register

# Test each service via ALB endpoints
services=("api" "web" "dash" "airflow")
for service in "${services[@]}"; do
    echo "Testing $service via ALB..."
    if curl -f --max-time 30 "$ALB_ENDPOINT/$service/health"; then
        echo "✅ $service service healthy via ALB"
    else
        echo "❌ $service service failed ALB health check"
        exit 1
    fi
done

echo "🎉 All services verified via Internal ALB!"
```

## Monitoring and Notifications

### 9. Build Monitoring

#### Bamboo Notifications
```yaml
Email Notifications:
  - Build Success: Project leads
  - Build Failure: Developers + Project leads
  - Deployment Success: Stakeholders
  - Deployment Failure: On-call team

Slack Integration:
  Webhook: https://hooks.slack.com/services/corporate/channel
  Channels:
    - #genai-builds (all builds)
    - #genai-deployments (deployments only)
    - #genai-alerts (failures only)
```

#### Build Metrics
```yaml
Metrics Collection:
  - Build duration
  - Test coverage
  - Deployment frequency
  - Lead time
  - Mean time to recovery

Dashboards:
  - Bamboo Plan dashboard
  - Custom Grafana dashboard
  - AWS CloudWatch metrics
```

## Security Considerations

### 10. Security Best Practices

#### Credential Management
- Store all secrets in Bamboo global/plan variables
- Use encrypted variables for sensitive data
- Rotate service account credentials regularly
- Implement least-privilege access

#### Network Security
- Restrict Bamboo server access to required ports only
- Use VPN for AWS API access
- Implement network segmentation
- Monitor and log all network connections

#### Code Security
- Implement SAST scanning in pipeline
- Container vulnerability scanning
- Dependency checking
- Infrastructure as Code security scanning

This configuration provides a comprehensive CI/CD setup that works entirely within your corporate intranet while securely deploying to AWS infrastructure through the VPN connection.

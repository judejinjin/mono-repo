# Internal ALB Role in Bamboo CI/CD Process

## Overview
The Internal Application Load Balancer (ALB) plays a **runtime access role** rather than a direct deployment role in the Bamboo CI/CD process. Here's the detailed breakdown:

## Internal ALB in CI/CD Context

### 🎯 **Primary Role: Runtime Service Access**
The Internal ALB is **NOT directly involved** in the CI/CD deployment process itself, but serves as the **access point** for deployed services.

### 🔄 **CI/CD Process Flow**

#### **Deployment Phase (Bamboo → EKS)**
```
Bamboo Server → VPN → EKS API Server → Pod Deployment
    ↓
Direct kubectl/helm commands to EKS
    ↓
Applications deployed to EKS pods
    ↓
Kubernetes Services created
```

#### **Runtime Access Phase (Users → Applications)**
```
Corporate Users → Internal ALB → Ingress Controller → EKS Services
```

## Detailed CI/CD Flow Analysis

### 1. **Build & Test Phase**
- **ALB Involvement**: ❌ None
- **Process**: Bamboo builds, tests, and packages applications
- **Target**: ECR (Elastic Container Registry)
- **Connection**: Direct AWS API calls via VPN

### 2. **Deployment Phase**
- **ALB Involvement**: ❌ None (direct EKS API access)
- **Process**: Bamboo deploys to EKS using kubectl/helm
- **Connection**: Bamboo → VPN → EKS API Server
- **Commands**:
  ```bash
  kubectl apply -f deployment.yaml
  helm upgrade myapp ./charts/myapp
  ```

### 3. **Post-Deployment Verification**
- **ALB Involvement**: ✅ **YES - Health Checks & Testing**
- **Process**: Bamboo tests deployed services via ALB endpoints
- **Connection**: Bamboo → VPN → Internal ALB → Services

### 4. **Runtime Operations**
- **ALB Involvement**: ✅ **YES - Service Access**
- **Process**: Corporate users access applications
- **Connection**: Corporate Network → Internal ALB → Applications

## Bamboo Deployment Methods

### **Method 1: Direct EKS API Access (Current)**
```yaml
Bamboo Deployment Task:
  Type: Script
  Commands:
    - aws eks update-kubeconfig --name genai-cluster
    - kubectl apply -f k8s-manifests/
    - kubectl rollout status deployment/risk-api
    
Connection Path:
  Bamboo → Corporate VPN → AWS VPC → EKS API Server
```

### **Method 2: ALB Health Check Validation**
```yaml
Post-Deployment Verification:
  Type: Script
  Commands:
    - curl -f http://internal-alb.corporate.aws/api/health
    - curl -f http://internal-alb.corporate.aws/web/health
    - curl -f http://internal-alb.corporate.aws/airflow/health
    
Connection Path:
  Bamboo → Corporate VPN → Internal ALB → Applications
```

## Internal ALB Configuration for CI/CD

### **Target Group Health Checks**
```hcl
# Health check endpoints that Bamboo can verify
resource "aws_lb_target_group" "fastapi" {
  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    path                = "/api/health"
    matcher             = "200"
  }
}
```

### **ALB Endpoints for Testing**
```yaml
Service Endpoints (accessible via ALB):
  - FastAPI: http://internal-alb.genai.corporate/api/
  - Web Apps: http://internal-alb.genai.corporate/web/
  - Dash: http://internal-alb.genai.corporate/dash/
  - Airflow: http://internal-alb.genai.corporate/airflow/
```

## Enhanced CI/CD Pipeline with ALB Integration

### **Updated Bamboo Pipeline Stages**

#### **Stage 1-3: Build, Test, Package (No ALB)**
```yaml
Jobs:
  - Source Checkout
  - Build Applications  
  - Run Unit Tests
  - Build Docker Images
  - Push to ECR
```

#### **Stage 4: Deploy to EKS (No ALB)**
```yaml
Deployment Task:
  - kubectl apply -f manifests/
  - helm upgrade applications ./charts/
  - kubectl wait --for=condition=ready pod -l app=risk-api
```

#### **Stage 5: Post-Deployment Verification (Uses ALB)**
```yaml
Verification Tasks:
  - Health Check via ALB endpoints
  - Smoke tests via ALB routes
  - Performance validation
  - Integration test execution

Example Script:
#!/bin/bash
ALB_ENDPOINT="http://internal-alb.genai.corporate"

# Test each service via ALB
curl -f $ALB_ENDPOINT/api/health || exit 1
curl -f $ALB_ENDPOINT/web/health || exit 1  
curl -f $ALB_ENDPOINT/dash/health || exit 1
curl -f $ALB_ENDPOINT/airflow/health || exit 1

echo "✅ All services healthy via Internal ALB"
```

## Network Architecture Implications

### **Deployment Network Path**
```
Bamboo Server (Corporate) 
    ↓ VPN Connection
AWS VPC Management Subnets
    ↓ Direct API Access  
EKS Control Plane
    ↓ Pod Scheduling
EKS Worker Nodes (Private Subnets)
```

### **Verification Network Path**
```
Bamboo Server (Corporate)
    ↓ VPN Connection
AWS VPC Management Subnets
    ↓ HTTP Requests
Internal ALB (Management Subnets)
    ↓ Load Balancing
Ingress Controller (Private Subnets)
    ↓ Service Routing
Application Pods (Private Subnets)
```

## Key Differences: Deployment vs Access

| Aspect | Deployment Process | Runtime Access |
|--------|-------------------|----------------|
| **Bamboo Role** | Deploy via EKS API | Test via ALB endpoints |
| **Network Path** | Direct to EKS API | Via Internal ALB |
| **Purpose** | Deploy applications | Access applications |
| **ALB Involvement** | None | Central access point |
| **Frequency** | During deployments | Continuous |

## Bamboo Configuration Updates

### **Environment Variables**
```yaml
Bamboo Global Variables:
  # For Deployment
  EKS_CLUSTER_NAME: genai-${environment}-cluster
  EKS_REGION: us-east-1
  
  # For Testing/Verification  
  INTERNAL_ALB_ENDPOINT: http://internal-alb.genai.corporate
  ALB_HEALTH_CHECK_TIMEOUT: 30
```

### **Post-Deployment Script**
```bash
#!/bin/bash
# File: bamboo-post-deploy-verification.sh

set -e

ENVIRONMENT=${bamboo.deploy.environment}
ALB_ENDPOINT=${bamboo.INTERNAL_ALB_ENDPOINT}

echo "🔍 Verifying deployment via Internal ALB..."

# Wait for ALB target groups to be healthy
sleep 30

# Test each service endpoint
services=("api" "web" "dash" "airflow")
for service in "${services[@]}"; do
    echo "Testing $service service..."
    if curl -f --max-time 30 "$ALB_ENDPOINT/$service/health"; then
        echo "✅ $service service is healthy"
    else
        echo "❌ $service service failed health check"
        exit 1
    fi
done

echo "🎉 All services verified successfully via Internal ALB!"
```

## Summary

### **Internal ALB's Role in CI/CD:**
- ❌ **NOT involved** in actual deployment process
- ✅ **IS involved** in post-deployment verification
- ✅ **IS the access point** for runtime operations
- ✅ **Enables health checking** and smoke testing

### **CI/CD Flow with ALB:**
1. **Deploy**: Bamboo → EKS API (bypasses ALB)
2. **Verify**: Bamboo → Internal ALB → Services (uses ALB)
3. **Access**: Users → Internal ALB → Services (uses ALB)

The Internal ALB serves as the **verification and access layer** rather than the **deployment layer** in your CI/CD process.

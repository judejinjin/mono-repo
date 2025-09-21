# Architecture Update: Bamboo Deployment Removal

## Overview
The architecture has been updated to remove Bamboo deployment from the AWS EKS cluster, as the organization will leverage existing corporate Bamboo servers for CI/CD automation.

## Key Changes Made

### 1. **AWS Architecture Components (Updated)**
```yaml
EKS Cluster Applications:
  - FastAPI (Risk Management API)
  - Web Applications (Frontend Services)
  - Dash (Analytics Dashboard)
  - Airflow (Workflow Management)
  # Bamboo REMOVED - using existing corporate servers
```

### 2. **CI/CD Architecture Pattern**
```
Corporate Network:
  ├── Bitbucket Server (Source Control)
  ├── Bamboo Server (CI/CD) ← Existing Corporate Infrastructure
  └── On-Premise Development Server

AWS Cloud (via VPN):
  ├── Internal ALB (Management Subnets)
  ├── EKS Cluster (Private Subnets)
  │   ├── FastAPI
  │   ├── Web Apps
  │   ├── Dash
  │   └── Airflow
  └── ECR (Container Registry)
```

## Benefits of This Approach

### 1. **Infrastructure Optimization**
- **Reduced AWS Costs**: No need for Bamboo EC2 instances or EKS pods
- **Simplified Architecture**: Fewer components to manage in AWS
- **Resource Efficiency**: Better utilization of existing corporate infrastructure

### 2. **Operational Advantages**
- **Centralized CI/CD**: All build processes managed by corporate IT
- **Consistent Tooling**: Same Bamboo environment across all projects
- **Corporate Compliance**: CI/CD remains within corporate security perimeter
- **Existing Expertise**: Leverage current team knowledge of Bamboo

### 3. **Security Benefits**
- **Corporate Control**: Build processes remain in corporate network
- **Reduced Attack Surface**: Fewer AWS components exposed
- **Consistent Security Policies**: Same security controls as other projects

## Updated Architecture Flow

### **Development Workflow**
```
1. Developer commits code → Bitbucket (Corporate)
2. Bitbucket webhook → Bamboo Server (Corporate)
3. Bamboo builds/tests → Within Corporate Network
4. Bamboo pushes images → ECR (via VPN)
5. Bamboo deploys → EKS (via VPN)
6. Bamboo verifies → Internal ALB (via VPN)
```

### **Network Architecture**
```
Corporate Intranet:
  ├── Source Control (Bitbucket)
  ├── CI/CD Platform (Bamboo)
  └── Development Team
       ↓ VPN Connection
AWS VPC:
  ├── Management Subnets
  │   └── Internal ALB
  └── Private Subnets
      └── EKS Cluster (4 applications)
```

## Infrastructure Components

### **Corporate Side (Existing)**
- **Bitbucket Server**: Source code management
- **Bamboo Server**: Automated CI/CD pipeline
- **Corporate Network**: Security, monitoring, compliance

### **AWS Side (Deployed via Terraform)**
- **VPC with VPN Connection**: Secure connectivity to corporate network
- **Internal Application Load Balancer**: Corporate intranet access
- **EKS Cluster**: Container orchestration platform
- **Application Services**: FastAPI, Web Apps, Dash, Airflow
- **ECR Registry**: Container image storage

## Files Updated

### **Architecture Diagrams**
- ✅ `create_architecture_diagrams.py`: Removed Bamboo from EKS components
- ✅ Main architecture diagrams regenerated (dev, uat, prod)
- ✅ CI/CD flow diagram remains accurate (shows corporate Bamboo)

### **Terraform Configuration**
- ✅ No changes needed - Bamboo was never deployed via Terraform
- ✅ All AWS infrastructure remains focused on application services

### **Kubernetes Deployments**
- ✅ No changes needed - Bamboo was never deployed to Kubernetes
- ✅ Application deployments (FastAPI, Web Apps, Dash, Airflow) unchanged

## Deployment Process

### **Corporate Bamboo Configuration**
```yaml
Bamboo Plan Configuration:
  Source: Bitbucket repository
  Build: Corporate Bamboo agents
  Deploy Target: AWS EKS (via VPN)
  
Connection Requirements:
  - VPN access to AWS VPC
  - ECR push permissions
  - EKS API access
  - kubectl/helm configuration
```

### **AWS Resource Access**
```yaml
Bamboo Service Account:
  IAM Permissions:
    - ECR: Push/Pull container images
    - EKS: Cluster API access
    - VPC: Network connectivity via VPN
  
Network Access:
  - Corporate firewall rules for AWS APIs
  - VPN tunnel for EKS communication
  - Internal ALB access for verification
```

## Monitoring and Operations

### **Build Monitoring**
- **Corporate Bamboo Dashboard**: All build status and metrics
- **AWS CloudWatch**: Application performance and health
- **Internal ALB**: Health checks and traffic metrics

### **Deployment Verification**
- **Bamboo Post-Deploy Tasks**: Health checks via Internal ALB
- **EKS Monitoring**: Pod status and resource utilization
- **Application Metrics**: Service-specific monitoring

## Migration Considerations

### **If Migrating from Previous Bamboo-in-EKS Setup**
1. **Remove Bamboo Kubernetes deployments** (if any existed)
2. **Update Bamboo configuration** to target EKS externally
3. **Configure VPN connectivity** for Bamboo servers
4. **Update service discovery** to use Internal ALB endpoints
5. **Migrate build agents** to corporate Bamboo infrastructure

### **Network Configuration Updates**
1. **Corporate Firewall**: Allow Bamboo → AWS API access
2. **VPN Configuration**: Ensure Bamboo can reach EKS
3. **DNS Configuration**: Internal ALB endpoint resolution
4. **Security Groups**: Allow corporate Bamboo IP ranges

## Cost Impact

### **AWS Cost Reduction**
- **EC2 Instances**: No Bamboo servers in AWS
- **EKS Node Resources**: Reduced cluster size requirements
- **Data Transfer**: Reduced inter-service communication

### **Corporate Infrastructure**
- **Existing Bamboo Capacity**: Utilize current servers
- **Network Costs**: VPN usage for deployments only
- **Operational Efficiency**: Centralized CI/CD management

This architectural approach provides the best of both worlds: leveraging existing corporate CI/CD infrastructure while maintaining modern cloud-native application deployment patterns.

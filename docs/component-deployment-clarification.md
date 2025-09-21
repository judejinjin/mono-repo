# Component Deployment Clarification

## 🎯 **Component Deployment Architecture**

Based on the Terraform configurations and Kubernetes deployment manifests, here's the **exact deployment topology** for all components:

## ☸️ **EKS Cluster Components (Running in Kubernetes)**

All of the following components are **deployed as Kubernetes pods inside the EKS cluster**:

### ✅ **FastAPI Services**
- **Location**: EKS Cluster (Private Subnets)
- **Deployment**: Kubernetes Deployment + Service
- **Configuration**: `deploy/kubernetes/fastapi/deployment.yaml`
- **Container**: `mono-repo/fastapi:${image_tag}`
- **Replicas**: Environment-specific (dev: 1-2, uat: 2-3, prod: 3-6)
- **Access**: Through Application Load Balancer → EKS Ingress

### ✅ **Web Applications (React/Vue)**
- **Location**: EKS Cluster (Private Subnets)
- **Deployment**: Kubernetes Deployment + Service
- **Configuration**: `deploy/kubernetes/web/`
- **Container**: Nginx serving static assets + Node.js backend
- **Replicas**: Environment-specific
- **Access**: Through Application Load Balancer → EKS Ingress

### ✅ **Dash Analytics Applications**
- **Location**: EKS Cluster (Private Subnets)
- **Deployment**: Kubernetes Deployment + Service
- **Configuration**: `deploy/kubernetes/dash/`
- **Container**: Python Dash application
- **Replicas**: Environment-specific
- **Access**: Through Application Load Balancer → EKS Ingress

### ✅ **Apache Airflow**
- **Location**: EKS Cluster (Private Subnets)
- **Deployment**: Helm Chart with custom values
- **Configuration**: `deploy/kubernetes/airflow/values-{env}.yaml`
- **Components**:
  - **Webserver**: Airflow UI (1-2 pods)
  - **Scheduler**: DAG scheduler (1 pod)
  - **Workers**: KubernetesExecutor (dynamic pods)
- **Database**: External PostgreSQL RDS
- **Access**: Through EKS Service (internal) or LoadBalancer

### ✅ **Bamboo CI/CD Server**
- **Location**: EKS Cluster (Private Subnets)  
- **Deployment**: Kubernetes Deployment + PVC
- **Container**: Atlassian Bamboo
- **Storage**: Persistent Volume for build artifacts
- **Access**: Through EKS Service or LoadBalancer
- **Integration**: Access to EKS cluster for deployments

## 🖥️ **EC2 Instance Components (Outside EKS)**

### ✅ **Development Server**
- **Location**: EC2 Instance (Public Subnet)
- **Instance Type**: t3.medium (dev), t3.large (uat/prod)
- **Purpose**: 
  - Developer SSH access via VS Code Remote
  - Python 3.11+ virtual environments
  - Node.js development environment
  - Git operations and testing
- **NOT running applications** - just development tools

## 🗄️ **Database Layer (Outside EKS)**

### ✅ **RDS PostgreSQL**
- **Location**: Database Subnets (Private)
- **Purpose**: 
  - Transactional data for applications
  - Airflow metadata database
- **Access**: Only from EKS cluster and dev server

### ✅ **Snowflake Data Warehouse**
- **Location**: External (Snowflake Cloud)
- **Purpose**: Analytics and data warehousing
- **Access**: From EKS applications via secure connection

## 📦 **Storage Layer (Outside EKS)**

### ✅ **S3 Buckets**
- **Location**: AWS S3 (Regional)
- **Purpose**: Object storage, backups, static assets
- **Access**: From EKS applications via IAM roles

## 🔄 **Data Flow Architecture**

```
Internet → ALB → EKS Cluster → Applications (FastAPI, Web, Dash, Airflow)
                     ↓
              Database Layer (RDS, Snowflake)
                     ↓
              Storage Layer (S3)

Developer → SSH → EC2 Dev Server (development only)
```

## 🏗️ **Network Architecture**

### VPC Structure:
- **Public Subnets**: ALB, NAT Gateways, Dev Server
- **Private Subnets**: EKS Worker Nodes (all applications run here)
- **Database Subnets**: RDS instances

### Security:
- **EKS applications**: No direct internet access (through NAT)
- **Databases**: Only accessible from EKS and dev server
- **Load Balancer**: Public-facing entry point

## ✅ **Clarification Summary**

### **Running IN EKS Cluster:**
1. ✅ FastAPI Services (Kubernetes pods)
2. ✅ Web Applications (Kubernetes pods)
3. ✅ Dash Analytics (Kubernetes pods)
4. ✅ Apache Airflow (Helm deployment with multiple pods)
5. ✅ Bamboo CI/CD (Kubernetes deployment)

### **Running OUTSIDE EKS Cluster:**
1. ❌ Development Server (on-premise Linux server for developers)
2. ❌ RDS PostgreSQL (Managed AWS service)
3. ❌ Snowflake (External cloud service)
4. ❌ S3 Storage (Managed AWS service)
5. ❌ Load Balancers (AWS ALB/NLB services)

## 🎯 **Key Points**

1. **All application workloads run in EKS** - no applications run directly on EC2
2. **Development server is for developers only** - not for running production applications
3. **Databases are external services** - RDS and Snowflake, not in containers
4. **Storage is external** - S3 buckets, not container storage
5. **Load balancing is handled by AWS ALB** - traffic flows to EKS via ingress

This architecture provides:
- **Scalability**: Kubernetes auto-scaling for all applications
- **High Availability**: Multi-AZ deployment across private subnets
- **Security**: Applications isolated in private subnets
- **Cost Efficiency**: Shared EKS cluster for all workloads
- **Development Flexibility**: Dedicated EC2 for developer access

The updated architecture diagrams now correctly show this topology with all application components grouped within the EKS cluster boundary.

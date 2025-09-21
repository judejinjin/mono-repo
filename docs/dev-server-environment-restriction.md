# Development Server Environment Restriction

## 🎯 **Changes Made**

The development server has been properly restricted to only exist in the **dev environment**, as developers should not have direct access to UAT or Production environments.

## 🔧 **Terraform Configuration Updates**

### 1. **New Variable Added**
```hcl
variable "create_dev_server" {
  description = "Whether to create development server (only for dev environment)"
  type        = bool
  default     = false
}
```

### 2. **Environment-Specific Configuration**

#### **Development Environment** (`dev.tfvars`)
```hcl
# Dev Server Configuration (only in dev environment)
create_dev_server        = true
dev_server_instance_type = "t3.medium"
dev_server_key_name      = "mono-repo-dev-key"
```

#### **UAT Environment** (`uat.tfvars`)
```hcl
# Dev Server Configuration (disabled in UAT)
create_dev_server        = false
dev_server_instance_type = "t3.large"  # Not used
dev_server_key_name      = ""          # Not needed in UAT
```

#### **Production Environment** (`prod.tfvars`)
```hcl
# Dev Server Configuration (disabled in production)
create_dev_server        = false
dev_server_instance_type = "t3.large"  # Not used
dev_server_key_name      = ""          # Not needed in production
```

### 3. **New Terraform Resources** (`dev_server.tf`)

#### **Conditional EC2 Instance**
```hcl
resource "aws_instance" "dev_server" {
  count = var.create_dev_server ? 1 : 0
  # ... configuration only applies when create_dev_server = true
}
```

#### **Security Group for Dev Server**
```hcl
resource "aws_security_group" "dev_server" {
  count = var.create_dev_server ? 1 : 0
  # SSH (22), HTTP (8000), HTTPS (8443), Node.js (3000)
}
```

#### **Elastic IP for Consistent Access**
```hcl
resource "aws_eip" "dev_server" {
  count = var.create_dev_server ? 1 : 0
  # Provides stable public IP for SSH access
}
```

### 4. **Development Server Setup** (`user_data.sh`)

The dev server is automatically configured with:
- **Python 3.11+** with virtual environment
- **Node.js 18.x** with global packages
- **Docker** with user permissions
- **kubectl** for Kubernetes access
- **AWS CLI v2** for infrastructure management
- **Terraform** for infrastructure as code
- **Development tools**: git, vim, htop, etc.
- **Useful aliases** and environment setup

## 🎨 **Updated Architecture Diagrams**

### **Development Environment**
- ✅ **Shows Dev Server**: EC2 instance in public subnet
- ✅ **SSH/kubectl Connection**: Dashed arrow to EKS cluster
- ✅ **Full Development Setup**: Complete development infrastructure

### **UAT Environment**
- ❌ **No Dev Server**: Clean production-like environment
- ✅ **EKS Cluster Only**: Applications and services only
- ✅ **Database & Storage**: External services remain

### **Production Environment**
- ❌ **No Dev Server**: Pure production environment
- ✅ **EKS Cluster Only**: Applications and services only
- ✅ **Database & Storage**: External services remain

## 🏗️ **Development Workflow**

### **Developers Work in Dev Environment**
1. **SSH to Dev Server**: `ssh -i ~/.ssh/mono-repo-dev-key.pem ubuntu@<dev-server-ip>`
2. **Clone Repository**: `git clone <repo-url> ~/workspace/mono-repo`
3. **Develop & Test**: Use Python/Node.js environments on dev server
4. **Deploy to Dev EKS**: Test deployments in dev Kubernetes cluster
5. **Submit PR**: Push changes and create pull request

### **Higher Environments (UAT/Prod)**
1. **CI/CD Only**: Bamboo handles all deployments
2. **No Direct Access**: Developers cannot SSH to these environments
3. **Automated Deployment**: Code flows through CI/CD pipeline
4. **Monitoring Only**: Developers can view logs/metrics but not modify

## ✅ **Security Benefits**

1. **Environment Isolation**: Developers can't accidentally modify UAT/prod
2. **Controlled Access**: Only dev environment has direct access
3. **Audit Trail**: All UAT/prod changes go through CI/CD
4. **Cost Optimization**: No unnecessary EC2 instances in higher environments
5. **Best Practices**: Follows enterprise development patterns

## 📊 **Cost Impact**

### **Before** (Dev server in all environments)
- **Dev**: 1 x t3.medium EC2 (~$30/month)
- **UAT**: 1 x t3.large EC2 (~$60/month)
- **Prod**: 1 x t3.large EC2 (~$60/month)
- **Total**: ~$150/month for dev servers

### **After** (Dev server only in dev)
- **Dev**: 1 x t3.medium EC2 (~$30/month)
- **UAT**: No dev server ($0/month)
- **Prod**: No dev server ($0/month)
- **Total**: ~$30/month for dev servers
- **Savings**: ~$120/month (80% cost reduction)

## 🎯 **Architecture Compliance**

This change aligns with enterprise best practices:
- ✅ **Separation of Concerns**: Dev vs. production environments
- ✅ **Least Privilege**: Developers only access what they need
- ✅ **Cost Optimization**: Resources only where needed
- ✅ **Security Compliance**: Reduced attack surface
- ✅ **Operational Excellence**: Clear environment boundaries

The updated Terraform configuration and diagrams now properly reflect that development servers are only needed in the development environment, where developers actually write and test code. UAT and Production environments remain clean and focused solely on running applications through automated CI/CD processes.

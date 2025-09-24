# Software Requirements for Dev Server Infrastructure Maintenance

This document lists all the software that needs to be installed on the development server to maintain the mono-repo infrastructure. Python packages are excluded as they are managed via `requirements.txt`.

## Core System Tools

### 1. Essential System Utilities

#### **curl & wget**
- **Purpose**: Download files, API calls, package installation
- **Usage**: AWS CLI installation, Terraform downloads, API testing
- **Installation**:
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y curl wget

# RHEL/CentOS
sudo yum install -y curl wget
```

#### **git**
- **Purpose**: Version control, repository management
- **Usage**: Code deployment, configuration management
- **Installation**:
```bash
# Ubuntu/Debian
sudo apt-get install -y git

# RHEL/CentOS
sudo yum install -y git
```

#### **unzip**
- **Purpose**: Extract compressed files (AWS CLI, Terraform)
- **Usage**: Package installation, archive extraction
- **Installation**:
```bash
# Ubuntu/Debian
sudo apt-get install -y unzip

# RHEL/CentOS
sudo yum install -y unzip
```

### 2. Development Tools

#### **vim**
- **Purpose**: Text editor for configuration files
- **Usage**: Editing configs, troubleshooting, log review
- **Installation**:
```bash
# Ubuntu/Debian
sudo apt-get install -y vim

# RHEL/CentOS
sudo yum install -y vim
```

#### **htop**
- **Purpose**: System monitoring and process management
- **Usage**: Performance monitoring, resource usage tracking
- **Installation**:
```bash
# Ubuntu/Debian
sudo apt-get install -y htop

# RHEL/CentOS
sudo yum install -y htop
```

#### **tree**
- **Purpose**: Directory structure visualization
- **Usage**: File structure analysis, documentation
- **Installation**:
```bash
# Ubuntu/Debian
sudo apt-get install -y tree

# RHEL/CentOS
sudo yum install -y tree
```

## Infrastructure Management Tools

### 3. Cloud & Infrastructure

#### **AWS CLI v2** ⭐ CRITICAL
- **Purpose**: AWS resource management and deployment
- **Usage**: EKS management, S3 operations, IAM configuration
- **Installation**:
```bash
# Linux x86_64
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
rm -rf aws awscliv2.zip

# Verify installation
aws --version
```

#### **Terraform** ⭐ CRITICAL
- **Purpose**: Infrastructure as Code (IaC) management
- **Usage**: AWS infrastructure deployment, state management
- **Installation**:
```bash
# Ubuntu/Debian
wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt-get update
sudo apt-get install -y terraform

# Verify installation
terraform --version
```

### 4. Container & Orchestration

#### **Docker** ⭐ CRITICAL
- **Purpose**: Containerization and image management
- **Usage**: Building application images, local testing
- **Installation**:
```bash
# Ubuntu/Debian
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER

# Verify installation
docker --version
docker-compose --version
```

#### **kubectl** ⭐ CRITICAL
- **Purpose**: Kubernetes cluster management
- **Usage**: EKS cluster operations, pod management, debugging
- **Installation**:
```bash
# Latest stable version
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Verify installation
kubectl version --client
```

#### **Helm** ⭐ CRITICAL
- **Purpose**: Kubernetes package management
- **Usage**: Airflow deployment, application charts management
- **Installation**:
```bash
# Using script
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Or using package manager (Ubuntu/Debian)
curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | sudo tee /usr/share/keyrings/helm.gpg > /dev/null
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
sudo apt-get update
sudo apt-get install -y helm

# Verify installation
helm version
```

## Visualization & Documentation Tools

### 5. Diagram Generation

#### **Graphviz** ⭐ CRITICAL
- **Purpose**: Generate infrastructure diagrams from DOT files
- **Usage**: Terraform dependency graphs, architecture visualization
- **Installation**:
```bash
# Ubuntu/Debian
sudo apt-get install -y graphviz

# RHEL/CentOS
sudo yum install -y graphviz

# Verify installation
dot -V
```

#### **inframap**
- **Purpose**: Generate AWS infrastructure diagrams from Terraform
- **Usage**: Visual AWS infrastructure documentation
- **Installation**:
```bash
# Using Go (if Go is installed)
go install github.com/cycloidio/inframap@latest

# Or download binary from releases
wget https://github.com/cycloidio/inframap/releases/download/v0.8.0/inframap-linux-amd64.tar.gz
tar -xzf inframap-linux-amd64.tar.gz
sudo mv inframap-linux-amd64 /usr/local/bin/inframap
rm inframap-linux-amd64.tar.gz

# Verify installation
inframap version
```

## Development Environment

### 6. Runtime Environments

#### **Python 3.11+** ⭐ CRITICAL
- **Purpose**: Application runtime and package management
- **Usage**: All Python applications, build scripts, deployment tools
- **Installation**:
```bash
# Ubuntu/Debian
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip python3.11-distutils

# Set as default
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1

# Verify installation
python --version
pip --version
```

#### **Node.js 18.x** ⭐ CRITICAL
- **Purpose**: Frontend application runtime and build tools
- **Usage**: React/Vue applications, build processes
- **Installation**:
```bash
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version
npm --version
```

### 7. Build Dependencies

#### **Build Essential Tools**
- **Purpose**: Compiling native packages and dependencies
- **Usage**: Building Python packages with C extensions
- **Installation**:
```bash
# Ubuntu/Debian
sudo apt-get install -y \
    build-essential \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release

# RHEL/CentOS
sudo yum groupinstall -y "Development Tools"
sudo yum install -y \
    gcc \
    gcc-c++ \
    make \
    openssl-devel \
    libffi-devel
```

## Utility & Monitoring Tools

### 8. Process Management

#### **timeout**
- **Purpose**: Command execution with time limits
- **Usage**: Prevent hanging operations in scripts
- **Installation**:
```bash
# Usually pre-installed in coreutils
# Ubuntu/Debian
sudo apt-get install -y coreutils

# Verify availability
timeout --version
```

### 9. Optional but Recommended

#### **jq**
- **Purpose**: JSON processing and parsing
- **Usage**: API response processing, configuration parsing
- **Installation**:
```bash
# Ubuntu/Debian
sudo apt-get install -y jq

# RHEL/CentOS
sudo yum install -y jq

# Verify installation
jq --version
```

#### **yq**
- **Purpose**: YAML processing and parsing
- **Usage**: Kubernetes manifest processing, configuration management
- **Installation**:
```bash
# Using pip (if Python is installed)
pip install yq

# Or using snap
sudo snap install yq

# Verify installation
yq --version
```

## Installation Verification Script

Create and run this verification script to ensure all tools are properly installed:

```bash
#!/bin/bash
# software-verification.sh

echo "🔍 Verifying Software Installation..."

tools=(
    "curl --version"
    "wget --version"
    "git --version"
    "unzip -v"
    "vim --version"
    "htop --version"
    "tree --version"
    "aws --version"
    "terraform --version"
    "docker --version"
    "kubectl version --client"
    "helm version"
    "dot -V"
    "inframap version"
    "python --version"
    "node --version"
    "npm --version"
    "timeout --version"
    "jq --version"
)

for tool in "${tools[@]}"; do
    if eval $tool &>/dev/null; then
        echo "✅ $tool"
    else
        echo "❌ $tool - NOT INSTALLED"
    fi
done

echo "🏁 Verification complete!"
```

## Critical Dependencies Summary

**Essential for Infrastructure Management:**
- ✅ **AWS CLI v2** - Cloud resource management
- ✅ **Terraform** - Infrastructure as Code
- ✅ **Docker** - Containerization
- ✅ **kubectl** - Kubernetes management
- ✅ **Helm** - Kubernetes package management
- ✅ **Graphviz** - Diagram generation
- ✅ **Python 3.11+** - Runtime environment
- ✅ **Node.js 18.x** - Frontend runtime

**System Requirements:**
- Linux-based OS (Ubuntu 20.04+ recommended)
- Minimum 4GB RAM, 20GB storage
- Internet connectivity for package downloads
- Sudo privileges for software installation

## Environment Setup

After installing all software, set up the development environment:

```bash
# 1. Create workspace directory
mkdir -p ~/workspace
cd ~/workspace

# 2. Clone repository
git clone <repository-url> mono-repo
cd mono-repo

# 3. Set up Python virtual environment
python3.11 -m venv venv
source venv/bin/activate

# 4. Install Python dependencies
pip install -r requirements.txt

# 5. Install Node.js dependencies
npm install

# 6. Configure AWS CLI
aws configure

# 7. Initialize Terraform
cd infrastructure/terraform
terraform init
```

## Maintenance Commands

Regular maintenance commands to keep software updated:

```bash
# Update system packages
sudo apt-get update && sudo apt-get upgrade -y

# Update AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install --update

# Update Terraform
# Check latest version and download accordingly
terraform version

# Update Node.js packages
npm update -g

# Update Python packages
pip list --outdated
pip install --upgrade <package-name>
```

---

**Note**: This document covers all software dependencies identified in the mono-repo infrastructure. Python packages are managed separately through `requirements.txt` files in the `build/requirements/` directory.

**Last Updated**: September 23, 2025
**Repository**: mono-repo
**Environment**: Development Server Infrastructure
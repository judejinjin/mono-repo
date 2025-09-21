# Terraform Architecture Visualization Guide

This guide provides multiple methods to generate architecture diagrams from our Terraform infrastructure code.

## 🎨 Visualization Tools Overview

### 1. **Terraform Graph + Graphviz** (Built-in)
- **Pros**: Built into Terraform, free, works offline
- **Cons**: Basic visualization, requires Graphviz installation
- **Best for**: Quick dependency visualization

### 2. **Inframap** (Recommended)
- **Pros**: Beautiful AWS-specific diagrams, automatic resource detection
- **Cons**: Limited to AWS resources
- **Best for**: AWS infrastructure diagrams

### 3. **Blast Radius**
- **Pros**: Interactive web-based visualization
- **Cons**: Requires Python, complex setup
- **Best for**: Interactive exploration

### 4. **Rover** (HashiCorp)
- **Pros**: Official HashiCorp tool, good for Terraform Cloud
- **Cons**: Requires Terraform Cloud/Enterprise
- **Best for**: Enterprise environments

### 5. **Terraform Visual**
- **Pros**: Simple online tool, no installation
- **Cons**: Limited customization, security concerns for sensitive configs
- **Best for**: Quick prototyping

### 6. **Draw.io/Lucidchart Integration**
- **Pros**: Professional diagrams, customizable
- **Cons**: Manual process, requires maintenance
- **Best for**: Presentation-ready diagrams

## 🚀 Implementation Methods

### Method 1: Terraform Graph (Quick Start)

```bash
# Generate basic dependency graph
terraform graph | dot -Tpng > infrastructure_graph.png

# Generate with more detail
terraform graph -type=plan | dot -Tpng > infrastructure_plan.png

# Generate in SVG for better quality
terraform graph | dot -Tsvg > infrastructure_graph.svg
```

**Requirements:**
```bash
# Install Graphviz
# Windows (using Chocolatey)
choco install graphviz

# macOS
brew install graphviz

# Ubuntu/Debian
sudo apt-get install graphviz
```

### Method 2: Inframap (Recommended for AWS)

**Installation:**
```bash
# Download latest release from GitHub
curl -LO https://github.com/cycloidio/inframap/releases/latest/download/inframap-linux-amd64.tar.gz
tar -xzf inframap-linux-amd64.tar.gz
sudo mv inframap /usr/local/bin/

# Or using Go
go install github.com/cycloidio/inframap@latest
```

**Usage:**
```bash
# Generate from Terraform state
inframap generate --tfstate terraform.tfstate | dot -Tpng > aws_infrastructure.png

# Generate from Terraform plan
terraform plan -out=plan.out
terraform show -json plan.out > plan.json
inframap generate plan.json | dot -Tpng > aws_infrastructure_plan.png

# Generate in SVG with better quality
inframap generate --tfstate terraform.tfstate | dot -Tsvg > aws_infrastructure.svg
```

### Method 3: Blast Radius (Interactive)

**Installation:**
```bash
pip install BlastRadius
```

**Usage:**
```bash
# Run from terraform directory
blast-radius --serve --port 8000

# Open browser to http://localhost:8000
```

### Method 4: Custom Python Script

We can create a custom script that parses our Terraform files and generates diagrams using Python libraries.

## 📋 Step-by-Step Implementation

### Option A: Quick Setup with Terraform Graph

1. **Install Graphviz**
2. **Run commands from terraform directory**
3. **Generate multiple formats**

### Option B: Professional Setup with Inframap

1. **Install Inframap**
2. **Generate Terraform plan**
3. **Create high-quality diagrams**

### Option C: Interactive Setup with Blast Radius

1. **Install Python dependencies**
2. **Run interactive server**
3. **Explore infrastructure interactively**

## 🔧 Automation Scripts

We can create scripts to automatically generate diagrams as part of our CI/CD pipeline or development workflow.

## 📊 Output Examples

### Terraform Graph Output
- Shows resource dependencies
- Basic node-and-edge visualization
- Good for understanding relationships

### Inframap Output
- AWS-specific icons and layouts
- Subnet and VPC visualization
- Security group relationships
- Load balancer configurations

### Blast Radius Output
- Interactive exploration
- Zoom and pan capabilities
- Resource details on hover
- Change impact visualization

## 🎯 Recommended Approach

For our mono-repo infrastructure, I recommend:

1. **Inframap** for production-ready AWS diagrams
2. **Terraform Graph** for quick dependency checks
3. **Custom scripts** for integration into our build process

## 📁 Integration with Our Project

The generated diagrams can be:
- Stored in `/docs/architecture/` directory
- Automatically updated in CI/CD pipeline
- Included in documentation and presentations
- Used for change impact analysis

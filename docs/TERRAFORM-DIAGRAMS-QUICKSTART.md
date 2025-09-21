# Quick Start: Terraform to Architecture Diagrams

## 🚀 Instant Setup (Recommended)

### Option 1: Using Inframap (Best Results)

1. **Install Inframap** (Windows):
```cmd
# Download from GitHub releases
curl -LO https://github.com/cycloidio/inframap/releases/latest/download/inframap-windows-amd64.zip
# Extract and add to PATH
```

2. **Install Graphviz**:
```cmd
choco install graphviz
# Or download from: https://graphviz.org/download/
```

3. **Generate Diagrams**:
```cmd
cd infrastructure\terraform
terraform init
terraform plan -out=plan.out
terraform show -json plan.out > plan.json
inframap generate plan.json | dot -Tsvg > aws_infrastructure.svg
```

### Option 2: Using Built-in Terraform Graph

1. **Install Graphviz** (if not already installed)
2. **Generate Basic Diagrams**:
```cmd
cd infrastructure\terraform
terraform graph | dot -Tsvg > terraform_dependencies.svg
```

## 🛠️ Available Tools Comparison

| Tool | Quality | Setup | AWS Support | Interactive |
|------|---------|-------|-------------|-------------|
| **Inframap** | ⭐⭐⭐⭐⭐ | Easy | ✅ | ❌ |
| **Terraform Graph** | ⭐⭐⭐ | Built-in | ❌ | ❌ |
| **Blast Radius** | ⭐⭐⭐⭐ | Medium | ❌ | ✅ |
| **Rover** | ⭐⭐⭐⭐ | Hard | ✅ | ✅ |

## 📱 One-Click Solutions

### Windows Users
```cmd
# Run our automated script
scripts\generate-diagrams.bat
```

### Linux/macOS Users
```bash
# Run our automated script
chmod +x scripts/generate-diagrams.sh
./scripts/generate-diagrams.sh
```

### Python Users
```bash
# Run our Python generator
python scripts/generate_terraform_diagrams.py
```

## 🎯 Expected Outputs

After running the scripts, you'll get:

### 📊 Diagram Types
- **Dependencies**: Shows resource relationships
- **AWS Infrastructure**: Visual AWS architecture
- **Environment-specific**: Separate diagrams for dev/uat/prod

### 📁 File Formats
- **SVG**: Best quality, scalable, browser-viewable
- **PNG**: Good for presentations and documents
- **DOT**: Source format, can be edited

### 📍 Output Location
```
docs/
└── architecture/
    ├── terraform_dependencies.svg
    ├── aws_infrastructure_plan.svg
    ├── dev_infrastructure.svg
    ├── uat_infrastructure.svg
    ├── prod_infrastructure.svg
    └── architecture_dev.md
```

## 🔧 Manual Installation Steps

### 1. Install Graphviz
```bash
# Ubuntu/Debian
sudo apt-get install graphviz

# macOS
brew install graphviz

# Windows
choco install graphviz
# Or download from: https://graphviz.org/download/
```

### 2. Install Inframap
```bash
# Linux
curl -LO https://github.com/cycloidio/inframap/releases/latest/download/inframap-linux-amd64.tar.gz
tar -xzf inframap-linux-amd64.tar.gz
sudo mv inframap /usr/local/bin/

# macOS
brew install inframap

# Windows
# Download from GitHub releases and add to PATH
```

### 3. Verify Installation
```bash
terraform --version
dot -V
inframap --version
```

## 🎨 Advanced Usage

### Custom Styling
```bash
# Generate with custom styling
inframap generate plan.json --config custom-style.yaml | dot -Tsvg > styled_diagram.svg
```

### Multiple Environments
```bash
# Generate for specific environment
terraform plan -var-file=prod.tfvars -out=prod.out
terraform show -json prod.out | inframap generate | dot -Tsvg > prod_infrastructure.svg
```

### Integration with CI/CD
Add to your build pipeline:
```yaml
# Example GitHub Actions step
- name: Generate Architecture Diagrams
  run: |
    scripts/generate-diagrams.sh
    git add docs/architecture/
    git commit -m "Update architecture diagrams"
```

## 🐛 Troubleshooting

### Common Issues

1. **"terraform graph" fails**
   - Run `terraform init` first
   - Check if you're in the terraform directory

2. **"dot command not found"**
   - Install Graphviz package
   - Add to PATH on Windows

3. **"inframap: command not found"**
   - Download from GitHub releases
   - Add to PATH

4. **Empty or broken diagrams**
   - Check terraform plan succeeds
   - Verify JSON output is valid

### Quick Fixes
```bash
# Reinitialize Terraform
terraform init -upgrade

# Validate configuration
terraform validate

# Check plan works
terraform plan
```

## 📚 Next Steps

1. **Integrate into Development Workflow**
   - Add scripts to package.json or Makefile
   - Set up pre-commit hooks

2. **Customize for Your Needs**
   - Modify colors and styling
   - Add company branding
   - Create presentation-ready versions

3. **Automate Updates**
   - Run in CI/CD pipeline
   - Schedule regular updates
   - Include in documentation builds

## 🌟 Pro Tips

- **Use SVG format** for scalable, high-quality diagrams
- **Generate for each environment** to show differences
- **Include in documentation** for better team understanding
- **Update automatically** to keep diagrams current
- **Version control diagrams** to track infrastructure changes

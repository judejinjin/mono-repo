# Terraform Visualization Integration

## 📊 Architecture Diagram Generation

This document describes how to generate architecture diagrams from our Terraform infrastructure code.

### Quick Start

Run one of these commands from the project root:

```bash
# Windows
scripts\generate-diagrams.bat

# Linux/macOS
./scripts/generate-diagrams.sh

# Python (cross-platform)
python scripts/generate_terraform_diagrams.py
```

### Available Tools

1. **Inframap** (Recommended)
   - Generates beautiful AWS-specific diagrams
   - Shows VPC, subnets, security groups, load balancers
   - Perfect for our AWS infrastructure

2. **Terraform Graph**
   - Built into Terraform
   - Shows resource dependencies
   - Good for understanding relationships

3. **Custom Python Generator**
   - Extensible for specific needs
   - Can integrate with company standards
   - Supports multiple output formats

### Output Examples

The scripts generate diagrams in multiple formats:

- **SVG**: Best quality, scalable, web-friendly
- **PNG**: Good for presentations and documents
- **DOT**: Source format for Graphviz

### Integration Points

- **CI/CD Pipeline**: Auto-generate on infrastructure changes
- **Documentation**: Include in technical documentation
- **Reviews**: Visual impact assessment for changes
- **Presentations**: Professional architecture diagrams

### Dependencies

Required tools:
- Terraform (already installed)
- Graphviz (`choco install graphviz` on Windows)
- Inframap (download from GitHub releases)

### Environment-Specific Diagrams

Generate separate diagrams for each environment:
- `dev_infrastructure.svg`
- `uat_infrastructure.svg`
- `prod_infrastructure.svg`

This helps visualize differences between environments and track scaling.

## 🔗 Related Documentation

- [Terraform Visualization Guide](terraform-visualization-guide.md)
- [Quick Start Guide](TERRAFORM-DIAGRAMS-QUICKSTART.md)
- [Infrastructure Documentation](../infrastructure/README.md)

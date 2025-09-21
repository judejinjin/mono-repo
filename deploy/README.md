# Deployment System for Mono-Repo Project

This directory contains deployment scripts and configurations for the mono-repo project.

## Structure
- `deploy.py` - Main deployment script
- `kubernetes/` - Kubernetes manifests
- `terraform/` - Terraform infrastructure code
- `scripts/` - Deployment helper scripts
- `configs/` - Environment-specific deployment configurations

## Usage

### Infrastructure Deployment
```bash
python deploy/deploy.py --target infrastructure --environment dev
python deploy/deploy.py --target infrastructure --environment uat
python deploy/deploy.py --target infrastructure --environment prod
```

### Application Deployment
```bash
python deploy/deploy.py --target applications --environment dev
python deploy/deploy.py --target services --component fastapi --environment uat
python deploy/deploy.py --target web --environment prod
```

### Database Migration
```bash
python deploy/deploy.py --target database --action migrate --environment dev
```

## Environment Configuration

Each environment has its own configuration in the `configs/` directory:
- `dev.yaml` - Development environment
- `uat.yaml` - UAT environment  
- `prod.yaml` - Production environment

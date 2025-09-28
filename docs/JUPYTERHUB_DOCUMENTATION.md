# JupyterHub Integration with Risk Platform

## Overview

This document provides comprehensive documentation for the JupyterHub integration with the Risk Platform. JupyterHub provides a multi-user notebook environment for business users to run risk analysis, develop models, and create interactive reports.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [User Guide](#user-guide)
3. [Deployment Guide](#deployment-guide)
4. [Operational Runbook](#operational-runbook)
5. [Developer Guide](#developer-guide)
6. [Troubleshooting](#troubleshooting)

## Architecture Overview

### Components

#### JupyterHub Platform
- **JupyterHub Hub**: Central authentication and user management service
- **Management API**: FastAPI service for programmatic user and session management
- **User Notebooks**: Individual notebook environments for different user types
- **Proxy**: Routes traffic to individual user servers

#### User Types and Environments
1. **Business Users**: Risk analysts with read-only access to Risk Platform APIs
2. **Data Scientists**: Model developers with enhanced data access and ML tools
3. **Platform Admins**: Full access to platform management and monitoring

#### Storage Architecture
- **EFS Shared Storage**: Persistent storage for user notebooks and shared data
- **S3 Backup**: Automated backup of user data and configurations
- **ECR Repositories**: Container images for different notebook environments

#### Security Features
- **Corporate SSO Integration**: OAuth-based authentication with corporate directory
- **IAM Role-Based Access**: Fine-grained permissions for different user types
- **Network Isolation**: Kubernetes network policies for secure communication
- **Encrypted Storage**: Data encryption at rest and in transit

## User Guide

### Getting Started

#### Accessing JupyterHub
1. Navigate to the JupyterHub URL (provided by your administrator)
2. Click "Login with Corporate SSO"
3. Enter your corporate credentials
4. Select your notebook environment (Business User or Data Scientist)

#### Notebook Environments

##### Business User Environment
- Pre-installed packages for risk analysis
- Access to Risk Platform APIs (read-only)
- Sample notebooks for common risk calculations
- Restricted resource allocation (2 CPU, 4GB RAM)

##### Data Scientist Environment
- Full data science toolkit (pandas, scikit-learn, tensorflow, etc.)
- Enhanced access to data sources and S3 buckets
- ML development and model training capabilities
- Higher resource allocation (4 CPU, 8GB RAM)

#### Sample Notebooks

##### Risk Analysis for Business Users
Located in `/shared/notebooks/risk_analysis_business_user.ipynb`:
- Portfolio risk calculations
- Market data analysis
- Risk reporting and visualization
- Integration with Risk Platform APIs

##### Data Science Template
Located in `/shared/notebooks/data_science_template.ipynb`:
- Model development framework
- Data preprocessing pipelines
- Model evaluation and validation
- MLOps integration patterns

#### Shared Resources
- **Shared Notebooks**: `/shared/notebooks/` - Collaborative notebooks
- **Shared Data**: `/shared/data/` - Common datasets and data files
- **Shared Libraries**: `/shared/libs/` - Custom Python packages and utilities

### Working with the Risk Platform

#### API Access
```python
import requests
import os

# Risk Platform API endpoint
RISK_API_URL = os.getenv('RISK_API_URL', 'http://fastapi-service.default.svc.cluster.local')

# Example: Get portfolio data
response = requests.get(f"{RISK_API_URL}/api/v1/portfolios")
portfolios = response.json()
```

#### Data Sources
- Market data feeds (real-time and historical)
- Portfolio data from risk systems
- Risk models and parameters
- Regulatory data and benchmarks

## Deployment Guide

### Prerequisites
- EKS cluster with sufficient resources
- IAM roles and policies configured
- EFS file system for persistent storage
- ECR repositories for container images
- Secrets configured in AWS Secrets Manager

### Infrastructure Deployment

#### 1. Deploy Terraform Infrastructure
```bash
cd infrastructure/terraform
terraform init
terraform plan -var environment=dev
terraform apply -var environment=dev
```

#### 2. Build and Push Container Images
```bash
cd build
python build.py --component jupyterhub --environment dev --push
```

#### 3. Deploy to Kubernetes
```bash
cd deploy/kubernetes/jupyterhub
kubectl apply -f deployment-dev.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml
```

#### 4. Configure JupyterHub
```bash
# Create ConfigMap for JupyterHub configuration
kubectl create configmap jupyterhub-config \
  --from-file=jupyterhub_config.py \
  --namespace=jupyterhub

# Create secrets
kubectl create secret generic jupyterhub-secrets \
  --from-literal=api_token=${JUPYTERHUB_API_TOKEN} \
  --from-literal=cookie_secret=${COOKIE_SECRET} \
  --from-literal=crypto_key=${CRYPTO_KEY} \
  --from-literal=database_url=${DATABASE_URL} \
  --namespace=jupyterhub
```

### Environment-Specific Configurations

#### Development
- Single replica deployments
- Reduced resource limits
- Debug logging enabled
- Local authentication fallback

#### UAT
- Scaled deployments for testing
- Production-like configurations
- UAT-specific OAuth endpoints
- Performance monitoring enabled

#### Production
- High availability deployments
- Auto-scaling enabled
- Production OAuth integration
- Full monitoring and alerting

## Operational Runbook

### Daily Operations

#### Health Checks
```bash
# Check JupyterHub status
kubectl get pods -n jupyterhub

# Check services
kubectl get svc -n jupyterhub

# Check resource utilization
kubectl top pods -n jupyterhub
```

#### User Management
```bash
# List active users
python devops/jupyterhub/monitor_jupyterhub.py --environment prod

# Cleanup idle sessions
python devops/jupyterhub/cleanup_sessions.py --environment prod --execute
```

### Monitoring and Alerting

#### Key Metrics
- Active user count
- Session utilization
- Resource consumption (CPU, Memory, Storage)
- API response times
- Error rates

#### Alerts
- High resource utilization (>80% CPU, >85% Memory)
- Failed health checks
- Authentication failures
- Storage capacity warnings

#### Monitoring Tools
- CloudWatch dashboards
- Prometheus metrics
- Grafana visualizations
- Custom monitoring scripts

### Backup and Recovery

#### Automated Backups
- Daily EFS snapshots
- S3 backup of user data
- Configuration backup
- Database backups

#### Recovery Procedures
1. **User Data Recovery**:
   ```bash
   # Restore from S3 backup
   aws s3 sync s3://jupyterhub-backup-bucket/user-data/ /mnt/efs/user-data/
   ```

2. **Configuration Recovery**:
   ```bash
   # Restore ConfigMaps and Secrets
   kubectl apply -f backup/configmaps/
   kubectl apply -f backup/secrets/
   ```

3. **Full Environment Recovery**:
   ```bash
   # Redeploy infrastructure
   cd infrastructure/terraform
   terraform apply
   
   # Redeploy applications
   kubectl apply -f deploy/kubernetes/jupyterhub/
   ```

### Maintenance Tasks

#### Weekly Tasks
- Review resource utilization
- Clean up idle sessions
- Update security patches
- Review access logs

#### Monthly Tasks
- Capacity planning review
- Security audit
- Performance optimization
- Documentation updates

#### Quarterly Tasks
- Major version updates
- Security assessment
- Disaster recovery testing
- User training sessions

## Developer Guide

### Architecture Patterns

#### Service Integration
```python
# services/jupyterhub_service.py
from fastapi import FastAPI, HTTPException
from jupyterhub.services.auth import HubAuth

app = FastAPI()
auth = HubAuth()

@app.get("/api/users")
async def get_users():
    # Implementation for user management
    pass
```

#### Notebook Templates
```python
# notebooks/templates/business_user_template.py
import pandas as pd
import numpy as np
from risk_platform_client import RiskPlatformAPI

class BusinessUserNotebook:
    def __init__(self):
        self.risk_api = RiskPlatformAPI()
        
    def analyze_portfolio_risk(self, portfolio_id):
        # Implementation for risk analysis
        pass
```

### Custom Extensions

#### JupyterHub Extensions
- Custom spawner configurations
- Authentication integrations
- Resource management extensions
- Monitoring integrations

#### Notebook Extensions
- Risk Platform API client
- Corporate data connectors
- Visualization libraries
- Reporting templates

### Configuration Management

#### Environment Variables
```bash
# JupyterHub configuration
JUPYTERHUB_API_TOKEN=<api-token>
JUPYTERHUB_COOKIE_SECRET=<cookie-secret>
JUPYTERHUB_CRYPT_KEY=<crypto-key>

# Risk Platform integration
RISK_API_URL=<risk-api-endpoint>
CORPORATE_AUTH_URL=<auth-endpoint>

# Storage configuration
EFS_MOUNT_POINT=/shared
S3_BACKUP_BUCKET=jupyterhub-backup
```

#### ConfigMaps and Secrets
- Kubernetes ConfigMaps for configuration files
- Secrets for sensitive data
- Environment-specific configurations
- Automated secret rotation

## Troubleshooting

### Common Issues

#### Authentication Problems
**Symptoms**: Users cannot log in or get authentication errors
**Solutions**:
1. Check OAuth configuration
2. Verify IAM roles and policies
3. Check corporate directory connectivity
4. Review authentication logs

#### Resource Issues
**Symptoms**: Slow notebook performance, out of memory errors
**Solutions**:
1. Check resource limits and requests
2. Review node capacity
3. Scale cluster if needed
4. Optimize notebook configurations

#### Storage Issues
**Symptoms**: Cannot save notebooks, storage full errors
**Solutions**:
1. Check EFS capacity and performance
2. Review storage utilization
3. Clean up old files
4. Expand storage if needed

#### Network Connectivity
**Symptoms**: Cannot access Risk Platform APIs
**Solutions**:
1. Check network policies
2. Verify service discovery
3. Review security groups
4. Test API connectivity

### Debugging Commands

#### Kubernetes Debugging
```bash
# Check pod logs
kubectl logs -n jupyterhub jupyterhub-hub-<pod-id>

# Describe pod for events
kubectl describe pod -n jupyterhub jupyterhub-hub-<pod-id>

# Check resource usage
kubectl top pod -n jupyterhub

# Check persistent volumes
kubectl get pv,pvc -n jupyterhub
```

#### JupyterHub Debugging
```bash
# Check JupyterHub API
curl -H "Authorization: Bearer $JUPYTERHUB_API_TOKEN" \
  http://jupyterhub-service:8000/hub/api/users

# Check user sessions
curl -H "Authorization: Bearer $JUPYTERHUB_API_TOKEN" \
  http://jupyterhub-service:8000/hub/api/users/<username>

# Check configuration
kubectl get configmap jupyterhub-config -o yaml
```

### Log Analysis

#### Important Log Locations
- JupyterHub Hub: `/var/log/jupyterhub/`
- User servers: `/home/jovyan/.local/share/jupyter/`
- Kubernetes events: `kubectl get events -n jupyterhub`
- CloudWatch Logs: JupyterHub log groups

#### Log Patterns to Monitor
- Authentication failures
- Resource allocation errors
- API call failures
- Storage access issues
- Security violations

### Performance Optimization

#### Resource Tuning
1. **CPU Optimization**:
   - Adjust CPU requests and limits
   - Enable CPU throttling
   - Monitor CPU utilization patterns

2. **Memory Optimization**:
   - Set appropriate memory limits
   - Monitor memory usage patterns
   - Implement memory cleanup

3. **Storage Optimization**:
   - Use appropriate storage classes
   - Optimize file system performance
   - Implement storage cleanup

#### Scaling Strategies
1. **Horizontal Scaling**:
   - Increase replica counts
   - Use Horizontal Pod Autoscaler
   - Load balance user sessions

2. **Vertical Scaling**:
   - Increase resource limits
   - Optimize container configurations
   - Use larger instance types

3. **Auto-scaling**:
   - Configure HPA policies
   - Set up cluster auto-scaling
   - Monitor scaling events

## Support and Contacts

### Support Channels
- **Technical Support**: risk-platform-support@company.com
- **User Training**: jupyterhub-training@company.com
- **Security Issues**: security@company.com

### Documentation Updates
This documentation is maintained in the mono-repo at `/docs/JUPYTERHUB_DOCUMENTATION.md`

For updates and contributions, please follow the standard development workflow and submit pull requests.
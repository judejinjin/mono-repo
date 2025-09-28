# Architecture Diagrams Index

This document provides an index of all generated architecture diagrams for the Risk Platform with JupyterHub integration.

## Generated: September 28, 2025

## 📊 **Main Architecture Diagrams**

### Enhanced Platform Architecture ✨ **NEW!**
- `enhanced_architecture_with_jupyterhub_dev.png` - **Complete dev environment with JupyterHub**
- `enhanced_architecture_with_jupyterhub_uat.png` - **Complete UAT environment with JupyterHub**
- `enhanced_architecture_with_jupyterhub_prod.png` - **Complete production environment with JupyterHub**

### Core Platform Architecture
- `architecture_dev.png/svg` - Development environment architecture
- `architecture_uat.png/svg` - UAT environment architecture  
- `architecture_prod.png/svg` - Production environment architecture

### CI/CD and Deployment
- `cicd_flow_corporate.png/svg` - Corporate CI/CD pipeline flow
- `deployment_strategies.png/svg` - Multi-environment deployment strategies

### Visual Overview ✨ **NEW!**
- `DIAGRAM_OVERVIEW.png` - **Complete visual guide to all available diagrams**

## 🔬 **JupyterHub Integration Diagrams**

Located in `/docs/diagrams/jupyterhub/`:

### JupyterHub Architecture
- `jupyterhub_architecture.png` - **Complete JupyterHub integration with Risk Platform**
  - Shows user types (Business Users, Data Scientists, Admins)
  - Corporate SSO authentication flow
  - Kubernetes deployment architecture
  - Storage integration (EFS, S3, ECR)
  - Risk Platform API integration
  - Security boundaries and RBAC

### Data Flow
- `jupyterhub_data_flow.png` - **Data flow through JupyterHub environment**
  - Market data feeds → Risk Platform → JupyterHub notebooks
  - User notebook outputs and reports
  - Collaboration through shared storage

### Security Architecture
- `jupyterhub_security.png` - **Security boundaries and access controls**
  - Authentication layers (Corporate OAuth, AWS IAM)
  - Kubernetes security (Network policies, RBAC, Pod security)
  - Data encryption and secrets management
  - VPC isolation and network controls

### Multi-Environment Deployment
- `jupyterhub_deployment.png` - **Deployment across dev/UAT/prod environments**
  - CI/CD pipeline integration
  - Environment-specific configurations
  - Container registry and image management

## 🚀 **Service-Specific Diagrams**

### Risk API Service
- `risk_api_architecture.png/svg` - Risk API service architecture
- `risk_api_deployment.png/svg` - Risk API deployment patterns

### Dash Analytics
- `dash_analytics_architecture.png/svg` - Dash application architecture
- `dash_interactive_flow.png/svg` - Interactive dashboard flow
- `dash_data_flow.png/svg` - Data flow in analytics dashboards

### Apache Airflow
- `airflow_architecture.png/svg` - Airflow deployment architecture
- `airflow_dag_management.png/svg` - DAG management and execution
- `airflow_scaling_monitoring.png/svg` - Scaling and monitoring setup

## 🛡️ **Security and Compliance Diagrams**

### Security Workflows
- `application_secrets_workflow.png/svg` - Secrets management workflow
- `break_glass_activation_workflow.png/svg` - Emergency access procedures
- `security_policy_enforcement.png/svg` - Security policy enforcement

### Monitoring and Alerting
- `alerting_notification_systems.png/svg` - Comprehensive alerting setup
- `budget_alerts_finops.png/svg` - Cost monitoring and FinOps
- `cloudwatch_logging_architecture.png/svg` - Centralized logging architecture

## 🌐 **Network and Infrastructure**

### AWS Infrastructure
- `aws_infrastructure_overview.png/svg` - Complete AWS infrastructure
- `eks_cluster_architecture.png/svg` - EKS cluster detailed architecture
- `data_pipeline_architecture.png/svg` - Data processing pipelines

### Network Architecture
- `network_security_architecture.png/svg` - Network security boundaries
- `vpc_architecture.png/svg` - VPC and subnetting architecture

## 📋 **How to Use These Diagrams**

### For Business Users
1. **Start with**: `jupyterhub_architecture.png` - Overview of your notebook environment
2. **Then review**: `jupyterhub_data_flow.png` - How to access and use data
3. **For troubleshooting**: `jupyterhub_security.png` - Understanding access controls

### For Data Scientists
1. **Architecture overview**: `jupyterhub_architecture.png` - Platform capabilities
2. **Data access patterns**: `dash_data_flow.png` - Integration with analytics
3. **Development workflow**: `cicd_flow_corporate.png` - Code deployment process

### for Platform Administrators
1. **Infrastructure**: `architecture_prod.png` - Production environment
2. **Security**: `security_policy_enforcement.png` - Security implementation
3. **Monitoring**: `alerting_notification_systems.png` - Operational monitoring
4. **JupyterHub operations**: All diagrams in `/jupyterhub/` folder

### For DevOps Teams
1. **Deployment**: `jupyterhub_deployment.png` - Multi-environment setup
2. **CI/CD**: `cicd_flow_corporate.png` - Pipeline architecture
3. **Infrastructure**: `aws_infrastructure_overview.png` - AWS resources

## 🔄 **Updating Diagrams**

To regenerate all diagrams:

```bash
# Generate main architecture diagrams
cd devops
python create_architecture_diagrams.py

# Generate JupyterHub-specific diagrams
cd jupyterhub
python generate_jupyterhub_diagrams.py

# Generate service-specific diagrams
python create_risk_api_diagrams.py
python create_dash_diagrams.py
python create_airflow_diagrams.py

# Generate enhanced diagrams with JupyterHub integration
python generate_enhanced_diagrams.py
```

## 📁 **File Organization**

```
docs/
├── architecture/          # Main architecture diagrams
├── diagrams/
│   └── jupyterhub/       # JupyterHub-specific diagrams
└── DIAGRAM_INDEX.md      # This file
```

## 🎯 **Key Integration Points Highlighted**

The diagrams specifically show:

1. **User Journey**: Corporate SSO → JupyterHub → Risk Platform APIs
2. **Data Flow**: Market Data → Risk Engine → Notebooks → Reports
3. **Security**: Multi-layer authentication, RBAC, network isolation
4. **Operations**: Monitoring, logging, backup, and maintenance workflows
5. **Development**: CI/CD integration, container management, environment promotion

---

**Generated**: September 28, 2025  
**Platform Version**: Risk Platform v2.0 with JupyterHub Integration  
**Last Updated**: Auto-generated with diagram scripts
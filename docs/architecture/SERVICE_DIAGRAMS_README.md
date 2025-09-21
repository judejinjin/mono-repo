# Service Architecture Diagrams

This directory contains comprehensive visual documentation for all services in the mono-repo infrastructure. All diagrams are generated using Python matplotlib and provide detailed architectural insights.

## 📊 Generated Diagrams Overview

### 🏗️ Overall Architecture
- `architecture_dev.png` - Development environment architecture
- `architecture_prod.png` - Production environment architecture  
- `architecture_uat.png` - UAT environment architecture
- `cicd_flow_corporate.png` - CI/CD pipeline flow

### 🔥 Apache Airflow (Workflow Management)
- `airflow_architecture.png` - Complete Airflow infrastructure on EKS with KubernetesExecutor
- `airflow_dag_management.png` - DAG development, deployment, and Git-sync workflow
- `airflow_scaling_monitoring.png` - Auto-scaling strategies and monitoring architecture

### 🚀 FastAPI Risk Management Service  
- `risk_api_architecture.png` - Risk API service architecture and data flow
- `risk_api_deployment.png` - Deployment pipeline and scaling configuration

### 📊 Dash Analytics Application
- `dash_analytics_architecture.png` - Dash application infrastructure and component layout
- `dash_data_flow.png` - Data processing and visualization pipeline
- `dash_interactive_flow.png` - Interactive callbacks and user interaction flows

### 🌐 React Web Applications
- `web_apps_architecture.png` - React applications infrastructure (Dashboard & Admin)
- `web_apps_user_flow.png` - User journey and application interaction flow
- `web_apps_component_architecture.png` - Component hierarchy and responsive design

## 🛠️ Technical Details

### Infrastructure Stack
- **Kubernetes**: EKS clusters with auto-scaling
- **Load Balancing**: Internal ALB with path-based routing
- **Databases**: PostgreSQL RDS clusters
- **Container Registry**: ECR for all service images
- **Monitoring**: Prometheus, Grafana, CloudWatch integration

### Service Characteristics

#### Airflow (Workflow Engine)
- **Version**: 2.7.0 with KubernetesExecutor
- **Scaling**: Dynamic pod creation/cleanup
- **Storage**: Git-sync for DAG management, S3 for logs
- **Database**: Dedicated PostgreSQL RDS instance

#### Risk API (FastAPI)
- **Framework**: FastAPI 0.104.1 with Python 3.11
- **Database**: PostgreSQL + Snowflake integration
- **Authentication**: JWT token support (planned)
- **Deployment**: Rolling updates with health checks

#### Dash Analytics
- **Framework**: Dash 2.14.2 with Plotly 5.17.0
- **Features**: Interactive dashboards, real-time data
- **Architecture**: Server-side rendering with callback system
- **Data Sources**: PostgreSQL, Snowflake, API integrations

#### Web Applications
- **Framework**: React 18.2 with TypeScript
- **Build Tool**: Vite with code splitting optimization
- **Styling**: Tailwind CSS with responsive design
- **State Management**: React Query + Context API

## 🔄 Diagram Generation

### How to Regenerate Diagrams
```bash
# Generate all diagrams
cd devops/
python generate_all_diagrams.py

# Generate specific service diagrams
python create_airflow_diagrams.py
python create_risk_api_diagrams.py  
python create_dash_diagrams.py
python create_web_apps_diagrams.py
```

### Requirements
- Python 3.8+
- matplotlib
- numpy
- pathlib

### Diagram Features
- **High Resolution**: 300 DPI PNG output
- **Corporate Styling**: Consistent color schemes and layouts
- **Multiple Views**: Architecture, deployment, scaling, and user flows
- **Technical Details**: Component versions, ports, resource limits
- **Auto-Layout**: Optimized spacing and connection flows

## 📋 Service Summary

| Service | Technology | Environment Access | Database | Scaling Strategy |
|---------|------------|-------------------|----------|------------------|
| Airflow | Python 3.11, KubernetesExecutor | Corporate intranet only | PostgreSQL RDS | Dynamic pod auto-scaling |
| Risk API | FastAPI 0.104.1 | Internal ALB routing | PostgreSQL + Snowflake | HPA based on CPU/memory |
| Dash Analytics | Dash 2.14.2, Plotly | Corporate network | PostgreSQL, APIs | Horizontal pod scaling |
| Web Apps | React 18.2, TypeScript | Internal load balancer | API integrations | Multi-replica deployment |

## 🔐 Security & Compliance

All services operate within corporate security boundaries:
- **Network**: Corporate intranet access only
- **Authentication**: IAM roles with service accounts
- **Encryption**: TLS in transit, encrypted storage
- **Monitoring**: Comprehensive logging and alerting

## 📈 Performance Characteristics

### Target SLAs
- **Availability**: 99.9%+ uptime
- **Response Times**: < 2s for web interfaces, < 500ms for APIs
- **Scalability**: Auto-scaling based on demand
- **Recovery**: < 15 minutes recovery time objective

### Resource Allocation
- **CPU**: Requests from 100m-500m, limits up to 2000m
- **Memory**: Requests from 128Mi-512Mi, limits up to 2Gi
- **Storage**: Persistent volumes for stateful components
- **Network**: Internal-only communication patterns

## 🔍 Monitoring & Observability

Comprehensive monitoring stack includes:
- **Metrics**: Prometheus + Grafana dashboards
- **Logging**: ELK stack integration
- **Alerting**: PagerDuty integration for critical alerts
- **Tracing**: Application performance monitoring
- **Health Checks**: Kubernetes liveness/readiness probes

---

*Last Updated: Generated automatically by diagram generation scripts*
*For questions about architecture or diagrams, see documentation in individual service analysis files*

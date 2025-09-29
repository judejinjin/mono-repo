# Mono-Repo Infrastructure Project

A comprehensive mono-repository for a Python/Node.js application with infrastructure automation, CI/CD, and multi-environment deployment capabilities.

## 🏗️ Architecture Overview

This project implements a modern cloud-native architecture with the following components:

- **Infrastructure**: AWS cloud with Terraform IaC
- **Container Orchestration**: Amazon EKS (Kubernetes)
- **Container Registry**: Amazon ECR
- **Development Environment**: On-premise Linux development server with VS Code Remote SSH
- **CI/CD**: Bamboo server integration via corporate network
- **Data Processing**: Apache Airflow with Kubernetes executor
- **Applications**: FastAPI services, React/Vue web apps, Dash analytics dashboards
- **Databases**: PostgreSQL on Amazon RDS, Snowflake for data warehousing
- **Storage**: Amazon S3 for data and artifacts
- **Performance**: Redis caching, async processing, comprehensive monitoring
- **Security**: OAuth 2.0/RBAC authentication, MFA, comprehensive security framework

## 📊 Architecture Diagrams ✨ **UPDATED**

**80+ comprehensive diagrams** covering all platform components and recent implementations:

- 📋 **[Complete Diagram Index](docs/DIAGRAM_INDEX.md)** - Full catalog of all available diagrams
- 🆕 **[Latest Updates Summary](docs/DIAGRAM_UPDATES_SUMMARY.md)** - Sept 29, 2025 diagram updates
- 🚀 **Performance Optimization Diagrams** - Caching, async processing, monitoring
- 🔐 **Security Framework Diagrams** - Authentication, RBAC, MFA workflows  
- 📈 **Enhanced Monitoring Diagrams** - CloudWatch, logging, alerting
- 🔄 **Updated Architecture Diagrams** - Complete production-ready platform

**View all diagrams**: [`docs/architecture/`](docs/architecture/)

## 📁 Project Structure

```
mono-repo/
├── config/                 # Configuration management
│   ├── __init__.py         # Config loader with environment support
│   ├── base.yaml           # Base configuration
│   ├── dev.yaml            # Development environment config
│   ├── uat.yaml            # UAT environment config
│   └── prod.yaml           # Production environment config
├── build/                  # Build system
│   ├── build.py            # Main build script
│   ├── requirements/       # Python dependencies by environment
│   └── package.json        # Node.js dependencies
├── deploy/                 # Deployment system
│   ├── deploy.py           # Main deployment script
│   ├── kubernetes/         # Kubernetes manifests
│   └── configs/            # Environment deployment configs
├── libs/                   # Shared libraries
│   ├── db/                 # Database abstraction layer
│   ├── cloud/              # Cloud services abstraction
│   └── business/           # Business logic modules
├── scripts/                # Airflow job scripts
│   ├── market_data_processor.py
│   └── report_generator.py
├── dags/                   # Airflow DAG definitions
│   └── daily_risk_processing.py
├── services/               # FastAPI services
│   └── risk_api.py
├── web/                    # Web applications (React/Vue)
├── dash/                   # Dash analytics applications
│   └── risk_dashboard.py
└── infrastructure/         # Infrastructure as Code
    └── terraform/          # Terraform configurations
└── docs/                   # Documentation
    ├── INFRASTRUCTURE-TEARDOWN.md      # Teardown guide
    ├── TERRAFORM-DIAGRAMS-QUICKSTART.md # Diagram generation
    └── architecture/       # Architecture diagrams
    └── terraform/          # Terraform configurations
```

## 🚀 Quick Start

### Prerequisites

- AWS CLI configured with appropriate credentials
- Terraform >= 1.0
- Python 3.11+
- Node.js 18+
- kubectl
- Docker

### 1. Infrastructure Deployment

```bash
# Navigate to terraform directory
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Plan deployment for development environment
terraform plan -var-file=dev.tfvars

# Apply infrastructure
terraform apply -var-file=dev.tfvars
```

### 2. Application Setup

```bash
# Set environment
export ENV=dev

# Build all components
python build/build.py --component all --environment dev

# Deploy applications
python deploy/deploy.py --target applications --environment dev
```

### 3. On-Premise Development Server Access

```bash
# Connect to existing on-premise Linux development server via SSH
ssh <username>@<on-premise-dev-server-ip>

# In VS Code, use Remote-SSH extension to connect to on-premise dev server
# Configure .ssh/config for easy access:
# Host on-premise-dev
#   HostName <on-premise-dev-server-ip>
#   User <username>
#   IdentityFile ~/.ssh/id_rsa
```

## 🔧 Configuration Management

The project uses a hierarchical configuration system:

1. **Base Configuration** (`config/base.yaml`): Common settings for all environments
2. **Environment Configs** (`config/{env}.yaml`): Environment-specific overrides
3. **Runtime Detection**: Uses `ENV` environment variable to determine current environment

### Usage Example

```python
from config import get_config, get_db_config, get_cloud_config

# Get general configuration
config = get_config()

# Get database configuration for 'riskdb'
db_config = get_db_config('riskdb')

# Get Snowflake database configuration
sf_config = get_db_config('snowflakedb')

# Get cloud service configuration
s3_config = get_cloud_config('s3')
```

## 🗄️ Database Management

The database abstraction layer provides:

- **Connection Pooling**: Automatic connection pool management
- **Environment-aware**: Different databases per environment
- **Multi-Database Support**: PostgreSQL and Snowflake integration
- **ORM Integration**: SQLAlchemy session management
- **Raw SQL Support**: Direct query execution when needed

### Usage Example

```python
from libs.db import get_session, execute_query

# Using session context manager (works for both PostgreSQL and Snowflake)
with get_session('riskdb') as session:
    # Perform database operations
    results = session.query(Portfolio).all()

# Using Snowflake for analytics
with get_session('snowflakedb') as session:
    # Large-scale analytics queries
    results = session.execute("SELECT * FROM large_analytics_table")

# Using direct queries
results = execute_query('riskdb', 'SELECT * FROM portfolios WHERE active = true')
```

## ☁️ Cloud Services Integration

Cloud services abstraction provides:

- **AWS Secrets Manager**: Secure credential management
- **S3 Storage**: File upload/download operations
- **Environment-aware**: Different resources per environment

### Usage Example

```python
from libs.cloud import get_secret, upload_to_s3

# Retrieve secrets
db_credentials = get_secret('dev/riskdb/credentials')

# Upload files to S3
upload_to_s3('/path/to/file.csv', 'data/processed/file.csv')
```

## 🔄 CI/CD Pipeline

### Development Workflow

1. **Feature Development**: Work on feature branches on on-premise dev server
2. **Pull Request**: Create PR to master branch
3. **Automated Testing**: Bamboo runs tests and builds
4. **Merge**: PR merged after approval
5. **Deployment**: Automatic deployment to development environment

### Build Process

```bash
# Build specific component
python build/build.py --component services --environment uat

# Run tests
python build/build.py --component libs --environment dev

# Build Docker images
python build/build.py --component all --environment prod
```

### Deployment Process

```bash
# Deploy infrastructure
python deploy/deploy.py --target infrastructure --environment prod

# Deploy specific service
python deploy/deploy.py --target services --environment uat

# Run database migrations
python deploy/deploy.py --target database --action migrate --environment dev
```

## 🌊 Airflow Data Pipeline

### DAG Structure

- **Daily Risk Processing**: Market data ingestion and risk calculations
- **Weekly Reporting**: Performance analytics and reporting
- **Monthly Reconciliation**: Data quality checks and reconciliation

### Example DAG

```python
# Located in dags/daily_risk_processing.py
# Runs daily at 6 AM on weekdays
# Processes market data, calculates risks, generates reports
```

### Script Execution

```bash
# Manual script execution
python scripts/market_data_processor.py --date 2025-09-01
python scripts/report_generator.py --date 2025-09-01 --type daily
```

## 📊 Applications

### FastAPI Risk Management Service

- **Endpoint**: `http://localhost:8000`
- **Features**: Risk calculations, portfolio analysis, report generation, Snowflake analytics
- **API Docs**: `http://localhost:8000/docs`
- **New Endpoints**: 
  - `/api/v1/databases` - List available databases
  - `/api/v1/snowflake/warehouses` - Snowflake warehouse info
  - `/api/v1/analytics/snowflake-query` - Execute Snowflake queries
  - `/api/v1/analytics/data-summary` - Data warehouse summary

### Dash Analytics Dashboard

- **Endpoint**: `http://localhost:8050`
- **Features**: Interactive risk visualizations, portfolio comparison
- **Real-time**: Live data updates from database

### Web Applications

- **Frontend**: React/Vue.js applications
- **API Integration**: Connects to FastAPI services
- **Responsive**: Mobile-friendly design

## 🔐 Security Considerations

### Network Security

- **VPC**: Isolated network environment
- **Private Subnets**: Sensitive services in private subnets
- **Security Groups**: Least-privilege access rules
- **NAT Gateways**: Secure outbound internet access

### Access Control

- **IAM Roles**: Minimal required permissions
- **RBAC**: Kubernetes role-based access control
- **SSH Keys**: Secure server access
- **Secrets Manager**: Encrypted credential storage

### Data Protection

- **Encryption**: Data encrypted at rest and in transit
- **Backup**: Automated database backups
- **Monitoring**: CloudWatch logging and metrics
- **Compliance**: SOC 2 and regulatory compliance ready

## 📈 Monitoring and Logging

### Infrastructure Monitoring

- **CloudWatch**: AWS resource metrics
- **Prometheus**: Kubernetes cluster metrics
- **Grafana**: Custom dashboards

### Application Monitoring

- **Structured Logging**: JSON-formatted logs
- **Metrics Collection**: Custom application metrics
- **Alerting**: Automated issue notifications

### Performance Monitoring

- **Database Performance**: Query optimization tracking
- **API Response Times**: Service performance metrics
- **Resource Utilization**: CPU, memory, storage monitoring

## 🛠️ Development Guidelines

### Code Organization

- **Modular Design**: Clear separation of concerns
- **Reusable Components**: Shared libraries for common functionality
- **Environment Parity**: Consistent behavior across environments

### Testing Strategy

- **Unit Tests**: Component-level testing
- **Integration Tests**: Service interaction testing
- **End-to-End Tests**: Full workflow validation

### Best Practices

- **Configuration**: Environment-specific settings
- **Error Handling**: Comprehensive exception management
- **Documentation**: Inline code documentation
- **Version Control**: Feature branch workflow

## 🔄 Maintenance and Operations

### Regular Tasks

- **Security Updates**: Monthly dependency updates
- **Database Maintenance**: Weekly optimization
- **Backup Verification**: Monthly restore testing
- **Cost Optimization**: Quarterly resource review

### Disaster Recovery

- **Infrastructure**: Terraform-based recreation
- **Data**: Automated backup and restore
- **Applications**: Container-based rapid deployment
- **Documentation**: Runbook procedures

## 📝 Environment-Specific Notes

### Development Environment

- **Purpose**: Feature development and testing
- **Resources**: Cost-optimized instances
- **Data**: Synthetic test data
- **Access**: Full developer access

### UAT Environment

- **Purpose**: User acceptance testing
- **Resources**: Production-similar sizing with Snowflake integration
- **Data**: Curated test datasets in both PostgreSQL and Snowflake
- **Access**: Business users and QA team

### Production Environment

- **Purpose**: Live business operations
- **Resources**: High-availability setup with dedicated Snowflake warehouse
- **Data**: Real business data with full data lineage
- **Access**: Restricted to operations team

## 🔥 Infrastructure Teardown and Cost Management

### ⚠️ Important for Testing in Personal AWS Account

Since you'll be testing this infrastructure in your personal AWS account, it's crucial to properly tear down resources to avoid unexpected charges.

### Quick Teardown Options

```bash
# Complete infrastructure teardown (Windows)
scripts\teardown-infrastructure.bat

# Complete infrastructure teardown (Linux/macOS)
./scripts/teardown-infrastructure.sh

# Python-based teardown (cross-platform)
python scripts/teardown_infrastructure.py --environment dev

# Emergency stop (immediate cost reduction)
scripts\emergency-stop.bat  # Windows
./scripts/emergency-stop.sh # Linux/macOS
```

### Safety Features

- **Automatic Backup**: Creates backup before destruction
- **Confirmation Prompts**: Prevents accidental deletions
- **Verification**: Checks that resources are properly removed
- **Cost Monitoring**: Guidance on verifying no ongoing charges

### What Gets Destroyed

✅ **Compute Resources** (main cost drivers):
- EC2 instances
- EKS clusters and node groups
- RDS instances
- Load balancers
- NAT gateways

✅ **Storage Resources**:
- EBS volumes
- S3 buckets (optional)

✅ **Network Resources**:
- VPC and subnets
- Security groups
- Internet gateways

### Emergency Stop vs Full Teardown

**Emergency Stop** (`emergency-stop.sh`):
- ⚡ **Fast**: Stops compute immediately
- 💰 **Cost Effective**: Reduces charges quickly
- 🔄 **Reversible**: Can restart resources
- 📊 **Preserves Data**: Keeps databases and S3

**Full Teardown** (`teardown-infrastructure.sh`):
- 🔥 **Complete**: Destroys everything
- 💾 **Backup First**: Creates backup automatically
- ✅ **Clean**: No remaining resources
- 💡 **Fresh Start**: Can redeploy from scratch

### Post-Teardown Verification

After running teardown scripts, verify in AWS Console:

1. **EC2 Dashboard**: No running instances
2. **RDS Dashboard**: No database instances
3. **EKS Dashboard**: No clusters
4. **VPC Dashboard**: No custom VPCs
5. **Billing Dashboard**: No ongoing charges

### 📖 Detailed Documentation

- [Complete Teardown Guide](docs/INFRASTRUCTURE-TEARDOWN.md)
- [Architecture Diagrams](docs/TERRAFORM-DIAGRAMS-QUICKSTART.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and add tests
4. Submit a pull request
5. Wait for review and approval

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For questions or support:

- **Documentation**: Check the implementation plan in `implementation.md`
- **Issues**: Create GitHub issues for bugs or feature requests
- **Team Contact**: Reach out to the development team

---

**Built with ❤️ for modern cloud-native applications**

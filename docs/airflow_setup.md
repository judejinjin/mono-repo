# Airflow Infrastructure Analysis

**Document Created:** September 21, 2025  
**Infrastructure Type:** Self-Managed Apache Airflow on Kubernetes

## Executive Summary

The current Airflow infrastructure is **self-managed** using Apache Airflow deployed on Kubernetes (EKS) with Helm charts, not Amazon's Managed Workflows for Apache Airflow (MWAA). The setup utilizes a KubernetesExecutor for dynamic worker scaling and external PostgreSQL databases for metadata storage.

## Architecture Overview

### Deployment Method
- **Technology Stack:** Apache Airflow 2.7.0/2.7.3
- **Deployment Tool:** Helm charts (`apache-airflow/airflow`)
- **Container Orchestration:** Amazon EKS (Elastic Kubernetes Service)
- **Namespaces:** Environment-specific (`airflow-dev`, `airflow-uat`, `airflow-prod`)

### Executor Configuration
- **Executor Type:** KubernetesExecutor
- **Worker Model:** Dynamic pod creation on-demand
- **Scaling:** Automatic based on task queue
- **Isolation:** Each task runs in its own Kubernetes pod

## Component Architecture

### 1. Scheduler Configuration

| Environment | Replicas | CPU Request | Memory Request | CPU Limit | Memory Limit |
|-------------|----------|-------------|----------------|-----------|--------------|
| Dev/UAT     | 1        | 100m        | 256Mi          | 500m      | 512Mi        |
| Production  | 2        | 500m        | 1Gi            | 2 CPU     | 2Gi          |

**Responsibilities:**
- DAG parsing and scheduling
- Task dependency resolution
- Worker pod orchestration
- Metadata database updates

### 2. Webserver Configuration

| Environment | Replicas | Service Type | Port | CPU Request | Memory Request |
|-------------|----------|--------------|------|-------------|----------------|
| Dev         | 1        | LoadBalancer | 8080 | 100m        | 256Mi          |
| UAT         | 1        | LoadBalancer | 8080 | 100m        | 256Mi          |
| Production  | 2        | ClusterIP    | 8080 | 500m        | 1Gi            |

**Features:**
- Airflow Web UI
- REST API endpoints
- Authentication enabled
- Corporate intranet access only

### 3. Worker Configuration (KubernetesExecutor)

**Dynamic Worker Model:**
- **Static Workers:** None (replicas = 0)
- **Dynamic Workers:** Kubernetes pods created on-demand
- **Resource Allocation:** Per-task pod configuration
- **Namespace:** Same as scheduler/webserver
- **Lifecycle:** Created when tasks are queued, destroyed after completion

**Benefits:**
- Resource efficiency (no idle workers)
- Automatic scaling based on workload
- Task isolation and fault tolerance
- Cost optimization

### 4. Backend Database

**Database Type:** External PostgreSQL (Amazon RDS)

| Environment | Host | Database Name | Connection Method |
|-------------|------|---------------|-------------------|
| Dev         | riskdb-dev.cluster-xyz.us-east-1.rds.amazonaws.com | airflow_dev | Secret-based auth |
| UAT         | riskdb-uat.cluster-xyz.us-east-1.rds.amazonaws.com | airflow_uat | Secret-based auth |
| Production  | riskdb-prod.cluster-xyz.us-east-1.rds.amazonaws.com | airflow_prod | Secret-based auth |

**Configuration:**
- **Port:** 5432
- **User:** airflow
- **Authentication:** Kubernetes secrets (`airflow-db-secret`)
- **SSL:** Enabled
- **Backup:** RDS automated backups

**Database Objects:**
- DAG metadata and state
- Task instances and logs
- User accounts and permissions
- Connection definitions
- Variable storage

### 5. DAG Storage and Management

**Storage Method:** Git-based synchronization

```yaml
dags:
  persistence:
    enabled: false  # No persistent volumes
  gitSync:
    enabled: true
    repo: https://github.com/your-org/mono-repo.git
    branch: main
    subPath: dags
    wait: 60  # Sync every 60 seconds
```

**DAG Repository Structure:**
```
dags/
├── daily_risk_processing.py      # Daily risk calculations
├── api_triggered_risk_analysis.py # On-demand risk analysis
└── [additional DAG files]
```

**Benefits:**
- Version control integration
- Automatic DAG deployment
- Rollback capabilities
- Multi-environment consistency

## Infrastructure Components

### Load Balancing Architecture

#### Internal Application Load Balancer
- **Purpose:** Corporate intranet access for all services
- **Type:** Application Load Balancer (ALB)
- **Scope:** Internal only (no internet access)
- **Security:** Corporate CIDR restrictions

#### Airflow-Specific Network Load Balancer
- **Purpose:** Dedicated Airflow webserver access
- **Type:** Network Load Balancer (NLB)
- **Port:** 8080
- **Health Check:** `/health` endpoint
- **Scope:** Internal corporate network

### IAM Security Model

#### Service Role: `airflow-service-role`
**Trust Relationship:**
- EKS OIDC provider integration
- Service account: `system:serviceaccount:airflow:airflow-service-account`

**Permissions:**
1. **S3 Access:**
   - Artifacts bucket: Read/Write/Delete
   - Logs bucket: Read/Write/Delete
   - Resource: `arn:aws:s3:::${prefix}-artifacts/*`

2. **Secrets Manager:**
   - Access: `GetSecretValue`
   - Resource: `arn:aws:secretsmanager:*:secret:${prefix}-airflow-*`

3. **Lambda Integration:**
   - Access: `InvokeFunction`
   - Resource: All project Lambda functions

4. **CloudWatch Logging:**
   - Log group creation and log streaming
   - Resource: `/aws/eks/${cluster}/airflow*`

### Network Security

#### Corporate Network Access
- **Access Method:** Corporate intranet only
- **CIDR Restrictions:** Configured corporate network ranges
- **Protocols:** HTTP (80), HTTPS (443)
- **Encryption:** TLS in transit

#### Kubernetes Network Policies
- **Namespace Isolation:** Environment-specific namespaces
- **Pod-to-Pod:** Controlled communication
- **External Access:** Load balancer only

## Environment-Specific Configurations

### Development Environment
```yaml
Environment: dev
Namespace: airflow-dev
Scheduler Replicas: 1
Webserver Replicas: 1
Service Type: LoadBalancer (NLB)
Resource Profile: Minimal
Config Exposure: Enabled (for debugging)
Autoscaling: Disabled
```

### UAT Environment
```yaml
Environment: uat
Namespace: airflow-uat
Scheduler Replicas: 1
Webserver Replicas: 1
Service Type: LoadBalancer (NLB)
Resource Profile: Minimal
Config Exposure: Limited
Autoscaling: Disabled
```

### Production Environment
```yaml
Environment: prod
Namespace: airflow-prod
Scheduler Replicas: 2 (High Availability)
Webserver Replicas: 2 (High Availability)
Service Type: ClusterIP
Resource Profile: Production-grade
Config Exposure: Disabled (Security)
Autoscaling: Enabled (2-5 replicas)
Target CPU: 70%
```

## Deployment Process

### Helm-Based Deployment
```bash
helm upgrade --install airflow \
  apache-airflow/airflow \
  --namespace airflow-{environment} \
  --create-namespace \
  --values values-{environment}.yaml
```

### Pre-Deployment Steps
1. **Database Preparation:**
   - Ensure RDS cluster is available
   - Create environment-specific database
   - Configure access credentials in Kubernetes secrets

2. **Namespace Setup:**
   - Create dedicated namespace
   - Apply RBAC configurations
   - Configure service accounts

3. **Configuration Validation:**
   - Validate Helm values files
   - Test database connectivity
   - Verify IAM role permissions

### Post-Deployment Verification
1. **Component Health:**
   - Scheduler pod status
   - Webserver accessibility
   - Database connectivity

2. **Functional Testing:**
   - DAG import and parsing
   - Task execution capability
   - API endpoint availability

## High Availability and Scaling

### Scheduler High Availability
- **Production:** 2 scheduler replicas
- **Leader Election:** Built-in Airflow mechanism
- **Failure Handling:** Automatic failover

### Webserver Scaling
- **Horizontal Scaling:** Multiple webserver replicas
- **Load Distribution:** NLB handles request distribution
- **Session Management:** Database-backed sessions

### Dynamic Worker Scaling
- **Auto Scaling:** KubernetesExecutor handles scaling
- **Resource Limits:** Per-pod resource constraints
- **Queue Management:** Automatic based on task backlog

### Database Resilience
- **RDS Multi-AZ:** Available for production
- **Automated Backups:** RDS automated backup retention
- **Point-in-Time Recovery:** RDS PITR capabilities

## Monitoring and Logging

### Application Logging
- **Destination:** CloudWatch Logs
- **Log Groups:** `/aws/eks/${cluster}/airflow*`
- **Retention:** Configurable per environment

### Metrics Collection
- **Airflow Metrics:** Built-in StatsD integration capability
- **Kubernetes Metrics:** Cluster-level monitoring
- **Custom Metrics:** Task execution metrics

### Health Monitoring
- **Health Checks:** HTTP endpoints (`/health`)
- **Liveness Probes:** Kubernetes native
- **Readiness Probes:** Service availability checks

## Security Considerations

### Authentication and Authorization
- **Webserver Auth:** Password-based authentication enabled
- **API Auth:** Basic auth and session-based
- **RBAC:** Airflow native role-based access control

### Network Security
- **Internal Only:** No public internet access
- **Corporate Network:** Restricted CIDR access
- **TLS Encryption:** HTTPS/TLS for all communications

### Secrets Management
- **Database Credentials:** Kubernetes secrets
- **Connection Strings:** Airflow connections in metadata DB
- **API Keys:** AWS Secrets Manager integration

## Current DAG Inventory

### 1. Daily Risk Processing (`daily_risk_processing.py`)
- **Schedule:** 6 AM weekdays (0 6 * * 1-5)
- **Purpose:** Daily market data processing and risk calculations
- **Dependencies:** MarketDataProcessor, business logic libraries

### 2. API-Triggered Risk Analysis (`api_triggered_risk_analysis.py`)
- **Trigger:** External API calls
- **Purpose:** On-demand risk analysis workflows
- **Integration:** REST API endpoints

## Operational Procedures

### Deployment Updates
1. Update Helm values files
2. Validate configuration changes
3. Deploy using Helm upgrade
4. Verify component health

### DAG Management
1. Commit DAGs to Git repository
2. Git sync automatically pulls changes
3. Airflow detects and imports new DAGs
4. Monitor DAG parsing logs

### Scaling Operations
1. **Horizontal Scaling:** Update replica counts in Helm values
2. **Vertical Scaling:** Adjust resource requests/limits
3. **Auto Scaling:** Configure HPA for production

## Cost Optimization

### Resource Efficiency
- **KubernetesExecutor:** No idle worker costs
- **Dynamic Scaling:** Resources allocated only when needed
- **Shared Infrastructure:** RDS shared across services

### Environment Sizing
- **Development:** Minimal resource allocation
- **Production:** Right-sized for actual workload
- **Autoscaling:** Automatic scale-down during low usage

## Future Considerations

### Potential Improvements
1. **Custom Operators:** Develop organization-specific operators
2. **Monitoring Enhancement:** Advanced metrics and alerting
3. **Security Hardening:** Enhanced RBAC and network policies
4. **Disaster Recovery:** Cross-region backup strategies

### Technology Evolution
- **Airflow Upgrades:** Regular version updates
- **Kubernetes Features:** Leverage new K8s capabilities
- **AWS Integration:** Enhanced AWS service integration

---

**Document Maintained By:** Infrastructure Team  
**Last Updated:** September 21, 2025  
**Next Review:** December 21, 2025

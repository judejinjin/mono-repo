# Risk API Service Infrastructure Analysis

**Document Created:** September 21, 2025  
**Service Type:** FastAPI-based REST API Service  
**Infrastructure:** Self-managed on Kubernetes (EKS)

## Executive Summary

The Risk API Service is a **self-managed FastAPI-based REST API** deployed on Amazon EKS (Elastic Kubernetes Service). It provides risk management operations including portfolio risk calculations, market data processing, and analytics report generation. The service uses modern Python web framework technologies with containerized deployment and external database integration.

## Architecture Overview

### Technology Stack
- **Framework:** FastAPI 0.104.1 (Python)
- **Runtime:** Uvicorn ASGI server
- **Container Orchestration:** Amazon EKS
- **Database:** External PostgreSQL (RDS) + Snowflake integration
- **Service Port:** 8000 (internal), 80 (service)

### Deployment Model
- **Container-based deployment** using Docker images
- **Kubernetes Deployment** with ClusterIP service
- **Multi-environment setup** (dev/uat/prod)
- **ECR-based image storage** with versioned releases

## Service Components

### 1. FastAPI Application (`risk_api.py`)

#### Core Features
```python
# Main Application
- Title: "Risk Management API"
- Version: "1.0.0"
- Port: 8000
- CORS: Enabled (configurable origins)
```

#### API Endpoints
1. **Health & Status:**
   - `GET /` - Root endpoint with service info
   - `GET /health` - Health check endpoint

2. **Risk Management:**
   - `POST /api/v1/risk/calculate` - Portfolio risk metrics calculation
   - Risk metrics: VaR 95%, VaR 99%, Expected Shortfall, Volatility, Sharpe Ratio

3. **Market Data:**
   - Market data processing endpoints
   - Asset class filtering capabilities

4. **Reporting:**
   - Report generation with configurable parameters
   - Date range and report type selection

#### Business Logic Integration
- **RiskCalculator:** Portfolio risk calculations
- **MarketDataProcessor:** Market data handling
- **ReportGenerator:** Analytics report creation
- **Database Integration:** SQLAlchemy with external databases

### 2. Kubernetes Deployment Configuration

#### Deployment Specification
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-app
  namespace: {{ environment-specific }}
spec:
  replicas: {{ configurable per environment }}
  selector:
    matchLabels:
      app: fastapi
```

#### Container Configuration
```yaml
containers:
- name: fastapi
  image: "{{ ECR_REGISTRY }}/mono-repo/fastapi:{{ VERSION_TAG }}"
  ports:
  - containerPort: 8000
  env:
  - name: ENV
    value: "{{ environment }}"
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: database-secrets
        key: riskdb_url
  - name: SNOWFLAKE_URL
    valueFrom:
      secretKeyRef:
        name: database-secrets
        key: snowflake_url
```

#### Health Monitoring
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

### 3. Service Configuration

#### Kubernetes Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: fastapi-service
spec:
  selector:
    app: fastapi
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP
```

#### Load Balancer Integration
- **Target Group:** `fastapi` (port 8000)
- **Health Check:** `/health` endpoint
- **Path Routing:** `/api/*` routes to FastAPI service
- **Load Balancer:** Internal Application Load Balancer

## Infrastructure Components

### 1. Container Registry
- **Registry:** Amazon ECR (Elastic Container Registry)
- **Repository Names:**
  - Dev: `mono-repo-test-api-service`
  - UAT: `mono-repo-uat-api-service`
  - Prod: `mono-repo-prod-api-service`
- **Image Tagging:** Version-based tagging strategy

### 2. Database Integration

#### Primary Database (PostgreSQL)
- **Connection:** External RDS PostgreSQL cluster
- **Authentication:** Kubernetes secrets (`database-secrets`)
- **Environment-specific endpoints:**
  - Dev: `riskdb-dev.cluster-xyz.us-east-1.rds.amazonaws.com`
  - UAT: `riskdb-uat.cluster-xyz.us-east-1.rds.amazonaws.com`
  - Prod: `riskdb-prod.cluster-xyz.us-east-1.rds.amazonaws.com`

#### Analytics Database (Snowflake)
- **Purpose:** Advanced analytics and data warehouse operations
- **Connection:** Snowflake URL via secrets
- **Integration:** SQLAlchemy-based connection management

### 3. IAM Security Model

#### Service Role: `risk_api_role`
**Trust Relationship:**
- EKS OIDC provider integration
- Service account: `system:serviceaccount:default:fastapi-service-account`

**Permissions:**
1. **RDS Access:**
   ```json
   {
     "Effect": "Allow",
     "Action": [
       "rds:DescribeDBInstances",
       "rds:DescribeDBClusters"
     ],
     "Resource": "arn:aws:rds:*:*:db:${rds_instance_identifier}"
   }
   ```

2. **Secrets Manager Access:**
   ```json
   {
     "Effect": "Allow", 
     "Action": ["secretsmanager:GetSecretValue"],
     "Resource": [
       "arn:aws:secretsmanager:*:secret:${prefix}-db-credentials-*",
       "arn:aws:secretsmanager:*:secret:${prefix}-api-keys-*"
     ]
   }
   ```

3. **S3 Access:**
   ```json
   {
     "Effect": "Allow",
     "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
     "Resource": [
       "arn:aws:s3:::${prefix}-assets/*",
       "arn:aws:s3:::${prefix}-backups/*"
     ]
   }
   ```

4. **CloudWatch Logging:**
   ```json
   {
     "Effect": "Allow",
     "Action": [
       "logs:CreateLogGroup",
       "logs:CreateLogStream", 
       "logs:PutLogEvents"
     ],
     "Resource": "arn:aws:logs:*:log-group:/aws/eks/${cluster}/risk-api*"
   }
   ```

## Network Architecture

### 1. Load Balancing Strategy

#### Internal Application Load Balancer
- **Type:** Application Load Balancer (ALB)
- **Scope:** Internal corporate network only
- **Security:** Corporate CIDR-restricted access
- **SSL:** Configurable HTTPS with certificate management

#### Path-Based Routing
```
Corporate Network → ALB → Target Groups
                    │
                    ├── /api/* → FastAPI Service (Port 8000)
                    ├── /airflow/* → Airflow Service (Port 8080)
                    ├── /dash/* → Dash Service (Port 8050)
                    └── /* → Web Application (Port 3000)
```

### 2. Target Group Configuration
```terraform
resource "aws_lb_target_group" "fastapi" {
  name     = "${project_name}-${environment}-fastapi"
  port     = 8000
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id
  
  health_check {
    enabled             = true
    healthy_threshold   = 2
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    matcher             = "200"
  }
}
```

### 3. Network Security
- **VPC:** Private subnets only
- **Security Groups:** Controlled ingress/egress
- **Corporate Access:** Intranet-only, no public internet exposure
- **Inter-service Communication:** Service mesh capabilities

## Environment-Specific Configurations

### Development Environment
```yaml
Environment: dev
Namespace: genai-dev
Replicas: 1 (typically)
Resource Profile: Minimal
CPU Requests: 100m
Memory Requests: 256Mi
CPU Limits: 500m
Memory Limits: 512Mi
Database: riskdb-dev
Logging Level: DEBUG
CORS: Permissive (development)
```

### UAT Environment
```yaml
Environment: uat
Namespace: genai-uat
Replicas: 1-2
Resource Profile: Testing
CPU Requests: 200m
Memory Requests: 512Mi
CPU Limits: 1 CPU
Memory Limits: 1Gi
Database: riskdb-uat
Logging Level: INFO
CORS: Restricted
```

### Production Environment
```yaml
Environment: prod
Namespace: genai-prod
Replicas: 2-5 (auto-scaling)
Resource Profile: Production
CPU Requests: 500m
Memory Requests: 1Gi
CPU Limits: 2 CPU
Memory Limits: 2Gi
Database: riskdb-prod
Logging Level: WARNING
CORS: Strict corporate domains
Autoscaling: HPA enabled
```

## API Documentation & Capabilities

### 1. Risk Management Endpoints

#### Calculate Portfolio Risk
```http
POST /api/v1/risk/calculate
Content-Type: application/json

{
  "portfolio_id": "PORT-12345",
  "calculation_date": "2025-09-21"
}
```

**Response:**
```json
{
  "portfolio_id": "PORT-12345",
  "var_95": 125000.50,
  "var_99": 187500.75,
  "expected_shortfall": 225000.00,
  "volatility": 0.15,
  "sharpe_ratio": 1.25,
  "calculated_at": "2025-09-21T10:30:00Z"
}
```

### 2. Market Data Endpoints
- Asset class filtering
- Date range processing
- Real-time and historical data access

### 3. Reporting Endpoints
- Configurable report generation
- Multiple output formats
- Scheduled and on-demand reports

## Deployment Process

### 1. CI/CD Pipeline Integration
```bash
# Build phase
docker build -t ${ECR_REGISTRY}/mono-repo/fastapi:${VERSION} .
docker push ${ECR_REGISTRY}/mono-repo/fastapi:${VERSION}

# Deploy phase
kubectl apply -f deploy/kubernetes/fastapi/
kubectl rollout status deployment/fastapi-app --namespace=${NAMESPACE}
```

### 2. Health Check Validation
```bash
# Verify deployment
kubectl get pods -n ${NAMESPACE} -l app=fastapi
kubectl logs -f deployment/fastapi-app -n ${NAMESPACE}

# Test health endpoint
curl http://fastapi-service.${NAMESPACE}.svc.cluster.local/health
```

### 3. Load Balancer Registration
- Automatic target registration via Kubernetes service discovery
- Health check validation before traffic routing
- Blue-green deployment support

## Monitoring and Observability

### 1. Application Logging
- **Destination:** CloudWatch Logs
- **Log Groups:** `/aws/eks/${cluster_name}/risk-api*`
- **Log Levels:** Configurable per environment
- **Structured Logging:** JSON format for analytics

### 2. Health Monitoring
- **Liveness Probe:** `/health` endpoint (30s delay, 10s interval)
- **Readiness Probe:** `/health` endpoint (5s delay, 5s interval)
- **Custom Metrics:** Business logic metrics via StatsD

### 3. Performance Monitoring
- **Response Time:** API endpoint latency tracking
- **Throughput:** Requests per second monitoring
- **Error Rates:** HTTP status code distribution
- **Database Performance:** Connection pool and query metrics

## Security Considerations

### 1. API Security Features
- **CORS:** Configurable cross-origin resource sharing
- **Authentication:** JWT token support (planned)
- **Rate Limiting:** Application-level throttling
- **Input Validation:** Pydantic model validation

### 2. Network Security
- **Internal Only:** No public internet exposure
- **Corporate Network:** Restricted CIDR access
- **TLS Encryption:** HTTPS-only in production
- **Security Groups:** Fine-grained network controls

### 3. Data Security
- **Secrets Management:** Kubernetes secrets + AWS Secrets Manager
- **Database Encryption:** TLS in transit, encryption at rest
- **Audit Logging:** Request/response logging for compliance

### 4. Container Security
- **Base Images:** Minimal, security-hardened images
- **Vulnerability Scanning:** ECR image scanning
- **Resource Limits:** Container resource constraints
- **Non-root User:** Container security best practices

## Performance and Scaling

### 1. Horizontal Scaling
- **Auto Scaling:** Horizontal Pod Autoscaler (HPA)
- **Metrics:** CPU and memory utilization
- **Scale Range:** 2-5 replicas (production)
- **Scale Triggers:** 70% CPU utilization threshold

### 2. Resource Optimization
- **CPU Efficiency:** Uvicorn worker processes
- **Memory Management:** Python garbage collection tuning
- **Connection Pooling:** Database connection optimization
- **Caching:** Application-level caching strategies

### 3. Database Performance
- **Connection Pooling:** SQLAlchemy pool management
- **Query Optimization:** Database indexing and query tuning
- **Read Replicas:** Potential for read scaling
- **Caching Layer:** Redis integration capability

## Operational Procedures

### 1. Deployment Operations
```bash
# Standard deployment
./deploy.py --target services --environment prod

# Rollback procedure
kubectl rollout undo deployment/fastapi-app -n genai-prod

# Configuration updates
kubectl patch deployment fastapi-app -p '{"spec":{"template":{"spec":{"containers":[{"name":"fastapi","env":[...]}]}}}}'
```

### 2. Troubleshooting
```bash
# Check pod status
kubectl get pods -n ${NAMESPACE} -l app=fastapi

# View logs
kubectl logs -f deployment/fastapi-app -n ${NAMESPACE}

# Port forwarding for debugging
kubectl port-forward svc/fastapi-service 8000:80 -n ${NAMESPACE}

# Database connectivity test
kubectl exec -it deployment/fastapi-app -n ${NAMESPACE} -- python -c "from config import get_config; print('DB OK')"
```

### 3. Maintenance Operations
- **Rolling Updates:** Zero-downtime deployments
- **Configuration Changes:** ConfigMap and Secret updates
- **Database Migrations:** Alembic migration support
- **Health Monitoring:** Continuous availability verification

## Cost Optimization

### 1. Resource Efficiency
- **Right-sizing:** Environment-appropriate resource allocation
- **Auto-scaling:** Scale down during low usage periods
- **Shared Infrastructure:** Common load balancer and networking

### 2. Container Optimization
- **Multi-stage Builds:** Minimal production images
- **Layer Caching:** Efficient Docker layer utilization
- **Resource Requests:** Accurate CPU/memory specifications

## Future Enhancements

### 1. Planned Improvements
- **JWT Authentication:** Comprehensive API security
- **API Rate Limiting:** Advanced throttling mechanisms
- **Caching Layer:** Redis integration for performance
- **Metrics Dashboard:** Custom Grafana dashboards

### 2. Scalability Enhancements
- **Service Mesh:** Istio integration for advanced traffic management
- **Circuit Breaker:** Resilience patterns implementation
- **Advanced Monitoring:** APM integration (New Relic, Datadog)
- **Multi-region:** Cross-region deployment capabilities

### 3. Integration Improvements
- **Event-driven Architecture:** Async message processing
- **GraphQL API:** Alternative API paradigm
- **Streaming APIs:** Real-time data processing
- **Microservices Split:** Domain-specific service separation

---

**Document Maintained By:** Platform Engineering Team  
**Last Updated:** September 21, 2025  
**Next Review:** December 21, 2025

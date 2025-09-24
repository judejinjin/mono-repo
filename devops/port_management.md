# Port Management Analysis - GenAI Mono-Repo

## Overview

This document provides a comprehensive analysis of how port numbers are managed across all services in the GenAI mono-repo project. The system implements a sophisticated multi-layered port management approach with consistent allocation standards and flexible configuration options.

## Service Port Allocation Standards

The project uses standardized port allocation across all environments to ensure consistency and avoid conflicts:

| Service | Internal Port | External Port | Load Balancer Port | Protocol |
|---------|---------------|---------------|--------------------|----------|
| **FastAPI** (Risk API) | 8000 | 8000 | 80 → 8000 | HTTP |
| **Web** (React Dashboard) | 3000 | 3000 | 80 → 3000 | HTTP |
| **Dash** (Analytics Dashboard) | 8050 | 8050 | 80 → 8050 | HTTP |
| **Airflow** (Webserver) | 8080 | 8080 | 80 → 8080 | HTTP |
| **Database** (PostgreSQL) | 5432 | 5432 | N/A | TCP |
| **Redis** | 6379 | 6379 | N/A | TCP |

### Port Range Allocation Strategy

- **1000-2999**: Reserved for system services
- **3000-3999**: Web applications (React, Vue, etc.)
- **8000-8999**: API services and backend applications
- **Above 9000**: Development and testing services

## Configuration Management Hierarchy

The port configuration follows a hierarchical precedence model ensuring flexibility while maintaining consistency:

### Priority Order
1. **Parameter Store** (Highest priority)
2. **Environment Variables**
3. **YAML Configuration Files**
4. **Code Defaults** (Lowest priority)

### A. YAML Configuration Files

#### Base Configuration (`config/base.yaml`)
```yaml
fastapi:
  host: "0.0.0.0"
  workers: 4
  reload: false

dash:
  host: "0.0.0.0"
  debug: false

# Note: Ports are defined in environment-specific files
```

#### Environment-Specific Configuration
**Development** (`config/dev.yaml`):
```yaml
fastapi:
  port: 8000
  reload: true    # Development-specific
  workers: 2

dash:
  port: 8050
  debug: true     # Development-specific

web:
  port: 3000
  api_base_url: "https://api-dev.monorepo.com"

airflow:
  webserver_port: 8080
  executor: "KubernetesExecutor"
  namespace: "airflow-dev"
```

**UAT** (`config/uat.yaml`):
```yaml
fastapi:
  port: 8000
  reload: false
  workers: 3

dash:
  port: 8050
  debug: false

web:
  port: 3000
  api_base_url: "https://api-uat.monorepo.com"

airflow:
  webserver_port: 8080
  namespace: "airflow-uat"
```

**Production** (`config/prod.yaml`):
```yaml
fastapi:
  port: 8000
  reload: false
  workers: 8      # Production scaling

dash:
  port: 8050
  debug: false

web:
  port: 3000
  api_base_url: "https://api.monorepo.com"

airflow:
  webserver_port: 8080
  namespace: "airflow-prod"
```

### B. Parameter Store Configuration

The `scripts/setup_environment_config.py` manages Parameter Store configuration:

```python
def populate_application_parameters(self):
    """Populate application-specific parameters."""
    
    # FastAPI parameters
    fastapi_params = {
        'port': os.getenv('FASTAPI_PORT', '8000'),
        'host': '0.0.0.0',
        'debug': str(self.environment == 'dev').lower(),
        'workers': '1' if self.environment == 'dev' else '4',
        'reload': str(self.environment == 'dev').lower()
    }
    
    # Web application parameters  
    web_params = {
        'port': os.getenv('WEB_PORT', '3000'),
        'debug': str(self.environment == 'dev').lower(),
        'build_env': self.environment
    }
    
    # Dash application parameters
    dash_params = {
        'port': os.getenv('DASH_PORT', '8050'),
        'debug': str(self.environment == 'dev').lower(),
        'dev_tools_hot_reload': str(self.environment == 'dev').lower()
    }
    
    # Airflow parameters
    airflow_params = {
        'webserver_port': os.getenv('AIRFLOW_WEBSERVER_PORT', '8080'),
        'executor': 'KubernetesExecutor',
        'namespace': f'airflow-{self.environment}',
        'dag_dir': '/opt/airflow/dags'
    }
```

### C. Environment Variable Fallbacks

Default environment variables for port configuration:

```bash
# Service Ports
FASTAPI_PORT=8000
WEB_PORT=3000  
DASH_PORT=8050
AIRFLOW_WEBSERVER_PORT=8080

# Database Ports
DATABASE_PORT=5432
REDIS_PORT=6379
```

## Service Implementation Patterns

### A. FastAPI Service (`services/risk_api.py`)

The FastAPI service demonstrates the configuration loading pattern:

```python
if __name__ == "__main__":
    import uvicorn
    
    # Load configuration from hierarchy
    config = get_config()
    fastapi_config = config.get('fastapi', {})
    
    # Start server with configured ports
    uvicorn.run(
        "main:app",
        host=fastapi_config.get('host', '0.0.0.0'),
        port=fastapi_config.get('port', 8000),  # Port from config hierarchy
        reload=fastapi_config.get('reload', False),
        workers=fastapi_config.get('workers', 1)
    )

@app.get("/api/v1/config")
async def get_api_config():
    """Expose current configuration including port."""
    config = get_config()
    api_config = config.get('fastapi', {})
    
    return {
        "environment": config.get('app', {}).get('environment', 'unknown'),
        "host": api_config.get('host', '0.0.0.0'),
        "port": api_config.get('port', 8000)  # Current port configuration
    }
```

### B. Dash Application (`dash/risk_dashboard.py`)

Dash analytics dashboard configuration:

```python
# Initialize configuration
config = get_config()
dash_config = config.get('dash', {})

if __name__ == '__main__':
    app.run_server(
        debug=dash_config.get('debug', False),
        host=dash_config.get('host', '0.0.0.0'),
        port=dash_config.get('port', 8050)  # Port from config hierarchy
    )
```

### C. Web Application (`web/dashboard/vite.config.ts`)

React application with development server configuration:

```typescript
export default defineConfig({
  server: {
    port: 3000,  // Configurable via CLI: --port 3001
    proxy: {
      '/api': {
        target: 'http://localhost:8000',  // Proxy to FastAPI service
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
```

## Kubernetes Deployment Port Management

### A. Service Definitions

Services expose applications through consistent port mappings:

**FastAPI Service** (`deploy/kubernetes/fastapi/service.yaml`):
```yaml
apiVersion: v1
kind: Service
metadata:
  name: fastapi-service
spec:
  type: ClusterIP
  ports:
  - port: 80           # External cluster port
    targetPort: 8000   # Internal container port
    protocol: TCP
    name: http
  selector:
    app: fastapi
```

**Web Service** (`deploy/kubernetes/web/service.yaml`):
```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-service
spec:
  type: ClusterIP
  ports:
  - port: 80           # External cluster port
    targetPort: 3000   # Internal container port
    protocol: TCP
```

**Dash Service** (`deploy/kubernetes/dash/service.yaml`):
```yaml
apiVersion: v1
kind: Service
metadata:
  name: dash-service
spec:
  type: ClusterIP
  ports:
  - port: 80           # External cluster port  
    targetPort: 8050   # Internal container port
    protocol: TCP
```

### B. Container Port Configuration

Deployments must specify container ports matching service targetPorts:

**FastAPI Deployment**:
```yaml
containers:
- name: fastapi
  image: "{{ .Values.registry.url }}/mono-repo/fastapi:{{ .Values.image_tag }}"
  ports:
  - containerPort: 8000  # Must match service targetPort
  env:
  - name: PORT
    value: "8000"
```

**Web Deployment**:
```yaml
containers:
- name: web
  image: "{{ .Values.registry.url }}/mono-repo/web:{{ .Values.image_tag }}"
  ports:
  - containerPort: 3000  # Must match service targetPort
```

**Dash Deployment**:
```yaml
containers:
- name: dash
  image: "{{ .Values.registry.url }}/mono-repo/dash:{{ .Values.image_tag }}"
  ports:
  - containerPort: 8050  # Must match service targetPort
  env:
  - name: PORT
    value: "8050"
```

### C. Health Check Configuration

Health checks use the same port configuration:

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000  # FastAPI health check
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health
    port: 8000  # FastAPI readiness check
  initialDelaySeconds: 5
  periodSeconds: 5
```

## Load Balancer and Ingress Configuration

### A. Application Load Balancer (Terraform)

Target groups for each service with health checks:

```hcl
# FastAPI Target Group
resource "aws_lb_target_group" "fastapi" {
  name     = "${var.project_name}-${var.environment}-fastapi"
  port     = 8000  # Application internal port
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id
  
  health_check {
    enabled             = true
    healthy_threshold   = 2
    path                = "/health"
    port                = "traffic-port"  # Uses target group port (8000)
    protocol            = "HTTP"
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    matcher             = "200"
  }
}

# Web Application Target Group
resource "aws_lb_target_group" "webapp" {
  name     = "${var.project_name}-${var.environment}-webapp"
  port     = 3000  # Application internal port  
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id
}

# Dash Analytics Target Group
resource "aws_lb_target_group" "dash" {
  name     = "${var.project_name}-${var.environment}-dash"
  port     = 8050  # Application internal port
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id
}

# Airflow Target Group  
resource "aws_lb_target_group" "airflow" {
  name     = "${var.project_name}-${var.environment}-airflow"
  port     = 8080  # Application internal port
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id
}
```

### B. Ingress Routing Configuration

Path-based routing through Application Load Balancer:

```yaml
# deploy/kubernetes/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: mono-repo-ingress
  annotations:
    kubernetes.io/ingress.class: "alb"
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTP": 80}, {"HTTPS": 443}]'
spec:
  rules:
  - http:
      paths:
      - path: /api/*
        pathType: Prefix
        backend:
          service:
            name: fastapi-service
            port:
              number: 80  # Routes to FastAPI (8000 internally)
      - path: /dash/*
        pathType: Prefix  
        backend:
          service:
            name: dash-service
            port:
              number: 80  # Routes to Dash (8050 internally)
      - path: /airflow/*
        pathType: Prefix
        backend:
          service:
            name: airflow-service
            port:
              number: 80  # Routes to Airflow (8080 internally)
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-service  
            port:
              number: 80  # Routes to Web (3000 internally)
```

### C. Routing Flow Diagram

```
External Traffic (Port 80/443)
         ↓
   Application Load Balancer
         ↓
   ┌─────────────────────────────────────┐
   │  Path-Based Routing Rules           │
   ├─────────────────────────────────────┤
   │ /api/*     → FastAPI Service:80     │
   │ /dash/*    → Dash Service:80        │
   │ /airflow/* → Airflow Service:80     │
   │ /*         → Web Service:80         │
   └─────────────────────────────────────┘
         ↓
   Kubernetes Services (Port 80)
         ↓
   ┌─────────────────────────────────────┐
   │  Service → Pod Port Mapping         │
   ├─────────────────────────────────────┤
   │ FastAPI Service:80  → Pod:8000      │
   │ Dash Service:80     → Pod:8050      │
   │ Airflow Service:80  → Pod:8080      │
   │ Web Service:80      → Pod:3000      │
   └─────────────────────────────────────┘
```

## Infrastructure Security Groups

Security group configurations for development and production environments:

### A. Development Server Security (`infrastructure/terraform/dev_server.tf`)

```hcl
# SSH Access
resource "aws_security_group_rule" "ssh_access" {
  type              = "ingress"
  from_port         = 22
  to_port           = 22
  protocol          = "tcp"
  cidr_blocks       = [var.allowed_cidr_blocks]
  security_group_id = aws_security_group.dev_server.id
}

# FastAPI Service Access
resource "aws_security_group_rule" "fastapi_access" {
  type              = "ingress"
  from_port         = 8000
  to_port           = 8000
  protocol          = "tcp"
  cidr_blocks       = [var.vpc_cidr]
  security_group_id = aws_security_group.dev_server.id
}

# Web Application Access  
resource "aws_security_group_rule" "web_access" {
  type              = "ingress"
  from_port         = 3000
  to_port           = 3000
  protocol          = "tcp"
  cidr_blocks       = [var.vpc_cidr]
  security_group_id = aws_security_group.dev_server.id
}

# Dash Analytics Access
resource "aws_security_group_rule" "dash_access" {
  type              = "ingress"
  from_port         = 8050
  to_port           = 8050
  protocol          = "tcp"
  cidr_blocks       = [var.vpc_cidr]
  security_group_id = aws_security_group.dev_server.id
}

# Airflow Webserver Access
resource "aws_security_group_rule" "airflow_access" {
  type              = "ingress"
  from_port         = 8080
  to_port           = 8080
  protocol          = "tcp"
  cidr_blocks       = [var.vpc_cidr]
  security_group_id = aws_security_group.dev_server.id
}
```

### B. EKS Cluster Security

```hcl
# Application Load Balancer Security Group
resource "aws_security_group" "alb" {
  name_prefix = "${var.project_name}-${var.environment}-alb-"
  vpc_id      = aws_vpc.main.id

  # HTTP Access
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Internet-facing
  }

  # HTTPS Access
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Internet-facing
  }

  # All outbound traffic
  egress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }
}
```

## Port Validation and Standards

### A. Parameter Validation (`scripts/validate_parameter_store.py`)

Automated validation ensures port configurations are within acceptable ranges:

```python
def get_validation_rules():
    """Define validation rules for port parameters."""
    return {
        'fastapi': {
            'port': lambda x: x.isdigit() and 1000 <= int(x) <= 65535,
            'host': lambda x: x in ['0.0.0.0', '127.0.0.1', 'localhost'] or is_valid_ip(x),
            'workers': lambda x: x.isdigit() and 1 <= int(x) <= 16
        },
        'web': {
            'port': lambda x: x.isdigit() and 1000 <= int(x) <= 65535,
            'debug': lambda x: x.lower() in ['true', 'false']
        },
        'dash': {
            'port': lambda x: x.isdigit() and 1000 <= int(x) <= 65535,
            'debug': lambda x: x.lower() in ['true', 'false']
        },
        'airflow': {
            'webserver_port': lambda x: x.isdigit() and 1000 <= int(x) <= 65535,
            'executor': lambda x: x in ['LocalExecutor', 'KubernetesExecutor', 'CeleryExecutor']
        }
    }
```

### B. Port Conflict Prevention

The system prevents port conflicts through:

1. **Standardized Port Ranges**: Each service type has dedicated ranges
2. **Validation Rules**: Automated checks for valid port numbers
3. **Environment Isolation**: Different namespaces per environment
4. **Documentation**: Clear port allocation standards

## Operational Procedures

### A. Port Configuration Updates

To update port configurations:

1. **Parameter Store** (Recommended for production):
   ```bash
   # Update FastAPI port
   aws ssm put-parameter \
     --name "/prod/mono-repo/fastapi/port" \
     --value "8001" \
     --type "String" \
     --overwrite
   
   # Restart services to pick up new configuration
   kubectl rollout restart deployment/fastapi-deployment -n mono-repo-prod
   ```

2. **Environment Variables** (For development):
   ```bash
   export FASTAPI_PORT=8001
   python services/risk_api.py
   ```

3. **YAML Configuration** (For permanent changes):
   ```yaml
   # config/prod.yaml
   fastapi:
     port: 8001  # Updated port
   ```

### B. Port Monitoring and Health Checks

Monitor port accessibility and service health:

```bash
# Check service availability
curl -f http://localhost:8000/health  # FastAPI health check
curl -f http://localhost:3000/        # Web application
curl -f http://localhost:8050/        # Dash analytics
curl -f http://localhost:8080/health  # Airflow health check

# Check port binding
netstat -tlnp | grep :8000  # FastAPI port
netstat -tlnp | grep :3000  # Web port
netstat -tlnp | grep :8050  # Dash port
netstat -tlnp | grep :8080  # Airflow port
```

### C. Troubleshooting Port Issues

Common port-related issues and solutions:

1. **Port Already in Use**:
   ```bash
   # Find process using port
   lsof -i :8000
   
   # Kill process if necessary
   kill -9 <PID>
   ```

2. **Service Not Accessible**:
   ```bash
   # Check security group rules
   aws ec2 describe-security-groups --group-ids sg-xxxxx
   
   # Verify service is running
   kubectl get pods -n mono-repo-prod
   kubectl logs deployment/fastapi-deployment -n mono-repo-prod
   ```

3. **Load Balancer Health Check Failures**:
   ```bash
   # Check target group health
   aws elbv2 describe-target-health --target-group-arn <target-group-arn>
   
   # Verify health endpoint
   curl -f http://<pod-ip>:8000/health
   ```

## Best Practices and Guidelines

### A. Port Management Principles

1. **Consistency**: Use the same ports across all environments (dev, UAT, prod)
2. **Flexibility**: Support configuration through multiple methods (Parameter Store, env vars, YAML)
3. **Security**: Use internal container ports mapped to standard external ports (80/443)
4. **Isolation**: Assign dedicated port ranges to avoid conflicts
5. **Standardization**: Follow industry standards (3000 for React, 8000 for FastAPI, etc.)
6. **Documentation**: Maintain clear documentation of all port assignments
7. **Validation**: Implement automated validation for port configurations
8. **Monitoring**: Include port accessibility in health checks

### B. Development Guidelines

1. **Local Development**: Use default ports for consistency
2. **Testing**: Avoid hardcoding ports in tests; use configuration
3. **Documentation**: Update this document when adding new services
4. **Security**: Never expose sensitive services on public ports
5. **Performance**: Consider port ranges for load balancing and scaling

### C. Production Considerations

1. **Change Management**: Use Parameter Store for production port changes
2. **Rollback Plan**: Maintain ability to quickly revert port changes
3. **Monitoring**: Set up alerts for port accessibility issues
4. **Security**: Regularly audit port configurations and access rules
5. **Capacity Planning**: Monitor port usage and plan for scaling

## Future Considerations

### A. Service Mesh Integration

When implementing service mesh (Istio/Linkerd):
- Service-to-service communication will use service names instead of ports
- Sidecar proxies will handle port translation
- Traffic policies will be defined at the service mesh level

### B. Container Orchestration Evolution

As Kubernetes evolves:
- Service mesh adoption may change port management strategies
- CNI plugins may provide additional networking capabilities
- Port policies may become more declarative

### C. Monitoring and Observability

Enhanced monitoring capabilities:
- Automatic service discovery based on port configurations
- Traffic flow analysis between services
- Port usage optimization recommendations

---

## Document Maintenance

**Last Updated**: September 23, 2025  
**Maintained By**: DevOps Team  
**Review Cycle**: Monthly  
**Next Review**: October 23, 2025

**Change Log**:
- 2025-09-23: Initial port management analysis documentation
- 2025-09-23: Added comprehensive service port mappings and configuration hierarchy
- 2025-09-23: Documented Kubernetes deployment patterns and security configurations

For questions or updates to this document, please contact the DevOps team or create an issue in the repository.
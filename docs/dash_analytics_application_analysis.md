# Dash Analytics Application Infrastructure Analysis

**Document Created:** September 21, 2025  
**Application Type:** Python Dash Analytics Dashboard  
**Infrastructure:** Self-managed on Kubernetes (EKS)

## Executive Summary

The Dash Analytics Application is a **self-managed Python-based interactive dashboard** deployed on Amazon EKS. Built with Dash 2.14.2 and Plotly 5.17.0, it provides real-time portfolio risk monitoring and analysis with interactive visualizations. The application serves as the primary analytics interface for risk management operations with corporate intranet access.

## Architecture Overview

### Technology Stack
- **Framework:** Dash 2.14.2 (Python-based web framework)
- **Visualization:** Plotly 5.17.0 (Interactive charts and graphs)
- **Runtime:** Python with Flask-based WSGI server
- **Container Orchestration:** Amazon EKS
- **Service Port:** 8050 (internal), 80 (service)

### Application Purpose
- **Primary Function:** Interactive risk management dashboard
- **Target Users:** Risk analysts, portfolio managers, executives
- **Core Features:**
  - Real-time portfolio risk visualization
  - Interactive VaR (Value at Risk) analysis
  - Multi-portfolio comparison tools
  - Historical trend analysis

## Application Components

### 1. Core Dash Application (`dash/risk_dashboard.py`)

#### Application Structure
```python
# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Risk Management Dashboard"

# Main features:
- Portfolio risk visualization
- Interactive date range selection
- Multi-metric dashboard layout
- Real-time data integration
```

#### Key Visualizations

**1. Value at Risk (VaR) Charts**
```python
@callback(
    Output('var-chart', 'figure'),
    [Input('portfolio-dropdown', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
```
- **Purpose:** 95% VaR risk measurement over time
- **Visualization:** Time series line charts with markers
- **Interactivity:** Portfolio selection and date filtering

**2. Portfolio Volatility Analysis**
```python
@callback(
    Output('volatility-chart', 'figure'),
    [...inputs...]
)
```
- **Purpose:** Historical volatility tracking
- **Visualization:** Time series with trend analysis
- **Features:** Portfolio-specific volatility patterns

**3. Sharpe Ratio Performance**
```python
@callback(
    Output('sharpe-chart', 'figure'),
    [...inputs...]
)
```
- **Purpose:** Risk-adjusted return analysis
- **Visualization:** Performance trend visualization
- **Metrics:** Risk-adjusted portfolio performance

**4. Portfolio Comparison Dashboard**
```python
@callback(
    Output('comparison-chart', 'figure'),
    [...inputs...]
)
```
- **Purpose:** Multi-portfolio risk comparison
- **Visualization:** Grouped bar charts with dual y-axes
- **Features:** Side-by-side portfolio analysis

#### Interactive Components

**Portfolio Selection Interface**
```python
dcc.Dropdown(
    id='portfolio-dropdown',
    options=[
        {'label': 'Equity Growth Portfolio', 'value': 'EQUITY_GROWTH'},
        {'label': 'Fixed Income Portfolio', 'value': 'FIXED_INCOME'},
        {'label': 'Balanced Portfolio', 'value': 'BALANCED'},
        {'label': 'Emerging Markets Portfolio', 'value': 'EMERGING_MARKETS'}
    ],
    value='EQUITY_GROWTH'
)
```

**Date Range Controls**
```python
dcc.DatePickerRange(
    id='date-picker-range',
    start_date=datetime.now() - timedelta(days=30),
    end_date=datetime.now(),
    display_format='YYYY-MM-DD'
)
```

**Risk Summary Tables**
- Dynamic summary statistics
- Calculated risk metrics
- Portfolio-specific analytics

### 2. Business Logic Integration

#### Data Sources
```python
from libs.business.analytics import ReportGenerator
from libs.business.risk_management import RiskCalculator
```

#### Portfolio Support
- **EQUITY_GROWTH:** Growth-focused equity portfolios
- **FIXED_INCOME:** Bond and fixed-income securities
- **BALANCED:** Mixed asset allocation portfolios
- **EMERGING_MARKETS:** Emerging market investments

#### Risk Metrics Calculated
- **VaR 95%:** Value at Risk at 95% confidence level
- **Volatility:** Historical price volatility
- **Sharpe Ratio:** Risk-adjusted return measurement
- **Summary Statistics:** Average, maximum, and trend analysis

## Kubernetes Deployment Architecture

### 1. Deployment Configuration

#### Dash Application Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dash-app
  namespace: {{ .Values.namespace }}
  labels:
    app: dash
    environment: {{ .Values.environment }}
spec:
  replicas: {{ .Values.replicas.dash }}
  selector:
    matchLabels:
      app: dash
  template:
    metadata:
      labels:
        app: dash
        environment: {{ .Values.environment }}
    spec:
      imagePullSecrets:
      - name: ecr-registry-secret
      containers:
      - name: dash
        image: "{{ .Values.registry.url }}/mono-repo/dash:{{ .Values.image_tag }}"
        ports:
        - containerPort: 8050
```

#### Environment Configuration
```yaml
env:
- name: ENV
  value: "{{ .Values.environment }}"
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

#### Resource Management
```yaml
resources:
  requests:
    cpu: {{ .Values.resources.dash.cpu }}
    memory: {{ .Values.resources.dash.memory }}
  limits:
    cpu: {{ .Values.resources.dash.limits.cpu }}
    memory: {{ .Values.resources.dash.limits.memory }}
```

#### Health Monitoring
```yaml
livenessProbe:
  httpGet:
    path: /
    port: 8050
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /
    port: 8050
  initialDelaySeconds: 5
  periodSeconds: 5
```

### 2. Service Configuration

#### Kubernetes Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: dash-service
  namespace: {{ .Values.namespace }}
  labels:
    app: dash
    environment: {{ .Values.environment }}
spec:
  selector:
    app: dash
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8050
  type: ClusterIP
```

#### ConfigMap Configuration
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: dash-config
  namespace: {{ .Values.namespace }}
data:
  ENV: "{{ .Values.environment }}"
  PORT: "8050"
  LOG_LEVEL: "INFO"
  DASH_DEBUG: "false"
```

### 3. Ingress Configuration

#### Application Load Balancer Ingress
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: dash-ingress
  namespace: {{ .Values.namespace }}
  annotations:
    kubernetes.io/ingress.class: "alb"
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
spec:
  rules:
  - host: {{ .Values.dash.domain }}
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: dash-service
            port:
              number: 80
```

## Infrastructure Components

### 1. Container Registry
- **Registry:** Amazon ECR (Elastic Container Registry)
- **Repository Names:**
  - Dev: `mono-repo-test-dash-app`
  - UAT: `mono-repo-uat-dash-app`
  - Prod: `mono-repo-prod-dash-app`
- **Image Strategy:** Python-based multi-stage builds

### 2. Load Balancing Architecture

#### Internal Application Load Balancer Integration
```terraform
# Dash Analytics Target Group
resource "aws_lb_target_group" "dash" {
  name     = "${var.project_name}-${var.environment}-dash"
  port     = 8050
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id
  
  health_check {
    enabled             = true
    healthy_threshold   = 2
    path                = "/"
    port                = "traffic-port"
    protocol            = "HTTP"
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    matcher             = "200"
  }
}
```

#### Path-Based Routing Strategy
```
Corporate Network → ALB → Target Groups
                    │
                    ├── /dash/* → Dash Service (Port 8050)
                    ├── /api/* → FastAPI Service (Port 8000)
                    ├── /airflow/* → Airflow Service (Port 8080)
                    └── /* → Web Application (Port 3000) [DEFAULT]
```

#### Routing Rules Configuration
```terraform
# Route /dash/* to Dash Analytics
resource "aws_lb_listener_rule" "dash_routing" {
  listener_arn = aws_lb_listener.intranet_http.arn
  priority     = 300

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.dash.arn
  }

  condition {
    path_pattern {
      values = ["/dash/*"]
    }
  }
}
```

### 3. Database Integration

#### Primary Database (PostgreSQL)
- **Connection:** External RDS PostgreSQL cluster
- **Authentication:** Kubernetes secrets (`database-secrets`)
- **Environment-specific endpoints:**
  - Dev: `riskdb-dev.cluster-xyz.us-east-1.rds.amazonaws.com`
  - UAT: `riskdb-uat.cluster-xyz.us-east-1.rds.amazonaws.com` 
  - Prod: `riskdb-prod.cluster-xyz.us-east-1.rds.amazonaws.com`

#### Analytics Database (Snowflake)
- **Purpose:** Advanced analytics and historical data
- **Connection:** Snowflake URL via secrets
- **Integration:** pandas-based data retrieval

## Build and Deployment Process

### 1. Build Pipeline

#### Python Application Build
```bash
# Development setup
pip install -r requirements.txt
python dash/risk_dashboard.py

# Production build
docker build -t dash-app .
docker tag dash-app ${ECR_REGISTRY}/mono-repo/dash:${VERSION}
docker push ${ECR_REGISTRY}/mono-repo/dash:${VERSION}
```

#### Dependencies Management
```python
# Core requirements (from requirements.txt)
dash==2.14.2
plotly==5.17.0
pandas>=1.5.0
sqlalchemy>=1.4.0
```

### 2. Docker Build Process

#### Multi-stage Dockerfile Strategy
```dockerfile
# Build stage
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY dash/ ./dash/
COPY libs/ ./libs/
COPY config.py .

EXPOSE 8050
CMD ["python", "dash/risk_dashboard.py"]
```

### 3. CI/CD Integration

#### Deployment Script Integration
```python
# deploy.py integration
def _deploy_dash_applications(self) -> bool:
    """Deploy Dash applications."""
    logger.info("Deploying Dash applications...")
    
    manifests_dir = self.deploy_dir / 'kubernetes' / 'dash'
    if not manifests_dir.exists():
        logger.error("Kubernetes manifests for dash not found")
        return False
    
    # Apply Kubernetes manifests
    for manifest_file in manifests_dir.glob('*.yaml'):
        if not self._apply_kubernetes_manifest(manifest_file):
            return False
    
    return self._wait_for_deployment('dash-app')
```

#### Build Process Integration
```python
def _build_dash_apps(self) -> bool:
    """Build Dash applications."""
    logger.info("Building Dash applications...")
    
    # Run tests
    if not self._run_python_tests('dash'):
        return False
    
    # Build Docker images
    return self._build_docker_images('dash')
```

## Environment-Specific Configurations

### Development Environment
```yaml
Environment: dev
Namespace: genai-dev
Replicas: 1
Resource Profile: Minimal
CPU Requests: 100m
Memory Requests: 256Mi
CPU Limits: 500m
Memory Limits: 512Mi
Debug Mode: Enabled
Database: riskdb-dev
Logging: DEBUG level
Data Refresh: Real-time
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
Debug Mode: Limited
Database: riskdb-uat
Logging: INFO level
Data Refresh: 5-minute intervals
```

### Production Environment
```yaml
Environment: prod
Namespace: genai-prod
Replicas: 2-3 (auto-scaling)
Resource Profile: Production
CPU Requests: 500m
Memory Requests: 1Gi
CPU Limits: 2 CPU
Memory Limits: 2Gi
Debug Mode: Disabled
Database: riskdb-prod
Logging: WARNING/ERROR only
Data Refresh: 1-minute intervals
Caching: Enabled
```

## Dashboard Features and Capabilities

### 1. Interactive Visualizations

#### Risk Metrics Dashboard
- **VaR Analysis:** 95% Value at Risk visualization
- **Volatility Tracking:** Historical volatility patterns
- **Sharpe Ratio:** Risk-adjusted performance metrics
- **Portfolio Comparison:** Multi-portfolio analysis

#### User Interface Components
```python
# Dashboard Layout Structure
app.layout = html.Div([
    # Header section
    html.Div([
        html.H1("Risk Management Dashboard"),
        html.P("Real-time portfolio risk monitoring and analysis")
    ], className="header"),
    
    # Control panels
    html.Div([
        # Portfolio selection dropdown
        # Date range picker
    ], className="controls-row"),
    
    # Visualization panels
    html.Div([
        # VaR chart container
        # Volatility chart container
    ], className="charts-row"),
    
    # Summary section  
    html.Div([
        # Risk summary table
        # Portfolio comparison chart
    ])
])
```

### 2. Data Processing Pipeline

#### Sample Data Generation
```python
def generate_sample_data():
    """Generate sample data for dashboard."""
    dates = pd.date_range(start='2025-01-01', end='2025-09-01', freq='D')
    portfolios = ['EQUITY_GROWTH', 'FIXED_INCOME', 'BALANCED', 'EMERGING_MARKETS']
    
    risk_data = []
    for portfolio in portfolios:
        for date in dates:
            risk_data.append({
                'date': date,
                'portfolio': portfolio,
                'var_95': -0.02 - (hash(f"{portfolio}{date}") % 100) / 10000,
                'volatility': 0.10 + (hash(f"{portfolio}{date}") % 50) / 1000,
                'sharpe_ratio': 0.5 + (hash(f"{portfolio}{date}") % 100) / 200
            })
    
    return pd.DataFrame(risk_data)
```

#### Real-time Data Integration
- **Business Logic Integration:** RiskCalculator and ReportGenerator
- **Database Connectivity:** PostgreSQL and Snowflake integration
- **Data Caching:** Pandas DataFrame caching for performance

### 3. Styling and User Experience

#### CSS Styling Framework
```python
# Custom CSS styling embedded in application
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        <style>
            .dashboard-container {
                font-family: Arial, sans-serif;
                margin: 20px;
            }
            .header {
                background-color: #2c3e50;
                color: white;
                padding: 20px;
                border-radius: 5px;
            }
            .charts-row {
                display: flex;
                gap: 20px;
                margin-bottom: 20px;
            }
            .chart-container {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 15px;
                flex: 1;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
    </body>
</html>
'''
```

#### Responsive Design Features
- **Flexible Layout:** CSS Flexbox-based responsive design
- **Chart Responsiveness:** Plotly automatic responsiveness
- **Corporate Styling:** Professional color scheme and typography

## Network Architecture

### 1. Corporate Network Access
- **Access Model:** Corporate intranet only
- **Path Access:** `/dash/*` URL pattern routing
- **Load Balancer:** Internal ALB with path-based routing
- **SSL/TLS:** HTTPS with corporate certificates

### 2. Service Communication
```
User Browser → Corporate Network → ALB → Dash Service (Port 8050)
                                   │
Dash Application → Database Connections:
                  ├── PostgreSQL (Risk data)
                  └── Snowflake (Analytics data)
```

### 3. Internal Service Integration
- **API Connectivity:** Potential integration with FastAPI services
- **Data Sharing:** Shared database access with other services
- **Authentication:** Corporate network-based access control

## Performance Optimization

### 1. Application-Level Optimizations

#### Data Caching Strategy
```python
# DataFrame caching for repeated queries
@lru_cache(maxsize=128)
def get_portfolio_data(portfolio, start_date, end_date):
    """Cached portfolio data retrieval."""
    return filtered_data
```

#### Callback Optimization
```python
# Efficient callback structure
@callback(
    [Output('var-chart', 'figure'),
     Output('volatility-chart', 'figure')],
    [Input('portfolio-dropdown', 'value'),
     Input('date-picker-range', 'start_date')]
)
def update_multiple_charts(portfolio, start_date):
    """Update multiple charts in single callback."""
    # Reduce database calls by combining updates
```

### 2. Infrastructure Optimizations

#### Resource Allocation
- **Memory Optimization:** Efficient pandas DataFrame handling
- **CPU Scaling:** Multi-threaded Dash server configuration
- **Container Optimization:** Minimal Python base images

#### Database Performance
- **Connection Pooling:** SQLAlchemy connection management
- **Query Optimization:** Efficient data filtering and aggregation
- **Caching Layer:** In-memory data caching for frequently accessed data

### 3. Visualization Performance

#### Plotly Optimizations
```python
# Efficient chart configuration
fig.update_layout(
    template="plotly_white",  # Lightweight template
    showlegend=True,
    hovermode='x unified',    # Optimized hover interactions
    dragmode='pan'            # Efficient interaction mode
)
```

#### Data Sampling
- **Large Dataset Handling:** Automatic data sampling for large time series
- **Progressive Loading:** Incremental data loading for better responsiveness
- **Chart Simplification:** Reduced marker density for performance

## Security Considerations

### 1. Application Security
- **Input Validation:** Dash callback input sanitization
- **SQL Injection Prevention:** Parameterized database queries
- **XSS Protection:** Dash built-in HTML escaping
- **Session Management:** Server-side session handling

### 2. Network Security
- **Corporate Access Only:** No public internet exposure
- **Path-based Routing:** Controlled URL access patterns
- **TLS Encryption:** HTTPS-only communication
- **Internal Load Balancer:** Corporate network restrictions

### 3. Data Security
- **Database Security:** Encrypted connections to PostgreSQL/Snowflake
- **Secrets Management:** Kubernetes secrets for database credentials
- **Access Logging:** User interaction tracking
- **Data Privacy:** No sensitive data caching in browser

## Monitoring and Observability

### 1. Application Monitoring
- **Health Checks:** HTTP health endpoint monitoring
- **Performance Metrics:** Response time and throughput tracking
- **Error Tracking:** Application error logging and alerting
- **User Analytics:** Dashboard usage statistics

### 2. Infrastructure Monitoring
- **Resource Usage:** CPU, memory, and network monitoring
- **Pod Health:** Kubernetes pod status and restart tracking
- **Database Connectivity:** Connection pool and query performance
- **Load Balancer Metrics:** Traffic distribution and health checks

### 3. Business Metrics
- **Dashboard Usage:** User engagement and feature utilization
- **Data Freshness:** Real-time data update monitoring
- **Report Generation:** Analytics report generation metrics
- **Performance Benchmarks:** Chart rendering and interaction times

## Operational Procedures

### 1. Deployment Operations
```bash
# Standard deployment
./deploy.py --target dash --environment prod

# Rolling update
kubectl rollout restart deployment/dash-app -n genai-prod

# Rollback procedure
kubectl rollout undo deployment/dash-app -n genai-prod

# Health verification
kubectl get pods -n genai-prod -l app=dash
```

### 2. Monitoring and Troubleshooting
```bash
# View application logs
kubectl logs -f deployment/dash-app -n genai-prod

# Port forwarding for debugging
kubectl port-forward svc/dash-service 8050:80 -n genai-prod

# Resource monitoring
kubectl top pods -n genai-prod -l app=dash

# Database connectivity test  
kubectl exec -it deployment/dash-app -n genai-prod -- python -c "import pandas as pd; print('DB OK')"
```

### 3. Configuration Management
```bash
# Update environment variables
kubectl patch deployment dash-app -p '{"spec":{"template":{"spec":{"containers":[{"name":"dash","env":[{"name":"LOG_LEVEL","value":"DEBUG"}]}]}}}}'

# ConfigMap updates
kubectl create configmap dash-config --from-env-file=dash.env --dry-run=client -o yaml | kubectl apply -f -

# Database connection updates
kubectl patch secret database-secrets --type='json' -p='[{"op": "replace", "path": "/data/riskdb_url", "value":"'$(echo -n "new_connection_string" | base64)'"}]'
```

## Cost Optimization

### 1. Resource Efficiency
- **Right-sizing:** Environment-appropriate resource allocation
- **Auto-scaling:** Scale down during off-hours
- **Shared Infrastructure:** Common load balancer and database usage
- **Efficient Images:** Optimized Python container images

### 2. Data Processing Efficiency
- **Query Optimization:** Efficient database queries
- **Caching Strategy:** Reduced database calls through caching
- **Data Sampling:** Smart data sampling for large datasets
- **Connection Pooling:** Optimized database connection usage

## Future Enhancements

### 1. Planned Improvements
- **Real-time Streaming:** WebSocket integration for live data updates
- **Advanced Analytics:** Machine learning integration for predictive analytics
- **Custom Themes:** Corporate branding and theme customization
- **Export Capabilities:** PDF and Excel report generation

### 2. Performance Enhancements
- **Redis Caching:** Distributed caching layer for improved performance
- **CDN Integration:** Static asset delivery optimization
- **Database Optimization:** Read replicas and query optimization
- **Microservices Architecture:** Service decomposition for scalability

### 3. Feature Expansions
- **User Authentication:** Role-based access control
- **Personalization:** User-specific dashboard configurations
- **Alert System:** Real-time risk threshold alerts
- **Mobile Optimization:** Responsive design for mobile devices

### 4. Integration Improvements
- **API Integration:** RESTful API for external data consumption
- **Webhook Support:** Event-driven data updates
- **Third-party Connectors:** Additional data source integrations
- **Slack/Teams Integration:** Notification and collaboration features

---

**Document Maintained By:** Analytics Engineering Team  
**Last Updated:** September 21, 2025  
**Next Review:** December 21, 2025

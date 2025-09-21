# Web Application Infrastructure Analysis

**Document Created:** September 21, 2025  
**Application Type:** React-based Web Applications  
**Infrastructure:** Self-managed on Kubernetes (EKS)

## Executive Summary

The Web Application infrastructure consists of **multiple React-based frontend applications** deployed on Amazon EKS. The setup includes a main dashboard application and an administrative panel, both built with modern React technologies and deployed as containerized applications with corporate intranet access through load balancers.

## Architecture Overview

### Technology Stack
- **Frontend Framework:** React 18.2.0 with TypeScript
- **Build Tool:** Vite 4.4.5
- **UI Library:** Tailwind CSS + Headless UI
- **State Management:** React Query + React Hook Form
- **Container Runtime:** Kubernetes (EKS)
- **Service Port:** 3000 (internal), 80 (service)

### Application Portfolio
1. **GenAI Dashboard** (`genai-dashboard`)
2. **GenAI Admin Panel** (`genai-admin`)
3. **Documentation Site** (`genai-docs`)

## Application Components

### 1. GenAI Dashboard (`web/dashboard/`)

#### Purpose and Features
- **Primary Interface:** Main user interface for risk management and analytics
- **Target Users:** Business users, analysts, risk managers
- **Core Features:**
  - Risk metrics visualization
  - Portfolio analytics dashboards
  - Real-time data monitoring
  - Interactive charts and reports

#### Technology Stack
```json
{
  "name": "genai-dashboard",
  "version": "1.0.0",
  "description": "Main user interface for risk management and analytics"
}
```

#### Key Dependencies
```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "react-router-dom": "^6.15.0",
  "react-query": "^3.39.3",
  "axios": "^1.5.0",
  "@tanstack/react-table": "^8.9.3",
  "recharts": "^2.8.0",
  "@headlessui/react": "^1.7.17",
  "@heroicons/react": "^2.0.18",
  "tailwind-merge": "^1.14.0",
  "react-hook-form": "^7.45.4",
  "zod": "^3.22.2"
}
```

#### Build Configuration
```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "vitest",
    "test:coverage": "vitest --coverage",
    "lint": "eslint . --ext ts,tsx"
  }
}
```

### 2. GenAI Admin Panel (`web/admin/`)

#### Purpose and Features
- **Administrative Interface:** System management and configuration
- **Target Users:** System administrators, DevOps engineers
- **Core Features:**
  - System configuration management
  - User access control
  - Monitoring dashboards
  - Code editor integration
  - JSON data visualization

#### Enhanced Dependencies
```json
{
  "additional_admin_features": {
    "@monaco-editor/react": "^4.5.1",
    "react-json-view": "^1.21.3"
  }
}
```

#### Administrative Capabilities
- **Monaco Editor:** In-browser code editing
- **JSON Viewer:** Structured data inspection
- **System Monitoring:** Application health and metrics
- **Configuration Management:** Runtime setting adjustments

### 3. Documentation Site (`web/docs/`)

#### Purpose and Features
- **Documentation Portal:** Technical documentation and guides
- **Technology:** Vue.js 3.3.4 based
- **Build System:** Vite-powered static site generation

## Kubernetes Deployment Architecture

### 1. Deployment Configuration

#### Web Application Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
  namespace: {{ .Values.namespace }}
  labels:
    app: web
    environment: {{ .Values.environment }}
spec:
  replicas: {{ .Values.replicas.web }}
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
        environment: {{ .Values.environment }}
    spec:
      imagePullSecrets:
      - name: ecr-registry-secret
      containers:
      - name: web
        image: "{{ .Values.registry.url }}/mono-repo/web:{{ .Values.image_tag }}"
        ports:
        - containerPort: 3000
```

#### Environment Configuration
```yaml
env:
- name: ENV
  value: "{{ .Values.environment }}"
- name: REACT_APP_API_URL
  value: "{{ .Values.web.api_base_url }}"
```

#### Resource Management
```yaml
resources:
  requests:
    cpu: {{ .Values.resources.web.cpu }}
    memory: {{ .Values.resources.web.memory }}
  limits:
    cpu: {{ .Values.resources.web.limits.cpu }}
    memory: {{ .Values.resources.web.limits.memory }}
```

#### Health Monitoring
```yaml
livenessProbe:
  httpGet:
    path: /
    port: 3000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /
    port: 3000
  initialDelaySeconds: 5
  periodSeconds: 5
```

### 2. Service Configuration

#### Kubernetes Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-service
  namespace: {{ .Values.namespace }}
  labels:
    app: web
    environment: {{ .Values.environment }}
spec:
  selector:
    app: web
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3000
  type: ClusterIP
```

### 3. Ingress Configuration

#### Application Load Balancer Ingress
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web-ingress
  namespace: {{ .Values.namespace }}
  annotations:
    kubernetes.io/ingress.class: "alb"
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
spec:
  rules:
  - host: {{ .Values.web.domain }}
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 80
```

## Infrastructure Components

### 1. Container Registry
- **Registry:** Amazon ECR (Elastic Container Registry)
- **Repository Names:**
  - Dev: `mono-repo-test-web-app`
  - UAT: `mono-repo-uat-web-app`
  - Prod: `mono-repo-prod-web-app`
- **Image Strategy:** Multi-stage Docker builds for optimized production images

### 2. Load Balancing Architecture

#### Internal Application Load Balancer Integration
```terraform
# Web Applications Target Group
resource "aws_lb_target_group" "webapp" {
  name     = "${var.project_name}-${var.environment}-webapp"
  port     = 3000
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
                    ├── /* → Web Application (Port 3000) [DEFAULT]
                    ├── /api/* → FastAPI Service (Port 8000)
                    ├── /airflow/* → Airflow Service (Port 8080)
                    └── /dash/* → Dash Service (Port 8050)
```

### 3. SSL/TLS Configuration
```terraform
# HTTPS Listener (if SSL enabled)
resource "aws_lb_listener" "intranet_https" {
  count             = var.enable_ssl ? 1 : 0
  load_balancer_arn = aws_lb.intranet_alb.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn   = var.ssl_certificate_arn
  
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.webapp.arn
  }
}
```

## Build and Deployment Process

### 1. Build Pipeline

#### Development Build
```bash
# Install dependencies
npm install

# Development server
npm run dev

# Type checking
npm run type-check

# Linting
npm run lint
```

#### Production Build
```bash
# TypeScript compilation + Vite build
npm run build

# Preview production build
npm run preview

# Run tests with coverage
npm run test:coverage
```

#### Vite Configuration Optimizations
```typescript
// vite.config.ts
export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          router: ['react-router-dom'],
          query: ['react-query'],
          ui: ['@headlessui/react', '@heroicons/react']
        }
      }
    }
  }
})
```

### 2. Docker Build Process

#### Multi-stage Dockerfile Strategy
```dockerfile
# Build stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
```

### 3. CI/CD Integration

#### Deployment Script Integration
```python
# deploy.py integration
def _deploy_web_applications(self) -> bool:
    """Deploy web applications."""
    logger.info("Deploying web applications...")
    
    # Build production assets first
    if not self._build_web_assets():
        return False
    
    manifests_dir = self.deploy_dir / 'kubernetes' / 'web'
    if not manifests_dir.exists():
        logger.error("Kubernetes manifests for web not found")
        return False
    
    # Apply Kubernetes manifests
    for manifest_file in manifests_dir.glob('*.yaml'):
        if not self._apply_kubernetes_manifest(manifest_file):
            return False
    
    return self._wait_for_deployment('web-app')
```

#### Build Asset Generation
```python
def _build_web_assets(self) -> bool:
    """Build web application assets."""
    web_dir = self.project_root / 'web'
    if not web_dir.exists():
        return True
    
    # Install dependencies and build
    commands = [
        ['npm', 'install'],
        ['npm', 'run', 'build']
    ]
    
    for cmd in commands:
        if not self._run_command(cmd, cwd=web_dir):
            return False
    
    return True
```

## Environment-Specific Configurations

### Development Environment
```yaml
Environment: dev
Namespace: genai-dev
Replicas: 1
Resource Profile: Minimal
CPU Requests: 100m
Memory Requests: 128Mi
CPU Limits: 250m
Memory Limits: 256Mi
Build Mode: Development with HMR
API Endpoints: Local/dev API services
Logging: Detailed development logs
```

### UAT Environment
```yaml
Environment: uat
Namespace: genai-uat
Replicas: 1-2
Resource Profile: Testing
CPU Requests: 200m
Memory Requests: 256Mi
CPU Limits: 500m
Memory Limits: 512Mi
Build Mode: Production build with source maps
API Endpoints: UAT API services
Logging: Info level logging
```

### Production Environment
```yaml
Environment: prod
Namespace: genai-prod
Replicas: 2-3 (auto-scaling)
Resource Profile: Production
CPU Requests: 250m
Memory Requests: 512Mi
CPU Limits: 500m
Memory Limits: 1Gi
Build Mode: Optimized production build
API Endpoints: Production API services
Logging: Warning/Error level only
Caching: Aggressive browser caching
```

## IAM and Security Model

### 1. Frontend Developer Access

#### Developer Group: `frontend-developers`
```terraform
resource "aws_iam_group" "frontend_developers" {
  name = "${local.name_prefix}-frontend-developers"
  path = "/developers/frontend/"
}

resource "aws_iam_group_membership" "frontend_developers" {
  name = "${local.name_prefix}-frontend-developers-membership"
  users = [
    for user in var.developers :
    aws_iam_user.developers[user.username].name
    if contains(["frontend", "ui", "ux"], user.team)
  ]
  group = aws_iam_group.frontend_developers.name
}
```

#### Frontend Developer Permissions
- **S3 Access:** Static asset deployment buckets
- **ECR Access:** Container image push/pull
- **EKS Access:** Limited kubectl access for debugging
- **CloudWatch:** Log access for troubleshooting

### 2. Application Security

#### Runtime Security
- **Container Security:** Non-root user execution
- **Resource Limits:** CPU and memory constraints
- **Network Policies:** Restricted ingress/egress
- **Image Scanning:** ECR vulnerability scanning

#### API Integration Security
- **CORS Configuration:** Restricted to corporate domains
- **API Authentication:** JWT token-based (when implemented)
- **Environment Variables:** Secure configuration injection
- **Secrets Management:** No sensitive data in client-side code

## Network Architecture

### 1. Corporate Network Access
- **Access Model:** Corporate intranet only
- **CIDR Restrictions:** Limited to corporate network ranges
- **Load Balancer:** Internal ALB with path-based routing
- **SSL/TLS:** HTTPS with corporate certificates

### 2. Service Communication
```
User Browser → Corporate Network → ALB → Web Service (Port 3000)
                                   │
Web Application → Kubernetes Service → FastAPI (Port 8000)
                                    → Airflow (Port 8080)
                                    → Dash (Port 8050)
```

### 3. CDN and Static Assets
- **Static Assets:** Served directly from container
- **Optimization:** Vite build optimizations
- **Caching:** Browser caching headers
- **Compression:** Gzip/Brotli compression

## Performance Optimization

### 1. Build-Time Optimizations

#### Code Splitting Strategy
```typescript
// Automatic code splitting
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
const Reports = React.lazy(() => import('./pages/Reports'));
const Settings = React.lazy(() => import('./pages/Settings'));

// Manual chunk splitting in vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          router: ['react-router-dom'],
          query: ['react-query'],
          ui: ['@headlessui/react', '@heroicons/react'],
          charts: ['recharts'],
          utils: ['date-fns', 'clsx', 'tailwind-merge']
        }
      }
    }
  }
})
```

#### Bundle Analysis
- **Bundle Size:** Optimized chunk sizes
- **Tree Shaking:** Dead code elimination
- **Asset Optimization:** Image and font optimization
- **Minification:** JavaScript and CSS minification

### 2. Runtime Optimizations

#### React Performance
```typescript
// React Query for efficient data fetching
const { data, isLoading, error } = useQuery(
  ['portfolio', portfolioId],
  () => fetchPortfolioData(portfolioId),
  {
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  }
);

// React Hook Form for efficient form handling
const { register, handleSubmit, formState: { errors } } = useForm({
  resolver: zodResolver(portfolioSchema)
});
```

#### Caching Strategy
- **API Response Caching:** React Query cache management
- **Static Asset Caching:** Browser cache headers
- **Service Worker:** Progressive Web App capabilities (future)

### 3. Monitoring and Analytics

#### Performance Monitoring
```typescript
// Performance monitoring setup
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

getCLS(console.log);
getFID(console.log);
getFCP(console.log);
getLCP(console.log);
getTTFB(console.log);
```

#### Error Tracking
- **Error Boundaries:** React error boundary implementation
- **Logging:** Structured client-side logging
- **Analytics:** User interaction tracking
- **Performance Metrics:** Core Web Vitals monitoring

## Testing Strategy

### 1. Unit Testing
```json
{
  "testing_framework": "vitest",
  "testing_library": "@testing-library/react",
  "coverage_target": "80%",
  "test_environment": "jsdom"
}
```

### 2. Integration Testing
```typescript
// Example integration test
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from 'react-query';
import Dashboard from '../Dashboard';

test('displays portfolio data after loading', async () => {
  const queryClient = new QueryClient();
  render(
    <QueryClientProvider client={queryClient}>
      <Dashboard />
    </QueryClientProvider>
  );
  
  await waitFor(() => {
    expect(screen.getByText('Portfolio Overview')).toBeInTheDocument();
  });
});
```

### 3. End-to-End Testing
- **Framework:** Playwright/Cypress (planned)
- **Test Scenarios:** Critical user journeys
- **Environment:** Dedicated testing environment
- **Automation:** CI/CD integration

## Operational Procedures

### 1. Deployment Operations
```bash
# Standard deployment
./deploy.py --target web --environment prod

# Rolling update
kubectl rollout restart deployment/web-app -n genai-prod

# Rollback procedure
kubectl rollout undo deployment/web-app -n genai-prod

# Health check
kubectl get pods -n genai-prod -l app=web
```

### 2. Monitoring and Troubleshooting
```bash
# View application logs
kubectl logs -f deployment/web-app -n genai-prod

# Port forwarding for debugging
kubectl port-forward svc/web-service 3000:80 -n genai-prod

# Resource usage monitoring
kubectl top pods -n genai-prod -l app=web

# Ingress status
kubectl describe ingress web-ingress -n genai-prod
```

### 3. Configuration Management
```bash
# Update environment variables
kubectl patch deployment web-app -p '{"spec":{"template":{"spec":{"containers":[{"name":"web","env":[{"name":"REACT_APP_API_URL","value":"https://new-api.company.com"}]}]}}}}'

# ConfigMap updates
kubectl create configmap web-config --from-env-file=.env.prod --dry-run=client -o yaml | kubectl apply -f -

# Secret updates
kubectl create secret generic web-secrets --from-env-file=.env.secrets --dry-run=client -o yaml | kubectl apply -f -
```

## Security Considerations

### 1. Application Security
- **Content Security Policy:** Strict CSP headers
- **XSS Protection:** Input sanitization and validation
- **CSRF Protection:** Token-based CSRF protection
- **Dependency Security:** Regular dependency updates and vulnerability scanning

### 2. Infrastructure Security
- **Container Security:** Minimal base images, non-root execution
- **Network Security:** Corporate network restrictions
- **Secrets Management:** No secrets in client-side code
- **Access Control:** IAM-based access management

## Cost Optimization

### 1. Resource Efficiency
- **Right-sizing:** Environment-appropriate resource allocation
- **Efficient Builds:** Multi-stage Docker builds
- **Shared Infrastructure:** Common load balancer usage
- **Auto-scaling:** Scale down during low usage

### 2. Build Optimization
- **Dependency Management:** Optimal package selection
- **Asset Optimization:** Image and bundle size optimization
- **Caching:** Efficient Docker layer caching
- **CDN Usage:** Future CloudFront integration

## Future Enhancements

### 1. Planned Improvements
- **Progressive Web App:** Service worker implementation
- **Advanced Caching:** Redis-backed caching layer
- **Micro-frontends:** Module federation architecture
- **Real-time Features:** WebSocket integration

### 2. Security Enhancements
- **OAuth Integration:** Corporate SSO integration
- **Advanced CSP:** Stricter content security policies
- **WAF Integration:** Web Application Firewall
- **Security Headers:** Comprehensive security header implementation

### 3. Performance Improvements
- **CDN Integration:** CloudFront distribution
- **Advanced Monitoring:** Real User Monitoring (RUM)
- **A/B Testing:** Feature flag implementation
- **Advanced Analytics:** User behavior analytics

---

**Document Maintained By:** Frontend Engineering Team  
**Last Updated:** September 21, 2025  
**Next Review:** December 21, 2025

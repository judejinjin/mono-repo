# Ingress Controller Architecture Overview

## 🔄 Updated Architecture with Ingress Controller

The updated architecture diagram now clearly shows how the **Ingress Controller** serves as the central traffic routing component within the EKS cluster, managing different access patterns for various services.

## 🏗️ Architecture Components & Relationships

### **Two Traffic Patterns in Our Architecture:**

#### 1. **Web Application Traffic (via Ingress Controller)**
```
Internet → Application Load Balancer → Ingress Controller → Services
```

#### 2. **API-Only Traffic (Direct Access)**
```
Internet → API Gateway → VPC Link → Network Load Balancer → Airflow Service
```

## 📊 Component Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                INTERNET                                     │
└─────────────────────┬─────────────────────┬─────────────────────────────────┘
                      │                     │
               ┌──────▼──────┐       ┌──────▼──────┐
               │ Web Traffic │       │ API Traffic │
               │             │       │             │
        ┌──────▼──────┐      │       │      ┌──────▼──────┐
        │Application  │      │       │      │ API Gateway │
        │Load Balancer│      │       │      │ (Airflow)   │
        └──────┬──────┘      │       │      └──────┬──────┘
               │             │       │             │
               │             │       │      ┌──────▼──────┐
               │             │       │      │  VPC Link   │
               │             │       │      └──────┬──────┘
               │             │       │             │
               │             │       │      ┌──────▼──────┐
               │             │       │      │ Network LB  │
               │             │       │      │ (Airflow)   │
               │             │       │      └──────┬──────┘
               │             │       │             │
┌──────────────▼─────────────────────────────────────────────────────────────┐│
│                        VPC (Private Network)                              ││
│ ┌────────────────────────────────────────────────────────────────────────┐ ││
│ │                         EKS CLUSTER                                   │ ││
│ │                                                                        │ ││
│ │  ┌──────▼──────┐                                  ┌──────▼──────┐      │ ││
│ │  │   Ingress   │─────────┬─────────┬─────────────▶│   Airflow   │      │ ││
│ │  │ Controller  │         │         │              │   Service   │      │ ││
│ │  │   (NGINX)   │         │         │              └─────────────┘      │ ││
│ │  └─────────────┘         │         │                                   │ ││
│ │                          │         │                                   │ ││
│ │  ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐                    │ ││
│ │  │   FastAPI   │  │  WebApps    │  │    Dash     │                    │ ││
│ │  │   Service   │  │  Service    │  │  Analytics  │                    │ ││
│ │  └─────────────┘  └─────────────┘  └─────────────┘                    │ ││
│ │                                                                        │ ││
│ │  ┌─────────────┐  ┌─────────────┐                                     │ ││
│ │  │   Bamboo    │  │ Dev Server  │ (dev env only)                     │ ││
│ │  │   CI/CD     │  │   (EC2)     │                                     │ ││
│ │  └─────────────┘  └─────────────┘                                     │ ││
│ └────────────────────────────────────────────────────────────────────────┘ ││
└──────────────────────────────────────────────────────────────────────────────┘│
                                │                                               │
┌───────────────────────────────▼───────────────────────────────────────────────┘
│                        EXTERNAL STORAGE                                       
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                           
│  │     RDS     │  │     S3      │  │ElastiCache  │                           
│  │ PostgreSQL  │  │   Bucket    │  │   (Redis)   │                           
│  └─────────────┘  └─────────────┘  └─────────────┘                           
└────────────────────────────────────────────────────────────────────────────────
```

## 🎯 Ingress Controller's Role

### **Central Traffic Router**
The Ingress Controller acts as the **single entry point** for web-based services within the EKS cluster:

1. **FastAPI Services** (`/api/*` routes)
   - RESTful API endpoints
   - Microservices architecture
   - Authentication and rate limiting

2. **Web Applications** (`/web/*` routes)
   - React/Vue.js frontend applications
   - Static content serving
   - Single Page Applications (SPAs)

3. **Dash Analytics** (`/dash/*` routes)
   - Interactive data visualization
   - Python-based dashboards
   - Real-time analytics interfaces

### **Smart Routing Rules**
```yaml
# Example Ingress Configuration
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: main-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: mycompany.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: fastapi-service
            port:
              number: 8000
      - path: /web
        pathType: Prefix
        backend:
          service:
            name: webapp-service
            port:
              number: 3000
      - path: /dash
        pathType: Prefix
        backend:
          service:
            name: dash-service
            port:
              number: 8050
```

## 🔐 Why Two Different Access Patterns?

### **Ingress Controller (Web Traffic)**
- **Best for**: Interactive applications, web interfaces, user-facing services
- **Features**: SSL termination, host-based routing, web-friendly protocols
- **Security**: WAF integration, DDoS protection, certificate management
- **Cost**: Single ALB serves multiple services

### **API Gateway + VPC Link (API Traffic)**
- **Best for**: External API integrations, machine-to-machine communication
- **Features**: API keys, usage plans, rate limiting, request/response transformation
- **Security**: Fine-grained access control, usage monitoring, audit trails
- **Cost**: Pay-per-request model, ideal for API workloads

## 🚀 Benefits of This Architecture

### **1. Separation of Concerns**
- Web traffic handled by Kubernetes-native Ingress
- API traffic handled by cloud-managed API Gateway
- Each optimized for its specific use case

### **2. Cost Optimization**
- Single ALB for all web services (instead of multiple load balancers)
- API Gateway only pays for actual API usage
- Efficient resource utilization

### **3. Security**
- Network isolation between web and API traffic
- Different authentication mechanisms for different use cases
- Granular access control policies

### **4. Scalability**
- Ingress Controller scales with Kubernetes cluster
- API Gateway scales automatically with demand
- Independent scaling for different traffic types

### **5. Operational Excellence**
- Kubernetes-native tooling for web services
- AWS-native tooling for API management
- Clear separation of responsibilities

## 🛠️ Implementation Details

### **Ingress Controller Setup**
```bash
# Install NGINX Ingress Controller
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --set controller.service.type=LoadBalancer \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/aws-load-balancer-type"="nlb"
```

### **Service Configuration**
```yaml
# FastAPI Service
apiVersion: v1
kind: Service
metadata:
  name: fastapi-service
spec:
  selector:
    app: fastapi
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP  # Internal service, accessed via Ingress
```

## 📈 Traffic Flow Examples

### **Web Application Access**
1. User navigates to `https://mycompany.com/web/dashboard`
2. DNS resolves to Application Load Balancer
3. ALB forwards to Ingress Controller
4. Ingress Controller routes to WebApp service based on `/web` path
5. WebApp service serves the dashboard

### **API Call via Ingress**
1. Frontend makes AJAX call to `https://mycompany.com/api/users`
2. Request follows same path to Ingress Controller
3. Ingress Controller routes to FastAPI service based on `/api` path
4. FastAPI service returns JSON response

### **External Airflow API Trigger**
1. External system calls `https://api-gateway-url/trigger-dag`
2. API Gateway validates API key and rate limits
3. VPC Link forwards to Network Load Balancer
4. NLB routes directly to Airflow service (bypassing Ingress)
5. Airflow API processes the DAG trigger request

This architecture provides the best of both worlds: efficient internal routing for web services and secure external API access for machine-to-machine communication.

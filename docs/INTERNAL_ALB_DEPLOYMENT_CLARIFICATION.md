# Internal Application Load Balancer Deployment Clarification

## Current Architecture: Internal ALB in Management Subnets

### 🎯 **Deployment Location**
The Internal Application Load Balancer (ALB) is deployed in the **Management Subnets**, not the Private Subnets.

### 📍 **Architecture Flow**
```
Corporate Network
        ↓
   VPN/Direct Connect
        ↓
   Corporate Gateway
        ↓
   Internal ALB (Management Subnets)
        ↓
   Ingress Controller (Private Subnets/EKS)
        ↓
   Application Services (FastAPI, WebApps, Dash, Airflow)
```

### 🏗️ **Infrastructure Configuration**

#### Terraform Configuration:
```hcl
resource "aws_lb" "intranet_alb" {
  name               = "${var.project_name}-${var.environment}-intranet-alb"
  internal           = true
  load_balancer_type = "application"
  subnets            = aws_subnet.management[*].id  # ← Deployed in Management Subnets
  security_groups    = [aws_security_group.intranet_alb.id]
}
```

### 🔄 **Why Management Subnets?**

1. **Corporate Network Access**: Management subnets are designed to handle corporate network traffic
2. **Security Segmentation**: Separates external-facing load balancer from internal EKS workloads
3. **Network Architecture**: Follows AWS best practices for intranet-only architectures
4. **Routing Efficiency**: Direct path from corporate network to load balancer

### 🛡️ **Security Benefits**

#### Network Segmentation:
- **Management Layer**: Internal ALB handles corporate traffic routing
- **Application Layer**: EKS services remain in private subnets
- **Data Layer**: Databases in dedicated database subnets

#### Traffic Flow Control:
- Corporate network → Management Subnets (ALB)
- Management Subnets → Private Subnets (EKS)
- No direct corporate access to EKS workloads

### 📊 **Updated Diagram Elements**

#### Visual Changes Made:
1. **ALB Position**: Moved to clearly show placement in Management Subnets
2. **Connection Arrows**: Updated to show proper traffic flows
3. **Labels**: Clarified "Management Subnets" deployment
4. **Architecture Flow**: Shows corporate network → management → private progression

#### Connection Paths:
- **Corporate Gateway → Internal ALB**: Purple arrow (corporate traffic)
- **Internal ALB → Ingress Controller**: Blue arrow (intranet routing)
- **Internal ALB → Airflow**: Dashed blue arrow (direct API access)

### 🎯 **Operational Implications**

#### Access Patterns:
- Corporate users access services via ALB in Management Subnets
- ALB routes traffic to appropriate EKS services via Ingress Controller
- Direct Airflow API access through path-based routing

#### Monitoring:
- ALB metrics available in Management Subnet context
- Clear separation between corporate access layer and application layer
- Enhanced visibility into traffic patterns

### 🔧 **Configuration Consistency**

This deployment pattern ensures:
- ✅ Internal ALB deployed in Management Subnets
- ✅ EKS cluster and services in Private Subnets
- ✅ Corporate network routing through Management layer
- ✅ No internet access from any subnet
- ✅ Proper network segmentation and security

The architecture now correctly reflects a three-tier intranet design:
1. **Corporate Access Tier**: Management Subnets with Internal ALB
2. **Application Tier**: Private Subnets with EKS services
3. **Data Tier**: Database Subnets with persistent storage

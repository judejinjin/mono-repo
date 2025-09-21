# Corporate Intran### Service Access Patterns
- **Web Services**: FastAPI, Web Apps, Dash accessible via `/api`, `/web`, `/dash` paths
- **Airflow API**: Direct access via `/airflow` path for internal DAG triggering
- **CI/CD Integration**: Corporate Bamboo servers deploy via VPN (not deployed in EKS)
- **Security**: All traffic restricted to corporate network CIDR rangesrchitecture Implementation

## Overview
The architecture has been successfully converted from an internet-facing design to a corporate intranet-only configuration. This change ensures that all services are accessible only within the corporate network, providing enhanced security and compliance with internal IT policies.

## Key Architecture Changes

### 1. Network Infrastructure Changes
- **Removed**: Internet Gateway and NAT Gateways
- **Added**: VPN Gateway, Customer Gateway, and VPN Connection for corporate connectivity
- **Modified**: Public subnets renamed to Management subnets (no internet access)
- **Enhanced**: Private subnets remain for EKS workloads

### 2. Load Balancing Strategy
- **Removed**: API Gateway and Network Load Balancer
- **Replaced with**: Single Internal Application Load Balancer
- **Benefits**: Simplified architecture, path-based routing for all services, corporate network-only access

### 3. Service Access Patterns
- **Web Services**: FastAPI, Web Apps, Dash accessible via `/api`, `/web`, `/dash` paths
- **Airflow API**: Direct access via `/airflow` path for internal DAG triggering
- **Security**: All traffic restricted to corporate network CIDR ranges

## Infrastructure Components

### Corporate Connectivity
```
Corporate Network (Bamboo CI/CD) → VPN/Direct Connect → VPC → Internal ALB → EKS Services
```

### CI/CD Integration
```
Corporate Bamboo → VPN → ECR (Push Images) → EKS (Deploy) → Internal ALB (Verify)
```

### Load Balancer Configuration
- **Type**: Internal Application Load Balancer
- **Subnets**: Management subnets (no internet access)
- **Security Groups**: Restricted to corporate network CIDRs
- **Target Groups**: FastAPI, WebApps, Dash, Airflow

### VPN Configuration
- **VPN Gateway**: Attached to VPC for corporate connectivity
- **Customer Gateway**: Corporate network endpoint
- **VPN Connection**: Encrypted tunnel for secure access
- **Route Propagation**: Automatic routing to corporate networks

## Security Enhancements

### Network Security
- No internet access from any subnet
- Corporate network CIDR restrictions on all security groups
- Internal-only load balancer (no public IP)
- VPN-only connectivity

### Access Control
- All services accessible only from corporate network
- Airflow API secured within corporate perimeter
- No external API endpoints or public access

## Benefits of Corporate Intranet Architecture

1. **Enhanced Security**: No internet exposure, corporate network-only access
2. **Compliance**: Meets corporate IT security requirements
3. **Simplified Architecture**: Single load balancer, reduced complexity
4. **Cost Optimization**: Eliminated NAT Gateways and API Gateway costs
5. **Performance**: Direct corporate network connectivity

## Terraform Files Modified

### Core Infrastructure
- `vpc.tf`: Removed Internet Gateway, NAT Gateways, converted public to management subnets
- `variables.tf`: Added corporate network variables, removed API Gateway config
- `intranet_load_balancer.tf`: New internal ALB replacing API Gateway architecture

### Security Groups
- Updated to allow traffic only from corporate network CIDRs
- Removed internet-facing security group rules
- Added VPN gateway security configurations

## Deployment Considerations

### Prerequisites
1. Corporate VPN/Direct Connect configuration
2. Corporate network CIDR ranges defined
3. DNS resolution for internal services
4. Corporate firewall rules for VPN traffic

### Access Patterns
- Developers access services via corporate VPN
- CI/CD systems connect through corporate network
- Monitoring and management via internal network only

## Monitoring and Operations

### Health Checks
- Internal ALB health checks for all target groups
- VPN connection monitoring
- Corporate network connectivity verification

### Logging
- ALB access logs to S3
- VPN connection logs
- EKS service logs via CloudWatch

## Future Enhancements

1. **Direct Connect**: Consider AWS Direct Connect for dedicated corporate connectivity
2. **Private DNS**: Implement Route 53 private hosted zones for internal service discovery
3. **Certificate Management**: Use internal CA for SSL certificates
4. **Network Segmentation**: Additional subnets for enhanced security zones

This corporate intranet architecture provides a secure, compliant, and efficient platform for internal application deployment while maintaining all the benefits of cloud-native EKS services.

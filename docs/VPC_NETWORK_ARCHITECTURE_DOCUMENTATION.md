# VPC Network Architecture Diagrams Documentation

Generated: 2025-09-25 13:32:29

## Overview

This document accompanies the visual VPC network architecture diagrams created to illustrate the complete network topology, routing, and connectivity patterns for the mono-repo infrastructure.

## Generated Diagrams

### 1. VPC Network Topology (`vpc_network_topology`)
**Purpose**: Complete network architecture showing VPCs, subnets, and CIDR allocations

**Network Structure**:
- **Development VPC**: 10.0.0.0/16 (Free tier optimized)
- **UAT VPC**: 10.1.0.0/16 (Production-like configuration)
- **Production VPC**: 10.2.0.0/16 (High availability setup)

**Subnet Design**:
- **Management Subnets**: x.x.1-2.0/24 (Bastion/Admin access)
- **Private Subnets**: x.x.101-102.0/24 (Application workloads)
- **Database Subnets**: x.x.201-202.0/24 (RDS instances)

**Multi-AZ Deployment**: All subnets deployed across two availability zones for redundancy

### 2. Routing Tables & Traffic Flow (`routing_traffic_flow`)
**Purpose**: Network traffic routing and path analysis

**Route Table Configuration**:
- **Management Routes**: Corporate network access via VPN Gateway
- **Private Routes**: Local VPC traffic and controlled external access
- **Database Routes**: Isolated tier with no external routing

**Traffic Flow Patterns**:
- ✅ **Allowed**: Corporate → Management, Management → Private, Private → Database
- ❌ **Blocked**: Direct Internet access, Cross-environment traffic, Unauthorized ports

**Path Analysis**: Detailed network paths for common traffic flows

### 3. Corporate Intranet Connectivity (`corporate_intranet_connectivity`)
**Purpose**: VPN gateways and corporate network integration

**VPN Configuration**:
- **Site-to-Site VPN**: Dual tunnel redundancy
- **Encryption**: AES-256-GCM with Perfect Forward Secrecy
- **BGP Routing**: Dynamic route propagation
- **Failover**: Automatic tunnel switching <60 seconds

**Network Integration**:
- **Corporate ASN**: 65000
- **AWS ASN**: 64512
- **Advertised Routes**: Complete network visibility

### 4. Load Balancer & Service Discovery (`load_balancer_service_discovery`)
**Purpose**: Internal ALB routing and service discovery architecture

**ALB Configuration**:
- **Type**: Internal Application Load Balancer
- **Scheme**: Internal (intranet-only)
- **Path-based Routing**: Service-specific URL routing

**Target Groups**:
- **Web App**: Port 3000, health check /health
- **Risk API**: Port 8000, health check /api/health
- **Dash Analytics**: Port 8050, health check /
- **Airflow**: Port 8080, health check /health

## Network Implementation

### CIDR Block Allocation
```
Development:  10.0.0.0/16
├── Management:   10.0.1.0/24, 10.0.2.0/24
├── Private:      10.0.101.0/24, 10.0.102.0/24
└── Database:     10.0.201.0/24, 10.0.202.0/24

UAT:          10.1.0.0/16
├── Management:   10.1.1.0/24, 10.1.2.0/24
├── Private:      10.1.101.0/24, 10.1.102.0/24
└── Database:     10.1.201.0/24, 10.1.202.0/24

Production:   10.2.0.0/16
├── Management:   10.2.1.0/24, 10.2.2.0/24
├── Private:      10.2.101.0/24, 10.2.102.0/24
└── Database:     10.2.201.0/24, 10.2.202.0/24
```

### Security Implementation
- **Network ACLs**: Subnet-level security controls
- **Security Groups**: Instance-level firewall rules
- **VPC Flow Logs**: Complete traffic monitoring
- **No Internet Gateway**: Intranet-only architecture

### High Availability
- **Multi-AZ Deployment**: All subnets across 2+ AZs
- **Redundant VPN Tunnels**: Automatic failover
- **Load Balancer**: Multi-AZ ALB configuration
- **Database**: Multi-AZ RDS deployment

## Corporate Integration

### VPN Gateway Configuration
```
Customer Gateway: 192.168.1.1 (Corporate)
VPN Gateway: vgw-12345678 (AWS)
Connection: vpn-87654321

Tunnel 1: 203.0.113.1 (Primary)
Tunnel 2: 203.0.113.2 (Backup)
```

### BGP Routing
- **Dynamic Route Propagation**: Automatic network discovery
- **Health Monitoring**: 30-second BGP keepalives
- **Route Advertisement**: Selective network exposure

### DNS Resolution
- **Corporate DNS**: Forward zones for AWS resources
- **AWS Route53**: Private hosted zones for internal services
- **Service Discovery**: EKS with AWS Cloud Map integration

## Performance & Monitoring

### Network Performance
- **Intra-VPC Latency**: <10ms average
- **VPN Latency**: 20-50ms to corporate
- **Throughput**: 10Gbps VPC capacity
- **Cross-AZ**: 25Gbps available bandwidth

### Monitoring Stack
- **VPC Flow Logs**: CloudWatch Logs integration
- **CloudWatch Metrics**: Network performance monitoring
- **GuardDuty**: Network threat detection
- **Custom Dashboards**: Traffic pattern analysis

### Health Checks
- **ALB Health Checks**: 30-second intervals
- **Target Registration**: Automatic service discovery
- **Failure Detection**: 2-failure threshold
- **Recovery**: Automatic target restoration

## Security Controls

### Network Security
- **Defense in Depth**: Multiple security layers
- **Zero Trust**: Explicit verification required
- **Microsegmentation**: Granular network controls
- **Threat Detection**: Real-time monitoring

### Access Controls
- **Corporate Network Only**: No public internet access
- **VPN Required**: Authenticated corporate connection
- **Role-based Access**: Network access by job function
- **Audit Logging**: Complete access tracking

### Compliance
- **Data Residency**: Regional data containment
- **Encryption in Transit**: All network traffic encrypted
- **Network Isolation**: Environment separation
- **Regulatory Alignment**: SOC 2 compliance

## Usage Instructions

### Network Access Setup
1. Configure corporate VPN connection
2. Establish BGP routing
3. Test network connectivity
4. Validate security group rules
5. Monitor traffic patterns

### Service Discovery
1. Register services with target groups
2. Configure health checks
3. Set up DNS resolution
4. Test load balancer routing
5. Monitor service health

### Troubleshooting
1. Check VPN tunnel status
2. Verify route propagation
3. Review security group rules
4. Analyze VPC Flow Logs
5. Monitor CloudWatch metrics

## File Structure
```
docs/architecture/
├── vpc_network_topology.png              # Complete network architecture
├── vpc_network_topology.svg              # Vector format
├── routing_traffic_flow.png              # Routing and traffic analysis
├── routing_traffic_flow.svg              # Vector format
├── corporate_intranet_connectivity.png   # VPN and corporate integration
├── corporate_intranet_connectivity.svg   # Vector format
├── load_balancer_service_discovery.png   # ALB and service routing
└── load_balancer_service_discovery.svg   # Vector format
```

Created: September 25, 2025
Generated by: create_network_architecture_diagrams.py

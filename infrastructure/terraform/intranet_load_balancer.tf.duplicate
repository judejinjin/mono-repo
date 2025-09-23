# Airflow API Gateway Configuration
# Exposes Airflow REST API securely through AWS API Gateway with authentication

# Corporate Intranet Access - Internal ALB for all services
# Note: API Gateway removed as this is intranet-only architecture

# Internal Application Load Balancer for intranet access
resource "aws_lb" "intranet_alb" {
  name               = "${var.project_name}-${var.environment}-intranet-alb"
  internal           = true  # Internal only - no internet access
  load_balancer_type = "application"
  subnets            = aws_subnet.management[*].id  # Deployed in management subnets for corporate access
  security_groups    = [aws_security_group.intranet_alb.id]
  
  enable_deletion_protection = var.environment == "prod" ? true : false

  tags = {
    Name        = "${var.project_name}-${var.environment}-intranet-alb"
    Environment = var.environment
    Purpose     = "Corporate Intranet Access"
  }
}

# Security Group for Internal ALB (Corporate Network Access)
resource "aws_security_group" "intranet_alb" {
  name        = "${var.project_name}-${var.environment}-intranet-alb-sg"
  description = "Security group for internal ALB - Corporate intranet access only"
  vpc_id      = aws_vpc.main.id

  # Allow HTTP from corporate network ranges
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = var.corporate_network_cidrs
    description = "HTTP from corporate intranet"
  }

  # Allow HTTPS from corporate network ranges  
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = var.corporate_network_cidrs
    description = "HTTPS from corporate intranet"
  }

  # Outbound to EKS cluster
  egress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.main.cidr_block]
    description = "To EKS cluster services"
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-intranet-alb-sg"
  }
}

# Network Load Balancer for Airflow service in EKS
resource "aws_lb" "airflow_nlb" {
  name               = "${var.project_name}-${var.environment}-airflow-nlb"
  internal           = true
  load_balancer_type = "network"
  subnets            = aws_subnet.private[*].id
  
  enable_deletion_protection = var.environment == "prod" ? true : false

  tags = {
    Name = "${var.project_name}-${var.environment}-airflow-nlb"
  }
}

# NLB Target Group for Airflow webserver
resource "aws_lb_target_group" "airflow_webserver" {
  name     = "${var.project_name}-${var.environment}-airflow-web"
  port     = 8080
  protocol = "TCP"
  vpc_id   = aws_vpc.main.id
  
  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-airflow-web-tg"
  }
}

# NLB Listener for Airflow webserver
resource "aws_lb_listener" "airflow_webserver" {
  load_balancer_arn = aws_lb.airflow_nlb.arn
  port              = "8080"
  protocol          = "TCP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.airflow_webserver.arn
  }
}

# ALB Target Groups for different services

# Airflow Web UI and API Target Group
resource "aws_lb_target_group" "airflow_web" {
  name     = "${var.project_name}-${var.environment}-airflow-web"
  port     = 8080
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

  tags = {
    Name = "${var.project_name}-${var.environment}-airflow-web"
  }
}

# FastAPI Services Target Group
resource "aws_lb_target_group" "fastapi" {
  name     = "${var.project_name}-${var.environment}-fastapi"
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

  tags = {
    Name = "${var.project_name}-${var.environment}-fastapi"
  }
}

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

  tags = {
    Name = "${var.project_name}-${var.environment}-webapp"
  }
}

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

  tags = {
    Name = "${var.project_name}-${var.environment}-dash"
  }
}

# ALB HTTP Listener with path-based routing
resource "aws_lb_listener" "intranet_http" {
  load_balancer_arn = aws_lb.intranet_alb.arn
  port              = "80"
  protocol          = "HTTP"

  # Default action - route to web application
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.webapp.arn
  }
}

# ALB HTTPS Listener with path-based routing (if SSL certificate available)
resource "aws_lb_listener" "intranet_https" {
  count             = var.enable_ssl ? 1 : 0
  load_balancer_arn = aws_lb.intranet_alb.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn   = var.ssl_certificate_arn

  # Default action - route to web application
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.webapp.arn
  }
}

# Listener Rules for path-based routing

# Route /api/* to FastAPI services
resource "aws_lb_listener_rule" "api_routing" {
  listener_arn = aws_lb_listener.intranet_http.arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.fastapi.arn
  }

  condition {
    path_pattern {
      values = ["/api/*"]
    }
  }
}

# Route /airflow/* to Airflow Web UI and API
resource "aws_lb_listener_rule" "airflow_routing" {
  listener_arn = aws_lb_listener.intranet_http.arn
  priority     = 200

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.airflow_web.arn
  }

  condition {
    path_pattern {
      values = ["/airflow/*"]
    }
  }
}

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

# HTTPS versions of the same rules (if SSL enabled)
resource "aws_lb_listener_rule" "api_routing_https" {
  count        = var.enable_ssl ? 1 : 0
  listener_arn = aws_lb_listener.intranet_https[0].arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.fastapi.arn
  }

  condition {
    path_pattern {
      values = ["/api/*"]
    }
  }
}

resource "aws_lb_listener_rule" "airflow_routing_https" {
  count        = var.enable_ssl ? 1 : 0
  listener_arn = aws_lb_listener.intranet_https[0].arn
  priority     = 200

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.airflow_web.arn
  }

  condition {
    path_pattern {
      values = ["/airflow/*"]
    }
  }
}

resource "aws_lb_listener_rule" "dash_routing_https" {
  count        = var.enable_ssl ? 1 : 0
  listener_arn = aws_lb_listener.intranet_https[0].arn
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

# Corporate Network Connectivity Resources

# VPN Gateway for corporate connectivity (optional)
resource "aws_vpn_gateway" "corporate" {
  count  = var.enable_vpn_gateway ? 1 : 0
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.project_name}-${var.environment}-vpn-gateway"
  }
}

# Customer Gateway for corporate network
resource "aws_customer_gateway" "corporate" {
  count      = var.enable_vpn_gateway ? 1 : 0
  bgp_asn    = 65000
  ip_address = var.corporate_gateway_ip
  type       = "ipsec.1"

  tags = {
    Name = "${var.project_name}-${var.environment}-customer-gateway"
  }
}

# VPN Connection to corporate network
resource "aws_vpn_connection" "corporate" {
  count               = var.enable_vpn_gateway ? 1 : 0
  vpn_gateway_id      = aws_vpn_gateway.corporate[0].id
  customer_gateway_id = aws_customer_gateway.corporate[0].id
  type                = "ipsec.1"
  static_routes_only  = true

  tags = {
    Name = "${var.project_name}-${var.environment}-vpn-connection"
  }
}

# VPN Connection Route for corporate network
resource "aws_vpn_connection_route" "corporate" {
  count                  = var.enable_vpn_gateway ? length(var.corporate_network_cidrs) : 0
  vpn_connection_id      = aws_vpn_connection.corporate[0].id
  destination_cidr_block = var.corporate_network_cidrs[count.index]
}

# Route propagation to corporate network
resource "aws_vpn_gateway_route_propagation" "private" {
  count          = var.enable_vpn_gateway ? length(aws_route_table.private) : 0
  vpn_gateway_id = aws_vpn_gateway.corporate[0].id
  route_table_id = aws_route_table.private[count.index].id
}

# CloudWatch Log Group for ALB access logs
resource "aws_cloudwatch_log_group" "intranet_alb" {
  name              = "/aws/elasticloadbalancing/${var.project_name}-${var.environment}-intranet-alb"
  retention_in_days = var.environment == "prod" ? 90 : 30

  tags = {
    Name = "${var.project_name}-${var.environment}-intranet-alb-logs"
  }
}

# Route 53 Private Hosted Zone for internal DNS (optional)
resource "aws_route53_zone" "internal" {
  count = var.create_internal_dns ? 1 : 0
  name  = "${var.environment}.${var.internal_domain_name}"

  vpc {
    vpc_id = aws_vpc.main.id
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-internal-zone"
  }
}

# Internal DNS record for ALB
resource "aws_route53_record" "intranet_alb" {
  count   = var.create_internal_dns ? 1 : 0
  zone_id = aws_route53_zone.internal[0].zone_id
  name    = "services"
  type    = "A"

  alias {
    name                   = aws_lb.intranet_alb.dns_name
    zone_id                = aws_lb.intranet_alb.zone_id
    evaluate_target_health = true
  }
}

# Outputs for corporate intranet access
output "intranet_alb_dns_name" {
  description = "DNS name of the internal Application Load Balancer"
  value       = aws_lb.intranet_alb.dns_name
}

output "intranet_alb_zone_id" {
  description = "Zone ID of the internal Application Load Balancer"
  value       = aws_lb.intranet_alb.zone_id
}

output "intranet_access_url" {
  description = "Internal URL for accessing services (HTTP)"
  value       = "http://${aws_lb.intranet_alb.dns_name}"
}

output "intranet_access_url_https" {
  description = "Internal URL for accessing services (HTTPS)"
  value       = var.enable_ssl ? "https://${aws_lb.intranet_alb.dns_name}" : "HTTPS not enabled"
}

output "service_endpoints" {
  description = "Service endpoint mappings for corporate users"
  value = {
    web_app        = "http://${aws_lb.intranet_alb.dns_name}/"
    api_services   = "http://${aws_lb.intranet_alb.dns_name}/api/"
    airflow_ui     = "http://${aws_lb.intranet_alb.dns_name}/airflow/"
    dash_analytics = "http://${aws_lb.intranet_alb.dns_name}/dash/"
  }
}

output "vpn_connection_id" {
  description = "VPN Connection ID for corporate network (if enabled)"
  value       = var.enable_vpn_gateway ? aws_vpn_connection.corporate[0].id : null
}

output "internal_dns_zone" {
  description = "Internal DNS zone for service discovery (if enabled)"
  value       = var.create_internal_dns ? aws_route53_zone.internal[0].name : null
}

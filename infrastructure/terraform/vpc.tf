# VPC and Networking Resources

# VPC
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name = "${var.project_name}-${var.environment}-vpc"
  }
}

# Corporate Intranet - No Internet Gateway (comment out for intranet-only)
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  
  tags = {
    Name = "${var.project_name}-${var.environment}-igw"
  }
}

# Management Subnets (formerly public, now for management/bastion access)
resource "aws_subnet" "management" {
  count = length(var.availability_zones)
  
  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index + 1)
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = false  # No public IPs for intranet-only
  
  tags = {
    Name = "${var.project_name}-${var.environment}-mgmt-${count.index + 1}"
    Type = "management"
    Purpose = "Corporate intranet access and management"
  }
}

# Private Subnets
resource "aws_subnet" "private" {
  count = length(var.availability_zones)
  
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 101)
  availability_zone = var.availability_zones[count.index]
  
  tags = {
    Name = "${var.project_name}-${var.environment}-private-${count.index + 1}"
    Type = "private"
    "kubernetes.io/role/internal-elb" = "1"
  }
}

# Database Subnets
resource "aws_subnet" "database" {
  count = length(var.availability_zones)
  
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 201)
  availability_zone = var.availability_zones[count.index]
  
  tags = {
    Name = "${var.project_name}-${var.environment}-database-${count.index + 1}"
    Type = "database"
  }
}

# Corporate Intranet - No NAT Gateways or EIPs needed
# (All traffic routed through corporate network via VPN/Direct Connect)

# Route Tables for Intranet-only Architecture
resource "aws_route_table" "management" {
  vpc_id = aws_vpc.main.id
  
  # Routes to corporate network will be added by VPN/Direct Connect
  # No default internet route for intranet-only setup
  
  tags = {
    Name = "${var.project_name}-${var.environment}-mgmt-rt"
    Purpose = "Management subnet routing for corporate access"
  }
}

resource "aws_route_table" "private" {
  count = length(var.availability_zones)
  
  vpc_id = aws_vpc.main.id
  
  # No default internet route - all external access via corporate network
  # Routes to corporate network will be propagated by VPN Gateway
  
  tags = {
    Name = "${var.project_name}-${var.environment}-private-rt-${count.index + 1}"
    Purpose = "Private subnet routing for EKS workloads"
  }
}

resource "aws_route_table" "database" {
  vpc_id = aws_vpc.main.id
  
  tags = {
    Name = "${var.project_name}-${var.environment}-database-rt"
  }
}

# Route Table Associations
resource "aws_route_table_association" "management" {
  count = length(var.availability_zones)
  
  subnet_id      = aws_subnet.management[count.index].id
  route_table_id = aws_route_table.management.id
}

resource "aws_route_table_association" "private" {
  count = length(var.availability_zones)
  
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}

resource "aws_route_table_association" "database" {
  count = length(var.availability_zones)
  
  subnet_id      = aws_subnet.database[count.index].id
  route_table_id = aws_route_table.database.id
}

# VPC Endpoints for S3 and other AWS services
resource "aws_vpc_endpoint" "s3" {
  vpc_id       = aws_vpc.main.id
  service_name = "com.amazonaws.${var.aws_region}.s3"
  
  tags = {
    Name = "${var.project_name}-${var.environment}-s3-endpoint"
  }
}

# VPC Flow Logs (optional, disabled in free trial to reduce costs)
resource "aws_flow_log" "vpc" {
  count = local.enable_vpc_flow_logs ? 1 : 0
  
  iam_role_arn    = aws_iam_role.flow_log[0].arn
  log_destination = aws_cloudwatch_log_group.vpc_flow_log[0].arn
  traffic_type    = "ALL"
  vpc_id          = aws_vpc.main.id
}

resource "aws_cloudwatch_log_group" "vpc_flow_log" {
  count = local.enable_vpc_flow_logs ? 1 : 0
  
  name              = "/aws/vpc/flow-logs/${var.project_name}-${var.environment}"
  retention_in_days = 14
}

resource "aws_iam_role" "flow_log" {
  count = local.enable_vpc_flow_logs ? 1 : 0
  
  name = "${var.project_name}-${var.environment}-flow-log-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "vpc-flow-logs.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "flow_log" {
  count = local.enable_vpc_flow_logs ? 1 : 0
  
  name = "${var.project_name}-${var.environment}-flow-log-policy"
  role = aws_iam_role.flow_log[0].id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams"
        ]
        Effect = "Allow"
        Resource = "*"
      }
    ]
  })
}

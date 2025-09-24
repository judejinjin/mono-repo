# RDS Database Configuration
# Conditionally optimized for AWS Free Trial

# DB Subnet Group
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-${var.environment}-db-subnet-group"
  subnet_ids = aws_subnet.database[*].id

  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-db-subnet-group"
    }
  )
}

# RDS PostgreSQL Instance
resource "aws_db_instance" "main" {
  identifier     = "${var.project_name}-${var.environment}-db"
  engine         = "postgres"
  engine_version = "15.4"
  
  # Instance configuration based on free trial flag
  instance_class    = local.rds_instance_class
  allocated_storage = local.rds_allocated_storage
  max_allocated_storage = local.rds_max_allocated_storage
  storage_type      = var.free_trial ? "gp2" : "gp3"  # gp2 for free tier
  storage_encrypted = true
  
  # Database configuration
  db_name  = replace("${var.project_name}_${var.environment}", "-", "_")
  username = "dbadmin"
  password = var.db_password
  
  # Networking
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  port                   = 5432
  
  # Backup and maintenance
  backup_retention_period = var.free_trial ? 7 : 14
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  # Free trial optimizations
  multi_az               = var.free_trial ? false : true  # Single AZ for free tier
  publicly_accessible    = false
  auto_minor_version_upgrade = true
  
  # Monitoring (disabled for free trial to reduce costs)
  monitoring_interval = var.free_trial ? 0 : 60
  monitoring_role_arn = var.free_trial ? null : aws_iam_role.rds_enhanced_monitoring[0].arn
  
  # Performance insights (disabled for free trial)
  performance_insights_enabled = var.free_trial ? false : true
  performance_insights_retention_period = var.free_trial ? 0 : 7
  
  # Deletion protection (disabled for easy cleanup in dev)
  deletion_protection = var.environment == "prod" ? true : false
  skip_final_snapshot = var.environment != "prod"
  final_snapshot_identifier = var.environment == "prod" ? "${var.project_name}-${var.environment}-final-snapshot" : null
  
  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-database"
    }
  )
}

# Enhanced monitoring IAM role (only created when not free trial)
resource "aws_iam_role" "rds_enhanced_monitoring" {
  count = var.free_trial ? 0 : 1
  name  = "${var.project_name}-${var.environment}-rds-monitoring-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "rds_enhanced_monitoring" {
  count      = var.free_trial ? 0 : 1
  role       = aws_iam_role.rds_enhanced_monitoring[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# Security Group for RDS
resource "aws_security_group" "rds" {
  name_prefix = "${var.project_name}-${var.environment}-rds-"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
    description = "PostgreSQL access from VPC"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-rds-sg"
    }
  )
}

# Outputs
output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.main.endpoint
}

output "rds_port" {
  description = "RDS instance port"
  value       = aws_db_instance.main.port
}

output "database_name" {
  description = "Database name"
  value       = aws_db_instance.main.db_name
}

output "rds_security_group_id" {
  description = "ID of the RDS security group"
  value       = aws_security_group.rds.id
}
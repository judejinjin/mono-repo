# EFS File System for JupyterHub shared storage
resource "aws_efs_file_system" "jupyterhub_efs" {
  creation_token = "${local.name_prefix}-jupyterhub-efs"
  
  performance_mode = "generalPurpose"
  throughput_mode  = "provisioned"
  provisioned_throughput_in_mibps = 100
  
  encrypted = true
  kms_key_id = aws_kms_key.main.arn
  
  lifecycle_policy {
    transition_to_ia = "AFTER_30_DAYS"
  }
  
  lifecycle_policy {
    transition_to_primary_storage_class = "AFTER_1_ACCESS"
  }
  
  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-jupyterhub-efs"
    Description = "EFS storage for JupyterHub shared notebooks and data"
    Service     = "JupyterHub"
    Component   = "Storage"
  })
}

# EFS Mount Targets for private subnets
resource "aws_efs_mount_target" "jupyterhub_efs" {
  count = length(data.aws_subnets.private.ids)
  
  file_system_id  = aws_efs_file_system.jupyterhub_efs.id
  subnet_id       = data.aws_subnets.private.ids[count.index]
  security_groups = [aws_security_group.jupyterhub_efs.id]
}

# Security Group for EFS
resource "aws_security_group" "jupyterhub_efs" {
  name        = "${local.name_prefix}-jupyterhub-efs-sg"
  description = "Security group for JupyterHub EFS mount targets"
  vpc_id      = data.aws_vpc.main.id
  
  ingress {
    description = "NFS from EKS nodes"
    from_port   = 2049
    to_port     = 2049
    protocol    = "tcp"
    security_groups = [data.aws_security_group.eks_node_group.id]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-jupyterhub-efs-sg"
  })
}

# EFS Access Point for JupyterHub shared directory
resource "aws_efs_access_point" "jupyterhub_shared" {
  file_system_id = aws_efs_file_system.jupyterhub_efs.id
  
  posix_user {
    gid = 1000
    uid = 1000
  }
  
  root_directory {
    path = "/shared"
    creation_info {
      owner_gid   = 1000
      owner_uid   = 1000
      permissions = "755"
    }
  }
  
  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-jupyterhub-shared-access-point"
    Description = "EFS access point for shared JupyterHub storage"
  })
}

# ECR Repository for JupyterHub Management Service
resource "aws_ecr_repository" "jupyterhub_management" {
  name = "${local.name_prefix}/jupyterhub-management"
  
  image_tag_mutability = "MUTABLE"
  
  image_scanning_configuration {
    scan_on_push = true
  }
  
  encryption_configuration {
    encryption_type = "KMS"
    kms_key = aws_kms_key.main.arn
  }
  
  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-jupyterhub-management-ecr"
    Description = "ECR repository for JupyterHub management service"
    Service     = "JupyterHub"
    Component   = "Container Registry"
  })
}

# ECR Repository for Custom JupyterHub Notebook Images
resource "aws_ecr_repository" "jupyterhub_notebook" {
  name = "${local.name_prefix}/jupyterhub-notebook"
  
  image_tag_mutability = "MUTABLE"
  
  image_scanning_configuration {
    scan_on_push = true
  }
  
  encryption_configuration {
    encryption_type = "KMS"
    kms_key = aws_kms_key.main.arn
  }
  
  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-jupyterhub-notebook-ecr"
    Description = "ECR repository for custom JupyterHub notebook images"
    Service     = "JupyterHub"
    Component   = "Container Registry"
  })
}

# ECR Lifecycle Policy for JupyterHub repositories
resource "aws_ecr_lifecycle_policy" "jupyterhub_management" {
  repository = aws_ecr_repository.jupyterhub_management.name
  
  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 10 images"
        selection = {
          tagStatus     = "tagged"
          tagPrefixList = ["v", "latest"]
          countType     = "imageCountMoreThan"
          countNumber   = 10
        }
        action = {
          type = "expire"
        }
      },
      {
        rulePriority = 2
        description  = "Delete untagged images older than 1 day"
        selection = {
          tagStatus   = "untagged"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = 1
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

resource "aws_ecr_lifecycle_policy" "jupyterhub_notebook" {
  repository = aws_ecr_repository.jupyterhub_notebook.name
  
  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 5 notebook images"
        selection = {
          tagStatus     = "tagged"
          tagPrefixList = ["v", "latest"]
          countType     = "imageCountMoreThan"
          countNumber   = 5
        }
        action = {
          type = "expire"
        }
      },
      {
        rulePriority = 2
        description  = "Delete untagged images older than 1 day"
        selection = {
          tagStatus   = "untagged"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = 1
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

# CloudWatch Log Group for JupyterHub
resource "aws_cloudwatch_log_group" "jupyterhub" {
  name = "/aws/eks/${local.cluster_name}/jupyterhub"
  
  retention_in_days = var.environment == "prod" ? 30 : 7
  kms_key_id        = aws_kms_key.main.arn
  
  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-jupyterhub-logs"
    Description = "CloudWatch logs for JupyterHub service"
    Service     = "JupyterHub"
    Component   = "Logging"
  })
}

# CloudWatch Log Group for JupyterHub Management API
resource "aws_cloudwatch_log_group" "jupyterhub_management" {
  name = "/aws/eks/${local.cluster_name}/jupyterhub-management"
  
  retention_in_days = var.environment == "prod" ? 30 : 7
  kms_key_id        = aws_kms_key.main.arn
  
  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-jupyterhub-management-logs"
    Description = "CloudWatch logs for JupyterHub management API"
    Service     = "JupyterHub"
    Component   = "Logging"
  })
}

# CloudWatch Log Group for JupyterHub User Notebooks
resource "aws_cloudwatch_log_group" "jupyterhub_notebooks" {
  name = "/aws/eks/${local.cluster_name}/jupyterhub-notebooks"
  
  retention_in_days = var.environment == "prod" ? 30 : 7
  kms_key_id        = aws_kms_key.main.arn
  
  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-jupyterhub-notebooks-logs"
    Description = "CloudWatch logs for JupyterHub user notebooks"
    Service     = "JupyterHub"
    Component   = "Logging"
  })
}

# S3 Bucket for JupyterHub backups and exports
resource "aws_s3_bucket" "jupyterhub_backups" {
  bucket = "${local.name_prefix}-jupyterhub-backups"
  
  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-jupyterhub-backups"
    Description = "S3 bucket for JupyterHub notebook backups and exports"
    Service     = "JupyterHub"
    Component   = "Backup"
  })
}

# S3 Bucket encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "jupyterhub_backups" {
  bucket = aws_s3_bucket.jupyterhub_backups.id
  
  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.main.arn
      sse_algorithm     = "aws:kms"
    }
    bucket_key_enabled = true
  }
}

# S3 Bucket versioning
resource "aws_s3_bucket_versioning" "jupyterhub_backups" {
  bucket = aws_s3_bucket.jupyterhub_backups.id
  versioning_configuration {
    status = "Enabled"
  }
}

# S3 Bucket lifecycle configuration
resource "aws_s3_bucket_lifecycle_configuration" "jupyterhub_backups" {
  bucket = aws_s3_bucket.jupyterhub_backups.id
  
  rule {
    id     = "jupyterhub_backup_lifecycle"
    status = "Enabled"
    
    expiration {
      days = var.environment == "prod" ? 90 : 30
    }
    
    noncurrent_version_expiration {
      noncurrent_days = 30
    }
    
    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

# S3 Bucket public access block
resource "aws_s3_bucket_public_access_block" "jupyterhub_backups" {
  bucket = aws_s3_bucket.jupyterhub_backups.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Security Group for JupyterHub services
resource "aws_security_group" "jupyterhub" {
  name        = "${local.name_prefix}-jupyterhub-sg"
  description = "Security group for JupyterHub services"
  vpc_id      = data.aws_vpc.main.id
  
  # Allow HTTP from load balancer
  ingress {
    description = "HTTP from ALB"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    security_groups = [aws_security_group.alb.id]
  }
  
  # Allow communication within JupyterHub namespace
  ingress {
    description = "Internal JupyterHub communication"
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    self        = true
  }
  
  # Allow egress to Risk API
  egress {
    description = "To Risk API"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    security_groups = [data.aws_security_group.risk_api.id]
  }
  
  # Allow egress to RDS
  egress {
    description = "To RDS"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    security_groups = [aws_security_group.rds.id]
  }
  
  # Allow egress to EFS
  egress {
    description = "To EFS"
    from_port   = 2049
    to_port     = 2049
    protocol    = "tcp"
    security_groups = [aws_security_group.jupyterhub_efs.id]
  }
  
  # Allow all outbound traffic for package installation and external APIs
  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-jupyterhub-sg"
    Description = "Security group for JupyterHub services"
    Service     = "JupyterHub"
  })
}

# Outputs for JupyterHub infrastructure
output "jupyterhub_efs_id" {
  description = "EFS file system ID for JupyterHub"
  value       = aws_efs_file_system.jupyterhub_efs.id
}

output "jupyterhub_ecr_management_repository" {
  description = "ECR repository for JupyterHub management service"
  value       = aws_ecr_repository.jupyterhub_management.repository_url
}

output "jupyterhub_ecr_notebook_repository" {
  description = "ECR repository for JupyterHub notebook images"
  value       = aws_ecr_repository.jupyterhub_notebook.repository_url
}

output "jupyterhub_backup_bucket" {
  description = "S3 bucket for JupyterHub backups"
  value       = aws_s3_bucket.jupyterhub_backups.bucket
}
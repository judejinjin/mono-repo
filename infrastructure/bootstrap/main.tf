# Terraform Bootstrap Configuration
# This creates the S3 bucket and DynamoDB table required for Terraform remote state management

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.4"
    }
  }
  
  # Use local backend for bootstrap - we can't use S3 backend until S3 bucket exists
  backend "local" {
    path = "terraform.tfstate"
  }
}

# Configure AWS provider 
provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = var.project_name
      Environment = "bootstrap"
      ManagedBy   = "Terraform"
      Purpose     = "Bootstrap Infrastructure"
    }
  }
}

# Generate random suffix for unique bucket naming
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# S3 bucket for Terraform state
resource "aws_s3_bucket" "terraform_state" {
  bucket        = "${var.project_name}-terraform-state-${random_id.bucket_suffix.hex}"
  force_destroy = false # Protect against accidental deletion

  tags = {
    Name        = "${var.project_name}-terraform-state"
    Description = "Terraform remote state storage"
  }
}

# Enable versioning for state bucket
resource "aws_s3_bucket_versioning" "terraform_state_versioning" {
  bucket = aws_s3_bucket.terraform_state.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Enable server-side encryption for state bucket
resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state_encryption" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
    bucket_key_enabled = true
  }
}

# Block public access to state bucket
resource "aws_s3_bucket_public_access_block" "terraform_state_pab" {
  bucket = aws_s3_bucket.terraform_state.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# DynamoDB table for state locking
resource "aws_dynamodb_table" "terraform_state_lock" {
  name           = "${var.project_name}-terraform-state-lock"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    Name        = "${var.project_name}-terraform-state-lock"
    Description = "Terraform state locking"
  }
}

# Optional: Create ECR repositories for container images
resource "aws_ecr_repository" "app_repositories" {
  for_each = var.create_ecr_repositories ? toset(var.ecr_repositories) : []
  
  name                 = "${var.project_name}-${each.key}"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  lifecycle_policy {
    policy = jsonencode({
      rules = [
        {
          rulePriority = 1
          description  = "Keep last 10 images"
          selection = {
            tagStatus     = "tagged"
            tagPrefixList = ["v"]
            countType     = "imageCountMoreThan"
            countNumber   = 10
          }
          action = {
            type = "expire"
          }
        }
      ]
    })
  }

  tags = {
    Name        = "${var.project_name}-${each.key}"
    Description = "Container repository for ${each.key}"
  }
}

# Output values for main Terraform configuration
output "terraform_state_bucket" {
  description = "Name of the S3 bucket for Terraform state"
  value       = aws_s3_bucket.terraform_state.bucket
}

output "terraform_state_bucket_arn" {
  description = "ARN of the S3 bucket for Terraform state"
  value       = aws_s3_bucket.terraform_state.arn
}

output "dynamodb_table_name" {
  description = "Name of the DynamoDB table for state locking"
  value       = aws_dynamodb_table.terraform_state_lock.name
}

output "dynamodb_table_arn" {
  description = "ARN of the DynamoDB table for state locking"
  value       = aws_dynamodb_table.terraform_state_lock.arn
}

output "ecr_repository_urls" {
  description = "URLs of created ECR repositories"
  value = var.create_ecr_repositories ? {
    for name, repo in aws_ecr_repository.app_repositories : name => repo.repository_url
  } : {}
}

output "aws_region" {
  description = "AWS region used for bootstrap"
  value       = var.aws_region
}

output "backend_configuration" {
  description = "Backend configuration for main Terraform"
  value = {
    bucket         = aws_s3_bucket.terraform_state.bucket
    key            = "infrastructure/terraform.tfstate"
    region         = var.aws_region
    dynamodb_table = aws_dynamodb_table.terraform_state_lock.name
    encrypt        = true
  }
}

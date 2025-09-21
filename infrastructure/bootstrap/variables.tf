# Variables for Terraform Bootstrap Configuration

variable "aws_region" {
  description = "AWS region for bootstrap resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name of the project (used for S3 bucket and DynamoDB table naming)"
  type        = string
  default     = "mono-repo"
  
  validation {
    condition     = can(regex("^[a-z0-9-]{3,20}$", var.project_name))
    error_message = "Project name must be 3-20 characters, lowercase letters, numbers, and hyphens only."
  }
}

variable "environment" {
  description = "Environment name (used for tagging)"
  type        = string
  default     = "bootstrap"
}

variable "create_ecr_repositories" {
  description = "Whether to create ECR repositories during bootstrap"
  type        = bool
  default     = true
}

variable "ecr_repositories" {
  description = "List of ECR repository names to create"
  type        = list(string)
  default = [
    "web-app",
    "api-service", 
    "airflow-worker",
    "dash-app",
    "data-processor"
  ]
}

variable "force_destroy_bucket" {
  description = "Allow force destruction of S3 bucket (use with caution)"
  type        = bool
  default     = false
}

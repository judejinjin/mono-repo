# IAM Infrastructure Variables
# Central configuration for IAM resource management

# Project Configuration
variable "project_name" {
  description = "Name of the project for resource naming"
  type        = string
  default     = "corporate-intranet"
}

variable "environment" {
  description = "Environment name (dev, uat, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "uat", "prod"], var.environment)
    error_message = "Environment must be dev, uat, or prod."
  }
}

variable "region" {
  description = "AWS region for IAM resources"
  type        = string
  default     = "us-west-2"
}

# Common Tags
variable "common_tags" {
  description = "Common tags applied to all IAM resources"
  type        = map(string)
  default = {
    Project     = "corporate-intranet"
    ManagedBy   = "terraform"
    Repository  = "mono-repo"
    Team        = "platform"
  }
}

# Organization Configuration
variable "organization_name" {
  description = "Organization name for IAM resource prefixes"
  type        = string
  default     = "corp"
}

variable "department_prefixes" {
  description = "Department prefixes for user organization"
  type        = list(string)
  default     = ["dev", "ops", "security", "business", "qa"]
}

# EKS Service Role Configuration
variable "eks_cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
  default     = "corporate-intranet-cluster"
}

variable "eks_node_group_name" {
  description = "Name of the EKS node group"
  type        = string
  default     = "corporate-intranet-nodes"
}

# RDS Service Role Configuration
variable "rds_instance_identifier" {
  description = "RDS instance identifier for IAM database authentication"
  type        = string
  default     = "corporate-intranet-db"
}

# S3 Bucket Configuration
variable "s3_buckets" {
  description = "List of S3 buckets requiring IAM access"
  type        = list(string)
  default = [
    "corporate-intranet-assets",
    "corporate-intranet-backups",
    "corporate-intranet-logs",
    "corporate-intranet-artifacts"
  ]
}

# Lambda Function Configuration
variable "lambda_functions" {
  description = "List of Lambda functions requiring IAM roles"
  type        = list(string)
  default = [
    "risk-calculator",
    "data-processor",
    "notification-handler",
    "backup-scheduler"
  ]
}

# Cross-Account Access Configuration
variable "trusted_accounts" {
  description = "List of AWS account IDs for cross-account access"
  type        = list(string)
  default     = []
}

variable "external_id" {
  description = "External ID for cross-account role assumption"
  type        = string
  default     = ""
  sensitive   = true
}

# User Management Configuration
variable "developer_users" {
  description = "List of developer users to create"
  type = list(object({
    name  = string
    email = string
    team  = string
  }))
  default = []
}

variable "admin_users" {
  description = "List of administrative users to create"
  type = list(object({
    name  = string
    email = string
    role  = string
  }))
  default = []
}

variable "service_accounts" {
  description = "List of service accounts to create"
  type = list(object({
    name        = string
    description = string
    service     = string
  }))
  default = []
}

# Security Configuration
variable "password_policy" {
  description = "Password policy configuration"
  type = object({
    minimum_password_length        = number
    require_lowercase_characters   = bool
    require_uppercase_characters   = bool
    require_numbers               = bool
    require_symbols               = bool
    allow_users_to_change_password = bool
    max_password_age              = number
    password_reuse_prevention     = number
  })
  default = {
    minimum_password_length        = 12
    require_lowercase_characters   = true
    require_uppercase_characters   = true
    require_numbers               = true
    require_symbols               = true
    allow_users_to_change_password = true
    max_password_age              = 90
    password_reuse_prevention     = 5
  }
}

variable "mfa_required" {
  description = "Whether MFA is required for users"
  type        = bool
  default     = true
}

variable "session_duration" {
  description = "Maximum session duration in seconds"
  type        = number
  default     = 3600  # 1 hour
  validation {
    condition     = var.session_duration >= 900 && var.session_duration <= 43200
    error_message = "Session duration must be between 900 and 43200 seconds."
  }
}

# IP Restriction Configuration
variable "allowed_ip_ranges" {
  description = "List of allowed IP ranges for access"
  type        = list(string)
  default     = []
}

variable "office_ip_ranges" {
  description = "Corporate office IP ranges"
  type        = list(string)
  default     = []
}

# CI/CD Configuration
variable "bamboo_server_ips" {
  description = "IP addresses of Bamboo servers for CI/CD access"
  type        = list(string)
  default     = []
}

variable "github_actions_role" {
  description = "Whether to create GitHub Actions OIDC role"
  type        = bool
  default     = true
}

variable "github_repository" {
  description = "GitHub repository for OIDC trust relationship"
  type        = string
  default     = "organization/mono-repo"
}

# Monitoring and Logging
variable "enable_cloudtrail" {
  description = "Whether to enable CloudTrail for IAM events"
  type        = bool
  default     = true
}

variable "cloudwatch_log_retention_days" {
  description = "CloudWatch log retention period in days"
  type        = number
  default     = 30
}

# Cost Management
variable "enable_cost_allocation_tags" {
  description = "Whether to enable cost allocation tags"
  type        = bool
  default     = true
}

variable "budget_alert_threshold" {
  description = "Budget alert threshold in USD"
  type        = number
  default     = 100
}

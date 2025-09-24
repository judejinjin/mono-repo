# Variables for Parameter Store Terraform Module

variable "environment" {
  description = "Environment name (dev, uat, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "uat", "prod"], var.environment)
    error_message = "Environment must be dev, uat, or prod."
  }
}

variable "app_name" {
  description = "Application name for parameter namespacing"
  type        = string
  default     = "mono-repo"
}

variable "regular_parameters" {
  description = "Map of regular (non-sensitive) parameters to create"
  type        = map(string)
  default     = {}
}

variable "secure_parameters" {
  description = "Map of secure (sensitive) parameters to create as SecureString"
  type        = map(string)
  default     = {}
  sensitive   = true
}

variable "create_kms_key" {
  description = "Whether to create a new KMS key for parameter encryption"
  type        = bool
  default     = true
}

variable "kms_key_id" {
  description = "Existing KMS key ID to use for encryption (if create_kms_key is false)"
  type        = string
  default     = null
}

variable "create_access_role" {
  description = "Whether to create an IAM role for Parameter Store access"
  type        = bool
  default     = true
}

variable "allow_write_access" {
  description = "Whether to allow write access in the IAM policy (for admin operations)"
  type        = bool
  default     = false
}

variable "create_instance_profile" {
  description = "Whether to create an instance profile for EC2 access"
  type        = bool
  default     = false
}

variable "assume_role_services" {
  description = "List of AWS services that can assume the Parameter Store access role"
  type        = list(string)
  default     = ["ec2.amazonaws.com", "ecs-tasks.amazonaws.com", "lambda.amazonaws.com"]
}

variable "assume_role_arns" {
  description = "List of IAM role/user ARNs that can assume the Parameter Store access role"
  type        = list(string)
  default     = []
}

variable "assume_role_conditions" {
  description = "Additional conditions for assume role policy"
  type        = any
  default     = null
}

variable "cross_account_access_arns" {
  description = "List of cross-account ARNs that should have read access to parameters"
  type        = list(string)
  default     = []
}

variable "enable_access_logging" {
  description = "Whether to enable CloudWatch logging for Parameter Store access"
  type        = bool
  default     = false
}

variable "log_retention_days" {
  description = "Number of days to retain CloudWatch logs"
  type        = number
  default     = 30
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default = {
    Project   = "mono-repo"
    ManagedBy = "Terraform"
  }
}
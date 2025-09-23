# Variables for Terraform configuration

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, uat, prod)"
  type        = string
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "mono-repo"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones for the VPC"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

# EKS Configuration
variable "eks_cluster_version" {
  description = "Kubernetes version for EKS cluster"
  type        = string
  default     = "1.28"
}

variable "eks_node_instance_types" {
  description = "Instance types for EKS worker nodes"
  type        = list(string)
  default     = ["t3.medium"]
}

variable "eks_node_desired_capacity" {
  description = "Desired number of worker nodes"
  type        = number
  default     = 3
}

variable "eks_node_max_capacity" {
  description = "Maximum number of worker nodes"
  type        = number
  default     = 10
}

variable "eks_node_min_capacity" {
  description = "Minimum number of worker nodes"
  type        = number
  default     = 1
}

# Dev Server Configuration
variable "create_dev_server" {
  description = "Whether to create development server (only for dev environment)"
  type        = bool
  default     = false
}

variable "dev_server_instance_type" {
  description = "Instance type for development server"
  type        = string
  default     = "t3.large"
}

variable "dev_server_key_name" {
  description = "EC2 Key Pair name for dev server"
  type        = string
  default     = ""
}

# Database Configuration
variable "rds_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "rds_allocated_storage" {
  description = "Allocated storage for RDS instances"
  type        = number
  default     = 20
}

variable "rds_max_allocated_storage" {
  description = "Maximum allocated storage for RDS instances"
  type        = number
  default     = 100
}

# Storage Configuration
variable "s3_bucket_prefix" {
  description = "Prefix for S3 bucket names"
  type        = string
  default     = "mono-repo"
}

# Monitoring Configuration
variable "enable_monitoring" {
  description = "Enable CloudWatch monitoring"
  type        = bool
  default     = true
}

variable "enable_logging" {
  description = "Enable CloudWatch logging"
  type        = bool
  default     = true
}

# Security Configuration
variable "allowed_cidr_blocks" {
  description = "CIDR blocks allowed to access resources"
  type        = list(string)
  default     = ["0.0.0.0/0"]  # Restrict in production
}

variable "enable_vpc_flow_logs" {
  description = "Enable VPC flow logs"
  type        = bool
  default     = true
}

# Corporate Intranet Configuration
variable "corporate_network_cidrs" {
  description = "CIDR blocks for corporate network access (e.g., office networks, VPN ranges)"
  type        = list(string)
  default     = ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]  # Common private ranges
}

variable "enable_vpn_gateway" {
  description = "Whether to create VPN Gateway for corporate connectivity"
  type        = bool
  default     = false
}

variable "corporate_gateway_ip" {
  description = "Public IP address of corporate gateway for VPN connection"
  type        = string
  default     = ""
}

variable "enable_ssl" {
  description = "Whether to enable SSL/TLS on internal load balancer"
  type        = bool
  default     = false
}

variable "ssl_certificate_arn" {
  description = "ARN of SSL certificate for internal load balancer (if enable_ssl is true)"
  type        = string
  default     = ""
}

variable "create_internal_dns" {
  description = "Whether to create internal Route 53 private hosted zone"
  type        = bool
  default     = true
}

variable "internal_domain_name" {
  description = "Internal domain name for private DNS (e.g., corp.company.com)"
  type        = string
  default     = "internal.local"
}

# Tags
variable "additional_tags" {
  description = "Additional tags to apply to resources"
  type        = map(string)
  default     = {}
}

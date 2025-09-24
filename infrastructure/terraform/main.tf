# Terraform configuration for mono-repo infrastructure

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
  }
  
  # Using local backend for diagram generation
  # backend "s3" {
  #   bucket = "mono-repo-terraform-state"
  #   key    = "infrastructure/terraform.tfstate"
  #   region = "us-east-1"
  #   
  #   dynamodb_table = "terraform-state-lock"
  #   encrypt        = true
  # }
}

# Configure providers
provider "aws" {
  region                      = var.aws_region
  access_key                  = var.aws_access_key
  secret_key                  = var.aws_secret_key
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Local values for conditional resource sizing
locals {
  # Free trial optimized configurations
  eks_node_instance_types = var.free_trial ? ["t3.micro"] : var.eks_node_instance_types
  eks_node_desired_capacity = var.free_trial ? 1 : var.eks_node_desired_capacity
  eks_node_max_capacity = var.free_trial ? 2 : var.eks_node_max_capacity
  eks_node_min_capacity = var.free_trial ? 0 : var.eks_node_min_capacity
  
  rds_instance_class = var.free_trial ? "db.t3.micro" : var.rds_instance_class
  rds_allocated_storage = var.free_trial ? 20 : var.rds_allocated_storage
  rds_max_allocated_storage = var.free_trial ? 20 : var.rds_max_allocated_storage
  
  dev_server_instance_type = var.free_trial ? "t3.micro" : var.dev_server_instance_type
  dev_server_volume_size = var.free_trial ? 20 : 50  # Smaller disk for free tier
  
  # Free trial specific settings
  enable_vpc_flow_logs = var.free_trial ? false : true  # Disable VPC flow logs to reduce costs
  enable_detailed_monitoring = var.free_trial ? false : true  # Reduce CloudWatch costs
  
  # Common tags with free trial indicator
  common_tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    },
    var.free_trial ? { FreeTrial = "true", CostOptimized = "true" } : {}
  )
}

provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
  
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args        = ["eks", "get-token", "--cluster-name", module.eks.cluster_name]
  }
}

provider "helm" {
  kubernetes {
    host                   = module.eks.cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
    
    exec {
      api_version = "client.authentication.k8s.io/v1beta1"
      command     = "aws"
      args        = ["eks", "get-token", "--cluster-name", module.eks.cluster_name]
    }
  }
}

# Parameter Store Module
module "parameter_store" {
  source = "./modules/parameter_store"
  
  environment = var.environment
  app_name    = var.app_name
  
  regular_parameters = var.regular_parameters
  secure_parameters  = var.secure_parameters
  
  create_kms_key         = var.parameter_store_create_kms_key
  create_access_role     = var.parameter_store_create_access_role
  allow_write_access     = var.parameter_store_allow_write_access
  create_instance_profile = var.parameter_store_create_instance_profile
  
  assume_role_services = var.parameter_store_assume_role_services
  assume_role_arns    = var.parameter_store_assume_role_arns
  
  enable_access_logging = var.parameter_store_enable_logging
  log_retention_days   = var.parameter_store_log_retention_days
  
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
    Component   = "parameter-store"
  }
}

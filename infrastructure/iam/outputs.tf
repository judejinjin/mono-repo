# IAM Infrastructure Outputs
# Export important values for use by other Terraform configurations

# Account Information
output "account_id" {
  description = "AWS Account ID"
  value       = data.aws_caller_identity.current.account_id
}

output "region" {
  description = "AWS Region"
  value       = data.aws_region.current.name
}

# Service Role ARNs
output "eks_cluster_role_arn" {
  description = "EKS Cluster Service Role ARN"
  value       = aws_iam_role.eks_cluster_role.arn
}

output "eks_node_group_role_arn" {
  description = "EKS Node Group Role ARN"
  value       = aws_iam_role.eks_node_group_role.arn
}

output "lambda_execution_role_arns" {
  description = "Lambda execution role ARNs by function name"
  value = {
    for name in var.lambda_functions : name => aws_iam_role.lambda_execution_role[name].arn
  }
}

output "rds_monitoring_role_arn" {
  description = "RDS Enhanced Monitoring Role ARN"
  value       = aws_iam_role.rds_monitoring_role.arn
}

# Cross-Account Role ARNs
output "cross_account_role_arns" {
  description = "Cross-account access role ARNs"
  value = length(var.trusted_accounts) > 0 ? {
    for account in var.trusted_accounts : account => aws_iam_role.cross_account_role[account].arn
  } : {}
}

# GitHub Actions Role (if enabled)
output "github_actions_role_arn" {
  description = "GitHub Actions OIDC role ARN"
  value       = var.github_actions_role ? aws_iam_role.github_actions[0].arn : null
}

output "github_oidc_provider_arn" {
  description = "GitHub Actions OIDC provider ARN"
  value       = var.github_actions_role ? aws_iam_openid_connect_provider.github_actions[0].arn : null
}

# User and Group Information
output "developer_user_arns" {
  description = "Developer user ARNs"
  value = {
    for user in var.developer_users : user.name => aws_iam_user.developers[user.name].arn
  }
}

output "admin_user_arns" {
  description = "Administrative user ARNs"
  value = {
    for user in var.admin_users : user.name => aws_iam_user.admins[user.name].arn
  }
}

output "service_account_arns" {
  description = "Service account ARNs"
  value = {
    for account in var.service_accounts : account.name => aws_iam_user.service_accounts[account.name].arn
  }
}

output "group_arns" {
  description = "IAM group ARNs"
  value = {
    developers = aws_iam_group.developers.arn
    operations = aws_iam_group.operations.arn
    security   = aws_iam_group.security.arn
    business   = aws_iam_group.business.arn
    qa         = aws_iam_group.qa.arn
    admins     = aws_iam_group.admins.arn
  }
}

# Custom Policy ARNs
output "custom_policy_arns" {
  description = "Custom IAM policy ARNs"
  value = {
    s3_bucket_access         = aws_iam_policy.s3_bucket_access.arn
    eks_cluster_access       = aws_iam_policy.eks_cluster_access.arn
    rds_database_access      = aws_iam_policy.rds_database_access.arn
    lambda_invoke_access     = aws_iam_policy.lambda_invoke_access.arn
    secrets_manager_access   = aws_iam_policy.secrets_manager_access.arn
    cloudwatch_logs_access   = aws_iam_policy.cloudwatch_logs_access.arn
    developer_boundary       = aws_iam_policy.developer_boundary.arn
    operations_boundary      = aws_iam_policy.operations_boundary.arn
    ci_cd_deployment        = aws_iam_policy.ci_cd_deployment.arn
  }
}

# Instance Profiles
output "instance_profile_arns" {
  description = "EC2 instance profile ARNs"
  value = {
    eks_node_group = aws_iam_instance_profile.eks_node_group.arn
    bastion_host   = aws_iam_instance_profile.bastion_host.arn
  }
}

# CloudTrail Information (if enabled)
output "cloudtrail_arn" {
  description = "CloudTrail ARN for IAM event logging"
  value       = var.enable_cloudtrail ? aws_cloudtrail.iam_events[0].arn : null
}

output "cloudtrail_s3_bucket" {
  description = "S3 bucket name for CloudTrail logs"
  value       = var.enable_cloudtrail ? aws_s3_bucket.cloudtrail_logs[0].bucket : null
}

output "cloudwatch_log_group_arn" {
  description = "CloudWatch log group ARN for IAM events"
  value       = var.enable_cloudtrail ? aws_cloudwatch_log_group.iam_events[0].arn : null
}

# Security Information
output "password_policy_configured" {
  description = "Whether password policy is configured"
  value       = true
}

output "mfa_required" {
  description = "Whether MFA is required for users"
  value       = var.mfa_required
}

# Access Key Information (sensitive)
output "service_account_access_keys" {
  description = "Service account access key IDs (secrets are sensitive)"
  value = {
    for account in var.service_accounts : account.name => {
      access_key_id = aws_iam_access_key.service_accounts[account.name].id
      # secret_access_key is intentionally not exported for security
    }
  }
  sensitive = true
}

# Resource Counts
output "resource_counts" {
  description = "Count of created IAM resources"
  value = {
    roles           = length(aws_iam_role.eks_cluster_role) + length(aws_iam_role.eks_node_group_role) + length(aws_iam_role.lambda_execution_role) + length(aws_iam_role.cross_account_role) + (var.github_actions_role ? 1 : 0)
    users           = length(var.developer_users) + length(var.admin_users) + length(var.service_accounts)
    groups          = 6  # developers, operations, security, business, qa, admins
    policies        = 9  # custom policies count
    instance_profiles = 2  # eks_node_group, bastion_host
  }
}

# Naming Convention Information
output "naming_convention" {
  description = "Naming convention used for resources"
  value = {
    prefix      = local.name_prefix
    environment = var.environment
    project     = var.project_name
    organization = var.organization_name
  }
}

# Tags Information
output "common_tags" {
  description = "Common tags applied to all resources"
  value       = local.common_tags
}

# Integration Points
output "integration_info" {
  description = "Information for integrating with other infrastructure"
  value = {
    eks_cluster_name     = var.eks_cluster_name
    rds_instance_id      = var.rds_instance_identifier
    s3_buckets          = var.s3_buckets
    lambda_functions    = var.lambda_functions
    github_repository   = var.github_repository
  }
}

# Cost Management
output "budget_configured" {
  description = "Whether cost budget is configured"
  value       = var.enable_cost_allocation_tags
}

output "budget_threshold" {
  description = "Budget alert threshold in USD"
  value       = var.budget_alert_threshold
}

# Outputs for Parameter Store Terraform Module

output "parameter_prefix" {
  description = "The prefix used for all parameters in this module"
  value       = local.parameter_prefix
}

output "parameters" {
  description = "Map of all created parameters with their names, ARNs, and types"
  value       = local.all_parameters
}

output "regular_parameter_names" {
  description = "List of regular parameter names"
  value       = [for k, v in aws_ssm_parameter.regular_parameters : v.name]
}

output "secure_parameter_names" {
  description = "List of secure parameter names"
  value       = [for k, v in aws_ssm_parameter.secure_parameters : v.name]
}

output "regular_parameter_arns" {
  description = "List of regular parameter ARNs"
  value       = [for k, v in aws_ssm_parameter.regular_parameters : v.arn]
}

output "secure_parameter_arns" {
  description = "List of secure parameter ARNs"
  value       = [for k, v in aws_ssm_parameter.secure_parameters : v.arn]
}

output "kms_key_id" {
  description = "KMS key ID used for parameter encryption"
  value       = var.create_kms_key ? aws_kms_key.parameter_store[0].key_id : var.kms_key_id
}

output "kms_key_arn" {
  description = "KMS key ARN used for parameter encryption"
  value       = var.create_kms_key ? aws_kms_key.parameter_store[0].arn : null
}

output "kms_key_alias" {
  description = "KMS key alias"
  value       = var.create_kms_key ? aws_kms_alias.parameter_store[0].name : null
}

output "access_role_arn" {
  description = "ARN of the IAM role for Parameter Store access"
  value       = var.create_access_role ? aws_iam_role.parameter_store_access[0].arn : null
}

output "access_role_name" {
  description = "Name of the IAM role for Parameter Store access"
  value       = var.create_access_role ? aws_iam_role.parameter_store_access[0].name : null
}

output "instance_profile_arn" {
  description = "ARN of the instance profile for EC2 access"
  value       = var.create_access_role && var.create_instance_profile ? aws_iam_instance_profile.parameter_store_access[0].arn : null
}

output "instance_profile_name" {
  description = "Name of the instance profile for EC2 access"
  value       = var.create_access_role && var.create_instance_profile ? aws_iam_instance_profile.parameter_store_access[0].name : null
}

output "cloudwatch_log_group_name" {
  description = "Name of the CloudWatch log group for access logging"
  value       = var.enable_access_logging ? aws_cloudwatch_log_group.parameter_store_access[0].name : null
}

output "cloudwatch_log_group_arn" {
  description = "ARN of the CloudWatch log group for access logging"
  value       = var.enable_access_logging ? aws_cloudwatch_log_group.parameter_store_access[0].arn : null
}

# Environment-specific outputs for easy reference
output "environment" {
  description = "Environment name"
  value       = var.environment
}

output "app_name" {
  description = "Application name"
  value       = var.app_name
}

# Parameter count summaries
output "parameter_count" {
  description = "Summary of parameter counts"
  value = {
    total   = length(aws_ssm_parameter.regular_parameters) + length(aws_ssm_parameter.secure_parameters)
    regular = length(aws_ssm_parameter.regular_parameters)
    secure  = length(aws_ssm_parameter.secure_parameters)
  }
}
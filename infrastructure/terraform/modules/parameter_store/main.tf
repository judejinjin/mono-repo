# Parameter Store Terraform Module
# This module manages AWS Systems Manager Parameter Store parameters for the mono-repo application
# Supports hierarchical parameter structure: /{environment}/{app_name}/{parameter_name}

# Data source for current AWS caller identity
data "aws_caller_identity" "current" {}

# Data source for current AWS region
data "aws_region" "current" {}

# Local values for parameter naming and tagging
locals {
  parameter_prefix = "/${var.environment}/${var.app_name}"
  
  # Common tags for all resources
  common_tags = merge(var.common_tags, {
    Environment = var.environment
    AppName     = var.app_name
    Module      = "parameter-store"
  })
}

# KMS Key for Parameter Store encryption
resource "aws_kms_key" "parameter_store" {
  count                   = var.create_kms_key ? 1 : 0
  description             = "KMS key for Parameter Store encryption - ${var.environment} ${var.app_name}"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = merge(local.common_tags, {
    Name = "${var.app_name}-parameter-store-key-${var.environment}"
  })
}

# KMS Key Alias
resource "aws_kms_alias" "parameter_store" {
  count         = var.create_kms_key ? 1 : 0
  name          = "alias/${var.app_name}-parameter-store-${var.environment}"
  target_key_id = aws_kms_key.parameter_store[0].key_id
}

# SSM Parameters - Regular (String type)
resource "aws_ssm_parameter" "regular_parameters" {
  for_each = var.regular_parameters

  name  = "${local.parameter_prefix}/${each.key}"
  type  = "String"
  value = each.value
  
  description = "Parameter for ${var.app_name} - ${each.key}"
  
  tags = merge(local.common_tags, {
    Name        = each.key
    Type        = "Regular"
    Sensitive   = "false"
  })
}

# SSM Parameters - Secure (SecureString type)
resource "aws_ssm_parameter" "secure_parameters" {
  for_each = var.secure_parameters

  name   = "${local.parameter_prefix}/${each.key}"
  type   = "SecureString"
  value  = each.value
  key_id = var.create_kms_key ? aws_kms_key.parameter_store[0].key_id : var.kms_key_id
  
  description = "Secure parameter for ${var.app_name} - ${each.key}"
  
  tags = merge(local.common_tags, {
    Name        = each.key
    Type        = "Secure"
    Sensitive   = "true"
  })
}

# IAM Role for Parameter Store access
resource "aws_iam_role" "parameter_store_access" {
  count = var.create_access_role ? 1 : 0
  name  = "${var.app_name}-parameter-store-access-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = var.assume_role_services
        }
      },
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          AWS = var.assume_role_arns
        }
        Condition = var.assume_role_conditions != null ? var.assume_role_conditions : {}
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name = "${var.app_name}-parameter-store-access-${var.environment}"
  })
}

# IAM Policy for Parameter Store read access
resource "aws_iam_role_policy" "parameter_store_read" {
  count = var.create_access_role ? 1 : 0
  name  = "parameter-store-read-policy"
  role  = aws_iam_role.parameter_store_access[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters",
          "ssm:GetParametersByPath"
        ]
        Resource = [
          "arn:aws:ssm:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:parameter${local.parameter_prefix}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt"
        ]
        Resource = var.create_kms_key ? aws_kms_key.parameter_store[0].arn : var.kms_key_id
        Condition = {
          StringEquals = {
            "kms:ViaService" = "ssm.${data.aws_region.current.name}.amazonaws.com"
          }
        }
      }
    ]
  })
}

# IAM Policy for Parameter Store write access (admin operations)
resource "aws_iam_role_policy" "parameter_store_write" {
  count = var.create_access_role && var.allow_write_access ? 1 : 0
  name  = "parameter-store-write-policy"
  role  = aws_iam_role.parameter_store_access[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssm:PutParameter",
          "ssm:DeleteParameter",
          "ssm:AddTagsToResource",
          "ssm:RemoveTagsFromResource"
        ]
        Resource = [
          "arn:aws:ssm:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:parameter${local.parameter_prefix}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Encrypt",
          "kms:GenerateDataKey"
        ]
        Resource = var.create_kms_key ? aws_kms_key.parameter_store[0].arn : var.kms_key_id
        Condition = {
          StringEquals = {
            "kms:ViaService" = "ssm.${data.aws_region.current.name}.amazonaws.com"
          }
        }
      }
    ]
  })
}

# Instance Profile for EC2 instances (if needed)
resource "aws_iam_instance_profile" "parameter_store_access" {
  count = var.create_access_role && var.create_instance_profile ? 1 : 0
  name  = "${var.app_name}-parameter-store-profile-${var.environment}"
  role  = aws_iam_role.parameter_store_access[0].name

  tags = local.common_tags
}

# CloudWatch Log Group for Parameter Store access logging (optional)
resource "aws_cloudwatch_log_group" "parameter_store_access" {
  count             = var.enable_access_logging ? 1 : 0
  name              = "/aws/ssm/parameter-store/${var.environment}/${var.app_name}"
  retention_in_days = var.log_retention_days

  tags = merge(local.common_tags, {
    Name = "parameter-store-access-logs"
  })
}

# Parameter Store policy document for cross-account access (if needed)
data "aws_iam_policy_document" "parameter_store_resource_policy" {
  count = length(var.cross_account_access_arns) > 0 ? 1 : 0

  statement {
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = var.cross_account_access_arns
    }
    actions = [
      "ssm:GetParameter",
      "ssm:GetParameters",
      "ssm:GetParametersByPath"
    ]
    resources = [
      "arn:aws:ssm:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:parameter${local.parameter_prefix}/*"
    ]
  }
}

# Output all parameter names and ARNs for reference
locals {
  all_parameters = merge(
    { for k, v in aws_ssm_parameter.regular_parameters : k => {
      name = v.name
      arn  = v.arn
      type = "String"
    }},
    { for k, v in aws_ssm_parameter.secure_parameters : k => {
      name = v.name
      arn  = v.arn
      type = "SecureString"
    }}
  )
}
# IAM Infrastructure Main Configuration
# Root configuration for IAM resource management

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
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
  }
}

# Data Sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Local Values
locals {
  account_id = data.aws_caller_identity.current.account_id
  region     = data.aws_region.current.name
  
  # Resource naming convention
  name_prefix = "${var.organization_name}-${var.project_name}-${var.environment}"
  
  # Common tags with environment-specific additions
  common_tags = merge(var.common_tags, {
    Environment = var.environment
    AccountId   = local.account_id
    Region      = local.region
    CreatedBy   = "terraform-iam"
  })
  
  # Policy ARNs for common AWS managed policies
  managed_policies = {
    read_only_access          = "arn:aws:iam::aws:policy/ReadOnlyAccess"
    power_user_access         = "arn:aws:iam::aws:policy/PowerUserAccess"
    administrator_access      = "arn:aws:iam::aws:policy/AdministratorAccess"
    billing_read_access       = "arn:aws:iam::aws:policy/job-function/Billing"
    support_user              = "arn:aws:iam::aws:policy/job-function/SupportUser"
    database_administrator    = "arn:aws:iam::aws:policy/job-function/DatabaseAdministrator"
    network_administrator     = "arn:aws:iam::aws:policy/job-function/NetworkAdministrator"
    security_audit            = "arn:aws:iam::aws:policy/SecurityAudit"
    systems_administrator     = "arn:aws:iam::aws:policy/job-function/SystemAdministrator"
  }
}

# Password Policy
resource "aws_iam_account_password_policy" "corporate_policy" {
  minimum_password_length        = var.password_policy.minimum_password_length
  require_lowercase_characters   = var.password_policy.require_lowercase_characters
  require_uppercase_characters   = var.password_policy.require_uppercase_characters
  require_numbers               = var.password_policy.require_numbers
  require_symbols               = var.password_policy.require_symbols
  allow_users_to_change_password = var.password_policy.allow_users_to_change_password
  max_password_age              = var.password_policy.max_password_age
  password_reuse_prevention     = var.password_policy.password_reuse_prevention

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-password-policy"
    Description = "Corporate password policy for all users"
  })
}

# OIDC Provider for GitHub Actions (if enabled)
resource "aws_iam_openid_connect_provider" "github_actions" {
  count = var.github_actions_role ? 1 : 0

  url = "https://token.actions.githubusercontent.com"
  client_id_list = [
    "sts.amazonaws.com"
  ]
  thumbprint_list = [
    "6938fd4d98bab03faadb97b34396831e3780aea1",
    "1c58a3a8518e8759bf075b76b750d4f2df264fcd"
  ]

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-github-oidc-provider"
    Description = "OIDC provider for GitHub Actions integration"
  })
}

# CloudTrail for IAM Event Logging (if enabled)
resource "aws_cloudtrail" "iam_events" {
  count = var.enable_cloudtrail ? 1 : 0

  name           = "${local.name_prefix}-iam-cloudtrail"
  s3_bucket_name = aws_s3_bucket.cloudtrail_logs[0].bucket

  event_selector {
    read_write_type                 = "All"
    include_management_events       = true
    exclude_management_event_sources = []

    data_resource {
      type   = "AWS::S3::Object"
      values = ["${aws_s3_bucket.cloudtrail_logs[0].arn}/*"]
    }
  }

  insight_selector {
    insight_type = "ApiCallRateInsight"
  }

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-iam-cloudtrail"
    Description = "CloudTrail for IAM event logging and compliance"
  })

  depends_on = [aws_s3_bucket_policy.cloudtrail_policy]
}

# S3 Bucket for CloudTrail Logs
resource "aws_s3_bucket" "cloudtrail_logs" {
  count = var.enable_cloudtrail ? 1 : 0

  bucket = "${local.name_prefix}-cloudtrail-logs"

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-cloudtrail-logs"
    Description = "S3 bucket for CloudTrail IAM event logs"
  })
}

resource "aws_s3_bucket_versioning" "cloudtrail_versioning" {
  count  = var.enable_cloudtrail ? 1 : 0
  bucket = aws_s3_bucket.cloudtrail_logs[0].id
  
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_encryption" "cloudtrail_encryption" {
  count  = var.enable_cloudtrail ? 1 : 0
  bucket = aws_s3_bucket.cloudtrail_logs[0].id

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

resource "aws_s3_bucket_public_access_block" "cloudtrail_pab" {
  count  = var.enable_cloudtrail ? 1 : 0
  bucket = aws_s3_bucket.cloudtrail_logs[0].id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# CloudTrail Bucket Policy
resource "aws_s3_bucket_policy" "cloudtrail_policy" {
  count  = var.enable_cloudtrail ? 1 : 0
  bucket = aws_s3_bucket.cloudtrail_logs[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AWSCloudTrailAclCheck"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "s3:GetBucketAcl"
        Resource = aws_s3_bucket.cloudtrail_logs[0].arn
        Condition = {
          StringEquals = {
            "AWS:SourceArn" = "arn:aws:cloudtrail:${local.region}:${local.account_id}:trail/${local.name_prefix}-iam-cloudtrail"
          }
        }
      },
      {
        Sid    = "AWSCloudTrailWrite"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "s3:PutObject"
        Resource = "${aws_s3_bucket.cloudtrail_logs[0].arn}/*"
        Condition = {
          StringEquals = {
            "s3:x-amz-acl" = "bucket-owner-full-control"
            "AWS:SourceArn" = "arn:aws:cloudtrail:${local.region}:${local.account_id}:trail/${local.name_prefix}-iam-cloudtrail"
          }
        }
      }
    ]
  })
}

# CloudWatch Log Group for IAM Events
resource "aws_cloudwatch_log_group" "iam_events" {
  count = var.enable_cloudtrail ? 1 : 0

  name              = "/aws/cloudtrail/${local.name_prefix}-iam-events"
  retention_in_days = var.cloudwatch_log_retention_days

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-iam-events-logs"
    Description = "CloudWatch logs for IAM events and compliance"
  })
}

# Cost Budget for IAM Resources (if enabled)
resource "aws_budgets_budget" "iam_costs" {
  count = var.enable_cost_allocation_tags ? 1 : 0

  name         = "${local.name_prefix}-iam-budget"
  budget_type  = "COST"
  limit_amount = var.budget_alert_threshold
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  cost_filters = {
    Service = ["AWS Identity and Access Management"]
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                 = 80
    threshold_type            = "PERCENTAGE"
    notification_type         = "ACTUAL"
    subscriber_email_addresses = []
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                 = 100
    threshold_type             = "PERCENTAGE"
    notification_type          = "FORECASTED"
    subscriber_email_addresses = []
  }

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-iam-budget"
    Description = "Cost budget monitoring for IAM resources"
  })
}

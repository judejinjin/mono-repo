# Permission Boundary Policies
# Policies that define maximum permissions for users and roles

# Developer Permission Boundary
resource "aws_iam_policy" "developer_boundary" {
  name        = "${local.name_prefix}-developer-boundary"
  path        = "/boundaries/"
  description = "Permission boundary for developers - defines maximum allowed permissions"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowedServices"
        Effect = "Allow"
        Action = [
          "eks:*",
          "lambda:*",
          "s3:*",
          "logs:*",
          "cloudwatch:*",
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret",
          "ssm:GetParameter",
          "ssm:GetParameters",
          "ssm:GetParametersByPath",
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "rds:DescribeDBInstances",
          "rds:DescribeDBClusters",
          "rds:CreateDBSnapshot",
          "rds-db:connect",
          "apigateway:GET",
          "apigateway:HEAD",
          "api:List*",
          "api:Get*"
        ]
        Resource = "*"
        Condition = {
          StringLike = {
            "aws:RequestedRegion" = local.region
          }
        }
      },
      {
        Sid    = "DenyHighRiskActions"
        Effect = "Deny"
        Action = [
          "iam:CreateRole",
          "iam:DeleteRole",
          "iam:CreateUser",
          "iam:DeleteUser",
          "iam:CreateGroup",
          "iam:DeleteGroup",
          "iam:AttachRolePolicy",
          "iam:DetachRolePolicy",
          "iam:AttachUserPolicy",
          "iam:DetachUserPolicy",
          "iam:AttachGroupPolicy",
          "iam:DetachGroupPolicy",
          "iam:PutRolePolicy",
          "iam:PutUserPolicy",
          "iam:PutGroupPolicy",
          "iam:DeleteRolePolicy",
          "iam:DeleteUserPolicy",
          "iam:DeleteGroupPolicy",
          "iam:CreateAccessKey",
          "iam:DeleteAccessKey",
          "iam:UpdateAccessKey"
        ]
        Resource = "*"
      },
      {
        Sid    = "DenyDestructiveActions"
        Effect = "Deny"
        Action = [
          "ec2:TerminateInstances",
          "eks:DeleteCluster",
          "rds:DeleteDBInstance",
          "rds:DeleteDBCluster",
          "s3:DeleteBucket",
          "lambda:DeleteFunction",
          "cloudformation:DeleteStack"
        ]
        Resource = "*"
      },
      {
        Sid    = "DenyBillingAccess"
        Effect = "Deny"
        Action = [
          "billing:*",
          "budgets:*",
          "ce:*",
          "cur:*",
          "aws-portal:*"
        ]
        Resource = "*"
      },
      {
        Sid    = "DenyOrganizationAccess"
        Effect = "Deny"
        Action = [
          "organizations:*",
          "account:*"
        ]
        Resource = "*"
      },
      {
        Sid    = "DenyProductionResources"
        Effect = "Deny"
        Action = "*"
        Resource = "*"
        Condition = {
          StringEquals = {
            "aws:ResourceTag/Environment" = "production"
          }
        }
      },
      {
        Sid    = "DenyProductionSecrets"
        Effect = "Deny"
        Action = [
          "secretsmanager:*"
        ]
        Resource = "*"
        Condition = {
          StringLike = {
            "secretsmanager:Name" = [
              "*-prod-*",
              "*-production-*",
              "*-admin-*",
              "*-root-*",
              "*-master-*"
            ]
          }
        }
      },
      {
        Sid    = "RestrictIPAccess"
        Effect = "Deny"
        Action = "*"
        Resource = "*"
        Condition = {
          Bool = {
            "aws:ViaAWSService" = "false"
          }
          IpAddressIfExists = {
            "aws:SourceIp" = var.office_ip_ranges
          }
        }
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-developer-boundary"
    Description = "Permission boundary for developers"
    PolicyType  = "boundary"
    UserType    = "developer"
  })
}

# Operations Permission Boundary
resource "aws_iam_policy" "operations_boundary" {
  name        = "${local.name_prefix}-operations-boundary"
  path        = "/boundaries/"
  description = "Permission boundary for operations team - defines maximum allowed permissions"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowedServices"
        Effect = "Allow"
        Action = [
          "ec2:*",
          "eks:*",
          "rds:*",
          "lambda:*",
          "s3:*",
          "logs:*",
          "cloudwatch:*",
          "events:*",
          "sns:*",
          "sqs:*",
          "secretsmanager:*",
          "ssm:*",
          "kms:*",
          "ecr:*",
          "elasticloadbalancing:*",
          "autoscaling:*",
          "application-autoscaling:*",
          "route53:*",
          "acm:*",
          "backup:*",
          "cloudformation:*",
          "codebuild:*",
          "codepipeline:*",
          "codedeploy:*",
          "config:*",
          "cloudtrail:*",
          "guardduty:*",
          "inspector:*",
          "securityhub:*",
          "wafv2:*",
          "shield:*"
        ]
        Resource = "*"
        Condition = {
          StringLike = {
            "aws:RequestedRegion" = local.region
          }
        }
      },
      {
        Sid    = "LimitedIAMAccess"
        Effect = "Allow"
        Action = [
          "iam:GetRole",
          "iam:GetPolicy",
          "iam:GetUser",
          "iam:GetGroup",
          "iam:ListRoles",
          "iam:ListPolicies",
          "iam:ListUsers",
          "iam:ListGroups",
          "iam:ListInstanceProfiles",
          "iam:PassRole",
          "iam:TagRole",
          "iam:UntagRole",
          "iam:CreateServiceLinkedRole"
        ]
        Resource = "*"
      },
      {
        Sid    = "DenyAdminIAMActions"
        Effect = "Deny"
        Action = [
          "iam:CreateRole",
          "iam:DeleteRole",
          "iam:CreateUser",
          "iam:DeleteUser",
          "iam:CreateGroup",
          "iam:DeleteGroup",
          "iam:AttachRolePolicy",
          "iam:DetachRolePolicy",
          "iam:AttachUserPolicy",
          "iam:DetachUserPolicy",
          "iam:AttachGroupPolicy",
          "iam:DetachGroupPolicy",
          "iam:PutRolePolicy",
          "iam:PutUserPolicy",
          "iam:PutGroupPolicy",
          "iam:DeleteRolePolicy",
          "iam:DeleteUserPolicy",
          "iam:DeleteGroupPolicy"
        ]
        Resource = [
          "arn:aws:iam::${local.account_id}:role/*-admin*",
          "arn:aws:iam::${local.account_id}:user/*-admin*",
          "arn:aws:iam::${local.account_id}:group/*-admin*"
        ]
      },
      {
        Sid    = "DenyBillingAccess"
        Effect = "Deny"
        Action = [
          "billing:*",
          "budgets:*",
          "ce:*",
          "cur:*",
          "aws-portal:*"
        ]
        Resource = "*"
      },
      {
        Sid    = "DenyOrganizationAccess"
        Effect = "Deny"
        Action = [
          "organizations:*",
          "account:*"
        ]
        Resource = "*"
      },
      {
        Sid    = "RequireMFAForSensitiveActions"
        Effect = "Deny"
        Action = [
          "ec2:TerminateInstances",
          "rds:DeleteDBInstance",
          "rds:DeleteDBCluster",
          "s3:DeleteBucket",
          "lambda:DeleteFunction",
          "eks:DeleteCluster"
        ]
        Resource = "*"
        Condition = {
          BoolIfExists = {
            "aws:MultiFactorAuthPresent" = "false"
          }
        }
      },
      {
        Sid    = "RestrictIPAccess"
        Effect = "Deny"
        Action = "*"
        Resource = "*"
        Condition = {
          Bool = {
            "aws:ViaAWSService" = "false"
          }
          IpAddressIfExists = {
            "aws:SourceIp" = concat(var.office_ip_ranges, var.bamboo_server_ips)
          }
        }
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-operations-boundary"
    Description = "Permission boundary for operations team"
    PolicyType  = "boundary"
    UserType    = "operations"
  })
}

# Security Team Permission Boundary
resource "aws_iam_policy" "security_boundary" {
  name        = "${local.name_prefix}-security-boundary"
  path        = "/boundaries/"
  description = "Permission boundary for security team - defines maximum allowed permissions"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowAllSecurityServices"
        Effect = "Allow"
        Action = [
          "iam:*",
          "kms:*",
          "secretsmanager:*",
          "ssm:*",
          "guardduty:*",
          "inspector:*",
          "securityhub:*",
          "config:*",
          "cloudtrail:*",
          "wafv2:*",
          "shield:*",
          "macie:*",
          "access-analyzer:*",
          "detective:*",
          "fms:*"
        ]
        Resource = "*"
      },
      {
        Sid    = "AllowReadOnlyAccess"
        Effect = "Allow"
        Action = [
          "ec2:Describe*",
          "eks:Describe*",
          "eks:List*",
          "rds:Describe*",
          "s3:Get*",
          "s3:List*",
          "lambda:Get*",
          "lambda:List*",
          "logs:Describe*",
          "logs:Get*",
          "cloudwatch:Get*",
          "cloudwatch:List*",
          "events:List*",
          "events:Describe*",
          "autoscaling:Describe*",
          "elasticloadbalancing:Describe*"
        ]
        Resource = "*"
      },
      {
        Sid    = "DenyBillingAccess"
        Effect = "Deny"
        Action = [
          "billing:*",
          "budgets:*",
          "ce:*",
          "cur:*",
          "aws-portal:*"
        ]
        Resource = "*"
      },
      {
        Sid    = "DenyOrganizationManagement"
        Effect = "Deny"
        Action = [
          "organizations:CreateAccount",
          "organizations:CloseAccount",
          "organizations:CreateOrganization",
          "organizations:DeleteOrganization"
        ]
        Resource = "*"
      },
      {
        Sid    = "RequireMFAForDestructiveActions"
        Effect = "Deny"
        Action = [
          "iam:DeleteRole",
          "iam:DeleteUser",
          "iam:DeleteGroup",
          "iam:DeletePolicy",
          "kms:DeleteKey",
          "kms:DisableKey",
          "secretsmanager:DeleteSecret"
        ]
        Resource = "*"
        Condition = {
          BoolIfExists = {
            "aws:MultiFactorAuthPresent" = "false"
          }
        }
      },
      {
        Sid    = "RestrictIPAccess"
        Effect = "Deny"
        Action = "*"
        Resource = "*"
        Condition = {
          Bool = {
            "aws:ViaAWSService" = "false"
          }
          IpAddressIfExists = {
            "aws:SourceIp" = var.office_ip_ranges
          }
        }
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-security-boundary"
    Description = "Permission boundary for security team"
    PolicyType  = "boundary"
    UserType    = "security"
  })
}

# Business Users Permission Boundary
resource "aws_iam_policy" "business_boundary" {
  name        = "${local.name_prefix}-business-boundary"
  path        = "/boundaries/"
  description = "Permission boundary for business users - defines maximum allowed permissions"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowReadOnlyAccess"
        Effect = "Allow"
        Action = [
          "cloudwatch:GetMetricStatistics",
          "cloudwatch:ListMetrics",
          "cloudwatch:GetDashboard",
          "cloudwatch:ListDashboards",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams",
          "logs:GetLogEvents",
          "s3:GetObject",
          "s3:ListBucket",
          "lambda:GetFunction",
          "lambda:ListFunctions",
          "apigateway:GET"
        ]
        Resource = "*"
        Condition = {
          StringLike = {
            "aws:ResourceTag/AccessLevel" = ["business", "public"]
          }
        }
      },
      {
        Sid    = "AllowBillingReadAccess"
        Effect = "Allow"
        Action = [
          "ce:GetCostAndUsage",
          "ce:GetUsageReport",
          "ce:ListCostCategoryDefinitions",
          "budgets:ViewBudget"
        ]
        Resource = "*"
      },
      {
        Sid    = "DenyAllWriteActions"
        Effect = "Deny"
        Action = [
          "iam:*",
          "ec2:*",
          "eks:*",
          "rds:*",
          "lambda:*",
          "s3:Put*",
          "s3:Delete*",
          "kms:*",
          "secretsmanager:*",
          "ssm:Put*",
          "ssm:Delete*"
        ]
        Resource = "*"
      },
      {
        Sid    = "DenySecurityServices"
        Effect = "Deny"
        Action = [
          "guardduty:*",
          "inspector:*",
          "securityhub:*",
          "config:*",
          "cloudtrail:*",
          "wafv2:*",
          "shield:*"
        ]
        Resource = "*"
      },
      {
        Sid    = "RestrictIPAccess"
        Effect = "Deny"
        Action = "*"
        Resource = "*"
        Condition = {
          Bool = {
            "aws:ViaAWSService" = "false"
          }
          IpAddressIfExists = {
            "aws:SourceIp" = var.office_ip_ranges
          }
        }
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-business-boundary"
    Description = "Permission boundary for business users"
    PolicyType  = "boundary"
    UserType    = "business"
  })
}

# Service Account Permission Boundary
resource "aws_iam_policy" "service_account_boundary" {
  name        = "${local.name_prefix}-service-account-boundary"
  path        = "/boundaries/"
  description = "Permission boundary for service accounts - defines maximum allowed permissions"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowServiceSpecificActions"
        Effect = "Allow"
        Action = [
          "eks:DescribeCluster",
          "eks:ListClusters",
          "lambda:InvokeFunction",
          "lambda:GetFunction",
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket",
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams",
          "cloudwatch:PutMetricData",
          "cloudwatch:GetMetricStatistics",
          "secretsmanager:GetSecretValue",
          "ssm:GetParameter",
          "ssm:GetParameters",
          "ssm:GetParametersByPath",
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload"
        ]
        Resource = "*"
        Condition = {
          StringLike = {
            "aws:RequestedRegion" = local.region
          }
        }
      },
      {
        Sid    = "DenyIAMActions"
        Effect = "Deny"
        Action = [
          "iam:*"
        ]
        Resource = "*"
      },
      {
        Sid    = "DenyDestructiveActions"
        Effect = "Deny"
        Action = [
          "ec2:TerminateInstances",
          "eks:DeleteCluster",
          "rds:DeleteDBInstance",
          "s3:DeleteBucket",
          "lambda:DeleteFunction",
          "kms:DeleteKey",
          "secretsmanager:DeleteSecret"
        ]
        Resource = "*"
      },
      {
        Sid    = "DenyBillingAccess"
        Effect = "Deny"
        Action = [
          "billing:*",
          "budgets:*",
          "ce:*",
          "cur:*",
          "aws-portal:*",
          "organizations:*",
          "account:*"
        ]
        Resource = "*"
      },
      {
        Sid    = "RestrictToProjectResources"
        Effect = "Deny"
        Action = "*"
        Resource = "*"
        Condition = {
          StringNotEquals = {
            "aws:ResourceTag/Project" = var.project_name
          }
          "ForAllValues:StringNotLike" = {
            "aws:ResourceTag/Project" = var.project_name
          }
        }
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-service-account-boundary"
    Description = "Permission boundary for service accounts"
    PolicyType  = "boundary"
    UserType    = "service-account"
  })
}

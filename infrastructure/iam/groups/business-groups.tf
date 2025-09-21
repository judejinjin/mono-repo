# Business and Administrative Groups
# Groups for business users, security teams, and general administrative access

# Security Group
resource "aws_iam_group" "security" {
  name = "${local.name_prefix}-security"
  path = "/security/"
}

# Security Group Membership (Admin users with security role)
resource "aws_iam_group_membership" "security" {
  name = "${local.name_prefix}-security-membership"
  
  users = [
    for user in var.admin_users : aws_iam_user.admins[user.name].name
    if user.role == "security-admin"
  ]
  
  group = aws_iam_group.security.name
  
  depends_on = [aws_iam_user.admins]
}

# Security Base Permissions
resource "aws_iam_group_policy" "security_base" {
  name  = "${local.name_prefix}-security-base-policy"
  group = aws_iam_group.security.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "iam:Get*",
          "iam:List*",
          "iam:GenerateCredentialReport",
          "iam:GetCredentialReport",
          "iam:GetAccountSummary"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "cloudtrail:*",
          "config:*",
          "guardduty:*",
          "inspector:*",
          "securityhub:*",
          "access-analyzer:*"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "kms:*"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:*"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "wafv2:*",
          "shield:*",
          "macie:*"
        ]
        Resource = "*"
      }
    ]
  })
}

# Business Group
resource "aws_iam_group" "business" {
  name = "${local.name_prefix}-business"
  path = "/business/"
}

# Business Group Policy (Read-Only Access)
resource "aws_iam_group_policy" "business_base" {
  name  = "${local.name_prefix}-business-base-policy"
  group = aws_iam_group.business.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:GetMetricStatistics",
          "cloudwatch:ListMetrics",
          "cloudwatch:GetDashboard",
          "cloudwatch:ListDashboards"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams",
          "logs:GetLogEvents"
        ]
        Resource = "arn:aws:logs:${local.region}:${local.account_id}:log-group:/aws/eks/${var.eks_cluster_name}/business/*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${local.name_prefix}-assets/reports/*",
          "arn:aws:s3:::${local.name_prefix}-assets/dashboards/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "ce:GetCostAndUsage",
          "ce:GetUsageReport",
          "ce:ListCostCategoryDefinitions",
          "ce:GetBudget"
        ]
        Resource = "*"
      }
    ]
  })
}

# QA Group
resource "aws_iam_group" "qa" {
  name = "${local.name_prefix}-qa"
  path = "/qa/"
}

# QA Group Policy
resource "aws_iam_group_policy" "qa_base" {
  name  = "${local.name_prefix}-qa-base-policy"
  group = aws_iam_group.qa.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "eks:DescribeCluster",
          "eks:ListClusters"
        ]
        Resource = "arn:aws:eks:${local.region}:${local.account_id}:cluster/${var.eks_cluster_name}"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${local.name_prefix}-assets/test/*",
          "arn:aws:s3:::${local.name_prefix}-assets/qa/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction",
          "lambda:GetFunction"
        ]
        Resource = [
          for func in var.lambda_functions : "arn:aws:lambda:${local.region}:${local.account_id}:function:${local.name_prefix}-${func}"
        ]
        Condition = {
          StringLike = {
            "lambda:FunctionName" = [
              "*-test-*",
              "*-qa-*",
              "*-staging-*"
            ]
          }
        }
      },
      {
        Effect = "Allow"
        Action = [
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams",
          "logs:GetLogEvents",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = [
          "arn:aws:logs:${local.region}:${local.account_id}:log-group:/aws/eks/${var.eks_cluster_name}/qa/*",
          "arn:aws:logs:${local.region}:${local.account_id}:log-group:/aws/lambda/${local.name_prefix}-*-test*",
          "arn:aws:logs:${local.region}:${local.account_id}:log-group:/aws/lambda/${local.name_prefix}-*-qa*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          "arn:aws:secretsmanager:${local.region}:${local.account_id}:secret:${local.name_prefix}-test-*",
          "arn:aws:secretsmanager:${local.region}:${local.account_id}:secret:${local.name_prefix}-qa-*"
        ]
      }
    ]
  })
}

# Admins Group (Super Admins)
resource "aws_iam_group" "admins" {
  name = "${local.name_prefix}-admins"
  path = "/administrators/"
}

# Admin Group Membership
resource "aws_iam_group_membership" "admins" {
  name = "${local.name_prefix}-admins-membership"
  
  users = [
    for user in var.admin_users : aws_iam_user.admins[user.name].name
    if user.role == "super-admin" || user.role == "platform-admin"
  ]
  
  group = aws_iam_group.admins.name
  
  depends_on = [aws_iam_user.admins]
}

# Admin Group Policy (High Privileges)
resource "aws_iam_group_policy" "admins_base" {
  name  = "${local.name_prefix}-admins-base-policy"
  group = aws_iam_group.admins.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "iam:*"
        ]
        Resource = "*"
        Condition = {
          Bool = {
            "aws:MultiFactorAuthPresent" = "true"
          }
        }
      },
      {
        Effect = "Allow"
        Action = [
          "sts:AssumeRole"
        ]
        Resource = [
          aws_iam_role.super_admin_role.arn,
          aws_iam_role.platform_admin_role.arn,
          aws_iam_role.emergency_access_role.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "organizations:*",
          "account:*",
          "billing:*",
          "budgets:*",
          "ce:*"
        ]
        Resource = "*"
      }
    ]
  })
}

# Billing Group
resource "aws_iam_group" "billing" {
  name = "${local.name_prefix}-billing"
  path = "/billing/"
}

# Billing Group Policy
resource "aws_iam_group_policy" "billing_base" {
  name  = "${local.name_prefix}-billing-base-policy"
  group = aws_iam_group.billing.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "billing:*",
          "ce:*",
          "budgets:*",
          "cur:*",
          "aws-portal:*"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${local.name_prefix}-billing-reports",
          "arn:aws:s3:::${local.name_prefix}-billing-reports/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "organizations:ListAccounts",
          "organizations:DescribeOrganization",
          "organizations:ListOrganizationalUnitsForParent",
          "organizations:ListRoots"
        ]
        Resource = "*"
      }
    ]
  })
}

# Support Group
resource "aws_iam_group" "support" {
  name = "${local.name_prefix}-support"
  path = "/support/"
}

# Support Group Policy
resource "aws_iam_group_policy" "support_base" {
  name  = "${local.name_prefix}-support-base-policy"
  group = aws_iam_group.support.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "support:*"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "trustedadvisor:Describe*",
          "trustedadvisor:DownloadRisk"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "health:Describe*",
          "health:Get*",
          "health:List*"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:GetMetricStatistics",
          "cloudwatch:ListMetrics",
          "logs:DescribeLogGroups",
          "logs:GetLogEvents"
        ]
        Resource = "*"
      }
    ]
  })
}

# Compliance Group
resource "aws_iam_group" "compliance" {
  name = "${local.name_prefix}-compliance"
  path = "/compliance/"
}

# Compliance Group Policy
resource "aws_iam_group_policy" "compliance_base" {
  name  = "${local.name_prefix}-compliance-base-policy"
  group = aws_iam_group.compliance.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "config:*",
          "cloudtrail:LookupEvents",
          "cloudtrail:GetTrailStatus",
          "cloudtrail:DescribeTrails"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "iam:GenerateCredentialReport",
          "iam:GetCredentialReport",
          "iam:Get*",
          "iam:List*"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "securityhub:*",
          "inspector:*",
          "guardduty:Get*",
          "guardduty:List*"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${local.name_prefix}-compliance-reports",
          "arn:aws:s3:::${local.name_prefix}-compliance-reports/*",
          "arn:aws:s3:::${local.name_prefix}-audit-logs",
          "arn:aws:s3:::${local.name_prefix}-audit-logs/*"
        ]
      }
    ]
  })
}

# External Auditors Group (Temporary Access)
resource "aws_iam_group" "external_auditors" {
  name = "${local.name_prefix}-external-auditors"
  path = "/auditors/"
}

# External Auditors Policy (Read-Only)
resource "aws_iam_group_policy" "external_auditors_base" {
  name  = "${local.name_prefix}-external-auditors-policy"
  group = aws_iam_group.external_auditors.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "iam:Get*",
          "iam:List*",
          "iam:GenerateCredentialReport",
          "iam:GetCredentialReport"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "config:Get*",
          "config:List*",
          "config:Describe*"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "cloudtrail:LookupEvents",
          "cloudtrail:GetTrailStatus",
          "cloudtrail:DescribeTrails"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${local.name_prefix}-audit-logs",
          "arn:aws:s3:::${local.name_prefix}-audit-logs/*",
          "arn:aws:s3:::${local.name_prefix}-compliance-reports",
          "arn:aws:s3:::${local.name_prefix}-compliance-reports/*"
        ]
      },
      {
        Effect = "Deny"
        Action = [
          "iam:Create*",
          "iam:Delete*",
          "iam:Update*",
          "iam:Put*",
          "iam:Attach*",
          "iam:Detach*"
        ]
        Resource = "*"
      }
    ]
  })
}

# Managed Policy Attachments for Business Groups
resource "aws_iam_group_policy_attachment" "security_audit" {
  group      = aws_iam_group.security.name
  policy_arn = local.managed_policies.security_audit
}

resource "aws_iam_group_policy_attachment" "business_read_only" {
  group      = aws_iam_group.business.name
  policy_arn = local.managed_policies.read_only_access
}

resource "aws_iam_group_policy_attachment" "billing_access" {
  group      = aws_iam_group.billing.name
  policy_arn = local.managed_policies.billing_read_access
}

resource "aws_iam_group_policy_attachment" "support_access" {
  group      = aws_iam_group.support.name
  policy_arn = local.managed_policies.support_user
}

resource "aws_iam_group_policy_attachment" "external_auditors_read_only" {
  group      = aws_iam_group.external_auditors.name
  policy_arn = local.managed_policies.read_only_access
}

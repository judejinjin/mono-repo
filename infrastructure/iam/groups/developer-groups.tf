# Developer Groups
# Groups for organizing developer access and permissions

# Developers Group
resource "aws_iam_group" "developers" {
  name = "${local.name_prefix}-developers"
  path = "/developers/"
}

# Developer Group Membership
resource "aws_iam_group_membership" "developers" {
  name = "${local.name_prefix}-developers-membership"
  
  users = [
    for user in var.developer_users : aws_iam_user.developers[user.name].name
  ]
  
  group = aws_iam_group.developers.name
  
  depends_on = [aws_iam_user.developers]
}

# Base Developer Permissions
resource "aws_iam_group_policy" "developers_base" {
  name  = "${local.name_prefix}-developers-base-policy"
  group = aws_iam_group.developers.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "iam:GetUser",
          "iam:GetRole",
          "iam:ListRoles",
          "iam:GetPolicy",
          "iam:ListPolicies",
          "iam:GetAccountSummary"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "iam:ChangePassword",
          "iam:GetLoginProfile",
          "iam:UpdateLoginProfile",
          "iam:CreateAccessKey",
          "iam:DeleteAccessKey",
          "iam:GetAccessKeyLastUsed",
          "iam:ListAccessKeys",
          "iam:UpdateAccessKey"
        ]
        Resource = "arn:aws:iam::${local.account_id}:user/$${aws:username}"
      },
      {
        Effect = "Allow"
        Action = [
          "iam:CreateVirtualMFADevice",
          "iam:EnableMFADevice",
          "iam:ResyncMFADevice",
          "iam:ListMFADevices",
          "iam:DeactivateMFADevice",
          "iam:DeleteVirtualMFADevice"
        ]
        Resource = [
          "arn:aws:iam::${local.account_id}:mfa/$${aws:username}",
          "arn:aws:iam::${local.account_id}:user/$${aws:username}"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          "arn:aws:secretsmanager:${local.region}:${local.account_id}:secret:${local.name_prefix}-dev-*"
        ]
        Condition = {
          StringEquals = {
            "secretsmanager:ResourceTag/UserType" = "developer"
          }
        }
      }
    ]
  })
}

# Developer EKS Access Policy
resource "aws_iam_group_policy" "developers_eks" {
  name  = "${local.name_prefix}-developers-eks-policy"
  group = aws_iam_group.developers.name

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
          "eks:DescribeAddon",
          "eks:ListAddons",
          "eks:DescribeNodegroup",
          "eks:ListNodegroups"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "eks:cluster-name" = var.eks_cluster_name
          }
        }
      }
    ]
  })
}

# Junior Developers Subgroup
resource "aws_iam_group" "junior_developers" {
  name = "${local.name_prefix}-junior-developers"
  path = "/developers/junior/"
}

resource "aws_iam_group_membership" "junior_developers" {
  name = "${local.name_prefix}-junior-developers-membership"
  
  users = [
    for user in var.developer_users : aws_iam_user.developers[user.name].name
    if user.team == "junior" || user.team == "intern"
  ]
  
  group = aws_iam_group.junior_developers.name
  
  depends_on = [aws_iam_user.developers]
}

resource "aws_iam_group_policy" "junior_developers_policy" {
  name  = "${local.name_prefix}-junior-developers-policy"
  group = aws_iam_group.junior_developers.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${local.name_prefix}-assets",
          "arn:aws:s3:::${local.name_prefix}-assets/dev/*",
          "arn:aws:s3:::${local.name_prefix}-assets/shared/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams",
          "logs:GetLogEvents"
        ]
        Resource = "arn:aws:logs:${local.region}:${local.account_id}:log-group:/aws/eks/${var.eks_cluster_name}/dev/*"
      },
      {
        Effect = "Deny"
        Action = [
          "iam:*",
          "ec2:TerminateInstances",
          "eks:DeleteCluster",
          "rds:DeleteDBInstance",
          "s3:DeleteBucket",
          "lambda:DeleteFunction"
        ]
        Resource = "*"
      }
    ]
  })
}

# Senior Developers Subgroup
resource "aws_iam_group" "senior_developers" {
  name = "${local.name_prefix}-senior-developers"
  path = "/developers/senior/"
}

resource "aws_iam_group_membership" "senior_developers" {
  name = "${local.name_prefix}-senior-developers-membership"
  
  users = [
    for user in var.developer_users : aws_iam_user.developers[user.name].name
    if user.team == "senior" || user.team == "lead"
  ]
  
  group = aws_iam_group.senior_developers.name
  
  depends_on = [aws_iam_user.developers]
}

resource "aws_iam_group_policy" "senior_developers_policy" {
  name  = "${local.name_prefix}-senior-developers-policy"
  group = aws_iam_group.senior_developers.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          for bucket in var.s3_buckets : "arn:aws:s3:::${bucket}"
          if bucket != "${local.name_prefix}-backups" # Exclude production backups
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = [
          for bucket in var.s3_buckets : "arn:aws:s3:::${bucket}/*"
          if bucket != "${local.name_prefix}-backups"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction",
          "lambda:GetFunction",
          "lambda:UpdateFunctionCode",
          "lambda:UpdateFunctionConfiguration"
        ]
        Resource = [
          for func in var.lambda_functions : "arn:aws:lambda:${local.region}:${local.account_id}:function:${local.name_prefix}-${func}"
        ]
        Condition = {
          StringNotEquals = {
            "lambda:FunctionName" = "${local.name_prefix}-backup-scheduler"
          }
        }
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams",
          "logs:GetLogEvents"
        ]
        Resource = "arn:aws:logs:${local.region}:${local.account_id}:log-group:/aws/eks/${var.eks_cluster_name}/*"
      }
    ]
  })
}

# Team Leads Subgroup
resource "aws_iam_group" "team_leads" {
  name = "${local.name_prefix}-team-leads"
  path = "/developers/leads/"
}

resource "aws_iam_group_membership" "team_leads" {
  name = "${local.name_prefix}-team-leads-membership"
  
  users = [
    for user in var.developer_users : aws_iam_user.developers[user.name].name
    if user.team == "lead" || user.team == "architect"
  ]
  
  group = aws_iam_group.team_leads.name
  
  depends_on = [aws_iam_user.developers]
}

resource "aws_iam_group_policy_attachment" "team_leads_power_user" {
  group      = aws_iam_group.team_leads.name
  policy_arn = local.managed_policies.power_user_access
}

# Frontend Developers Subgroup
resource "aws_iam_group" "frontend_developers" {
  name = "${local.name_prefix}-frontend-developers"
  path = "/developers/frontend/"
}

resource "aws_iam_group_membership" "frontend_developers" {
  name = "${local.name_prefix}-frontend-developers-membership"
  
  users = [
    for user in var.developer_users : aws_iam_user.developers[user.name].name
    if contains(["frontend", "ui", "ux"], user.team)
  ]
  
  group = aws_iam_group.frontend_developers.name
  
  depends_on = [aws_iam_user.developers]
}

resource "aws_iam_group_policy" "frontend_developers_policy" {
  name  = "${local.name_prefix}-frontend-developers-policy"
  group = aws_iam_group.frontend_developers.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${local.name_prefix}-assets",
          "arn:aws:s3:::${local.name_prefix}-assets/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "cloudfront:CreateInvalidation",
          "cloudfront:GetInvalidation",
          "cloudfront:ListInvalidations"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "apigateway:GET",
          "apigateway:HEAD",
          "apigateway:OPTIONS"
        ]
        Resource = "arn:aws:apigateway:${local.region}::/restapis/*"
      }
    ]
  })
}

# Backend Developers Subgroup
resource "aws_iam_group" "backend_developers" {
  name = "${local.name_prefix}-backend-developers"
  path = "/developers/backend/"
}

resource "aws_iam_group_membership" "backend_developers" {
  name = "${local.name_prefix}-backend-developers-membership"
  
  users = [
    for user in var.developer_users : aws_iam_user.developers[user.name].name
    if contains(["backend", "api", "microservices"], user.team)
  ]
  
  group = aws_iam_group.backend_developers.name
  
  depends_on = [aws_iam_user.developers]
}

resource "aws_iam_group_policy" "backend_developers_policy" {
  name  = "${local.name_prefix}-backend-developers-policy"
  group = aws_iam_group.backend_developers.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "rds:DescribeDBInstances",
          "rds:DescribeDBClusters",
          "rds:CreateDBSnapshot"
        ]
        Resource = "arn:aws:rds:${local.region}:${local.account_id}:db:${var.rds_instance_identifier}"
      },
      {
        Effect = "Allow"
        Action = [
          "lambda:*"
        ]
        Resource = [
          for func in var.lambda_functions : "arn:aws:lambda:${local.region}:${local.account_id}:function:${local.name_prefix}-${func}"
        ]
        Condition = {
          StringNotEquals = {
            "lambda:FunctionName" = "${local.name_prefix}-backup-scheduler"
          }
        }
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          "arn:aws:secretsmanager:${local.region}:${local.account_id}:secret:${local.name_prefix}-api-*",
          "arn:aws:secretsmanager:${local.region}:${local.account_id}:secret:${local.name_prefix}-db-*"
        ]
        Condition = {
          StringNotLike = {
            "secretsmanager:Name" = [
              "*-prod-*",
              "*-production-*"
            ]
          }
        }
      }
    ]
  })
}

# Permission Boundaries for Developer Groups
resource "aws_iam_group_policy_attachment" "developers_boundary" {
  group      = aws_iam_group.developers.name
  policy_arn = aws_iam_policy.developer_boundary.arn
}

resource "aws_iam_group_policy_attachment" "junior_developers_boundary" {
  group      = aws_iam_group.junior_developers.name
  policy_arn = aws_iam_policy.developer_boundary.arn
}

resource "aws_iam_group_policy_attachment" "senior_developers_boundary" {
  group      = aws_iam_group.senior_developers.name
  policy_arn = aws_iam_policy.developer_boundary.arn
}

resource "aws_iam_group_policy_attachment" "team_leads_boundary" {
  group      = aws_iam_group.team_leads.name
  policy_arn = aws_iam_policy.developer_boundary.arn
}

resource "aws_iam_group_policy_attachment" "frontend_developers_boundary" {
  group      = aws_iam_group.frontend_developers.name
  policy_arn = aws_iam_policy.developer_boundary.arn
}

resource "aws_iam_group_policy_attachment" "backend_developers_boundary" {
  group      = aws_iam_group.backend_developers.name
  policy_arn = aws_iam_policy.developer_boundary.arn
}

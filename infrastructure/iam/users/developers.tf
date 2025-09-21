# Developer User Accounts
# Individual developer user accounts with appropriate permissions

# Developer Users
resource "aws_iam_user" "developers" {
  for_each = {
    for user in var.developer_users : user.name => user
  }
  
  name          = "${local.name_prefix}-dev-${each.value.name}"
  path          = "/developers/"
  force_destroy = false

  tags = merge(local.common_tags, {
    Name       = "${local.name_prefix}-dev-${each.value.name}"
    Email      = each.value.email
    Team       = each.value.team
    UserType   = "developer"
    Department = "engineering"
  })
}

# Developer User Login Profiles (Console Access)
resource "aws_iam_user_login_profile" "developers" {
  for_each = {
    for user in var.developer_users : user.name => user
  }
  
  user                    = aws_iam_user.developers[each.key].name
  password_reset_required = true
  password_length         = var.password_policy.minimum_password_length

  lifecycle {
    ignore_changes = [password_reset_required]
  }
}

# Developer Access Keys (Programmatic Access)
resource "aws_iam_access_key" "developers" {
  for_each = {
    for user in var.developer_users : user.name => user
  }
  
  user = aws_iam_user.developers[each.key].name
  
  depends_on = [aws_iam_user.developers]
}

# Store Developer Access Keys in Secrets Manager
resource "aws_secretsmanager_secret" "developer_access_keys" {
  for_each = {
    for user in var.developer_users : user.name => user
  }
  
  name        = "${local.name_prefix}-dev-${each.key}-access-key"
  description = "Access key for developer ${each.key}"
  
  tags = merge(local.common_tags, {
    Name     = "${local.name_prefix}-dev-${each.key}-access-key"
    UserType = "developer"
    User     = each.key
  })
}

resource "aws_secretsmanager_secret_version" "developer_access_keys" {
  for_each = {
    for user in var.developer_users : user.name => user
  }
  
  secret_id = aws_secretsmanager_secret.developer_access_keys[each.key].id
  secret_string = jsonencode({
    access_key_id     = aws_iam_access_key.developers[each.key].id
    secret_access_key = aws_iam_access_key.developers[each.key].secret
    user_name         = aws_iam_user.developers[each.key].name
    email             = each.value.email
    team              = each.value.team
  })
}

# Developer MFA Devices (Virtual MFA)
resource "aws_iam_virtual_mfa_device" "developers" {
  for_each = var.mfa_required ? {
    for user in var.developer_users : user.name => user
  } : {}
  
  virtual_mfa_device_name = "${local.name_prefix}-dev-${each.key}-mfa"
  path                    = "/developers/"

  tags = merge(local.common_tags, {
    Name     = "${local.name_prefix}-dev-${each.key}-mfa"
    UserType = "developer"
    User     = each.key
  })
}

# Junior Developer Role (Limited Permissions)
resource "aws_iam_role" "junior_developer_role" {
  name = "${local.name_prefix}-junior-developer-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          AWS = [
            for user in var.developer_users : aws_iam_user.developers[user.name].arn
            if user.team == "junior" || user.team == "intern"
          ]
        }
        Condition = {
          Bool = {
            "aws:MultiFactorAuthPresent" = var.mfa_required ? "true" : "false"
          }
          IpAddress = {
            "aws:SourceIp" = var.office_ip_ranges
          }
          NumericLessThan = {
            "aws:TokenIssueTime" = "300"  # Token must be issued within last 5 minutes
          }
        }
      }
    ]
  })

  max_session_duration = 3600  # 1 hour

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-junior-developer-role"
    Description = "Limited access role for junior developers and interns"
    AccessLevel = "junior"
    UserType    = "developer"
  })
}

# Junior Developer Policy
resource "aws_iam_role_policy" "junior_developer_policy" {
  name = "${local.name_prefix}-junior-developer-policy"
  role = aws_iam_role.junior_developer_role.id

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
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams",
          "logs:GetLogEvents"
        ]
        Resource = "arn:aws:logs:${local.region}:${local.account_id}:log-group:/aws/eks/${var.eks_cluster_name}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:GetMetricStatistics",
          "cloudwatch:ListMetrics"
        ]
        Resource = "*"
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

# Senior Developer Role (Extended Permissions)
resource "aws_iam_role" "senior_developer_role" {
  name = "${local.name_prefix}-senior-developer-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          AWS = [
            for user in var.developer_users : aws_iam_user.developers[user.name].arn
            if user.team == "senior" || user.team == "lead"
          ]
        }
        Condition = {
          Bool = {
            "aws:MultiFactorAuthPresent" = var.mfa_required ? "true" : "false"
          }
          IpAddress = {
            "aws:SourceIp" = var.office_ip_ranges
          }
        }
      }
    ]
  })

  max_session_duration = var.session_duration

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-senior-developer-role"
    Description = "Extended access role for senior developers and team leads"
    AccessLevel = "senior"
    UserType    = "developer"
  })
}

# Senior Developer Policy
resource "aws_iam_role_policy" "senior_developer_policy" {
  name = "${local.name_prefix}-senior-developer-policy"
  role = aws_iam_role.senior_developer_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "eks:*"
        ]
        Resource = "arn:aws:eks:${local.region}:${local.account_id}:cluster/${var.eks_cluster_name}"
      },
      {
        Effect = "Allow"
        Action = [
          "eks:DescribeNodegroup",
          "eks:ListNodegroups",
          "eks:UpdateNodegroupConfig",
          "eks:UpdateNodegroupVersion"
        ]
        Resource = "arn:aws:eks:${local.region}:${local.account_id}:nodegroup/${var.eks_cluster_name}/*/*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:*"
        ]
        Resource = [
          for bucket in var.s3_buckets : "arn:aws:s3:::${bucket}"
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
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "lambda:*"
        ]
        Resource = [
          for func in var.lambda_functions : "arn:aws:lambda:${local.region}:${local.account_id}:function:${local.name_prefix}-${func}"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          "arn:aws:secretsmanager:${local.region}:${local.account_id}:secret:${local.name_prefix}-*"
        ]
        Condition = {
          StringNotLike = {
            "secretsmanager:Name" = [
              "*-admin-*",
              "*-root-*",
              "*-master-*"
            ]
          }
        }
      },
      {
        Effect = "Allow"
        Action = [
          "rds:DescribeDBInstances",
          "rds:DescribeDBClusters",
          "rds:CreateDBSnapshot",
          "rds:DescribeDBSnapshots"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:*",
          "logs:*"
        ]
        Resource = "*"
      },
      {
        Effect = "Deny"
        Action = [
          "iam:CreateRole",
          "iam:DeleteRole",
          "iam:CreateUser",
          "iam:DeleteUser",
          "iam:AttachRolePolicy",
          "iam:DetachRolePolicy",
          "iam:PutRolePolicy",
          "iam:DeleteRolePolicy"
        ]
        Resource = "*"
      }
    ]
  })
}

# Team Lead Role (Management Permissions)
resource "aws_iam_role" "team_lead_role" {
  name = "${local.name_prefix}-team-lead-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          AWS = [
            for user in var.developer_users : aws_iam_user.developers[user.name].arn
            if user.team == "lead" || user.team == "architect"
          ]
        }
        Condition = {
          Bool = {
            "aws:MultiFactorAuthPresent" = "true"
          }
          IpAddress = {
            "aws:SourceIp" = var.office_ip_ranges
          }
        }
      }
    ]
  })

  max_session_duration = var.session_duration

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-team-lead-role"
    Description = "Management role for team leads and architects"
    AccessLevel = "lead"
    UserType    = "developer"
  })
}

resource "aws_iam_role_policy_attachment" "team_lead_power_user" {
  policy_arn = local.managed_policies.power_user_access
  role       = aws_iam_role.team_lead_role.name
}

# Permission Boundary for All Developers
resource "aws_iam_role_policy_attachment" "developer_boundary" {
  for_each = {
    junior = aws_iam_role.junior_developer_role.name
    senior = aws_iam_role.senior_developer_role.name
    lead   = aws_iam_role.team_lead_role.name
  }
  
  policy_arn = aws_iam_policy.developer_boundary.arn
  role       = each.value
}

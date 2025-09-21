# Cross-Account Access Roles
# Roles for accessing resources across different AWS accounts

# Cross-Account Role for Trusted Accounts
resource "aws_iam_role" "cross_account_role" {
  for_each = toset(var.trusted_accounts)
  
  name = "${local.name_prefix}-cross-account-${each.key}-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${each.key}:root"
        }
        Condition = var.external_id != "" ? {
          StringEquals = {
            "sts:ExternalId" = var.external_id
          }
        } : {}
      }
    ]
  })

  max_session_duration = var.session_duration

  tags = merge(local.common_tags, {
    Name          = "${local.name_prefix}-cross-account-${each.key}-role"
    Description   = "Cross-account access role for account ${each.key}"
    TrustedAccount = each.key
    AccessType    = "cross-account"
  })
}

# Cross-Account Read-Only Access Policy
resource "aws_iam_role_policy" "cross_account_readonly" {
  for_each = toset(var.trusted_accounts)
  
  name = "${local.name_prefix}-cross-account-readonly-policy"
  role = aws_iam_role.cross_account_role[each.key].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:Describe*",
          "eks:Describe*",
          "eks:List*",
          "rds:Describe*",
          "s3:List*",
          "s3:GetBucketLocation",
          "lambda:List*",
          "lambda:Get*",
          "iam:List*",
          "iam:Get*",
          "cloudwatch:Describe*",
          "cloudwatch:Get*",
          "cloudwatch:List*",
          "logs:Describe*",
          "logs:Get*"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject"
        ]
        Resource = [
          for bucket in var.s3_buckets : "arn:aws:s3:::${bucket}/*"
        ]
        Condition = {
          StringLike = {
            "s3:x-amz-server-side-encryption" = "AES256"
          }
        }
      }
    ]
  })
}

# GitHub Actions OIDC Role (if enabled)
resource "aws_iam_role" "github_actions" {
  count = var.github_actions_role ? 1 : 0
  
  name = "${local.name_prefix}-github-actions-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Federated = aws_iam_openid_connect_provider.github_actions[0].arn
        }
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          }
          StringLike = {
            "token.actions.githubusercontent.com:sub" = "repo:${var.github_repository}:*"
          }
        }
      }
    ]
  })

  max_session_duration = var.session_duration

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-github-actions-role"
    Description = "OIDC role for GitHub Actions CI/CD"
    Repository  = var.github_repository
    AccessType  = "github-actions"
  })
}

# GitHub Actions Deployment Policy
resource "aws_iam_role_policy" "github_actions_deployment" {
  count = var.github_actions_role ? 1 : 0
  
  name = "${local.name_prefix}-github-actions-deployment-policy"
  role = aws_iam_role.github_actions[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "eks:DescribeCluster",
          "eks:DescribeNodegroup",
          "eks:ListClusters",
          "eks:ListNodegroups"
        ]
        Resource = "arn:aws:eks:${local.region}:${local.account_id}:cluster/${var.eks_cluster_name}"
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload"
        ]
        Resource = [
          "arn:aws:ecr:${local.region}:${local.account_id}:repository/${local.name_prefix}-*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = [
          "arn:aws:s3:::${local.name_prefix}-artifacts/*",
          "arn:aws:s3:::${local.name_prefix}-backups/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          "arn:aws:secretsmanager:${local.region}:${local.account_id}:secret:${local.name_prefix}-github-*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "lambda:UpdateFunctionCode",
          "lambda:UpdateFunctionConfiguration",
          "lambda:GetFunction",
          "lambda:InvokeFunction"
        ]
        Resource = [
          for func in var.lambda_functions : "arn:aws:lambda:${local.region}:${local.account_id}:function:${local.name_prefix}-${func}"
        ]
      }
    ]
  })
}

# Terraform Cloud/Enterprise Role
resource "aws_iam_role" "terraform_execution_role" {
  name = "${local.name_prefix}-terraform-execution-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          AWS = [
            # Add specific user ARNs or roles that can assume this role
            "arn:aws:iam::${local.account_id}:user/terraform-user",
            "arn:aws:iam::${local.account_id}:role/${local.name_prefix}-admin-role"
          ]
        }
        Condition = {
          StringEquals = {
            "aws:RequestedRegion" = local.region
          }
          IpAddress = {
            "aws:SourceIp" = concat(var.office_ip_ranges, var.bamboo_server_ips)
          }
          Bool = {
            "aws:MultiFactorAuthPresent" = "true"
          }
        }
      }
    ]
  })

  max_session_duration = 7200  # 2 hours for infrastructure operations

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-terraform-execution-role"
    Description = "Role for Terraform infrastructure management"
    AccessType  = "terraform"
    Purpose     = "infrastructure-management"
  })
}

# Terraform Execution Policy
resource "aws_iam_role_policy" "terraform_execution_policy" {
  name = "${local.name_prefix}-terraform-execution-policy"
  role = aws_iam_role.terraform_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:*",
          "eks:*",
          "rds:*",
          "s3:*",
          "lambda:*",
          "iam:*",
          "cloudwatch:*",
          "logs:*",
          "secretsmanager:*",
          "kms:*",
          "route53:*",
          "elasticloadbalancing:*",
          "autoscaling:*",
          "cloudformation:*",
          "ssm:*"
        ]
        Resource = "*"
      },
      {
        Effect = "Deny"
        Action = [
          "iam:DeleteRole",
          "iam:DeleteUser",
          "iam:DeleteGroup"
        ]
        Resource = [
          "arn:aws:iam::${local.account_id}:role/${local.name_prefix}-admin-*",
          "arn:aws:iam::${local.account_id}:user/*-admin",
          "arn:aws:iam::${local.account_id}:group/*-admin*"
        ]
      }
    ]
  })
}

# Backup Cross-Account Role
resource "aws_iam_role" "backup_cross_account_role" {
  count = length(var.trusted_accounts) > 0 ? 1 : 0
  
  name = "${local.name_prefix}-backup-cross-account-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          AWS = [
            for account in var.trusted_accounts : "arn:aws:iam::${account}:root"
          ]
        }
        Condition = {
          StringEquals = {
            "sts:ExternalId" = var.external_id
          }
        }
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-backup-cross-account-role"
    Description = "Cross-account role for backup operations"
    AccessType  = "backup-cross-account"
  })
}

# Backup Cross-Account Policy
resource "aws_iam_role_policy" "backup_cross_account_policy" {
  count = length(var.trusted_accounts) > 0 ? 1 : 0
  
  name = "${local.name_prefix}-backup-cross-account-policy"
  role = aws_iam_role.backup_cross_account_role[0].id

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
          "arn:aws:s3:::${local.name_prefix}-backups",
          "arn:aws:s3:::${local.name_prefix}-backups/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "backup:StartBackupJob",
          "backup:StopBackupJob",
          "backup:GetBackupPlan",
          "backup:GetBackupSelection",
          "backup:ListBackupJobs",
          "backup:DescribeBackupJob"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:GenerateDataKey"
        ]
        Resource = "arn:aws:kms:${local.region}:${local.account_id}:key/*"
        Condition = {
          StringEquals = {
            "kms:ViaService" = "s3.${local.region}.amazonaws.com"
          }
        }
      }
    ]
  })
}

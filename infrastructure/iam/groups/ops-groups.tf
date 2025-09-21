# Operations Groups
# Groups for DevOps, SRE, and operational personnel

# Operations Group (General Ops)
resource "aws_iam_group" "operations" {
  name = "${local.name_prefix}-operations"
  path = "/operations/"
}

# Operations Group Membership
resource "aws_iam_group_membership" "operations" {
  name = "${local.name_prefix}-operations-membership"
  
  users = [
    aws_iam_user.cicd_service_account.name,
    aws_iam_user.monitoring_service_account.name,
    aws_iam_user.backup_service_account.name,
    aws_iam_user.logging_service_account.name
  ]
  
  group = aws_iam_group.operations.name
  
  depends_on = [
    aws_iam_user.cicd_service_account,
    aws_iam_user.monitoring_service_account,
    aws_iam_user.backup_service_account,
    aws_iam_user.logging_service_account
  ]
}

# Base Operations Permissions
resource "aws_iam_group_policy" "operations_base" {
  name  = "${local.name_prefix}-operations-base-policy"
  group = aws_iam_group.operations.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:*",
          "logs:*",
          "events:*"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ec2:Describe*",
          "eks:Describe*",
          "eks:List*",
          "rds:Describe*",
          "elasticloadbalancing:Describe*",
          "autoscaling:Describe*"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters",
          "ssm:GetParametersByPath",
          "ssm:DescribeParameters"
        ]
        Resource = "arn:aws:ssm:${local.region}:${local.account_id}:parameter/${local.name_prefix}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = [
          "arn:aws:secretsmanager:${local.region}:${local.account_id}:secret:${local.name_prefix}-ops-*",
          "arn:aws:secretsmanager:${local.region}:${local.account_id}:secret:${local.name_prefix}-monitoring-*"
        ]
      }
    ]
  })
}

# DevOps Engineers Subgroup
resource "aws_iam_group" "devops_engineers" {
  name = "${local.name_prefix}-devops-engineers"
  path = "/operations/devops/"
}

resource "aws_iam_group_policy" "devops_engineers_policy" {
  name  = "${local.name_prefix}-devops-engineers-policy"
  group = aws_iam_group.devops_engineers.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "eks:*"
        ]
        Resource = [
          "arn:aws:eks:${local.region}:${local.account_id}:cluster/${var.eks_cluster_name}",
          "arn:aws:eks:${local.region}:${local.account_id}:nodegroup/${var.eks_cluster_name}/*/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:*"
        ]
        Resource = "arn:aws:ecr:${local.region}:${local.account_id}:repository/${local.name_prefix}-*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:*"
        ]
        Resource = [
          "arn:aws:s3:::${local.name_prefix}-artifacts",
          "arn:aws:s3:::${local.name_prefix}-artifacts/*",
          "arn:aws:s3:::${local.name_prefix}-logs",
          "arn:aws:s3:::${local.name_prefix}-logs/*"
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
          "codebuild:*",
          "codepipeline:*",
          "codedeploy:*"
        ]
        Resource = "*"
        Condition = {
          StringLike = {
            "codebuild:project-name" = "${local.name_prefix}-*",
            "codepipeline:pipeline-name" = "${local.name_prefix}-*"
          }
        }
      }
    ]
  })
}

# Site Reliability Engineers (SRE) Subgroup
resource "aws_iam_group" "sre_engineers" {
  name = "${local.name_prefix}-sre-engineers"
  path = "/operations/sre/"
}

resource "aws_iam_group_policy" "sre_engineers_policy" {
  name  = "${local.name_prefix}-sre-engineers-policy"
  group = aws_iam_group.sre_engineers.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:*",
          "logs:*",
          "events:*",
          "sns:*",
          "sqs:*"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "application-autoscaling:*",
          "autoscaling:*"
        ]
        Resource = "*"
        Condition = {
          StringLike = {
            "autoscaling:ResourceTag/Project" = var.project_name
          }
        }
      },
      {
        Effect = "Allow"
        Action = [
          "elasticloadbalancing:*"
        ]
        Resource = "*"
        Condition = {
          StringLike = {
            "elasticloadbalancing:ResourceTag/Project" = var.project_name
          }
        }
      },
      {
        Effect = "Allow"
        Action = [
          "rds:CreateDBSnapshot",
          "rds:DeleteDBSnapshot",
          "rds:DescribeDBSnapshots",
          "rds:ModifyDBInstance",
          "rds:RebootDBInstance"
        ]
        Resource = "arn:aws:rds:${local.region}:${local.account_id}:db:${var.rds_instance_identifier}"
      },
      {
        Effect = "Allow"
        Action = [
          "backup:*"
        ]
        Resource = "*"
      }
    ]
  })
}

# Infrastructure Engineers Subgroup
resource "aws_iam_group" "infrastructure_engineers" {
  name = "${local.name_prefix}-infrastructure-engineers"
  path = "/operations/infrastructure/"
}

resource "aws_iam_group_policy" "infrastructure_engineers_policy" {
  name  = "${local.name_prefix}-infrastructure-engineers-policy"
  group = aws_iam_group.infrastructure_engineers.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:*",
          "vpc:*",
          "route53:*"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "ec2:ResourceTag/Project" = var.project_name
          }
        }
      },
      {
        Effect = "Allow"
        Action = [
          "elasticloadbalancing:*"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "acm:*"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "kms:CreateKey",
          "kms:CreateAlias",
          "kms:DescribeKey",
          "kms:GetKeyPolicy",
          "kms:ListKeys",
          "kms:ListAliases",
          "kms:TagResource",
          "kms:UntagResource"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "cloudformation:*"
        ]
        Resource = "arn:aws:cloudformation:${local.region}:${local.account_id}:stack/${local.name_prefix}-*/*"
      }
    ]
  })
}

# Security Operations Subgroup
resource "aws_iam_group" "security_operations" {
  name = "${local.name_prefix}-security-operations"
  path = "/operations/security/"
}

resource "aws_iam_group_policy" "security_operations_policy" {
  name  = "${local.name_prefix}-security-operations-policy"
  group = aws_iam_group.security_operations.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "guardduty:*",
          "inspector:*",
          "securityhub:*",
          "config:*",
          "cloudtrail:*"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "wafv2:*",
          "shield:*"
        ]
        Resource = "*"
      },
      {
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
          "iam:GenerateCredentialReport",
          "iam:GetCredentialReport"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "kms:*"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "kms:ResourceTag/Project" = var.project_name
          }
        }
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:*"
        ]
        Resource = "arn:aws:secretsmanager:${local.region}:${local.account_id}:secret:${local.name_prefix}-*"
      }
    ]
  })
}

# Database Operations Subgroup
resource "aws_iam_group" "database_operations" {
  name = "${local.name_prefix}-database-operations"
  path = "/operations/database/"
}

resource "aws_iam_group_policy" "database_operations_policy" {
  name  = "${local.name_prefix}-database-operations-policy"
  group = aws_iam_group.database_operations.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "rds:*"
        ]
        Resource = [
          "arn:aws:rds:${local.region}:${local.account_id}:db:${var.rds_instance_identifier}",
          "arn:aws:rds:${local.region}:${local.account_id}:cluster:${var.rds_instance_identifier}-cluster",
          "arn:aws:rds:${local.region}:${local.account_id}:snapshot:*",
          "arn:aws:rds:${local.region}:${local.account_id}:cluster-snapshot:*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "rds:DescribeDBInstances",
          "rds:DescribeDBClusters",
          "rds:DescribeDBSnapshots",
          "rds:DescribeDBClusterSnapshots",
          "rds:DescribeDBParameterGroups",
          "rds:DescribeDBParameters"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret",
          "secretsmanager:CreateSecret",
          "secretsmanager:UpdateSecret"
        ]
        Resource = [
          "arn:aws:secretsmanager:${local.region}:${local.account_id}:secret:${local.name_prefix}-db-*",
          "arn:aws:secretsmanager:${local.region}:${local.account_id}:secret:${local.name_prefix}-rds-*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${local.name_prefix}-backups",
          "arn:aws:s3:::${local.name_prefix}-backups/*"
        ]
      }
    ]
  })
}

# On-Call Operations Subgroup
resource "aws_iam_group" "oncall_operations" {
  name = "${local.name_prefix}-oncall-operations"
  path = "/operations/oncall/"
}

resource "aws_iam_group_policy" "oncall_operations_policy" {
  name  = "${local.name_prefix}-oncall-operations-policy"
  group = aws_iam_group.oncall_operations.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:*",
          "logs:*",
          "events:*"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ec2:StartInstances",
          "ec2:StopInstances",
          "ec2:RebootInstances",
          "ec2:DescribeInstances",
          "ec2:DescribeInstanceStatus"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "ec2:ResourceTag/Project" = var.project_name
          }
        }
      },
      {
        Effect = "Allow"
        Action = [
          "autoscaling:SetDesiredCapacity",
          "autoscaling:UpdateAutoScalingGroup",
          "autoscaling:DescribeAutoScalingGroups"
        ]
        Resource = "*"
        Condition = {
          StringLike = {
            "autoscaling:ResourceTag/Project" = var.project_name
          }
        }
      },
      {
        Effect = "Allow"
        Action = [
          "sns:Publish"
        ]
        Resource = "arn:aws:sns:${local.region}:${local.account_id}:${local.name_prefix}-alerts"
      },
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction"
        ]
        Resource = [
          for func in var.lambda_functions : "arn:aws:lambda:${local.region}:${local.account_id}:function:${local.name_prefix}-${func}"
        ]
      }
    ]
  })
}

# Permission Boundaries for Operations Groups
resource "aws_iam_group_policy_attachment" "operations_boundary" {
  group      = aws_iam_group.operations.name
  policy_arn = aws_iam_policy.operations_boundary.arn
}

resource "aws_iam_group_policy_attachment" "devops_engineers_boundary" {
  group      = aws_iam_group.devops_engineers.name
  policy_arn = aws_iam_policy.operations_boundary.arn
}

resource "aws_iam_group_policy_attachment" "sre_engineers_boundary" {
  group      = aws_iam_group.sre_engineers.name
  policy_arn = aws_iam_policy.operations_boundary.arn
}

resource "aws_iam_group_policy_attachment" "infrastructure_engineers_boundary" {
  group      = aws_iam_group.infrastructure_engineers.name
  policy_arn = aws_iam_policy.operations_boundary.arn
}

resource "aws_iam_group_policy_attachment" "security_operations_boundary" {
  group      = aws_iam_group.security_operations.name
  policy_arn = aws_iam_policy.operations_boundary.arn
}

resource "aws_iam_group_policy_attachment" "database_operations_boundary" {
  group      = aws_iam_group.database_operations.name
  policy_arn = aws_iam_policy.operations_boundary.arn
}

resource "aws_iam_group_policy_attachment" "oncall_operations_boundary" {
  group      = aws_iam_group.oncall_operations.name
  policy_arn = aws_iam_policy.operations_boundary.arn
}

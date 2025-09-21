# Custom IAM Policies
# Application-specific and custom permission policies

# S3 Bucket Access Policy
resource "aws_iam_policy" "s3_bucket_access" {
  name        = "${local.name_prefix}-s3-bucket-access"
  path        = "/custom/"
  description = "Access to project-specific S3 buckets"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket",
          "s3:GetBucketLocation",
          "s3:GetBucketVersioning"
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
          "s3:DeleteObject",
          "s3:GetObjectVersion",
          "s3:PutObjectAcl"
        ]
        Resource = [
          for bucket in var.s3_buckets : "arn:aws:s3:::${bucket}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetBucketNotification",
          "s3:PutBucketNotification"
        ]
        Resource = [
          for bucket in var.s3_buckets : "arn:aws:s3:::${bucket}"
        ]
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-s3-bucket-access"
    Description = "S3 bucket access policy"
    PolicyType  = "custom"
  })
}

# EKS Cluster Access Policy
resource "aws_iam_policy" "eks_cluster_access" {
  name        = "${local.name_prefix}-eks-cluster-access"
  path        = "/custom/"
  description = "Access to EKS cluster operations"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "eks:DescribeCluster",
          "eks:ListClusters",
          "eks:DescribeAddon",
          "eks:ListAddons",
          "eks:DescribeNodegroup",
          "eks:ListNodegroups",
          "eks:DescribeUpdate",
          "eks:ListUpdates"
        ]
        Resource = [
          "arn:aws:eks:${local.region}:${local.account_id}:cluster/${var.eks_cluster_name}",
          "arn:aws:eks:${local.region}:${local.account_id}:nodegroup/${var.eks_cluster_name}/*/*",
          "arn:aws:eks:${local.region}:${local.account_id}:addon/${var.eks_cluster_name}/*/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "eks:AccessKubernetesApi"
        ]
        Resource = "arn:aws:eks:${local.region}:${local.account_id}:cluster/${var.eks_cluster_name}"
        Condition = {
          StringEquals = {
            "kubernetes.io/namespace" = ["default", "kube-system", "monitoring"]
          }
        }
      },
      {
        Effect = "Allow"
        Action = [
          "ec2:DescribeInstances",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DescribeSecurityGroups",
          "ec2:DescribeSubnets",
          "ec2:DescribeVpcs"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "ec2:ResourceTag/kubernetes.io/cluster/${var.eks_cluster_name}" = "owned"
          }
        }
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-eks-cluster-access"
    Description = "EKS cluster access policy"
    PolicyType  = "custom"
  })
}

# RDS Database Access Policy
resource "aws_iam_policy" "rds_database_access" {
  name        = "${local.name_prefix}-rds-database-access"
  path        = "/custom/"
  description = "Access to RDS database operations"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "rds:DescribeDBInstances",
          "rds:DescribeDBClusters",
          "rds:DescribeDBSnapshots",
          "rds:DescribeDBClusterSnapshots",
          "rds:ListTagsForResource"
        ]
        Resource = [
          "arn:aws:rds:${local.region}:${local.account_id}:db:${var.rds_instance_identifier}",
          "arn:aws:rds:${local.region}:${local.account_id}:cluster:${var.rds_instance_identifier}-cluster",
          "arn:aws:rds:${local.region}:${local.account_id}:snapshot:${var.rds_instance_identifier}*",
          "arn:aws:rds:${local.region}:${local.account_id}:cluster-snapshot:${var.rds_instance_identifier}*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "rds-db:connect"
        ]
        Resource = [
          "arn:aws:rds-db:${local.region}:${local.account_id}:dbuser:${var.rds_instance_identifier}/app-user",
          "arn:aws:rds-db:${local.region}:${local.account_id}:dbuser:${var.rds_instance_identifier}/readonly-user"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "rds:CreateDBSnapshot"
        ]
        Resource = [
          "arn:aws:rds:${local.region}:${local.account_id}:db:${var.rds_instance_identifier}",
          "arn:aws:rds:${local.region}:${local.account_id}:snapshot:${var.rds_instance_identifier}-manual-*"
        ]
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-rds-database-access"
    Description = "RDS database access policy"
    PolicyType  = "custom"
  })
}

# Lambda Invoke Access Policy
resource "aws_iam_policy" "lambda_invoke_access" {
  name        = "${local.name_prefix}-lambda-invoke-access"
  path        = "/custom/"
  description = "Access to invoke Lambda functions"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction",
          "lambda:GetFunction",
          "lambda:GetFunctionConfiguration",
          "lambda:ListVersionsByFunction",
          "lambda:GetAlias"
        ]
        Resource = [
          for func in var.lambda_functions : "arn:aws:lambda:${local.region}:${local.account_id}:function:${local.name_prefix}-${func}"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "lambda:ListFunctions"
        ]
        Resource = "*"
        Condition = {
          StringLike = {
            "lambda:FunctionName" = "${local.name_prefix}-*"
          }
        }
      },
      {
        Effect = "Allow"
        Action = [
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams",
          "logs:GetLogEvents"
        ]
        Resource = [
          for func in var.lambda_functions : "arn:aws:logs:${local.region}:${local.account_id}:log-group:/aws/lambda/${local.name_prefix}-${func}*"
        ]
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-lambda-invoke-access"
    Description = "Lambda function invoke access policy"
    PolicyType  = "custom"
  })
}

# Secrets Manager Access Policy
resource "aws_iam_policy" "secrets_manager_access" {
  name        = "${local.name_prefix}-secrets-manager-access"
  path        = "/custom/"
  description = "Access to Secrets Manager secrets"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = [
          "arn:aws:secretsmanager:${local.region}:${local.account_id}:secret:${local.name_prefix}-*"
        ]
        Condition = {
          StringNotLike = {
            "secretsmanager:Name" = [
              "*-admin-*",
              "*-root-*",
              "*-master-*",
              "*-emergency-*"
            ]
          }
        }
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:ListSecrets"
        ]
        Resource = "*"
        Condition = {
          StringLike = {
            "secretsmanager:Name" = "${local.name_prefix}-*"
          }
        }
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:GenerateDataKey"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "kms:ViaService" = "secretsmanager.${local.region}.amazonaws.com"
          }
          StringLike = {
            "kms:EncryptionContext:SecretARN" = "arn:aws:secretsmanager:${local.region}:${local.account_id}:secret:${local.name_prefix}-*"
          }
        }
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-secrets-manager-access"
    Description = "Secrets Manager access policy"
    PolicyType  = "custom"
  })
}

# CloudWatch Logs Access Policy
resource "aws_iam_policy" "cloudwatch_logs_access" {
  name        = "${local.name_prefix}-cloudwatch-logs-access"
  path        = "/custom/"
  description = "Access to CloudWatch Logs"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams",
          "logs:GetLogEvents",
          "logs:FilterLogEvents"
        ]
        Resource = [
          "arn:aws:logs:${local.region}:${local.account_id}:log-group:/aws/eks/${var.eks_cluster_name}*",
          "arn:aws:logs:${local.region}:${local.account_id}:log-group:/aws/lambda/${local.name_prefix}-*",
          "arn:aws:logs:${local.region}:${local.account_id}:log-group:${local.name_prefix}-*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:DescribeLogGroups"
        ]
        Resource = "arn:aws:logs:${local.region}:${local.account_id}:*"
      },
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:PutMetricData",
          "cloudwatch:GetMetricStatistics",
          "cloudwatch:ListMetrics"
        ]
        Resource = "*"
        Condition = {
          StringLike = {
            "cloudwatch:namespace" = "${local.name_prefix}*"
          }
        }
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-cloudwatch-logs-access"
    Description = "CloudWatch Logs access policy"
    PolicyType  = "custom"
  })
}

# CI/CD Deployment Policy
resource "aws_iam_policy" "ci_cd_deployment" {
  name        = "${local.name_prefix}-ci-cd-deployment"
  path        = "/custom/"
  description = "Policy for CI/CD deployment operations"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
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
          "eks:DescribeCluster",
          "eks:DescribeNodegroup",
          "eks:ListNodegroups"
        ]
        Resource = [
          "arn:aws:eks:${local.region}:${local.account_id}:cluster/${var.eks_cluster_name}",
          "arn:aws:eks:${local.region}:${local.account_id}:nodegroup/${var.eks_cluster_name}/*/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "lambda:UpdateFunctionCode",
          "lambda:UpdateFunctionConfiguration",
          "lambda:PublishVersion",
          "lambda:CreateAlias",
          "lambda:UpdateAlias",
          "lambda:GetFunction",
          "lambda:InvokeFunction"
        ]
        Resource = [
          for func in var.lambda_functions : "arn:aws:lambda:${local.region}:${local.account_id}:function:${local.name_prefix}-${func}"
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
          "arn:aws:s3:::${local.name_prefix}-artifacts/*",
          "arn:aws:s3:::${local.name_prefix}-assets/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          "arn:aws:secretsmanager:${local.region}:${local.account_id}:secret:${local.name_prefix}-cicd-*",
          "arn:aws:secretsmanager:${local.region}:${local.account_id}:secret:${local.name_prefix}-deploy-*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters",
          "ssm:GetParametersByPath"
        ]
        Resource = "arn:aws:ssm:${local.region}:${local.account_id}:parameter/${local.name_prefix}/deploy/*"
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-ci-cd-deployment"
    Description = "CI/CD deployment policy"
    PolicyType  = "custom"
  })
}

# ECR Repository Access Policy
resource "aws_iam_policy" "ecr_repository_access" {
  name        = "${local.name_prefix}-ecr-repository-access"
  path        = "/custom/"
  description = "Access to ECR repositories"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
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
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:DescribeRepositories",
          "ecr:ListImages",
          "ecr:DescribeImages",
          "ecr:GetRepositoryPolicy"
        ]
        Resource = "arn:aws:ecr:${local.region}:${local.account_id}:repository/${local.name_prefix}-*"
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload"
        ]
        Resource = "arn:aws:ecr:${local.region}:${local.account_id}:repository/${local.name_prefix}-*"
        Condition = {
          StringEquals = {
            "ecr:ResourceTag/Project" = var.project_name
          }
        }
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-ecr-repository-access"
    Description = "ECR repository access policy"
    PolicyType  = "custom"
  })
}

# SSM Parameter Store Access Policy
resource "aws_iam_policy" "ssm_parameter_access" {
  name        = "${local.name_prefix}-ssm-parameter-access"
  path        = "/custom/"
  description = "Access to SSM Parameter Store"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
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
          "ssm:PutParameter",
          "ssm:DeleteParameter",
          "ssm:AddTagsToResource",
          "ssm:RemoveTagsFromResource"
        ]
        Resource = "arn:aws:ssm:${local.region}:${local.account_id}:parameter/${local.name_prefix}/*"
        Condition = {
          StringNotLike = {
            "ssm:Name" = [
              "/${local.name_prefix}/prod/*",
              "/${local.name_prefix}/production/*"
            ]
          }
        }
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:GenerateDataKey"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "kms:ViaService" = "ssm.${local.region}.amazonaws.com"
          }
          StringLike = {
            "kms:EncryptionContext:PARAMETER_ARN" = "arn:aws:ssm:${local.region}:${local.account_id}:parameter/${local.name_prefix}/*"
          }
        }
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-ssm-parameter-access"
    Description = "SSM Parameter Store access policy"
    PolicyType  = "custom"
  })
}

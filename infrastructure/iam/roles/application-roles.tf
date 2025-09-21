# Application-Specific IAM Roles
# Custom roles for application services and components

# Risk API Service Role
resource "aws_iam_role" "risk_api_role" {
  name = "${local.name_prefix}-risk-api-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      },
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Federated = "arn:aws:iam::${local.account_id}:oidc-provider/${replace(var.eks_cluster_name, "${local.name_prefix}-", "")}"
        }
        Condition = {
          StringEquals = {
            "${replace(var.eks_cluster_name, "${local.name_prefix}-", "")}:sub" = "system:serviceaccount:default:risk-api-service-account"
            "${replace(var.eks_cluster_name, "${local.name_prefix}-", "")}:aud" = "sts.amazonaws.com"
          }
        }
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-risk-api-role"
    Description = "Application role for Risk API service"
    Application = "risk-api"
    Service     = "EKS"
  })
}

# Risk API Custom Policy
resource "aws_iam_role_policy" "risk_api_policy" {
  name = "${local.name_prefix}-risk-api-policy"
  role = aws_iam_role.risk_api_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "rds:DescribeDBInstances",
          "rds:DescribeDBClusters"
        ]
        Resource = "arn:aws:rds:${local.region}:${local.account_id}:db:${var.rds_instance_identifier}"
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          "arn:aws:secretsmanager:${local.region}:${local.account_id}:secret:${local.name_prefix}-db-credentials-*",
          "arn:aws:secretsmanager:${local.region}:${local.account_id}:secret:${local.name_prefix}-api-keys-*"
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
          "arn:aws:s3:::${local.name_prefix}-assets/*",
          "arn:aws:s3:::${local.name_prefix}-backups/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${local.region}:${local.account_id}:log-group:/aws/eks/${var.eks_cluster_name}/risk-api*"
      }
    ]
  })
}

# Airflow Service Role
resource "aws_iam_role" "airflow_service_role" {
  name = "${local.name_prefix}-airflow-service-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Federated = "arn:aws:iam::${local.account_id}:oidc-provider/${replace(var.eks_cluster_name, "${local.name_prefix}-", "")}"
        }
        Condition = {
          StringEquals = {
            "${replace(var.eks_cluster_name, "${local.name_prefix}-", "")}:sub" = "system:serviceaccount:airflow:airflow-service-account"
            "${replace(var.eks_cluster_name, "${local.name_prefix}-", "")}:aud" = "sts.amazonaws.com"
          }
        }
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-airflow-service-role"
    Description = "Service role for Apache Airflow in EKS"
    Application = "airflow"
    Service     = "EKS"
  })
}

# Airflow Custom Policy
resource "aws_iam_role_policy" "airflow_service_policy" {
  name = "${local.name_prefix}-airflow-service-policy"
  role = aws_iam_role.airflow_service_role.id

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
          "arn:aws:s3:::${local.name_prefix}-artifacts",
          "arn:aws:s3:::${local.name_prefix}-artifacts/*",
          "arn:aws:s3:::${local.name_prefix}-logs",
          "arn:aws:s3:::${local.name_prefix}-logs/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          "arn:aws:secretsmanager:${local.region}:${local.account_id}:secret:${local.name_prefix}-airflow-*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction"
        ]
        Resource = [
          for func in var.lambda_functions : "arn:aws:lambda:${local.region}:${local.account_id}:function:${local.name_prefix}-${func}"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${local.region}:${local.account_id}:log-group:/aws/eks/${var.eks_cluster_name}/airflow*"
      }
    ]
  })
}

# Data Processing Service Role
resource "aws_iam_role" "data_processor_role" {
  name = "${local.name_prefix}-data-processor-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Federated = "arn:aws:iam::${local.account_id}:oidc-provider/${replace(var.eks_cluster_name, "${local.name_prefix}-", "")}"
        }
        Condition = {
          StringEquals = {
            "${replace(var.eks_cluster_name, "${local.name_prefix}-", "")}:sub" = "system:serviceaccount:default:data-processor-service-account"
            "${replace(var.eks_cluster_name, "${local.name_prefix}-", "")}:aud" = "sts.amazonaws.com"
          }
        }
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-data-processor-role"
    Description = "Role for data processing services"
    Application = "data-processor"
    Service     = "Lambda/EKS"
  })
}

# Data Processing Custom Policy
resource "aws_iam_role_policy" "data_processor_policy" {
  name = "${local.name_prefix}-data-processor-policy"
  role = aws_iam_role.data_processor_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "rds:Connect",
          "rds:DescribeDBInstances"
        ]
        Resource = "arn:aws:rds-db:${local.region}:${local.account_id}:dbuser:${var.rds_instance_identifier}/data-processor"
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
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          "arn:aws:secretsmanager:${local.region}:${local.account_id}:secret:${local.name_prefix}-data-*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "sqs:SendMessage",
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]
        Resource = "arn:aws:sqs:${local.region}:${local.account_id}:${local.name_prefix}-*"
      }
    ]
  })
}

# Monitoring Service Role
resource "aws_iam_role" "monitoring_service_role" {
  name = "${local.name_prefix}-monitoring-service-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Federated = "arn:aws:iam::${local.account_id}:oidc-provider/${replace(var.eks_cluster_name, "${local.name_prefix}-", "")}"
        }
        Condition = {
          StringEquals = {
            "${replace(var.eks_cluster_name, "${local.name_prefix}-", "")}:sub" = "system:serviceaccount:monitoring:monitoring-service-account"
            "${replace(var.eks_cluster_name, "${local.name_prefix}-", "")}:aud" = "sts.amazonaws.com"
          }
        }
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-monitoring-service-role"
    Description = "Role for monitoring and observability services"
    Application = "monitoring"
    Service     = "EKS"
  })
}

# Monitoring Service Policy
resource "aws_iam_role_policy" "monitoring_service_policy" {
  name = "${local.name_prefix}-monitoring-service-policy"
  role = aws_iam_role.monitoring_service_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:PutMetricData",
          "cloudwatch:GetMetricStatistics",
          "cloudwatch:ListMetrics"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams"
        ]
        Resource = "arn:aws:logs:${local.region}:${local.account_id}:*"
      },
      {
        Effect = "Allow"
        Action = [
          "ec2:DescribeInstances",
          "ec2:DescribeVolumes",
          "ec2:DescribeNetworkInterfaces"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "eks:DescribeCluster",
          "eks:ListClusters",
          "eks:DescribeNodegroup",
          "eks:ListNodegroups"
        ]
        Resource = "*"
      }
    ]
  })
}

# Backup Service Role
resource "aws_iam_role" "backup_service_role" {
  name = "${local.name_prefix}-backup-service-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "backup.amazonaws.com"
        }
      },
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-backup-service-role"
    Description = "Role for AWS Backup and backup automation"
    Application = "backup"
    Service     = "Backup/Lambda"
  })
}

resource "aws_iam_role_policy_attachment" "backup_service_policy" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBackupServiceRolePolicyForBackup"
  role       = aws_iam_role.backup_service_role.name
}

resource "aws_iam_role_policy_attachment" "backup_restore_policy" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBackupServiceRolePolicyForRestores"
  role       = aws_iam_role.backup_service_role.name
}

# API Gateway Execution Role
resource "aws_iam_role" "api_gateway_role" {
  name = "${local.name_prefix}-api-gateway-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "apigateway.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-api-gateway-role"
    Description = "Execution role for API Gateway"
    Application = "api-gateway"
    Service     = "APIGateway"
  })
}

resource "aws_iam_role_policy_attachment" "api_gateway_logs" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs"
  role       = aws_iam_role.api_gateway_role.name
}

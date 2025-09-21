# Service Account Users
# System and service accounts for automated processes

# Service Accounts
resource "aws_iam_user" "service_accounts" {
  for_each = {
    for account in var.service_accounts : account.name => account
  }
  
  name          = "${local.name_prefix}-svc-${each.value.name}"
  path          = "/service-accounts/"
  force_destroy = true  # Service accounts can be recreated

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-svc-${each.value.name}"
    Description = each.value.description
    Service     = each.value.service
    UserType    = "service-account"
    Department  = "automation"
  })
}

# Service Account Access Keys
resource "aws_iam_access_key" "service_accounts" {
  for_each = {
    for account in var.service_accounts : account.name => account
  }
  
  user = aws_iam_user.service_accounts[each.key].name
  
  depends_on = [aws_iam_user.service_accounts]
}

# Store Service Account Credentials in Secrets Manager
resource "aws_secretsmanager_secret" "service_account_credentials" {
  for_each = {
    for account in var.service_accounts : account.name => account
  }
  
  name        = "${local.name_prefix}-svc-${each.key}-credentials"
  description = "Credentials for ${each.key} service account"
  
  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-svc-${each.key}-credentials"
    UserType    = "service-account"
    Service     = each.value.service
    Description = each.value.description
  })
}

resource "aws_secretsmanager_secret_version" "service_account_credentials" {
  for_each = {
    for account in var.service_accounts : account.name => account
  }
  
  secret_id = aws_secretsmanager_secret.service_account_credentials[each.key].id
  secret_string = jsonencode({
    access_key_id     = aws_iam_access_key.service_accounts[each.key].id
    secret_access_key = aws_iam_access_key.service_accounts[each.key].secret
    user_name         = aws_iam_user.service_accounts[each.key].name
    service           = each.value.service
    description       = each.value.description
  })
}

# CI/CD Service Account
resource "aws_iam_user" "cicd_service_account" {
  name          = "${local.name_prefix}-svc-cicd"
  path          = "/service-accounts/"
  force_destroy = true

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-svc-cicd"
    Description = "CI/CD pipeline service account"
    Service     = "bamboo"
    UserType    = "service-account"
    Department  = "devops"
  })
}

resource "aws_iam_access_key" "cicd_service_account" {
  user = aws_iam_user.cicd_service_account.name
}

resource "aws_secretsmanager_secret" "cicd_credentials" {
  name        = "${local.name_prefix}-svc-cicd-credentials"
  description = "CI/CD pipeline service account credentials"
  
  tags = merge(local.common_tags, {
    Name    = "${local.name_prefix}-svc-cicd-credentials"
    Service = "bamboo"
    UserType = "service-account"
  })
}

resource "aws_secretsmanager_secret_version" "cicd_credentials" {
  secret_id = aws_secretsmanager_secret.cicd_credentials.id
  secret_string = jsonencode({
    access_key_id     = aws_iam_access_key.cicd_service_account.id
    secret_access_key = aws_iam_access_key.cicd_service_account.secret
    user_name         = aws_iam_user.cicd_service_account.name
    service           = "bamboo"
    description       = "CI/CD pipeline automation"
  })
}

# Monitoring Service Account
resource "aws_iam_user" "monitoring_service_account" {
  name          = "${local.name_prefix}-svc-monitoring"
  path          = "/service-accounts/"
  force_destroy = true

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-svc-monitoring"
    Description = "Monitoring and observability service account"
    Service     = "prometheus"
    UserType    = "service-account"
    Department  = "operations"
  })
}

resource "aws_iam_access_key" "monitoring_service_account" {
  user = aws_iam_user.monitoring_service_account.name
}

resource "aws_secretsmanager_secret" "monitoring_credentials" {
  name        = "${local.name_prefix}-svc-monitoring-credentials"
  description = "Monitoring service account credentials"
  
  tags = merge(local.common_tags, {
    Name    = "${local.name_prefix}-svc-monitoring-credentials"
    Service = "prometheus"
    UserType = "service-account"
  })
}

resource "aws_secretsmanager_secret_version" "monitoring_credentials" {
  secret_id = aws_secretsmanager_secret.monitoring_credentials.id
  secret_string = jsonencode({
    access_key_id     = aws_iam_access_key.monitoring_service_account.id
    secret_access_key = aws_iam_access_key.monitoring_service_account.secret
    user_name         = aws_iam_user.monitoring_service_account.name
    service           = "prometheus"
    description       = "Monitoring and metrics collection"
  })
}

# Backup Service Account
resource "aws_iam_user" "backup_service_account" {
  name          = "${local.name_prefix}-svc-backup"
  path          = "/service-accounts/"
  force_destroy = true

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-svc-backup"
    Description = "Backup and disaster recovery service account"
    Service     = "backup"
    UserType    = "service-account" 
    Department  = "operations"
  })
}

resource "aws_iam_access_key" "backup_service_account" {
  user = aws_iam_user.backup_service_account.name
}

resource "aws_secretsmanager_secret" "backup_credentials" {
  name        = "${local.name_prefix}-svc-backup-credentials"
  description = "Backup service account credentials"
  
  tags = merge(local.common_tags, {
    Name    = "${local.name_prefix}-svc-backup-credentials"
    Service = "backup"
    UserType = "service-account"
  })
}

resource "aws_secretsmanager_secret_version" "backup_credentials" {
  secret_id = aws_secretsmanager_secret.backup_credentials.id
  secret_string = jsonencode({
    access_key_id     = aws_iam_access_key.backup_service_account.id
    secret_access_key = aws_iam_access_key.backup_service_account.secret
    user_name         = aws_iam_user.backup_service_account.name
    service           = "backup"
    description       = "Automated backup and recovery operations"
  })
}

# Log Aggregation Service Account
resource "aws_iam_user" "logging_service_account" {
  name          = "${local.name_prefix}-svc-logging"
  path          = "/service-accounts/"
  force_destroy = true

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-svc-logging"
    Description = "Log aggregation and analysis service account"
    Service     = "fluentd"
    UserType    = "service-account"
    Department  = "operations"
  })
}

resource "aws_iam_access_key" "logging_service_account" {
  user = aws_iam_user.logging_service_account.name
}

resource "aws_secretsmanager_secret" "logging_credentials" {
  name        = "${local.name_prefix}-svc-logging-credentials"
  description = "Logging service account credentials"
  
  tags = merge(local.common_tags, {
    Name    = "${local.name_prefix}-svc-logging-credentials"
    Service = "fluentd"
    UserType = "service-account"
  })
}

resource "aws_secretsmanager_secret_version" "logging_credentials" {
  secret_id = aws_secretsmanager_secret.logging_credentials.id
  secret_string = jsonencode({
    access_key_id     = aws_iam_access_key.logging_service_account.id
    secret_access_key = aws_iam_access_key.logging_service_account.secret
    user_name         = aws_iam_user.logging_service_account.name
    service           = "fluentd"
    description       = "Log collection and forwarding"
  })
}

# Service Account Policies
resource "aws_iam_user_policy" "cicd_policy" {
  name = "${local.name_prefix}-cicd-policy"
  user = aws_iam_user.cicd_service_account.name

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
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload"
        ]
        Resource = "arn:aws:ecr:${local.region}:${local.account_id}:repository/${local.name_prefix}-*"
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
          "lambda:UpdateFunctionCode",
          "lambda:UpdateFunctionConfiguration",
          "lambda:InvokeFunction"
        ]
        Resource = [
          for func in var.lambda_functions : "arn:aws:lambda:${local.region}:${local.account_id}:function:${local.name_prefix}-${func}"
        ]
      }
    ]
  })
}

resource "aws_iam_user_policy" "monitoring_policy" {
  name = "${local.name_prefix}-monitoring-policy"
  user = aws_iam_user.monitoring_service_account.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:GetMetricStatistics",
          "cloudwatch:ListMetrics",
          "cloudwatch:PutMetricData"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams",
          "logs:GetLogEvents",
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ec2:DescribeInstances",
          "eks:DescribeCluster",
          "rds:DescribeDBInstances"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_user_policy" "backup_policy" {
  name = "${local.name_prefix}-backup-policy"
  user = aws_iam_user.backup_service_account.name

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
          "backup:ListBackupJobs"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "rds:CreateDBSnapshot",
          "rds:DescribeDBSnapshots",
          "rds:DeleteDBSnapshot"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_user_policy" "logging_policy" {
  name = "${local.name_prefix}-logging-policy"
  user = aws_iam_user.logging_service_account.name

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
          "logs:DescribeLogStreams"
        ]
        Resource = "arn:aws:logs:${local.region}:${local.account_id}:*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject"
        ]
        Resource = "arn:aws:s3:::${local.name_prefix}-logs/*"
      }
    ]
  })
}

# Policy Attachments
# Attaching policies to users, groups, and roles

# Attach Custom Policies to Service Roles
resource "aws_iam_role_policy_attachment" "lambda_s3_access" {
  for_each = toset(var.lambda_functions)
  
  role       = aws_iam_role.lambda_execution_role[each.key].name
  policy_arn = aws_iam_policy.s3_bucket_access.arn
}

resource "aws_iam_role_policy_attachment" "lambda_secrets_access" {
  for_each = toset(var.lambda_functions)
  
  role       = aws_iam_role.lambda_execution_role[each.key].name
  policy_arn = aws_iam_policy.secrets_manager_access.arn
}

resource "aws_iam_role_policy_attachment" "lambda_logs_access" {
  for_each = toset(var.lambda_functions)
  
  role       = aws_iam_role.lambda_execution_role[each.key].name
  policy_arn = aws_iam_policy.cloudwatch_logs_access.arn
}

# Attach Policies to Application Roles
resource "aws_iam_role_policy_attachment" "risk_api_s3_access" {
  role       = aws_iam_role.risk_api_role.name
  policy_arn = aws_iam_policy.s3_bucket_access.arn
}

resource "aws_iam_role_policy_attachment" "risk_api_secrets_access" {
  role       = aws_iam_role.risk_api_role.name
  policy_arn = aws_iam_policy.secrets_manager_access.arn
}

resource "aws_iam_role_policy_attachment" "risk_api_rds_access" {
  role       = aws_iam_role.risk_api_role.name
  policy_arn = aws_iam_policy.rds_database_access.arn
}

resource "aws_iam_role_policy_attachment" "airflow_s3_access" {
  role       = aws_iam_role.airflow_service_role.name
  policy_arn = aws_iam_policy.s3_bucket_access.arn
}

resource "aws_iam_role_policy_attachment" "airflow_lambda_access" {
  role       = aws_iam_role.airflow_service_role.name
  policy_arn = aws_iam_policy.lambda_invoke_access.arn
}

resource "aws_iam_role_policy_attachment" "airflow_secrets_access" {
  role       = aws_iam_role.airflow_service_role.name
  policy_arn = aws_iam_policy.secrets_manager_access.arn
}

# Attach Policies to Cross-Account Roles
resource "aws_iam_role_policy_attachment" "github_actions_s3_access" {
  count = var.github_actions_role ? 1 : 0
  
  role       = aws_iam_role.github_actions[0].name
  policy_arn = aws_iam_policy.ci_cd_deployment.arn
}

resource "aws_iam_role_policy_attachment" "github_actions_ecr_access" {
  count = var.github_actions_role ? 1 : 0
  
  role       = aws_iam_role.github_actions[0].name
  policy_arn = aws_iam_policy.ecr_repository_access.arn
}

resource "aws_iam_role_policy_attachment" "github_actions_eks_access" {
  count = var.github_actions_role ? 1 : 0
  
  role       = aws_iam_role.github_actions[0].name
  policy_arn = aws_iam_policy.eks_cluster_access.arn
}

# Attach Policies to EKS Service Account Roles
resource "aws_iam_role_policy_attachment" "alb_controller_policy" {
  role       = aws_iam_role.alb_controller_role.name
  policy_arn = "arn:aws:iam::aws:policy/ElasticLoadBalancingFullAccess"
}

resource "aws_iam_role_policy_attachment" "alb_controller_ec2_policy" {
  role       = aws_iam_role.alb_controller_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess"
}

# Custom ALB Controller Policy
resource "aws_iam_role_policy" "alb_controller_custom" {
  name = "${local.name_prefix}-alb-controller-custom-policy"
  role = aws_iam_role.alb_controller_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "iam:CreateServiceLinkedRole",
          "ec2:CreateTags"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "iam:AWSServiceName" = "elasticloadbalancing.amazonaws.com"
          }
        }
      },
      {
        Effect = "Allow"
        Action = [
          "ec2:CreateTags",
          "ec2:DeleteTags"
        ]
        Resource = "arn:aws:ec2:*:*:security-group/*"
        Condition = {
          StringEquals = {
            "ec2:ResourceTag/elbv2.k8s.aws/cluster" = var.eks_cluster_name
          }
        }
      },
      {
        Effect = "Allow"
        Action = [
          "wafv2:GetWebACL",
          "wafv2:GetWebACLForResource",
          "wafv2:AssociateWebACL",
          "wafv2:DisassociateWebACL"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "shield:DescribeProtection",
          "shield:GetSubscriptionState",
          "shield:DescribeSubscription",
          "shield:ListProtections"
        ]
        Resource = "*"
      }
    ]
  })
}

# Attach Permission Boundaries to Users
resource "aws_iam_user_policy_attachment" "developers_custom_policy" {
  for_each = {
    for user in var.developer_users : user.name => user
  }
  
  user       = aws_iam_user.developers[each.key].name
  policy_arn = aws_iam_policy.eks_cluster_access.arn
}

resource "aws_iam_user_policy_attachment" "developers_s3_policy" {
  for_each = {
    for user in var.developer_users : user.name => user
  }
  
  user       = aws_iam_user.developers[each.key].name
  policy_arn = aws_iam_policy.s3_bucket_access.arn
}

# Set Permission Boundaries for Users
resource "aws_iam_user" "developers_with_boundary" {
  for_each = {
    for user in var.developer_users : user.name => user
  }
  
  name                 = aws_iam_user.developers[each.key].name
  permissions_boundary = aws_iam_policy.developer_boundary.arn
  
  lifecycle {
    ignore_changes = [name, path, force_destroy, tags]
  }
  
  depends_on = [aws_iam_user.developers]
}

resource "aws_iam_user" "admins_with_boundary" {
  for_each = {
    for user in var.admin_users : user.name => user
  }
  
  name                 = aws_iam_user.admins[each.key].name
  permissions_boundary = user.role == "security-admin" ? aws_iam_policy.security_boundary.arn : null
  
  lifecycle {
    ignore_changes = [name, path, force_destroy, tags]
  }
  
  depends_on = [aws_iam_user.admins]
}

resource "aws_iam_user" "service_accounts_with_boundary" {
  for_each = {
    for account in var.service_accounts : account.name => account
  }
  
  name                 = aws_iam_user.service_accounts[each.key].name
  permissions_boundary = aws_iam_policy.service_account_boundary.arn
  
  lifecycle {
    ignore_changes = [name, path, force_destroy, tags]
  }
  
  depends_on = [aws_iam_user.service_accounts]
}

# Set Permission Boundaries for Service Accounts
resource "aws_iam_user" "cicd_with_boundary" {
  name                 = aws_iam_user.cicd_service_account.name
  permissions_boundary = aws_iam_policy.service_account_boundary.arn
  
  lifecycle {
    ignore_changes = [name, path, force_destroy, tags]
  }
  
  depends_on = [aws_iam_user.cicd_service_account]
}

resource "aws_iam_user" "monitoring_with_boundary" {
  name                 = aws_iam_user.monitoring_service_account.name
  permissions_boundary = aws_iam_policy.service_account_boundary.arn
  
  lifecycle {
    ignore_changes = [name, path, force_destroy, tags]
  }
  
  depends_on = [aws_iam_user.monitoring_service_account]
}

resource "aws_iam_user" "backup_with_boundary" {
  name                 = aws_iam_user.backup_service_account.name
  permissions_boundary = aws_iam_policy.service_account_boundary.arn
  
  lifecycle {
    ignore_changes = [name, path, force_destroy, tags]
  }
  
  depends_on = [aws_iam_user.backup_service_account]
}

resource "aws_iam_user" "logging_with_boundary" {
  name                 = aws_iam_user.logging_service_account.name
  permissions_boundary = aws_iam_policy.service_account_boundary.arn
  
  lifecycle {
    ignore_changes = [name, path, force_destroy, tags]
  }
  
  depends_on = [aws_iam_user.logging_service_account]
}

# Attach Policies to Terraform Execution Role
resource "aws_iam_role_policy_attachment" "terraform_role_power_user" {
  role       = aws_iam_role.terraform_execution_role.name
  policy_arn = local.managed_policies.power_user_access
}

# Custom Terraform Policy for IAM Operations
resource "aws_iam_role_policy" "terraform_iam_operations" {
  name = "${local.name_prefix}-terraform-iam-operations"
  role = aws_iam_role.terraform_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "iam:CreateRole",
          "iam:CreateUser",
          "iam:CreateGroup",
          "iam:CreatePolicy",
          "iam:AttachRolePolicy",
          "iam:AttachUserPolicy",
          "iam:AttachGroupPolicy",
          "iam:PutRolePolicy",
          "iam:PutUserPolicy",
          "iam:PutGroupPolicy",
          "iam:TagRole",
          "iam:TagUser",
          "iam:TagPolicy",
          "iam:CreateInstanceProfile",
          "iam:AddRoleToInstanceProfile"
        ]
        Resource = "*"
        Condition = {
          StringLike = {
            "iam:ResourceTag/Project" = var.project_name
          }
        }
      },
      {
        Effect = "Allow"
        Action = [
          "iam:PassRole"
        ]
        Resource = "arn:aws:iam::${local.account_id}:role/${local.name_prefix}-*"
      }
    ]
  })
}

# Attach Monitoring Policies
resource "aws_iam_role_policy_attachment" "monitoring_service_cloudwatch" {
  role       = aws_iam_role.monitoring_service_role.name
  policy_arn = aws_iam_policy.cloudwatch_logs_access.arn
}

# Attach ECR Policies to CI/CD Service Account
resource "aws_iam_user_policy_attachment" "cicd_ecr_access" {
  user       = aws_iam_user.cicd_service_account.name
  policy_arn = aws_iam_policy.ecr_repository_access.arn
}

resource "aws_iam_user_policy_attachment" "cicd_ssm_access" {
  user       = aws_iam_user.cicd_service_account.name
  policy_arn = aws_iam_policy.ssm_parameter_access.arn
}

# Create Instance Profile Associations
resource "aws_iam_role_policy_attachment" "bastion_host_ssm" {
  role       = aws_iam_role.bastion_host_role.name
  policy_arn = aws_iam_policy.ssm_parameter_access.arn
}

# Data Processing Role Attachments
resource "aws_iam_role_policy_attachment" "data_processor_s3" {
  role       = aws_iam_role.data_processor_role.name
  policy_arn = aws_iam_policy.s3_bucket_access.arn
}

resource "aws_iam_role_policy_attachment" "data_processor_rds" {
  role       = aws_iam_role.data_processor_role.name
  policy_arn = aws_iam_policy.rds_database_access.arn
}

resource "aws_iam_role_policy_attachment" "data_processor_secrets" {
  role       = aws_iam_role.data_processor_role.name
  policy_arn = aws_iam_policy.secrets_manager_access.arn
}

# Monitoring Service Account Attachments
resource "aws_iam_user_policy_attachment" "monitoring_logs_access" {
  user       = aws_iam_user.monitoring_service_account.name
  policy_arn = aws_iam_policy.cloudwatch_logs_access.arn
}

# Backup Service Account Attachments
resource "aws_iam_user_policy_attachment" "backup_s3_access" {
  user       = aws_iam_user.backup_service_account.name
  policy_arn = aws_iam_policy.s3_bucket_access.arn
}

# Logging Service Account Attachments
resource "aws_iam_user_policy_attachment" "logging_logs_access" {
  user       = aws_iam_user.logging_service_account.name
  policy_arn = aws_iam_policy.cloudwatch_logs_access.arn
}

resource "aws_iam_user_policy_attachment" "logging_s3_access" {
  user       = aws_iam_user.logging_service_account.name
  policy_arn = aws_iam_policy.s3_bucket_access.arn
}

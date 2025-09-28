# IAM roles and policies for JupyterHub business users
# Provides access to Risk Platform resources with appropriate permissions

# JupyterHub Service Role
resource "aws_iam_role" "jupyterhub_role" {
  name = "${local.name_prefix}-jupyterhub-role"
  
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
            "${replace(var.eks_cluster_name, "${local.name_prefix}-", "")}:sub" = "system:serviceaccount:${local.jupyterhub_namespace}:${local.jupyterhub_service_account}"
            "${replace(var.eks_cluster_name, "${local.name_prefix}-", "")}:aud" = "sts.amazonaws.com"
          }
        }
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-jupyterhub-role"
    Description = "Service role for JupyterHub platform"
    Application = "jupyterhub"
    Service     = "EKS"
  })
}

# JupyterHub Service Policy
resource "aws_iam_role_policy" "jupyterhub_service_policy" {
  name = "${local.name_prefix}-jupyterhub-service-policy"
  role = aws_iam_role.jupyterhub_role.id

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
          "arn:aws:secretsmanager:${local.region}:${local.account_id}:secret:${local.name_prefix}-jupyterhub-secrets-*",
          "arn:aws:secretsmanager:${local.region}:${local.account_id}:secret:${local.name_prefix}-db-credentials-*"
        ]
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
          "${aws_s3_bucket.jupyterhub_backups.arn}",
          "${aws_s3_bucket.jupyterhub_backups.arn}/*"
        ]
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
        Resource = [
          "arn:aws:logs:${local.region}:${local.account_id}:log-group:/aws/eks/${local.cluster_name}/jupyterhub*",
          "arn:aws:logs:${local.region}:${local.account_id}:log-group:/aws/eks/${local.cluster_name}/jupyterhub*:*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ]
        Resource = [
          aws_ecr_repository.jupyterhub_management.arn,
          aws_ecr_repository.jupyterhub_notebook.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "elasticfilesystem:AccessPointExists",
          "elasticfilesystem:AccessedViaMountTarget"
        ]
        Resource = aws_efs_access_point.jupyterhub_shared.arn
      }
    ]
  })
}

# Business User Role for JupyterHub
resource "aws_iam_role" "jupyterhub_business_user_role" {
  name = "${local.name_prefix}-jupyterhub-business-user-role"
  
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
            "${replace(var.eks_cluster_name, "${local.name_prefix}-", "")}:sub" = "system:serviceaccount:${local.jupyterhub_namespace}:jupyterhub-user-pods"
            "${replace(var.eks_cluster_name, "${local.name_prefix}-", "")}:aud" = "sts.amazonaws.com"
          }
        }
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-jupyterhub-business-user-role"
    Description = "Role for business users accessing JupyterHub notebooks"
    Application = "jupyterhub"
    UserType    = "business-user"
    Service     = "EKS"
  })
}

# Business User Policy - Read-only access to Risk Platform APIs
resource "aws_iam_role_policy" "jupyterhub_business_user_policy" {
  name = "${local.name_prefix}-jupyterhub-business-user-policy"
  role = aws_iam_role.jupyterhub_business_user_role.id

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
          "arn:aws:s3:::${local.name_prefix}-risk-data/*",
          "arn:aws:s3:::${local.name_prefix}-risk-data"
        ]
        Condition = {
          StringLike = {
            "s3:prefix": [
              "public/*",
              "business-users/*",
              "reports/*"
            ]
          }
        }
      },
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = [
          "${aws_s3_bucket.jupyterhub_backups.arn}/business-users/*"
        ]
      },
      {
        Effect = "Deny"
        Action = [
          "rds:*",
          "secretsmanager:*"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = [
          "arn:aws:logs:${local.region}:${local.account_id}:log-group:/aws/eks/${local.cluster_name}/jupyterhub-notebooks*"
        ]
      }
    ]
  })
}

# Data Scientist Role for JupyterHub
resource "aws_iam_role" "jupyterhub_data_scientist_role" {
  name = "${local.name_prefix}-jupyterhub-data-scientist-role"
  
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
            "${replace(var.eks_cluster_name, "${local.name_prefix}-", "")}:sub" = "system:serviceaccount:${local.jupyterhub_namespace}:jupyterhub-user-pods"
            "${replace(var.eks_cluster_name, "${local.name_prefix}-", "")}:aud" = "sts.amazonaws.com"
          }
        }
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-jupyterhub-data-scientist-role"
    Description = "Role for data scientists with enhanced access to Risk Platform"
    Application = "jupyterhub"
    UserType    = "data-scientist"
    Service     = "EKS"
  })
}

# Data Scientist Policy - Enhanced access for model development
resource "aws_iam_role_policy" "jupyterhub_data_scientist_policy" {
  name = "${local.name_prefix}-jupyterhub-data-scientist-policy"
  role = aws_iam_role.jupyterhub_data_scientist_role.id

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
          "arn:aws:s3:::${local.name_prefix}-risk-data/*",
          "arn:aws:s3:::${local.name_prefix}-risk-data",
          "${aws_s3_bucket.jupyterhub_backups.arn}/data-scientists/*",
          "${aws_s3_bucket.jupyterhub_backups.arn}/models/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          "arn:aws:secretsmanager:${local.region}:${local.account_id}:secret:${local.name_prefix}-api-keys-*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "rds:DescribeDBInstances"
        ]
        Resource = "arn:aws:rds:${local.region}:${local.account_id}:db:${var.rds_instance_identifier}"
      },
      {
        Effect = "Allow"
        Action = [
          "sagemaker:CreateModel",
          "sagemaker:CreateEndpoint",
          "sagemaker:CreateEndpointConfig",
          "sagemaker:InvokeEndpoint",
          "sagemaker:DescribeModel",
          "sagemaker:DescribeEndpoint",
          "sagemaker:ListModels",
          "sagemaker:ListEndpoints"
        ]
        Resource = [
          "arn:aws:sagemaker:${local.region}:${local.account_id}:model/${local.name_prefix}-*",
          "arn:aws:sagemaker:${local.region}:${local.account_id}:endpoint/${local.name_prefix}-*",
          "arn:aws:sagemaker:${local.region}:${local.account_id}:endpoint-config/${local.name_prefix}-*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = [
          "arn:aws:logs:${local.region}:${local.account_id}:log-group:/aws/eks/${local.cluster_name}/jupyterhub-notebooks*"
        ]
      }
    ]
  })
}

# Admin Role for JupyterHub
resource "aws_iam_role" "jupyterhub_admin_role" {
  name = "${local.name_prefix}-jupyterhub-admin-role"
  
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
            "${replace(var.eks_cluster_name, "${local.name_prefix}-", "")}:sub" = "system:serviceaccount:${local.jupyterhub_namespace}:jupyterhub-user-pods"
            "${replace(var.eks_cluster_name, "${local.name_prefix}-", "")}:aud" = "sts.amazonaws.com"
          }
        }
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-jupyterhub-admin-role"
    Description = "Administrative role for JupyterHub platform management"
    Application = "jupyterhub"
    UserType    = "admin"
    Service     = "EKS"
  })
}

# Admin Policy - Full access for platform management
resource "aws_iam_role_policy" "jupyterhub_admin_policy" {
  name = "${local.name_prefix}-jupyterhub-admin-policy"
  role = aws_iam_role.jupyterhub_admin_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:*"
        ]
        Resource = [
          "arn:aws:s3:::${local.name_prefix}-*",
          "arn:aws:s3:::${local.name_prefix}-*/*",
          "${aws_s3_bucket.jupyterhub_backups.arn}",
          "${aws_s3_bucket.jupyterhub_backups.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:ListSecrets"
        ]
        Resource = [
          "arn:aws:secretsmanager:${local.region}:${local.account_id}:secret:${local.name_prefix}-*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "rds:DescribeDBInstances",
          "rds:DescribeDBClusters",
          "rds:ListTagsForResource"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "eks:DescribeCluster",
          "eks:ListClusters",
          "eks:DescribeNodegroup"
        ]
        Resource = "*"
      },
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
          "logs:*"
        ]
        Resource = [
          "arn:aws:logs:${local.region}:${local.account_id}:log-group:/aws/eks/${local.cluster_name}/*"
        ]
      }
    ]
  })
}

# Service Account for JupyterHub User Pods
resource "kubernetes_service_account" "jupyterhub_user_pods" {
  metadata {
    name      = "jupyterhub-user-pods"
    namespace = kubernetes_namespace.jupyterhub.metadata[0].name
    
    annotations = {
      "eks.amazonaws.com/role-arn" = aws_iam_role.jupyterhub_business_user_role.arn
      "kubernetes.io/managed-by" = "terraform"
    }
    
    labels = {
      "app.kubernetes.io/name" = "jupyterhub"
      "app.kubernetes.io/component" = "user-pods"
    }
  }
}

# RBAC ClusterRole for JupyterHub
resource "kubernetes_cluster_role" "jupyterhub" {
  metadata {
    name = "${local.name_prefix}-jupyterhub-role"
    
    labels = {
      "app.kubernetes.io/name" = "jupyterhub"
      "app.kubernetes.io/component" = "rbac"
    }
  }
  
  rule {
    api_groups = [""]
    resources  = ["pods", "services", "configmaps", "secrets", "persistentvolumeclaims"]
    verbs      = ["create", "get", "list", "delete", "patch", "update"]
  }
  
  rule {
    api_groups = ["apps"]
    resources  = ["deployments", "replicasets"]
    verbs      = ["create", "get", "list", "delete", "patch", "update"]
  }
  
  rule {
    api_groups = [""]
    resources  = ["events"]
    verbs      = ["get", "list", "watch"]
  }
  
  rule {
    api_groups = [""]
    resources  = ["nodes"]
    verbs      = ["get", "list"]
  }
}

# RBAC ClusterRoleBinding for JupyterHub
resource "kubernetes_cluster_role_binding" "jupyterhub" {
  metadata {
    name = "${local.name_prefix}-jupyterhub-binding"
    
    labels = {
      "app.kubernetes.io/name" = "jupyterhub"
      "app.kubernetes.io/component" = "rbac"
    }
  }
  
  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = kubernetes_cluster_role.jupyterhub.metadata[0].name
  }
  
  subject {
    kind      = "ServiceAccount"
    name      = kubernetes_service_account.jupyterhub.metadata[0].name
    namespace = kubernetes_namespace.jupyterhub.metadata[0].name
  }
}

# Role for user pod management within namespace
resource "kubernetes_role" "jupyterhub_user_pods" {
  metadata {
    name      = "jupyterhub-user-pods"
    namespace = kubernetes_namespace.jupyterhub.metadata[0].name
    
    labels = {
      "app.kubernetes.io/name" = "jupyterhub"
      "app.kubernetes.io/component" = "rbac"
    }
  }
  
  rule {
    api_groups = [""]
    resources  = ["pods", "configmaps", "secrets", "persistentvolumeclaims"]
    verbs      = ["create", "get", "list", "delete", "patch", "update", "watch"]
  }
  
  rule {
    api_groups = [""]
    resources  = ["services"]
    verbs      = ["create", "get", "list", "delete", "patch", "update"]
  }
  
  rule {
    api_groups = ["apps"]
    resources  = ["deployments"]
    verbs      = ["create", "get", "list", "delete", "patch", "update"]
  }
  
  rule {
    api_groups = [""]
    resources  = ["events"]
    verbs      = ["get", "list", "watch"]
  }
}

# RoleBinding for user pods
resource "kubernetes_role_binding" "jupyterhub_user_pods" {
  metadata {
    name      = "jupyterhub-user-pods"
    namespace = kubernetes_namespace.jupyterhub.metadata[0].name
    
    labels = {
      "app.kubernetes.io/name" = "jupyterhub"
      "app.kubernetes.io/component" = "rbac"
    }
  }
  
  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "Role"
    name      = kubernetes_role.jupyterhub_user_pods.metadata[0].name
  }
  
  subject {
    kind      = "ServiceAccount"
    name      = kubernetes_service_account.jupyterhub_user_pods.metadata[0].name
    namespace = kubernetes_namespace.jupyterhub.metadata[0].name
  }
}

# Business User Group (for corporate LDAP integration)
resource "aws_iam_group" "jupyterhub_business_users" {
  name = "${local.name_prefix}-jupyterhub-business-users"
  path = "/jupyterhub/"
}

# Policy attachment for business users group
resource "aws_iam_group_policy_attachment" "jupyterhub_business_users" {
  group      = aws_iam_group.jupyterhub_business_users.name
  policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
}

# Data Scientists Group
resource "aws_iam_group" "jupyterhub_data_scientists" {
  name = "${local.name_prefix}-jupyterhub-data-scientists"
  path = "/jupyterhub/"
}

# Admins Group
resource "aws_iam_group" "jupyterhub_admins" {
  name = "${local.name_prefix}-jupyterhub-admins"
  path = "/jupyterhub/"
}

# Outputs
output "jupyterhub_service_role_arn" {
  description = "ARN of JupyterHub service role"
  value       = aws_iam_role.jupyterhub_role.arn
}

output "jupyterhub_business_user_role_arn" {
  description = "ARN of business user role for JupyterHub"
  value       = aws_iam_role.jupyterhub_business_user_role.arn
}

output "jupyterhub_data_scientist_role_arn" {
  description = "ARN of data scientist role for JupyterHub"
  value       = aws_iam_role.jupyterhub_data_scientist_role.arn
}

output "jupyterhub_admin_role_arn" {
  description = "ARN of admin role for JupyterHub"
  value       = aws_iam_role.jupyterhub_admin_role.arn
}
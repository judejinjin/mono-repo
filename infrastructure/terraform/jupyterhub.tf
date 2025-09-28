# JupyterHub Infrastructure Components
# EKS deployment with persistent storage and business user access

locals {
  jupyterhub_namespace = "jupyterhub"
  jupyterhub_service_account = "jupyterhub-service-account"
}

# Kubernetes namespace for JupyterHub
resource "kubernetes_namespace" "jupyterhub" {
  metadata {
    name = local.jupyterhub_namespace
    
    labels = {
      name = local.jupyterhub_namespace
      "app.kubernetes.io/name" = "jupyterhub"
      "app.kubernetes.io/component" = "notebook-platform"
      "app.kubernetes.io/part-of" = "risk-platform"
      environment = var.environment
    }
    
    annotations = {
      "kubernetes.io/managed-by" = "terraform"
      "deployment.kubernetes.io/revision" = "1"
    }
  }
  
  depends_on = [module.eks]
}

# JupyterHub Service Account
resource "kubernetes_service_account" "jupyterhub" {
  metadata {
    name      = local.jupyterhub_service_account
    namespace = kubernetes_namespace.jupyterhub.metadata[0].name
    
    annotations = {
      "eks.amazonaws.com/role-arn" = aws_iam_role.jupyterhub_role.arn
      "kubernetes.io/managed-by" = "terraform"
    }
    
    labels = {
      "app.kubernetes.io/name" = "jupyterhub"
      "app.kubernetes.io/component" = "service-account"
    }
  }
  
  depends_on = [aws_iam_role.jupyterhub_role]
}

# Persistent Volume for JupyterHub shared storage
resource "kubernetes_persistent_volume" "jupyterhub_shared" {
  metadata {
    name = "${local.name_prefix}-jupyterhub-shared-pv"
    
    labels = {
      "app.kubernetes.io/name" = "jupyterhub"
      "app.kubernetes.io/component" = "storage"
    }
  }
  
  spec {
    capacity = {
      storage = "100Gi"
    }
    
    access_modes = ["ReadWriteMany"]
    storage_class_name = "efs-sc"
    
    persistent_volume_source {
      csi {
        driver = "efs.csi.aws.com"
        volume_handle = aws_efs_file_system.jupyterhub_efs.id
        volume_attributes = {
          path = "/"
        }
      }
    }
  }
  
  depends_on = [aws_efs_file_system.jupyterhub_efs]
}

# Persistent Volume Claim for shared storage
resource "kubernetes_persistent_volume_claim" "jupyterhub_shared" {
  metadata {
    name      = "jupyterhub-shared-pvc"
    namespace = kubernetes_namespace.jupyterhub.metadata[0].name
    
    labels = {
      "app.kubernetes.io/name" = "jupyterhub"
      "app.kubernetes.io/component" = "storage"
    }
  }
  
  spec {
    access_modes = ["ReadWriteMany"]
    storage_class_name = "efs-sc"
    
    resources {
      requests = {
        storage = "100Gi"
      }
    }
    
    volume_name = kubernetes_persistent_volume.jupyterhub_shared.metadata[0].name
  }
  
  depends_on = [kubernetes_persistent_volume.jupyterhub_shared]
}

# ConfigMap for JupyterHub configuration
resource "kubernetes_config_map" "jupyterhub_config" {
  metadata {
    name      = "jupyterhub-config"
    namespace = kubernetes_namespace.jupyterhub.metadata[0].name
    
    labels = {
      "app.kubernetes.io/name" = "jupyterhub"
      "app.kubernetes.io/component" = "config"
    }
  }
  
  data = {
    "jupyterhub_config.py" = templatefile("${path.module}/templates/jupyterhub_config.py.tpl", {
      environment = var.environment
      risk_api_url = "http://fastapi-service.default.svc.cluster.local"
      shared_storage_path = "/home/jovyan/shared"
      corporate_domain = var.corporate_domain
    })
    
    "requirements.txt" = file("${path.module}/templates/jupyterhub_requirements.txt")
  }
}

# Secret for JupyterHub API tokens and database credentials
resource "kubernetes_secret" "jupyterhub_secrets" {
  metadata {
    name      = "jupyterhub-secrets"
    namespace = kubernetes_namespace.jupyterhub.metadata[0].name
    
    labels = {
      "app.kubernetes.io/name" = "jupyterhub"
      "app.kubernetes.io/component" = "secrets"
    }
  }
  
  type = "Opaque"
  
  data = {
    # Generate random tokens for production deployment
    api_token = base64encode(random_password.jupyterhub_api_token.result)
    cookie_secret = base64encode(random_password.jupyterhub_cookie_secret.result)
    crypto_key = base64encode(random_password.jupyterhub_crypto_key.result)
    
    # Database connection string
    database_url = base64encode("postgresql://${aws_db_instance.rds.username}:${aws_db_instance.rds.password}@${aws_db_instance.rds.endpoint}:5432/jupyterhub")
    
    # Risk Platform integration
    risk_api_key = base64encode(random_password.risk_api_integration_key.result)
  }
  
  depends_on = [
    random_password.jupyterhub_api_token,
    random_password.jupyterhub_cookie_secret,
    random_password.jupyterhub_crypto_key,
    random_password.risk_api_integration_key,
    aws_db_instance.rds
  ]
}

# JupyterHub Hub Deployment
resource "kubernetes_deployment" "jupyterhub_hub" {
  metadata {
    name      = "jupyterhub-hub"
    namespace = kubernetes_namespace.jupyterhub.metadata[0].name
    
    labels = {
      "app.kubernetes.io/name" = "jupyterhub"
      "app.kubernetes.io/component" = "hub"
      "app.kubernetes.io/version" = "4.0.2"
    }
  }
  
  spec {
    replicas = var.environment == "prod" ? 2 : 1
    
    strategy {
      type = "RollingUpdate"
      rolling_update {
        max_unavailable = 1
        max_surge       = 1
      }
    }
    
    selector {
      match_labels = {
        "app.kubernetes.io/name" = "jupyterhub"
        "app.kubernetes.io/component" = "hub"
      }
    }
    
    template {
      metadata {
        labels = {
          "app.kubernetes.io/name" = "jupyterhub"
          "app.kubernetes.io/component" = "hub"
          "app.kubernetes.io/version" = "4.0.2"
        }
        
        annotations = {
          "prometheus.io/scrape" = "true"
          "prometheus.io/port" = "8081"
          "prometheus.io/path" = "/hub/metrics"
        }
      }
      
      spec {
        service_account_name = kubernetes_service_account.jupyterhub.metadata[0].name
        
        security_context {
          run_as_user = 1000
          run_as_group = 1000
          fs_group = 1000
        }
        
        container {
          name  = "jupyterhub"
          image = "quay.io/jupyterhub/jupyterhub:4.0.2"
          
          image_pull_policy = "IfNotPresent"
          
          port {
            name           = "http"
            container_port = 8000
            protocol       = "TCP"
          }
          
          port {
            name           = "metrics"
            container_port = 8081
            protocol       = "TCP"
          }
          
          env {
            name = "JUPYTERHUB_API_TOKEN"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.jupyterhub_secrets.metadata[0].name
                key  = "api_token"
              }
            }
          }
          
          env {
            name = "JUPYTERHUB_COOKIE_SECRET"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.jupyterhub_secrets.metadata[0].name
                key  = "cookie_secret"
              }
            }
          }
          
          env {
            name = "JUPYTERHUB_CRYPT_KEY"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.jupyterhub_secrets.metadata[0].name
                key  = "crypto_key"
              }
            }
          }
          
          env {
            name = "JUPYTERHUB_DATABASE_URL"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.jupyterhub_secrets.metadata[0].name
                key  = "database_url"
              }
            }
          }
          
          env {
            name  = "ENVIRONMENT"
            value = var.environment
          }
          
          volume_mount {
            name       = "config"
            mount_path = "/etc/jupyterhub"
            read_only  = true
          }
          
          volume_mount {
            name       = "shared-storage"
            mount_path = "/home/jovyan/shared"
          }
          
          command = [
            "jupyterhub",
            "--config",
            "/etc/jupyterhub/jupyterhub_config.py"
          ]
          
          resources {
            requests = {
              cpu    = "500m"
              memory = "1Gi"
            }
            limits = {
              cpu    = "2000m"
              memory = "4Gi"
            }
          }
          
          liveness_probe {
            http_get {
              path = "/hub/health"
              port = 8000
            }
            initial_delay_seconds = 60
            period_seconds        = 30
            timeout_seconds       = 10
            failure_threshold     = 3
          }
          
          readiness_probe {
            http_get {
              path = "/hub/health"
              port = 8000
            }
            initial_delay_seconds = 30
            period_seconds        = 10
            timeout_seconds       = 5
            failure_threshold     = 3
          }
        }
        
        volume {
          name = "config"
          config_map {
            name = kubernetes_config_map.jupyterhub_config.metadata[0].name
          }
        }
        
        volume {
          name = "shared-storage"
          persistent_volume_claim {
            claim_name = kubernetes_persistent_volume_claim.jupyterhub_shared.metadata[0].name
          }
        }
      }
    }
  }
  
  depends_on = [
    kubernetes_config_map.jupyterhub_config,
    kubernetes_secret.jupyterhub_secrets,
    kubernetes_persistent_volume_claim.jupyterhub_shared
  ]
}

# JupyterHub Management Service Deployment (FastAPI)
resource "kubernetes_deployment" "jupyterhub_management" {
  metadata {
    name      = "jupyterhub-management"
    namespace = kubernetes_namespace.jupyterhub.metadata[0].name
    
    labels = {
      "app.kubernetes.io/name" = "jupyterhub-management"
      "app.kubernetes.io/component" = "api"
    }
  }
  
  spec {
    replicas = var.environment == "prod" ? 2 : 1
    
    selector {
      match_labels = {
        "app.kubernetes.io/name" = "jupyterhub-management"
        "app.kubernetes.io/component" = "api"
      }
    }
    
    template {
      metadata {
        labels = {
          "app.kubernetes.io/name" = "jupyterhub-management"
          "app.kubernetes.io/component" = "api"
        }
        
        annotations = {
          "prometheus.io/scrape" = "true"
          "prometheus.io/port" = "8000"
        }
      }
      
      spec {
        service_account_name = kubernetes_service_account.jupyterhub.metadata[0].name
        
        container {
          name  = "jupyterhub-management"
          image = "${aws_ecr_repository.jupyterhub_management.repository_url}:${var.image_tag}"
          
          port {
            name           = "http"
            container_port = 8000
            protocol       = "TCP"
          }
          
          env {
            name  = "JUPYTERHUB_API_URL"
            value = "http://jupyterhub-service.${kubernetes_namespace.jupyterhub.metadata[0].name}.svc.cluster.local:8000"
          }
          
          env {
            name = "JUPYTERHUB_API_TOKEN"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.jupyterhub_secrets.metadata[0].name
                key  = "api_token"
              }
            }
          }
          
          env {
            name  = "RISK_API_URL"
            value = "http://fastapi-service.default.svc.cluster.local"
          }
          
          resources {
            requests = {
              cpu    = "250m"
              memory = "512Mi"
            }
            limits = {
              cpu    = "1000m"
              memory = "2Gi"
            }
          }
          
          liveness_probe {
            http_get {
              path = "/health"
              port = 8000
            }
            initial_delay_seconds = 30
            period_seconds        = 30
          }
          
          readiness_probe {
            http_get {
              path = "/health"
              port = 8000
            }
            initial_delay_seconds = 10
            period_seconds        = 10
          }
        }
      }
    }
  }
  
  depends_on = [
    kubernetes_secret.jupyterhub_secrets,
    aws_ecr_repository.jupyterhub_management
  ]
}

# JupyterHub Hub Service
resource "kubernetes_service" "jupyterhub" {
  metadata {
    name      = "jupyterhub-service"
    namespace = kubernetes_namespace.jupyterhub.metadata[0].name
    
    labels = {
      "app.kubernetes.io/name" = "jupyterhub"
      "app.kubernetes.io/component" = "hub"
    }
    
    annotations = {
      "service.beta.kubernetes.io/aws-load-balancer-type" = "nlb"
      "service.beta.kubernetes.io/aws-load-balancer-internal" = "true"
      "service.beta.kubernetes.io/aws-load-balancer-subnets" = join(",", data.aws_subnets.private.ids)
    }
  }
  
  spec {
    type = "LoadBalancer"
    
    selector = {
      "app.kubernetes.io/name" = "jupyterhub"
      "app.kubernetes.io/component" = "hub"
    }
    
    port {
      name        = "http"
      port        = 80
      target_port = 8000
      protocol    = "TCP"
    }
    
    port {
      name        = "https"
      port        = 443
      target_port = 8000
      protocol    = "TCP"
    }
    
    session_affinity = "ClientIP"
  }
}

# JupyterHub Management API Service
resource "kubernetes_service" "jupyterhub_management" {
  metadata {
    name      = "jupyterhub-management-service"
    namespace = kubernetes_namespace.jupyterhub.metadata[0].name
    
    labels = {
      "app.kubernetes.io/name" = "jupyterhub-management"
      "app.kubernetes.io/component" = "api"
    }
  }
  
  spec {
    type = "ClusterIP"
    
    selector = {
      "app.kubernetes.io/name" = "jupyterhub-management"
      "app.kubernetes.io/component" = "api"
    }
    
    port {
      name        = "http"
      port        = 8000
      target_port = 8000
      protocol    = "TCP"
    }
  }
}

# Horizontal Pod Autoscaler for JupyterHub Hub
resource "kubernetes_horizontal_pod_autoscaler_v2" "jupyterhub_hub" {
  metadata {
    name      = "jupyterhub-hub-hpa"
    namespace = kubernetes_namespace.jupyterhub.metadata[0].name
  }
  
  spec {
    scale_target_ref {
      api_version = "apps/v1"
      kind        = "Deployment"
      name        = kubernetes_deployment.jupyterhub_hub.metadata[0].name
    }
    
    min_replicas = 1
    max_replicas = var.environment == "prod" ? 5 : 3
    
    metric {
      type = "Resource"
      resource {
        name = "cpu"
        target {
          type                = "Utilization"
          average_utilization = 70
        }
      }
    }
    
    metric {
      type = "Resource"
      resource {
        name = "memory"
        target {
          type                = "Utilization"
          average_utilization = 80
        }
      }
    }
    
    behavior {
      scale_up {
        stabilization_window_seconds = 300
        policy {
          type          = "Percent"
          value         = 100
          period_seconds = 60
        }
      }
      
      scale_down {
        stabilization_window_seconds = 300
        policy {
          type          = "Percent"
          value         = 10
          period_seconds = 60
        }
      }
    }
  }
}

# Network Policy for JupyterHub
resource "kubernetes_network_policy" "jupyterhub" {
  metadata {
    name      = "jupyterhub-network-policy"
    namespace = kubernetes_namespace.jupyterhub.metadata[0].name
  }
  
  spec {
    pod_selector {
      match_labels = {
        "app.kubernetes.io/name" = "jupyterhub"
      }
    }
    
    policy_types = ["Ingress", "Egress"]
    
    # Allow ingress from load balancer and within namespace
    ingress {
      ports {
        port     = "8000"
        protocol = "TCP"
      }
      
      # Allow from load balancer
      from {
        namespace_selector {
          match_labels = {
            name = "kube-system"
          }
        }
      }
      
      # Allow from same namespace
      from {
        namespace_selector {
          match_labels = {
            name = kubernetes_namespace.jupyterhub.metadata[0].name
          }
        }
      }
    }
    
    # Allow egress to Risk API and external services
    egress {
      # Allow to Risk API
      to {
        namespace_selector {
          match_labels = {
            name = "default"
          }
        }
      }
      
      ports {
        port     = "8000"
        protocol = "TCP"
      }
    }
    
    egress {
      # Allow to database
      to {}
      ports {
        port     = "5432"
        protocol = "TCP"
      }
    }
    
    egress {
      # Allow DNS resolution
      to {}
      ports {
        port     = "53"
        protocol = "UDP"
      }
    }
  }
}

# Random passwords for JupyterHub secrets
resource "random_password" "jupyterhub_api_token" {
  length  = 64
  special = false
}

resource "random_password" "jupyterhub_cookie_secret" {
  length  = 64
  special = false
}

resource "random_password" "jupyterhub_crypto_key" {
  length  = 64
  special = false
}

resource "random_password" "risk_api_integration_key" {
  length  = 32
  special = false
}

# Outputs
output "jupyterhub_namespace" {
  description = "JupyterHub Kubernetes namespace"
  value       = kubernetes_namespace.jupyterhub.metadata[0].name
}

output "jupyterhub_service_endpoint" {
  description = "JupyterHub service endpoint"
  value       = kubernetes_service.jupyterhub.status[0].load_balancer[0].ingress[0].hostname
}

output "jupyterhub_management_endpoint" {
  description = "JupyterHub management API endpoint"
  value       = "http://jupyterhub-management-service.${kubernetes_namespace.jupyterhub.metadata[0].name}.svc.cluster.local:8000"
}
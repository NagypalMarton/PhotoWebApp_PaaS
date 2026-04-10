locals {
  labels = {
    app = "photowebapp"
  }

  database_url = "mysql+pymysql://${var.mysql_user}:${var.mysql_password}@mysql:3306/${var.mysql_database}"
}

resource "kubernetes_namespace_v1" "app" {
  metadata {
    name   = var.namespace
    labels = local.labels
  }
}

resource "kubernetes_secret_v1" "app_secrets" {
  metadata {
    name      = "photowebapp-secrets"
    namespace = kubernetes_namespace_v1.app.metadata[0].name
  }

  type = "Opaque"

  string_data = {
    MYSQL_DATABASE      = var.mysql_database
    MYSQL_USER          = var.mysql_user
    MYSQL_PASSWORD      = var.mysql_password
    MYSQL_ROOT_PASSWORD = var.mysql_root_password
    SECRET_KEY          = var.backend_secret_key
    FLASK_SECRET_KEY    = var.frontend_secret_key
    DATABASE_URL        = local.database_url
  }
}

resource "kubernetes_persistent_volume_claim_v1" "mysql" {
  metadata {
    name      = "mysql-pvc"
    namespace = kubernetes_namespace_v1.app.metadata[0].name
  }

  spec {
    access_modes = ["ReadWriteOnce"]
    resources {
      requests = {
        storage = var.mysql_storage_size
      }
    }
  }

  lifecycle {
    prevent_destroy = true
  }
}

resource "kubernetes_deployment_v1" "mysql" {
  metadata {
    name      = "mysql"
    namespace = kubernetes_namespace_v1.app.metadata[0].name
    labels = {
      app = "mysql"
    }
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "mysql"
      }
    }

    strategy {
      type = "Recreate"
    }

    template {
      metadata {
        labels = {
          app = "mysql"
        }
      }

      spec {
        container {
          name  = "mysql"
          image = var.mysql_image

          port {
            container_port = 3306
          }

          resources {
            requests = {
              cpu    = "200m"
              memory = "512Mi"
            }
            limits = {
              cpu    = "500m"
              memory = "1Gi"
            }
          }

          env {
            name = "MYSQL_DATABASE"
            value_from {
              secret_key_ref {
                name = kubernetes_secret_v1.app_secrets.metadata[0].name
                key  = "MYSQL_DATABASE"
              }
            }
          }

          env {
            name = "MYSQL_USER"
            value_from {
              secret_key_ref {
                name = kubernetes_secret_v1.app_secrets.metadata[0].name
                key  = "MYSQL_USER"
              }
            }
          }

          env {
            name = "MYSQL_PASSWORD"
            value_from {
              secret_key_ref {
                name = kubernetes_secret_v1.app_secrets.metadata[0].name
                key  = "MYSQL_PASSWORD"
              }
            }
          }

          env {
            name = "MYSQL_ROOT_PASSWORD"
            value_from {
              secret_key_ref {
                name = kubernetes_secret_v1.app_secrets.metadata[0].name
                key  = "MYSQL_ROOT_PASSWORD"
              }
            }
          }

          volume_mount {
            name       = "mysql-storage"
            mount_path = "/var/lib/mysql"
          }
        }

        volume {
          name = "mysql-storage"
          persistent_volume_claim {
            claim_name = kubernetes_persistent_volume_claim_v1.mysql.metadata[0].name
          }
        }
      }
    }
  }
}

resource "kubernetes_service_v1" "mysql" {
  metadata {
    name      = "mysql"
    namespace = kubernetes_namespace_v1.app.metadata[0].name
  }

  spec {
    selector = {
      app = "mysql"
    }

    port {
      name        = "mysql"
      port        = 3306
      target_port = 3306
      protocol    = "TCP"
    }
  }
}

resource "kubernetes_deployment_v1" "backend" {
  metadata {
    name      = "backend"
    namespace = kubernetes_namespace_v1.app.metadata[0].name
    labels = {
      app = "backend"
    }
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "backend"
      }
    }

    strategy {
      type = "RollingUpdate"
    }

    template {
      metadata {
        labels = {
          app = "backend"
        }
      }

      spec {
        init_container {
          name  = "wait-for-mysql"
          image = "busybox:1.36"
          command = [
            "sh",
            "-c",
            "until nc -z mysql 3306; do echo waiting for mysql; sleep 2; done;"
          ]
        }

        init_container {
          name  = "migrate-photo-schema"
          image = var.backend_image
          command = [
            "python",
            "/app/migrate_photo_schema.py"
          ]

          env {
            name = "DATABASE_URL"
            value_from {
              secret_key_ref {
                name = kubernetes_secret_v1.app_secrets.metadata[0].name
                key  = "DATABASE_URL"
              }
            }
          }
        }

        container {
          name              = "backend"
          image             = var.backend_image
          image_pull_policy = "Always"

          port {
            container_port = 5001
          }

          resources {
            requests = {
              cpu    = "50m"
              memory = "128Mi"
            }
            limits = {
              cpu    = "250m"
              memory = "512Mi"
            }
          }

          env {
            name = "DATABASE_URL"
            value_from {
              secret_key_ref {
                name = kubernetes_secret_v1.app_secrets.metadata[0].name
                key  = "DATABASE_URL"
              }
            }
          }

          env {
            name = "SECRET_KEY"
            value_from {
              secret_key_ref {
                name = kubernetes_secret_v1.app_secrets.metadata[0].name
                key  = "SECRET_KEY"
              }
            }
          }
        }
      }
    }
  }

  depends_on = [kubernetes_service_v1.mysql]
}

resource "kubernetes_service_v1" "backend" {
  metadata {
    name      = "backend"
    namespace = kubernetes_namespace_v1.app.metadata[0].name
  }

  spec {
    selector = {
      app = "backend"
    }

    port {
      name        = "http"
      port        = 5001
      target_port = 5001
      protocol    = "TCP"
    }
  }
}

resource "kubernetes_deployment_v1" "frontend" {
  metadata {
    name      = "frontend"
    namespace = kubernetes_namespace_v1.app.metadata[0].name
    labels = {
      app = "frontend"
    }
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "frontend"
      }
    }

    strategy {
      type = "RollingUpdate"
    }

    template {
      metadata {
        labels = {
          app = "frontend"
        }
      }

      spec {
        init_container {
          name  = "wait-for-backend"
          image = "busybox:1.36"
          command = [
            "sh",
            "-c",
            "until nc -z backend 5001; do echo waiting for backend; sleep 2; done;"
          ]
        }

        container {
          name              = "frontend"
          image             = var.frontend_image
          image_pull_policy = "Always"

          port {
            container_port = 5000
          }

          resources {
            requests = {
              cpu    = "50m"
              memory = "128Mi"
            }
            limits = {
              cpu    = "250m"
              memory = "512Mi"
            }
          }

          env {
            name  = "BACKEND_URL"
            value = "http://backend:5001"
          }

          env {
            name = "FLASK_SECRET_KEY"
            value_from {
              secret_key_ref {
                name = kubernetes_secret_v1.app_secrets.metadata[0].name
                key  = "FLASK_SECRET_KEY"
              }
            }
          }
        }
      }
    }
  }

  depends_on = [kubernetes_service_v1.backend]
}

resource "kubernetes_service_v1" "frontend" {
  metadata {
    name      = "frontend"
    namespace = kubernetes_namespace_v1.app.metadata[0].name
  }

  spec {
    selector = {
      app = "frontend"
    }

    port {
      name        = "http"
      port        = 80
      target_port = 5000
      protocol    = "TCP"
    }

    type = "ClusterIP"
  }
}

resource "kubectl_manifest" "frontend_route" {
  yaml_body = <<-YAML
    apiVersion: route.openshift.io/v1
    kind: Route
    metadata:
      name: frontend
      namespace: ${var.namespace}
    spec:
      to:
        kind: Service
        name: frontend
      port:
        targetPort: http
      tls:
        termination: edge
        insecureEdgeTerminationPolicy: Redirect
  YAML

  depends_on = [kubernetes_service_v1.frontend]
}

resource "kubernetes_network_policy_v1" "default_deny_ingress" {
  metadata {
    name      = "default-deny-ingress"
    namespace = kubernetes_namespace_v1.app.metadata[0].name
  }

  spec {
    pod_selector {}
    policy_types = ["Ingress"]
  }
}

resource "kubernetes_network_policy_v1" "allow_mysql_from_backend" {
  metadata {
    name      = "allow-mysql-from-backend"
    namespace = kubernetes_namespace_v1.app.metadata[0].name
  }

  spec {
    pod_selector {
      match_labels = {
        app = "mysql"
      }
    }

    ingress {
      from {
        pod_selector {
          match_labels = {
            app = "backend"
          }
        }
      }

      ports {
        protocol = "TCP"
        port     = "3306"
      }
    }

    policy_types = ["Ingress"]
  }
}

resource "kubernetes_network_policy_v1" "allow_backend_from_frontend" {
  metadata {
    name      = "allow-backend-from-frontend"
    namespace = kubernetes_namespace_v1.app.metadata[0].name
  }

  spec {
    pod_selector {
      match_labels = {
        app = "backend"
      }
    }

    ingress {
      from {
        pod_selector {
          match_labels = {
            app = "frontend"
          }
        }
      }

      ports {
        protocol = "TCP"
        port     = "5001"
      }
    }

    policy_types = ["Ingress"]
  }
}

resource "kubernetes_network_policy_v1" "allow_frontend_from_router" {
  metadata {
    name      = "allow-frontend-from-router"
    namespace = kubernetes_namespace_v1.app.metadata[0].name
  }

  spec {
    pod_selector {
      match_labels = {
        app = "frontend"
      }
    }

    ingress {
      from {
        namespace_selector {
          match_labels = {
            "network.openshift.io/policy-group" = "ingress"
          }
        }
      }

      ports {
        protocol = "TCP"
        port     = "5000"
      }
    }

    policy_types = ["Ingress"]
  }
}

resource "kubernetes_horizontal_pod_autoscaler_v2" "frontend" {
  count = var.enable_hpa ? 1 : 0

  metadata {
    name      = "frontend-hpa"
    namespace = kubernetes_namespace_v1.app.metadata[0].name
  }

  spec {
    min_replicas = 1
    max_replicas = 5

    scale_target_ref {
      api_version = "apps/v1"
      kind        = "Deployment"
      name        = kubernetes_deployment_v1.frontend.metadata[0].name
    }

    metric {
      type = "Resource"
      resource {
        name = "cpu"
        target {
          type                = "Utilization"
          average_utilization = 75
        }
      }
    }

    behavior {
      scale_up {
        stabilization_window_seconds = 15

        policy {
          type           = "Pods"
          value          = 2
          period_seconds = 30
        }
      }

      scale_down {
        stabilization_window_seconds = 30

        policy {
          type           = "Pods"
          value          = 1
          period_seconds = 60
        }
      }
    }
  }
}

resource "kubernetes_horizontal_pod_autoscaler_v2" "backend" {
  count = var.enable_hpa ? 1 : 0

  metadata {
    name      = "backend-hpa"
    namespace = kubernetes_namespace_v1.app.metadata[0].name
  }

  spec {
    min_replicas = 1
    max_replicas = 5

    scale_target_ref {
      api_version = "apps/v1"
      kind        = "Deployment"
      name        = kubernetes_deployment_v1.backend.metadata[0].name
    }

    metric {
      type = "Resource"
      resource {
        name = "cpu"
        target {
          type                = "Utilization"
          average_utilization = 75
        }
      }
    }

    behavior {
      scale_up {
        stabilization_window_seconds = 15

        policy {
          type           = "Pods"
          value          = 2
          period_seconds = 30
        }
      }

      scale_down {
        stabilization_window_seconds = 30

        policy {
          type           = "Pods"
          value          = 1
          period_seconds = 60
        }
      }
    }
  }
}

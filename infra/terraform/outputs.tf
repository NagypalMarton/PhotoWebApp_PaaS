output "namespace" {
  description = "Namespace where resources are deployed"
  value       = kubernetes_namespace_v1.app.metadata[0].name
}

output "frontend_service" {
  description = "Frontend service DNS name inside the namespace"
  value       = "frontend.${kubernetes_namespace_v1.app.metadata[0].name}.svc"
}

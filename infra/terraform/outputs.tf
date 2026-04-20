output "namespace" {
  description = "Namespace where resources are deployed"
  value       = local.namespace_name
}

output "frontend_service" {
  description = "Frontend service DNS name inside the namespace"
  value       = "frontend.${local.namespace_name}.svc"
}

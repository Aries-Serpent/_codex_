output "kubernetes_cluster_name" {
  description = "GKE Cluster Name"
  value       = google_container_cluster.primary.name
  depends_on  = [google_container_node_pool.primary_nodes]
}

output "region" {
  description = "GCP region"
  value       = var.gcp_region
}

output "project_id" {
  description = "GCP project ID"
  value       = var.gcp_project
}

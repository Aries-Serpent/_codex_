variable "gcp_project" {
  description = "GCP project ID"
  type        = string
}

variable "gcp_region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "cluster_name" {
  description = "Cluster name"
  type        = string
  default     = "codex-prod-gke"
}

variable "environment" {
  description = "Environment"
  type        = string
  default     = "prod"
}

variable "subnet_cidr" {
  description = "Subnet CIDR range"
  type        = string
  default     = "10.0.0.0/16"
}

variable "azure_region" {
  description = "Azure region"
  type        = string
  default     = "eastus"
}

variable "cluster_name" {
  description = "AKS cluster name"
  type        = string
  default     = "codex-prod-aks"
}

variable "environment" {
  description = "Environment"
  type        = string
  default     = "prod"
}

variable "kubernetes_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.28.0"
}

variable "vnet_cidr" {
  description = "Virtual network CIDR"
  type        = string
  default     = "10.0.0.0/16"
}

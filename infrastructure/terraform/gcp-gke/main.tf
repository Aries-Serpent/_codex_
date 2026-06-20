# GCP GKE Cluster Configuration - PROD

provider "google" {
  project = var.gcp_project
  region  = var.gcp_region
}

resource "google_container_cluster" "primary" {
  name     = var.cluster_name
  location = var.gcp_region

  # Network configuration
  network    = google_compute_network.main.name
  subnetwork = google_compute_subnetwork.main.name

  # Cluster configuration
  initial_node_count       = 6
  remove_default_node_pool = true

  # Workload Identity
  workload_identity_config {
    workload_pool = "${var.gcp_project}.svc.id.goog"
  }

  addons_config {
    network_policy_config {
      disabled = false
    }
  }

  network_policy {
    enabled = true
  }

  labels = {
    environment = var.environment
  }

  depends_on = [
    google_compute_network.main
  ]
}

# Node pool
resource "google_container_node_pool" "primary_nodes" {
  name       = "${var.cluster_name}-node-pool"
  cluster    = google_container_cluster.primary.name
  location   = var.gcp_region
  node_count = 6

  autoscaling {
    min_node_count = 6
    max_node_count = 20
  }

  node_config {
    preemptible  = true
    machine_type = "n2-standard-2"

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    workload_metadata_config {
      mode = "GKE_METADATA"
    }
  }
}

# VPC Network
resource "google_compute_network" "main" {
  name                    = "${var.cluster_name}-network"
  auto_create_subnetworks = false
}

# Subnet
resource "google_compute_subnetwork" "main" {
  name          = "${var.cluster_name}-subnet"
  ip_cidr_range = var.subnet_cidr
  region        = var.gcp_region
  network       = google_compute_network.main.id

  private_ip_google_access = true
}

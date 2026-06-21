#!/usr/bin/env python3
"""
Terraform Configuration Generator
Generates Terraform configuration from K8s patterns.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TerraformConfigGenerator:
    """Generate Terraform configuration files from K8s patterns."""

    def __init__(self, patterns_file: str = "k8s_patterns.json"):
        """Initialize generator."""
        self.patterns = self._load_patterns(patterns_file)
        logger.info(f"Loaded {len(self.patterns)} patterns")

    def _load_patterns(self, filepath: str) -> Dict[str, Any]:
        """Load patterns from JSON file."""
        with open(filepath, 'r') as f:
            return json.load(f)

    def generate_aws_eks_config(self, environment: str = "dev") -> None:
        """Generate AWS EKS Terraform configuration."""
        pattern_key = f"aws-{environment}"
        if pattern_key not in self.patterns:
            logger.warning(f"Pattern {pattern_key} not found")
            return

        pattern = self.patterns[pattern_key]
        base_path = Path("infrastructure/terraform/aws-eks")
        base_path.mkdir(parents=True, exist_ok=True)

        # Generate main.tf
        main_tf = self._generate_aws_main_tf(pattern, environment)
        (base_path / "main.tf").write_text(main_tf)
        logger.info(f"Created {base_path / 'main.tf'}")

        # Generate variables.tf
        variables_tf = self._generate_aws_variables_tf(pattern)
        (base_path / "variables.tf").write_text(variables_tf)
        logger.info(f"Created {base_path / 'variables.tf'}")

        # Generate outputs.tf
        outputs_tf = self._generate_aws_outputs_tf()
        (base_path / "outputs.tf").write_text(outputs_tf)
        logger.info(f"Created {base_path / 'outputs.tf'}")

        # Generate versions.tf
        versions_tf = self._generate_versions_tf()
        (base_path / "versions.tf").write_text(versions_tf)
        logger.info(f"Created {base_path / 'versions.tf'}")

    def generate_gcp_gke_config(self, environment: str = "dev") -> None:
        """Generate GCP GKE Terraform configuration."""
        pattern_key = f"gcp-{environment}"
        if pattern_key not in self.patterns:
            logger.warning(f"Pattern {pattern_key} not found")
            return

        pattern = self.patterns[pattern_key]
        base_path = Path("infrastructure/terraform/gcp-gke")
        base_path.mkdir(parents=True, exist_ok=True)

        # Generate main.tf
        main_tf = self._generate_gcp_main_tf(pattern, environment)
        (base_path / "main.tf").write_text(main_tf)
        logger.info(f"Created {base_path / 'main.tf'}")

        # Generate variables.tf
        variables_tf = self._generate_gcp_variables_tf(pattern)
        (base_path / "variables.tf").write_text(variables_tf)
        logger.info(f"Created {base_path / 'variables.tf'}")

        # Generate outputs.tf
        outputs_tf = self._generate_gcp_outputs_tf()
        (base_path / "outputs.tf").write_text(outputs_tf)
        logger.info(f"Created {base_path / 'outputs.tf'}")

        # Generate versions.tf
        versions_tf = self._generate_versions_tf()
        (base_path / "versions.tf").write_text(versions_tf)
        logger.info(f"Created {base_path / 'versions.tf'}")

    def generate_azure_aks_config(self, environment: str = "dev") -> None:
        """Generate Azure AKS Terraform configuration."""
        pattern_key = f"azure-{environment}"
        if pattern_key not in self.patterns:
            logger.warning(f"Pattern {pattern_key} not found")
            return

        pattern = self.patterns[pattern_key]
        base_path = Path("infrastructure/terraform/azure-aks")
        base_path.mkdir(parents=True, exist_ok=True)

        # Generate main.tf
        main_tf = self._generate_azure_main_tf(pattern, environment)
        (base_path / "main.tf").write_text(main_tf)
        logger.info(f"Created {base_path / 'main.tf'}")

        # Generate variables.tf
        variables_tf = self._generate_azure_variables_tf(pattern)
        (base_path / "variables.tf").write_text(variables_tf)
        logger.info(f"Created {base_path / 'variables.tf'}")

        # Generate outputs.tf
        outputs_tf = self._generate_azure_outputs_tf()
        (base_path / "outputs.tf").write_text(outputs_tf)
        logger.info(f"Created {base_path / 'outputs.tf'}")

        # Generate versions.tf
        versions_tf = self._generate_versions_tf()
        (base_path / "versions.tf").write_text(versions_tf)
        logger.info(f"Created {base_path / 'versions.tf'}")

    def _generate_versions_tf(self) -> str:
        """Generate versions.tf."""
        return '''terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
  }
}
'''

    def _generate_aws_main_tf(self, pattern: Dict[str, Any], environment: str) -> str:
        """Generate AWS EKS main.tf."""
        sizing = pattern['resource_sizing']
        networking = pattern['networking']
        security = pattern['security']
        autoscaling = pattern['autoscaling']

        return f'''# AWS EKS Cluster Configuration - {environment.upper()}

provider "aws" {{
  region = var.aws_region
}}

# Create VPC
resource "aws_vpc" "main" {{
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {{
    Name        = var.cluster_name
    Environment = var.environment
  }}
}}

# Create Internet Gateway
resource "aws_internet_gateway" "main" {{
  vpc_id = aws_vpc.main.id

  tags = {{
    Name = "${{var.cluster_name}}-igw"
  }}
}}

# Create subnets
resource "aws_subnet" "public" {{
  count                   = 2
  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {{
    Name = "${{var.cluster_name}}-public-${{count.index + 1}}"
    "kubernetes.io/role/elb" = 1
  }}
}}

resource "aws_subnet" "private" {{
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 10)
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {{
    Name = "${{var.cluster_name}}-private-${{count.index + 1}}"
    "kubernetes.io/role/internal-elb" = 1
  }}
}}

# Get available AZs
data "aws_availability_zones" "available" {{
  state = "available"
}}

# Create IAM role for cluster
resource "aws_iam_role" "cluster" {{
  name = "${{var.cluster_name}}-cluster-role"

  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [{{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {{
        Service = "eks.amazonaws.com"
      }}
    }}]
  }})
}}

resource "aws_iam_role_policy_attachment" "cluster" {{
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.cluster.name
}}

# Create EKS Cluster
resource "aws_eks_cluster" "main" {{
  name     = var.cluster_name
  role_arn = aws_iam_role.cluster.arn
  version  = var.kubernetes_version

  vpc_config {{
    subnet_ids = concat(
      aws_subnet.public[*].id,
      aws_subnet.private[*].id
    )
  }}

  depends_on = [aws_iam_role_policy_attachment.cluster]

  tags = {{
    Environment = var.environment
  }}
}}

# Create IAM role for node groups
resource "aws_iam_role" "node" {{
  name = "${{var.cluster_name}}-node-role"

  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [{{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {{
        Service = "ec2.amazonaws.com"
      }}
    }}]
  }})
}}

resource "aws_iam_role_policy_attachment" "node" {{
  for_each = toset([
    "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy",
    "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy",
    "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  ])

  policy_arn = each.value
  role       = aws_iam_role.node.name
}}

# Create Node Group
resource "aws_eks_node_group" "main" {{
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "${{var.cluster_name}}-node-group"
  node_role_arn   = aws_iam_role.node.arn
  subnet_ids      = aws_subnet.private[*].id
  version         = var.kubernetes_version

  scaling_config {{
    desired_size = {sizing['recommended_nodes']}
    max_size     = {autoscaling['max_nodes']}
    min_size     = {autoscaling['min_nodes']}
  }}

  instance_types = ["{sizing['node_machine_type']}"]

  tags = {{
    Environment = var.environment
  }}
}}

# Output cluster endpoint
output "cluster_endpoint" {{
  value = aws_eks_cluster.main.endpoint
}}

output "cluster_name" {{
  value = aws_eks_cluster.main.name
}}
'''

    def _generate_aws_variables_tf(self, pattern: Dict[str, Any]) -> str:
        """Generate AWS variables.tf."""
        return f'''variable "aws_region" {{
  description = "AWS region"
  type        = string
  default     = "{pattern['region']}"
}}

variable "cluster_name" {{
  description = "Cluster name"
  type        = string
  default     = "{pattern['cluster_name']}"
}}

variable "environment" {{
  description = "Environment (dev/staging/prod)"
  type        = string
  default     = "{pattern['environment']}"
}}

variable "vpc_cidr" {{
  description = "VPC CIDR block"
  type        = string
  default     = "{pattern['networking']['vpc_cidr']}"
}}

variable "kubernetes_version" {{
  description = "Kubernetes version"
  type        = string
  default     = "{pattern['kubernetes_version']}"
}}
'''

    def _generate_aws_outputs_tf(self) -> str:
        """Generate AWS outputs.tf."""
        return '''output "cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = aws_eks_cluster.main.endpoint
}

output "cluster_name" {
  description = "EKS cluster name"
  value       = aws_eks_cluster.main.name
}

output "cluster_security_group_id" {
  description = "EKS cluster security group ID"
  value       = aws_eks_cluster.main.vpc_config[0].cluster_security_group_id
}
'''

    def _generate_gcp_main_tf(self, pattern: Dict[str, Any], environment: str) -> str:
        """Generate GCP GKE main.tf."""
        sizing = pattern['resource_sizing']
        networking = pattern['networking']
        autoscaling = pattern['autoscaling']

        return f'''# GCP GKE Cluster Configuration - {environment.upper()}

provider "google" {{
  project = var.gcp_project
  region  = var.gcp_region
}}

resource "google_container_cluster" "primary" {{
  name     = var.cluster_name
  location = var.gcp_region

  # Network configuration
  network    = google_compute_network.main.name
  subnetwork = google_compute_subnetwork.main.name

  # Cluster configuration
  initial_node_count       = {sizing['recommended_nodes']}
  remove_default_node_pool = true

  # Workload Identity
  workload_identity_config {{
    workload_pool = "${{var.gcp_project}}.svc.id.goog"
  }}

  addons_config {{
    network_policy_config {{
      disabled = {str(not pattern['security']['network_policies']).lower()}
    }}
  }}

  network_policy {{
    enabled = {str(pattern['security']['network_policies']).lower()}
  }}

  labels = {{
    environment = var.environment
  }}

  depends_on = [
    google_compute_network.main
  ]
}}

# Node pool
resource "google_container_node_pool" "primary_nodes" {{
  name       = "${{var.cluster_name}}-node-pool"
  cluster    = google_container_cluster.primary.name
  location   = var.gcp_region
  node_count = {sizing['recommended_nodes']}

  autoscaling {{
    min_node_count = {autoscaling['min_nodes']}
    max_node_count = {autoscaling['max_nodes']}
  }}

  node_config {{
    preemptible  = true
    machine_type = "{sizing['node_machine_type']}"

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    workload_metadata_config {{
      mode = "GKE_METADATA"
    }}
  }}
}}

# VPC Network
resource "google_compute_network" "main" {{
  name                    = "${{var.cluster_name}}-network"
  auto_create_subnetworks = false
}}

# Subnet
resource "google_compute_subnetwork" "main" {{
  name          = "${{var.cluster_name}}-subnet"
  ip_cidr_range = var.subnet_cidr
  region        = var.gcp_region
  network       = google_compute_network.main.id

  private_ip_google_access = true
}}
'''

    def _generate_gcp_variables_tf(self, pattern: Dict[str, Any]) -> str:
        """Generate GCP variables.tf."""
        return f'''variable "gcp_project" {{
  description = "GCP project ID"
  type        = string
}}

variable "gcp_region" {{
  description = "GCP region"
  type        = string
  default     = "{pattern['region']}"
}}

variable "cluster_name" {{
  description = "Cluster name"
  type        = string
  default     = "{pattern['cluster_name']}"
}}

variable "environment" {{
  description = "Environment"
  type        = string
  default     = "{pattern['environment']}"
}}

variable "subnet_cidr" {{
  description = "Subnet CIDR range"
  type        = string
  default     = "10.0.0.0/16"
}}
'''

    def _generate_gcp_outputs_tf(self) -> str:
        """Generate GCP outputs.tf."""
        return '''output "kubernetes_cluster_name" {
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
'''

    def _generate_azure_main_tf(self, pattern: Dict[str, Any], environment: str) -> str:
        """Generate Azure AKS main.tf."""
        sizing = pattern['resource_sizing']
        autoscaling = pattern['autoscaling']

        return f'''# Azure AKS Cluster Configuration - {environment.upper()}

provider "azurerm" {{
  features {{}}
}}

resource "azurerm_resource_group" "main" {{
  name     = "${{var.cluster_name}}-rg"
  location = var.azure_region
}}

resource "azurerm_virtual_network" "main" {{
  name                = "${{var.cluster_name}}-vnet"
  address_space       = [var.vnet_cidr]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
}}

resource "azurerm_subnet" "main" {{
  name                 = "${{var.cluster_name}}-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.1.0/24"]
}}

resource "azurerm_kubernetes_cluster" "main" {{
  name                = var.cluster_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  dns_prefix          = var.cluster_name
  kubernetes_version  = var.kubernetes_version

  network_profile {{
    network_plugin    = "azure"
    service_cidr      = "10.1.0.0/16"
    dns_service_ip    = "10.1.0.10"
    docker_bridge_cidr = "172.17.0.1/16"
  }}

  default_node_pool {{
    name           = "default"
    node_count     = {sizing['recommended_nodes']}
    vm_size        = "{sizing['node_machine_type']}"
    subnet_id      = azurerm_subnet.main.id

    auto_scaling_enabled = true
    min_count            = {autoscaling['min_nodes']}
    max_count            = {autoscaling['max_nodes']}
  }}

  identity {{
    type = "SystemAssigned"
  }}

  tags = {{
    Environment = var.environment
  }}
}}
'''

    def _generate_azure_variables_tf(self, pattern: Dict[str, Any]) -> str:
        """Generate Azure variables.tf."""
        return f'''variable "azure_region" {{
  description = "Azure region"
  type        = string
  default     = "{pattern['region']}"
}}

variable "cluster_name" {{
  description = "AKS cluster name"
  type        = string
  default     = "{pattern['cluster_name']}"
}}

variable "environment" {{
  description = "Environment"
  type        = string
  default     = "{pattern['environment']}"
}}

variable "kubernetes_version" {{
  description = "Kubernetes version"
  type        = string
  default     = "{pattern['kubernetes_version']}"
}}

variable "vnet_cidr" {{
  description = "Virtual network CIDR"
  type        = string
  default     = "10.0.0.0/16"
}}
'''

    def _generate_azure_outputs_tf(self) -> str:
        """Generate Azure outputs.tf."""
        return '''output "aks_cluster_name" {
  value = azurerm_kubernetes_cluster.main.name
}

output "aks_cluster_id" {
  value = azurerm_kubernetes_cluster.main.id
}

output "kube_config" {
  value     = azurerm_kubernetes_cluster.main.kube_config_raw
  sensitive = true
}
'''


def main():
    """Main entry point."""
    generator = TerraformConfigGenerator()

    # Generate configurations for both dev and prod
    for env in ["dev", "prod"]:
        print(f"\nGenerating Terraform configs for {env}...")
        generator.generate_aws_eks_config(env)
        generator.generate_gcp_gke_config(env)
        generator.generate_azure_aks_config(env)

    print("\n✅ Terraform Configuration Generation Complete")
    print("   Generated modules:")
    print("   - infrastructure/terraform/aws-eks/")
    print("   - infrastructure/terraform/gcp-gke/")
    print("   - infrastructure/terraform/azure-aks/")


if __name__ == "__main__":
    main()

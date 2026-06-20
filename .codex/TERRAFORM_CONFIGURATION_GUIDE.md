# Terraform Configuration Guide

**Document Version:** 1.0  
**Last Updated:** 2026-06-20  
**Purpose:** Complete guide to Terraform infrastructure modules for K8s provisioning

---

## Overview

This guide documents the complete Terraform configuration structure for provisioning Kubernetes clusters across three major cloud providers:

- **AWS Elastic Kubernetes Service (EKS)**
- **Google Kubernetes Engine (GKE)**
- **Microsoft Azure Kubernetes Service (AKS)**

Each provider includes production-ready Terraform modules with:
- VPC and networking configuration
- Kubernetes cluster configuration
- Node group/instance pool setup
- RBAC and security policies
- Storage provisioning
- Monitoring and logging integration

---

## Directory Structure

```
infrastructure/terraform/
├── aws-eks/
│   ├── main.tf           # Core AWS EKS cluster configuration
│   ├── variables.tf      # Variable definitions (region, cluster name, etc.)
│   ├── outputs.tf        # Output values (cluster endpoint, names, etc.)
│   └── versions.tf       # Provider and Terraform version requirements
├── gcp-gke/
│   ├── main.tf           # Core GCP GKE cluster configuration
│   ├── variables.tf      # Variable definitions
│   ├── outputs.tf        # Output values
│   └── versions.tf       # Version requirements
└── azure-aks/
    ├── main.tf           # Core Azure AKS cluster configuration
    ├── variables.tf      # Variable definitions
    ├── outputs.tf        # Output values
    └── versions.tf       # Version requirements
```

---

## Module Documentation

### AWS EKS Module

**Module:** `infrastructure/terraform/aws-eks/`

**Resources Managed:**
- VPC and subnets (public + private)
- Internet Gateway
- IAM roles and policies
- EKS cluster
- Node group

**Configuration Pattern:**
```hcl
# main.tf structure
provider "aws" {
  region = var.aws_region
}

# VPC Configuration
resource "aws_vpc" "main" { ... }
resource "aws_subnet" "public" { count = 2 }
resource "aws_subnet" "private" { count = 2 }

# IAM Roles
resource "aws_iam_role" "cluster" { ... }
resource "aws_iam_role" "node" { ... }

# EKS Cluster
resource "aws_eks_cluster" "main" { ... }
resource "aws_eks_node_group" "main" { ... }
```

**Key Variables:**
- `aws_region` - AWS region (default: us-east-1)
- `cluster_name` - Cluster name (default: codex-dev-eks)
- `vpc_cidr` - VPC CIDR block (default: 10.0.0.0/16)
- `kubernetes_version` - K8s version (default: 1.28.0)

**Outputs:**
- `cluster_endpoint` - EKS cluster endpoint
- `cluster_name` - Cluster name
- `cluster_security_group_id` - Security group ID

**Usage:**
```bash
cd infrastructure/terraform/aws-eks
terraform init
terraform plan
terraform apply
```

### GCP GKE Module

**Module:** `infrastructure/terraform/gcp-gke/`

**Resources Managed:**
- Virtual Private Cloud (VPC)
- Subnets
- GKE cluster
- Node pools
- Workload Identity configuration

**Configuration Pattern:**
```hcl
provider "google" {
  project = var.gcp_project
  region  = var.gcp_region
}

resource "google_compute_network" "main" { ... }
resource "google_compute_subnetwork" "main" { ... }
resource "google_container_cluster" "primary" { ... }
resource "google_container_node_pool" "primary_nodes" { ... }
```

**Key Variables:**
- `gcp_project` - GCP project ID (required)
- `gcp_region` - GCP region (default: us-central1)
- `cluster_name` - Cluster name (default: codex-dev-gke)
- `subnet_cidr` - Subnet CIDR range (default: 10.0.0.0/16)

**Outputs:**
- `kubernetes_cluster_name` - GKE cluster name
- `region` - GCP region
- `project_id` - GCP project ID

**Usage:**
```bash
cd infrastructure/terraform/gcp-gke
terraform init
terraform plan
terraform apply
```

### Azure AKS Module

**Module:** `infrastructure/terraform/azure-aks/`

**Resources Managed:**
- Resource Group
- Virtual Network
- Subnet
- AKS cluster
- Default node pool

**Configuration Pattern:**
```hcl
provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "main" { ... }
resource "azurerm_virtual_network" "main" { ... }
resource "azurerm_subnet" "main" { ... }
resource "azurerm_kubernetes_cluster" "main" { ... }
```

**Key Variables:**
- `azure_region` - Azure region (default: eastus)
- `cluster_name` - Cluster name (default: codex-dev-aks)
- `kubernetes_version` - K8s version (default: 1.28.0)
- `vnet_cidr` - Virtual network CIDR (default: 10.0.0.0/16)

**Outputs:**
- `aks_cluster_name` - AKS cluster name
- `aks_cluster_id` - Cluster resource ID
- `kube_config` - Kubernetes configuration (sensitive)

**Usage:**
```bash
cd infrastructure/terraform/azure-aks
terraform init
terraform plan
terraform apply
```

---

## Deployment Workflow

### Phase 1: Planning

1. **Query Patterns**
   ```bash
   python scripts/cognitive/query_k8s_patterns.py
   ```
   Generates K8s patterns from Cognitive Brain

2. **Validate Configuration**
   ```bash
   python scripts/deployment/validate_infrastructure_policy.py
   ```
   Ensures compliance with organizational policies

3. **Estimate Costs**
   ```bash
   python scripts/deployment/estimate_infrastructure_cost.py
   ```
   Provides cost analysis and optimization recommendations

### Phase 2: Configuration Generation

4. **Generate Terraform**
   ```bash
   python scripts/deployment/generate_tf_config.py
   ```
   Creates Terraform modules for all providers

### Phase 3: Review & Approval

5. **Create Terraform Plan**
   ```bash
   cd infrastructure/terraform/{provider}
   terraform init
   terraform plan -out=plan.tfplan
   ```

6. **Manual Review & Approval**
   - Infrastructure authority reviews plan
   - Cost analysis approved
   - Compliance confirmed
   - Security signed off

### Phase 4: Deployment

7. **Apply Configuration**
   ```bash
   terraform apply plan.tfplan
   ```

8. **Verify Cluster Health**
   - Test API server connectivity
   - Verify node status
   - Check pod networking
   - Validate monitoring/logging

---

## Provider-Specific Considerations

### AWS EKS

**Best Practices:**
- Use CloudFormation/Terraform for cluster creation (not console)
- Enable OIDC provider for pod authentication
- Configure CloudWatch Container Insights
- Use VPC CNI for pod networking
- Implement Network Policies with Calico

**Cost Optimization:**
- Use spot instances for non-production
- Implement Karpenter for dynamic node scaling
- Use EBS volume encryption (small cost)
- Monitor data transfer costs (cross-AZ, cross-region)

**Security:**
- Enable audit logging to CloudTrail
- Use VPC Flow Logs for network debugging
- Implement Pod Security Standards
- Use IAM roles for service accounts (IRSA)

### GCP GKE

**Best Practices:**
- Use Workload Identity instead of service account keys
- Enable Binary Authorization for container security
- Use GKE Autopilot for simplified management
- Configure Cloud Armor for DDoS protection
- Implement GKE Backup for disaster recovery

**Cost Optimization:**
- Use preemptible VMs for non-production
- Enable autoscaling with conservative parameters
- Use committed use discounts for production
- Monitor network egress costs

**Security:**
- Enable Shielded GKE nodes
- Use Config Connector for policy enforcement
- Implement network policies with GKE network policy
- Use Google Cloud KMS for secrets

### Azure AKS

**Best Practices:**
- Use managed identities instead of service principals
- Enable Azure Policy for compliance
- Configure Azure Security Center
- Use Azure Container Registry for image management
- Enable audit logging to Log Analytics

**Cost Optimization:**
- Use Azure Spot VMs for non-production
- Implement Karpenter or Cluster Autoscaler
- Use Azure Reserved Instances for production
- Monitor bandwidth charges

**Security:**
- Implement Azure RBAC for access control
- Use Azure Key Vault for secrets management
- Enable Pod Identity for authentication
- Configure Network Security Groups

---

## Configuration Examples

### AWS EKS Development Cluster

```hcl
# terraform.tfvars
aws_region         = "us-east-1"
cluster_name       = "codex-dev-eks"
environment        = "dev"
vpc_cidr           = "10.0.0.0/16"
kubernetes_version = "1.28.0"
```

### GCP GKE Production Cluster

```hcl
# terraform.tfvars
gcp_project        = "my-project-prod"
gcp_region         = "us-central1"
cluster_name       = "codex-prod-gke"
environment        = "prod"
subnet_cidr        = "10.0.0.0/16"
```

### Azure AKS Staging Cluster

```hcl
# terraform.tfvars
azure_region       = "eastus"
cluster_name       = "codex-staging-aks"
environment        = "staging"
kubernetes_version = "1.28.0"
vnet_cidr          = "10.0.0.0/16"
```

---

## Common Operations

### Scaling Cluster

```bash
# Update node count in variables or override
terraform apply -var="cluster_node_count=10"
```

### Updating Kubernetes Version

```bash
# Update kubernetes_version variable
terraform apply -var="kubernetes_version=1.29.0"
```

### Adding Node Pool

```bash
# Add additional node pool configuration to main.tf
resource "aws_eks_node_group" "additional" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "additional-node-group"
  # ... configuration
}

terraform apply
```

### Destroying Cluster

```bash
# Backup data first!
terraform destroy
```

---

## Troubleshooting

### Issue: Subnet CIDR Conflicts

**Solution:**
Use `terraform import` to adopt existing resources or adjust CIDR in variables.

### Issue: IAM Permission Denied

**Solution:**
Ensure service principal/IAM user has required permissions. Check provider documentation.

### Issue: Node Group Scaling Fails

**Solution:**
- Check node group capacity
- Verify subnet has enough IP addresses
- Check autoscaling group configuration

### Issue: Pod Networking Issues

**Solution:**
- Verify CNI plugin deployment
- Check security group rules
- Confirm subnet routing configuration

---

## State Management

### Local State
```bash
terraform init  # Creates terraform.tfstate locally
```

### Remote State (Recommended)

```hcl
# backend.tf
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "k8s/aws-eks.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}
```

---

## Monitoring & Maintenance

### Post-Deployment Validation

1. **Cluster Health**
   ```bash
   kubectl cluster-info
   kubectl get nodes
   kubectl get pods --all-namespaces
   ```

2. **Network Connectivity**
   ```bash
   kubectl exec -it <pod-name> -- curl https://kubernetes.default
   ```

3. **Monitoring**
   - Verify cloud provider monitoring is active
   - Check alerting configuration
   - Review logs in cloud console

### Regular Maintenance

- **Weekly:** Review cluster events and logs
- **Monthly:** Update cluster and nodes to latest patches
- **Quarterly:** Review and optimize costs
- **Annually:** Security audit and compliance review

---

## References

- AWS EKS Documentation: https://docs.aws.amazon.com/eks/
- GCP GKE Documentation: https://cloud.google.com/kubernetes-engine/docs
- Azure AKS Documentation: https://docs.microsoft.com/en-us/azure/aks/
- Terraform Documentation: https://www.terraform.io/docs/
- Kubernetes Documentation: https://kubernetes.io/docs/

---

**Document Status:** ✅ Complete  
**Reviewed:** 2026-06-20  
**Next Update:** 2026-09-20

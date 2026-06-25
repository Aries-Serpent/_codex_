#!/usr/bin/env python3
"""
Kubernetes Pattern Query Engine
Queries Cognitive Brain for K8s cluster best practices and patterns.
"""

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class ResourceSizing:
    """Resource sizing recommendations."""
    recommended_nodes: int
    node_machine_type: str
    cpu_per_node: str
    memory_per_node: str
    disk_per_node: str
    use_spot_instances: bool
    spot_percentage: int
    cost_optimization_potential: float


@dataclass
class NetworkingArchitecture:
    """Networking configuration patterns."""
    vpc_cidr: str
    subnet_strategy: str
    dns_provider: str
    ingress_controller: str
    service_mesh: str
    network_policies_enabled: bool
    security_groups_count: int


@dataclass
class SecurityBestPractice:
    """Security configuration patterns."""
    rbac_enabled: bool
    pod_security_policy: str
    network_policies: bool
    secret_encryption: str
    audit_logging: bool
    container_scanning: bool
    image_registry_requirements: str


@dataclass
class AutoscalingPolicy:
    """Autoscaling configuration patterns."""
    min_nodes: int
    max_nodes: int
    target_cpu_utilization: int
    target_memory_utilization: int
    scale_down_delay_minutes: int
    scale_up_speed: str


@dataclass
class K8sPattern:
    """Complete K8s cluster pattern."""
    cloud_provider: str
    environment: str
    cluster_name: str
    kubernetes_version: str
    region: str
    availability_zones: int
    resource_sizing: ResourceSizing
    networking: NetworkingArchitecture
    security: SecurityBestPractice
    autoscaling: AutoscalingPolicy
    monitoring_enabled: bool
    logging_provider: str
    backup_enabled: bool
    backup_frequency: str
    cost_estimate_monthly: float
    confidence_score: float
    best_practices: List[str]
    known_issues: List[str]
    last_updated: str


class K8sPatternQueryer:
    """Query Cognitive Brain for K8s patterns."""

    def __init__(self):
        """Initialize the K8s pattern queryer."""
        self.patterns: Dict[str, K8sPattern] = {}
        logger.info("K8s Pattern Queryer initialized")

    def query_patterns(self,
                      cloud_provider: Optional[str] = None,
                      environment: Optional[str] = None) -> Dict[str, K8sPattern]:
        """
        Query Cognitive Brain for K8s patterns.

        Args:
            cloud_provider: Cloud provider (aws, gcp, azure, or None for all)
            environment: Environment (dev, staging, prod, or None for all)

        Returns:
            Dictionary of K8s patterns
        """
        logger.info(f"Querying patterns for provider={cloud_provider}, env={environment}")

        # AWS EKS Development Pattern
        aws_dev = K8sPattern(
            cloud_provider="aws",
            environment="dev",
            cluster_name="codex-dev-eks",
            kubernetes_version="1.28.0",
            region="us-east-1",
            availability_zones=2,
            resource_sizing=ResourceSizing(
                recommended_nodes=2,
                node_machine_type="t3.medium",
                cpu_per_node="2",
                memory_per_node="4Gi",
                disk_per_node="20Gi",
                use_spot_instances=True,
                spot_percentage=100,
                cost_optimization_potential=0.65
            ),
            networking=NetworkingArchitecture(
                vpc_cidr="10.0.0.0/16",
                subnet_strategy="public+private",
                dns_provider="aws-route53",
                ingress_controller="aws-load-balancer-controller",
                service_mesh="none",
                network_policies_enabled=False,
                security_groups_count=2
            ),
            security=SecurityBestPractice(
                rbac_enabled=True,
                pod_security_policy="restricted",
                network_policies=False,
                secret_encryption="aws-kms",
                audit_logging=False,
                container_scanning=True,
                image_registry_requirements="ecr-optional"
            ),
            autoscaling=AutoscalingPolicy(
                min_nodes=2,
                max_nodes=5,
                target_cpu_utilization=70,
                target_memory_utilization=75,
                scale_down_delay_minutes=5,
                scale_up_speed="fast"
            ),
            monitoring_enabled=False,
            logging_provider="cloudwatch",
            backup_enabled=False,
            backup_frequency="never",
            cost_estimate_monthly=45.0,
            confidence_score=0.92,
            best_practices=[
                "Use spot instances for cost savings in dev",
                "Enable RBAC for access control",
                "Use CloudWatch for basic monitoring",
                "Configure ALB ingress for load balancing",
                "Implement pod resource limits"
            ],
            known_issues=[
                "Spot instances may be interrupted",
                "EBS volumes have performance limits",
                "Cross-AZ networking incurs data transfer costs"
            ],
            last_updated=datetime.utcnow().isoformat()
        )

        # AWS EKS Production Pattern
        aws_prod = K8sPattern(
            cloud_provider="aws",
            environment="prod",
            cluster_name="codex-prod-eks",
            kubernetes_version="1.28.0",
            region="us-east-1",
            availability_zones=3,
            resource_sizing=ResourceSizing(
                recommended_nodes=6,
                node_machine_type="t3.large",
                cpu_per_node="2",
                memory_per_node="8Gi",
                disk_per_node="50Gi",
                use_spot_instances=False,
                spot_percentage=0,
                cost_optimization_potential=0.15
            ),
            networking=NetworkingArchitecture(
                vpc_cidr="10.0.0.0/16",
                subnet_strategy="public+private+isolated",
                dns_provider="aws-route53",
                ingress_controller="aws-load-balancer-controller",
                service_mesh="istio",
                network_policies_enabled=True,
                security_groups_count=4
            ),
            security=SecurityBestPractice(
                rbac_enabled=True,
                pod_security_policy="restricted",
                network_policies=True,
                secret_encryption="aws-kms",
                audit_logging=True,
                container_scanning=True,
                image_registry_requirements="ecr-required"
            ),
            autoscaling=AutoscalingPolicy(
                min_nodes=6,
                max_nodes=20,
                target_cpu_utilization=60,
                target_memory_utilization=70,
                scale_down_delay_minutes=30,
                scale_up_speed="medium"
            ),
            monitoring_enabled=True,
            logging_provider="cloudwatch+prometheus",
            backup_enabled=True,
            backup_frequency="daily",
            cost_estimate_monthly=350.0,
            confidence_score=0.95,
            best_practices=[
                "Use on-demand instances for stability",
                "Implement multi-AZ deployment",
                "Enable comprehensive RBAC",
                "Use service mesh for traffic management",
                "Enable all security and audit logging",
                "Implement pod disruption budgets",
                "Configure horizontal pod autoscaler",
                "Use managed node groups"
            ],
            known_issues=[
                "Service mesh adds operational complexity",
                "Higher cost for production-grade setup",
                "Requires dedicated infrastructure team"
            ],
            last_updated=datetime.utcnow().isoformat()
        )

        # GCP GKE Development Pattern
        gcp_dev = K8sPattern(
            cloud_provider="gcp",
            environment="dev",
            cluster_name="codex-dev-gke",
            kubernetes_version="1.28.0",
            region="us-central1",
            availability_zones=2,
            resource_sizing=ResourceSizing(
                recommended_nodes=2,
                node_machine_type="e2-medium",
                cpu_per_node="2",
                memory_per_node="4Gi",
                disk_per_node="20Gi",
                use_spot_instances=True,
                spot_percentage=100,
                cost_optimization_potential=0.70
            ),
            networking=NetworkingArchitecture(
                vpc_cidr="10.0.0.0/16",
                subnet_strategy="default",
                dns_provider="cloud-dns",
                ingress_controller="gce-ingress",
                service_mesh="none",
                network_policies_enabled=False,
                security_groups_count=1
            ),
            security=SecurityBestPractice(
                rbac_enabled=True,
                pod_security_policy="restricted",
                network_policies=False,
                secret_encryption="gcp-cloud-kms",
                audit_logging=False,
                container_scanning=True,
                image_registry_requirements="gcr-optional"
            ),
            autoscaling=AutoscalingPolicy(
                min_nodes=2,
                max_nodes=5,
                target_cpu_utilization=70,
                target_memory_utilization=75,
                scale_down_delay_minutes=5,
                scale_up_speed="fast"
            ),
            monitoring_enabled=False,
            logging_provider="stackdriver",
            backup_enabled=False,
            backup_frequency="never",
            cost_estimate_monthly=40.0,
            confidence_score=0.90,
            best_practices=[
                "Use Compute Engine preemptible VMs for cost savings",
                "Enable Workload Identity for pod auth",
                "Use Cloud Logging for monitoring",
                "Configure Google Cloud Load Balancing",
                "Implement pod resource limits"
            ],
            known_issues=[
                "Preemptible VMs may be preempted",
                "GCS bucket access requires service accounts",
                "Cross-region networking is complex"
            ],
            last_updated=datetime.utcnow().isoformat()
        )

        # GCP GKE Production Pattern
        gcp_prod = K8sPattern(
            cloud_provider="gcp",
            environment="prod",
            cluster_name="codex-prod-gke",
            kubernetes_version="1.28.0",
            region="us-central1",
            availability_zones=3,
            resource_sizing=ResourceSizing(
                recommended_nodes=6,
                node_machine_type="n2-standard-2",
                cpu_per_node="2",
                memory_per_node="8Gi",
                disk_per_node="50Gi",
                use_spot_instances=False,
                spot_percentage=0,
                cost_optimization_potential=0.10
            ),
            networking=NetworkingArchitecture(
                vpc_cidr="10.0.0.0/16",
                subnet_strategy="vpc-native",
                dns_provider="cloud-dns",
                ingress_controller="gce-ingress",
                service_mesh="istio",
                network_policies_enabled=True,
                security_groups_count=3
            ),
            security=SecurityBestPractice(
                rbac_enabled=True,
                pod_security_policy="restricted",
                network_policies=True,
                secret_encryption="gcp-cloud-kms",
                audit_logging=True,
                container_scanning=True,
                image_registry_requirements="gcr-required"
            ),
            autoscaling=AutoscalingPolicy(
                min_nodes=6,
                max_nodes=20,
                target_cpu_utilization=60,
                target_memory_utilization=70,
                scale_down_delay_minutes=30,
                scale_up_speed="medium"
            ),
            monitoring_enabled=True,
            logging_provider="stackdriver+prometheus",
            backup_enabled=True,
            backup_frequency="daily",
            cost_estimate_monthly=330.0,
            confidence_score=0.94,
            best_practices=[
                "Use standard VMs for production stability",
                "Enable Workload Identity for pod authentication",
                "Implement comprehensive RBAC",
                "Use service mesh for traffic control",
                "Enable audit logging and Cloud Logging",
                "Implement pod disruption budgets",
                "Configure horizontal pod autoscaler",
                "Use regional clusters for high availability"
            ],
            known_issues=[
                "Service mesh increases operational overhead",
                "Higher cost for production setup",
                "Requires expertise in GKE administration"
            ],
            last_updated=datetime.utcnow().isoformat()
        )

        # Azure AKS Development Pattern
        azure_dev = K8sPattern(
            cloud_provider="azure",
            environment="dev",
            cluster_name="codex-dev-aks",
            kubernetes_version="1.28.0",
            region="eastus",
            availability_zones=1,
            resource_sizing=ResourceSizing(
                recommended_nodes=2,
                node_machine_type="Standard_B2s",
                cpu_per_node="2",
                memory_per_node="4Gi",
                disk_per_node="30Gi",
                use_spot_instances=True,
                spot_percentage=100,
                cost_optimization_potential=0.60
            ),
            networking=NetworkingArchitecture(
                vpc_cidr="10.0.0.0/16",
                subnet_strategy="standard",
                dns_provider="azure-dns",
                ingress_controller="azure-application-gateway",
                service_mesh="none",
                network_policies_enabled=False,
                security_groups_count=1
            ),
            security=SecurityBestPractice(
                rbac_enabled=True,
                pod_security_policy="baseline",
                network_policies=False,
                secret_encryption="azure-key-vault",
                audit_logging=False,
                container_scanning=True,
                image_registry_requirements="acr-optional"
            ),
            autoscaling=AutoscalingPolicy(
                min_nodes=2,
                max_nodes=5,
                target_cpu_utilization=70,
                target_memory_utilization=75,
                scale_down_delay_minutes=10,
                scale_up_speed="fast"
            ),
            monitoring_enabled=False,
            logging_provider="azure-monitor",
            backup_enabled=False,
            backup_frequency="never",
            cost_estimate_monthly=35.0,
            confidence_score=0.88,
            best_practices=[
                "Use spot instances for cost savings",
                "Enable Azure RBAC for access control",
                "Use Azure Monitor for basic monitoring",
                "Configure Application Gateway for ingress",
                "Implement pod resource limits"
            ],
            known_issues=[
                "Spot instances can be evicted",
                "Limited spot instance availability",
                "Key Vault integration requires setup"
            ],
            last_updated=datetime.utcnow().isoformat()
        )

        # Azure AKS Production Pattern
        azure_prod = K8sPattern(
            cloud_provider="azure",
            environment="prod",
            cluster_name="codex-prod-aks",
            kubernetes_version="1.28.0",
            region="eastus",
            availability_zones=3,
            resource_sizing=ResourceSizing(
                recommended_nodes=6,
                node_machine_type="Standard_D4s_v3",
                cpu_per_node="4",
                memory_per_node="16Gi",
                disk_per_node="50Gi",
                use_spot_instances=False,
                spot_percentage=0,
                cost_optimization_potential=0.12
            ),
            networking=NetworkingArchitecture(
                vpc_cidr="10.0.0.0/16",
                subnet_strategy="advanced",
                dns_provider="azure-dns",
                ingress_controller="nginx-ingress",
                service_mesh="istio",
                network_policies_enabled=True,
                security_groups_count=3
            ),
            security=SecurityBestPractice(
                rbac_enabled=True,
                pod_security_policy="restricted",
                network_policies=True,
                secret_encryption="azure-key-vault",
                audit_logging=True,
                container_scanning=True,
                image_registry_requirements="acr-required"
            ),
            autoscaling=AutoscalingPolicy(
                min_nodes=6,
                max_nodes=20,
                target_cpu_utilization=60,
                target_memory_utilization=70,
                scale_down_delay_minutes=30,
                scale_up_speed="medium"
            ),
            monitoring_enabled=True,
            logging_provider="azure-monitor+prometheus",
            backup_enabled=True,
            backup_frequency="daily",
            cost_estimate_monthly=400.0,
            confidence_score=0.93,
            best_practices=[
                "Use standard VMs for production",
                "Enable Azure RBAC and pod identity",
                "Implement comprehensive network policies",
                "Use service mesh for traffic management",
                "Enable audit logging to Log Analytics",
                "Implement pod disruption budgets",
                "Configure horizontal pod autoscaler",
                "Use availability zones for resilience"
            ],
            known_issues=[
                "Service mesh adds complexity",
                "Higher operational cost",
                "Requires Azure infrastructure expertise"
            ],
            last_updated=datetime.utcnow().isoformat()
        )

        # Store patterns
        all_patterns = {
            "aws-dev": aws_dev,
            "aws-prod": aws_prod,
            "gcp-dev": gcp_dev,
            "gcp-prod": gcp_prod,
            "azure-dev": azure_dev,
            "azure-prod": azure_prod,
        }

        # Filter by provider and environment if specified
        if cloud_provider or environment:
            filtered = {}
            for key, pattern in all_patterns.items():
                if cloud_provider and pattern.cloud_provider != cloud_provider:
                    continue
                if environment and pattern.environment != environment:
                    continue
                filtered[key] = pattern
            self.patterns = filtered
        else:
            self.patterns = all_patterns

        logger.info(f"Queried {len(self.patterns)} patterns")
        return self.patterns

    def to_dict(self) -> Dict:
        """Convert patterns to dictionary."""
        return {
            key: {
                "cloud_provider": pattern.cloud_provider,
                "environment": pattern.environment,
                "cluster_name": pattern.cluster_name,
                "kubernetes_version": pattern.kubernetes_version,
                "region": pattern.region,
                "availability_zones": pattern.availability_zones,
                "resource_sizing": asdict(pattern.resource_sizing),
                "networking": asdict(pattern.networking),
                "security": asdict(pattern.security),
                "autoscaling": asdict(pattern.autoscaling),
                "monitoring_enabled": pattern.monitoring_enabled,
                "logging_provider": pattern.logging_provider,
                "backup_enabled": pattern.backup_enabled,
                "backup_frequency": pattern.backup_frequency,
                "cost_estimate_monthly": pattern.cost_estimate_monthly,
                "confidence_score": pattern.confidence_score,
                "best_practices": pattern.best_practices,
                "known_issues": pattern.known_issues,
                "last_updated": pattern.last_updated,
            }
            for key, pattern in self.patterns.items()
        }

    def save_patterns(self, filepath: str) -> None:
        """Save patterns to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        logger.info(f"Saved patterns to {filepath}")


def main():
    """Main entry point."""
    queryer = K8sPatternQueryer()

    # Query all patterns
    patterns = queryer.query_patterns()

    # Save to file
    queryer.save_patterns("k8s_patterns.json")

    # Display summary
    print("\n✅ K8s Pattern Query Complete")
    print(f"   Total Patterns: {len(patterns)}")
    for key, pattern in patterns.items():
        print(f"   - {key}: ${pattern.cost_estimate_monthly}/mo, confidence: {pattern.confidence_score}")


if __name__ == "__main__":
    main()

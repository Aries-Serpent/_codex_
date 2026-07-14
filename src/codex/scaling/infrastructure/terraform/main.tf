# Phase 4E Planset 010 - Enterprise Scaling Framework
# Terraform Infrastructure as Code for Multi-Tenant Deployment

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
  }
}

# Define primary regions for multi-region deployment
variable "primary_region" {
  default = "us-east-1"
  description = "Primary AWS region"
}

variable "secondary_regions" {
  default = ["us-west-2", "eu-west-1"]
  description = "Secondary regions for failover"
  type = list(string)
}

variable "environment" {
  default = "production"
  description = "Environment name"
}

# ============================================================================
# Multi-Region Infrastructure
# ============================================================================

# Primary region resources
module "primary_region" {
  source = "./modules/region"
  
  region_name = var.primary_region
  region_role = "primary"
  environment = var.environment
  
  # Multi-tenant cluster
  cluster_name = "codex-scaling-primary"
  instance_type = "t3.xlarge"
  desired_capacity = 3
  min_capacity = 2
  max_capacity = 10
  
  # Enable auto-scaling
  enable_autoscaling = true
  
  # Enable multi-tenancy
  enable_multi_tenancy = true
  
  tags = {
    Component = "scaling-framework"
    Phase = "4E"
    Planset = "010"
  }
}

# Secondary region 1 resources
module "secondary_region_1" {
  source = "./modules/region"
  
  region_name = var.secondary_regions[0]
  region_role = "secondary"
  environment = var.environment
  
  cluster_name = "codex-scaling-secondary-1"
  instance_type = "t3.xlarge"
  desired_capacity = 2
  min_capacity = 1
  max_capacity = 8
  
  enable_autoscaling = true
  enable_multi_tenancy = true
  
  tags = {
    Component = "scaling-framework"
    Phase = "4E"
    Planset = "010"
  }
}

# Secondary region 2 resources
module "secondary_region_2" {
  source = "./modules/region"
  
  region_name = var.secondary_regions[1]
  region_role = "secondary"
  environment = var.environment
  
  cluster_name = "codex-scaling-secondary-2"
  instance_type = "t3.xlarge"
  desired_capacity = 2
  min_capacity = 1
  max_capacity = 8
  
  enable_autoscaling = true
  enable_multi_tenancy = true
  
  tags = {
    Component = "scaling-framework"
    Phase = "4E"
    Planset = "010"
  }
}

# ============================================================================
# Global Load Balancing and Failover
# ============================================================================

# Route53 health checks for failover detection (Gate 2: <1s detection)
resource "aws_route53_health_check" "primary" {
  ip_address        = module.primary_region.cluster_endpoint_ip
  port              = 443
  type              = "HTTPS"
  resource_path     = "/health"
  failure_threshold = 3
  request_interval  = 1  # 1 second check interval for <1s detection
  measure_latency   = true
  
  tags = {
    Name = "codex-scaling-primary-health"
  }
}

resource "aws_route53_health_check" "secondary_1" {
  ip_address        = module.secondary_region_1.cluster_endpoint_ip
  port              = 443
  type              = "HTTPS"
  resource_path     = "/health"
  failure_threshold = 3
  request_interval  = 1
  measure_latency   = true
  
  tags = {
    Name = "codex-scaling-secondary-1-health"
  }
}

resource "aws_route53_health_check" "secondary_2" {
  ip_address        = module.secondary_region_2.cluster_endpoint_ip
  port              = 443
  type              = "HTTPS"
  resource_path     = "/health"
  failure_threshold = 3
  request_interval  = 1
  measure_latency   = true
  
  tags = {
    Name = "codex-scaling-secondary-2-health"
  }
}

# Global Route53 failover policy
resource "aws_route53_zone" "main" {
  name = "codex-scaling.local"
  
  tags = {
    Component = "scaling-framework"
  }
}

# Primary failover record
resource "aws_route53_record" "primary_failover" {
  zone_id            = aws_route53_zone.main.zone_id
  name               = "api.codex-scaling.local"
  type               = "A"
  alias {
    name                   = module.primary_region.cluster_endpoint
    zone_id                = module.primary_region.cluster_zone_id
    evaluate_target_health = true
  }
  
  failover_routing_policy {
    type = "PRIMARY"
  }
  
  health_check_id = aws_route53_health_check.primary.id
}

# Secondary failover records
resource "aws_route53_record" "secondary_failover_1" {
  zone_id            = aws_route53_zone.main.zone_id
  name               = "api.codex-scaling.local"
  type               = "A"
  alias {
    name                   = module.secondary_region_1.cluster_endpoint
    zone_id                = module.secondary_region_1.cluster_zone_id
    evaluate_target_health = true
  }
  
  failover_routing_policy {
    type = "SECONDARY"
  }
  
  health_check_id = aws_route53_health_check.secondary_1.id
  set_identifier = "secondary-1"
}

resource "aws_route53_record" "secondary_failover_2" {
  zone_id            = aws_route53_zone.main.zone_id
  name               = "api.codex-scaling.local"
  type               = "A"
  alias {
    name                   = module.secondary_region_2.cluster_endpoint
    zone_id                = module.secondary_region_2.cluster_zone_id
    evaluate_target_health = true
  }
  
  failover_routing_policy {
    type = "SECONDARY"
  }
  
  health_check_id = aws_route53_health_check.secondary_2.id
  set_identifier = "secondary-2"
}

# ============================================================================
# Reserved Instances for Cost Optimization (Gate 5: ≥15% savings)
# ============================================================================

resource "aws_ec2_instance_reservation" "reserved_instances" {
  instance_type     = "t3.xlarge"
  availability_zone = "${var.primary_region}a"
  instance_count    = 5
  term_length       = 12  # 1-year reserved instance
  offering_type     = "ALL_UPFRONT"
  
  tags = {
    Name = "codex-scaling-reserved-instances"
    Component = "cost-optimization"
  }
}

# ============================================================================
# Cost Allocation Tags
# ============================================================================

resource "aws_ec2_tag" "cost_allocation" {
  for_each = {
    "CostCenter" = "scaling-framework"
    "Environment" = var.environment
    "Phase" = "4E"
    "Planset" = "010"
    "Team" = "infrastructure"
  }
  
  resource_id = module.primary_region.cluster_id
  key         = each.key
  value       = each.value
}

# ============================================================================
# Monitoring and Alerting
# ============================================================================

resource "aws_cloudwatch_metric_alarm" "cpu_scale_up" {
  alarm_name          = "codex-scaling-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 60
  statistic           = "Average"
  threshold           = 75  # Gate 4: Scale up at 75% CPU
  
  dimensions = {
    AutoScalingGroupName = module.primary_region.asg_name
  }
  
  alarm_actions = [module.primary_region.scale_up_policy_arn]
}

resource "aws_cloudwatch_metric_alarm" "memory_scale_up" {
  alarm_name          = "codex-scaling-memory-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/EC2"
  period              = 60
  statistic           = "Average"
  threshold           = 80  # Gate 4: Scale up at 80% memory
  
  dimensions = {
    AutoScalingGroupName = module.primary_region.asg_name
  }
  
  alarm_actions = [module.primary_region.scale_up_policy_arn]
}

# ============================================================================
# Outputs
# ============================================================================

output "primary_cluster_endpoint" {
  value       = module.primary_region.cluster_endpoint
  description = "Primary region cluster endpoint"
}

output "api_endpoint" {
  value       = aws_route53_record.primary_failover.fqdn
  description = "Global API endpoint with automatic failover"
}

output "health_check_ids" {
  value = {
    primary     = aws_route53_health_check.primary.id
    secondary_1 = aws_route53_health_check.secondary_1.id
    secondary_2 = aws_route53_health_check.secondary_2.id
  }
  description = "Health check IDs for monitoring"
}

output "ri_count" {
  value       = aws_ec2_instance_reservation.reserved_instances.instance_count
  description = "Number of reserved instances for cost optimization"
}

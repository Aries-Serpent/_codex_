# AWS ECS Deployment Guide
**Last Updated:** 2026-07-11
**Version:** v0.2.0

**Last Updated**: 2026-07-08
**Version**: 1.0
**Audience**: DevOps engineers, AWS platform engineers, production operators
**Environment**: AWS ECS (Elastic Container Service)
**Tier**: Production-Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Architecture](#architecture)
4. [Step-by-Step Deployment](#step-by-step-deployment)
5. [Load Balancing](#load-balancing)
6. [Auto-Scaling Configuration](#auto-scaling-configuration)
7. [Monitoring & Logging](#monitoring--logging)
8. [Troubleshooting](#troubleshooting)
9. [Cost Optimization](#cost-optimization)

---

## Overview

This guide covers deploying Codex ML on AWS ECS with production-grade reliability, auto-scaling, and observability.

### Deployment Architecture

```

 AWS Account 

 
 
 Application Load Balancer (ALB) 
 - TLS/HTTPS termination 
 - Path-based routing 
 
 
 
 ECS Cluster ECS Cluster 
 (Region 1) (Region 2) 
 (Standby) 
 
 Task Def 
 Codex ML 
 (v1.0) 
 
 
 
 Service 
 (Desired:4) 
 
 
 
 
 RDS Database (PostgreSQL) 
 - Multi-AZ deployment 
 - Automated backups 
 
 
 
 ElastiCache (Redis) 
 - Session cache 
 - Model cache 
 
 
 
 CloudWatch Logs & Metrics 
 - Container logs 
 - Performance metrics 
 
 

```

---

## Prerequisites

### AWS Resources Required

```bash
# Minimum IAM permissions needed
{
 "Version": "2012-10-17",
 "Statement": [
 {
 "Effect": "Allow",
 "Action": [
 "ecs:*",
 "ec2:*",
 "ecr:*",
 "elasticloadbalancing:*",
 "rds:*",
 "elasticache:*",
 "cloudwatch:*",
 "logs:*",
 "iam:PassRole"
 ],
 "Resource": "*"
 }
 ]
}
```

### AWS CLI Configuration

```bash
# Install AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure credentials
aws configure
# Output:
# AWS Access Key ID: [your-key-id]
# AWS Secret Access Key: [your-secret-key]
# Default region: us-east-1
# Default output format: json
```

### Local Tools

```bash
# Docker for image building/testing
docker --version # Requires >= 20.10

# AWS SAM CLI (optional, for IaC)
pip install aws-sam-cli

# Terraform (optional, for IaC)
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/
```

---

## Step-by-Step Deployment

### 1. Create ECR Repository

```bash
# Create repository for Codex ML image
aws ecr create-repository \
 --repository-name codex-ml \
 --region us-east-1 \
 --encryption-configuration encryptionType=AES

# Output:
# {
# "repository": {
# "repositoryArn": "arn:aws:ecr:us-east-1:123456789:repository/codex-ml",
# "registryId": "123456789",
# "repositoryName": "codex-ml",
# "repositoryUri": "123456789.dkr.ecr.us-east-1.amazonaws.com/codex-ml"
# }
# }

# Save the repository URI
REPO_URI="123456789.dkr.ecr.us-east-1.amazonaws.com/codex-ml"
```

### 2. Build and Push Docker Image

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
 docker login --username AWS --password-stdin $REPO_URI

# Build image
docker build \
 --file docker/Dockerfile.cpu \
 --tag codex-ml:1.0.0 \
 --build-arg VERSION=1.0.0 \
 .

# Tag for ECR
docker tag codex-ml:1.0.0 $REPO_URI:1.0.0
docker tag codex-ml:1.0.0 $REPO_URI:latest

# Push to ECR
docker push $REPO_URI:1.0.0
docker push $REPO_URI:latest

# Verify image
aws ecr describe-images \
 --repository-name codex-ml \
 --region us-east-1
```

### 3. Create IAM Roles

```bash
# Create ECS task execution role
aws iam create-role \
 --role-name ecsTaskExecutionRole \
 --assume-role-policy-document '{
 "Version": "2012-10-17",
 "Statement": [{
 "Effect": "Allow",
 "Principal": {"Service": "ecs-tasks.amazonaws.com"},
 "Action": "sts:AssumeRole"
 }]
 }'

# Attach execution policy
aws iam attach-role-policy \
 --role-name ecsTaskExecutionRole \
 --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

# Create ECS task role (for application permissions)
aws iam create-role \
 --role-name ecsTaskRole \
 --assume-role-policy-document '{
 "Version": "2012-10-17",
 "Statement": [{
 "Effect": "Allow",
 "Principal": {"Service": "ecs-tasks.amazonaws.com"},
 "Action": "sts:AssumeRole"
 }]
 }'

# Add inline policy for S3 access
aws iam put-role-policy \
 --role-name ecsTaskRole \
 --policy-name s3-access \
 --policy-document '{
 "Version": "2012-10-17",
 "Statement": [{
 "Effect": "Allow",
 "Action": ["s3:GetObject", "s3:PutObject"],
 "Resource": "arn:aws:s3:::codex-ml-bucket/*"
 }]
 }'
```

### 4. Create ECS Cluster

```bash
# Create ECS cluster
aws ecs create-cluster \
 --cluster-name codex-ml-prod \
 --region us-east-1 \
 --settings name=containerInsights,value=enabled \
 --capacity-providers FARGATE FARGATE_SPOT

# Output:
# {
# "cluster": {
# "clusterName": "codex-ml-prod",
# "clusterArn": "arn:aws:ecs:us-east-1:123456789:cluster/codex-ml-prod"
# }
# }
```

### 5. Create VPC and Networking

```bash
# Create VPC
VPC_ID=$(aws ec2 create-vpc \
 --cidr-block 10.0.0.0/16 \
 --query 'Vpc.VpcId' \
 --output text)

# Create subnets (at least 2 for HA)
SUBNET_1=$(aws ec2 create-subnet \
 --vpc-id $VPC_ID \
 --cidr-block 10.0.1.0/24 \
 --availability-zone us-east-1a \
 --query 'Subnet.SubnetId' \
 --output text)

SUBNET_2=$(aws ec2 create-subnet \
 --vpc-id $VPC_ID \
 --cidr-block 10.0.2.0/24 \
 --availability-zone us-east-1b \
 --query 'Subnet.SubnetId' \
 --output text)

# Create security group
SG_ID=$(aws ec2 create-security-group \
 --group-name codex-ml-sg \
 --description "Security group for Codex ML ECS" \
 --vpc-id $VPC_ID \
 --query 'GroupId' \
 --output text)

# Allow ALB traffic
aws ec2 authorize-security-group-ingress \
 --group-id $SG_ID \
 --protocol tcp \
 --port 8000 \
 --cidr 10.0.0.0/16

# Allow external HTTPS
aws ec2 authorize-security-group-ingress \
 --group-id $SG_ID \
 --protocol tcp \
 --port 443 \
 --cidr 0.0.0.0/0
```

### 6. Create Application Load Balancer

```bash
# Create load balancer
ALB_ARN=$(aws elbv2 create-load-balancer \
 --name codex-ml-alb \
 --subnets $SUBNET_1 $SUBNET_2 \
 --security-groups $SG_ID \
 --scheme internet-facing \
 --type application \
 --query 'LoadBalancers[0].LoadBalancerArn' \
 --output text)

# Get ALB DNS name
ALB_DNS=$(aws elbv2 describe-load-balancers \
 --load-balancer-arns $ALB_ARN \
 --query 'LoadBalancers[0].DNSName' \
 --output text)

# Create target group
TG_ARN=$(aws elbv2 create-target-group \
 --name codex-ml-targets \
 --protocol HTTP \
 --port 8000 \
 --vpc-id $VPC_ID \
 --target-type ip \
 --health-check-protocol HTTP \
 --health-check-path /health \
 --health-check-interval-seconds 30 \
 --health-check-timeout-seconds 5 \
 --healthy-threshold-count 2 \
 --unhealthy-threshold-count 3 \
 --query 'TargetGroups[0].TargetGroupArn' \
 --output text)

# Create listener (HTTP for now, add HTTPS later)
aws elbv2 create-listener \
 --load-balancer-arn $ALB_ARN \
 --protocol HTTP \
 --port 80 \
 --default-actions Type=forward,TargetGroupArn=$TG_ARN
```

### 7. Create RDS Database

```bash
# Create DB subnet group
aws rds create-db-subnet-group \
 --db-subnet-group-name codex-ml-subnet \
 --db-subnet-group-description "Subnet group for Codex ML" \
 --subnet-ids $SUBNET_1 $SUBNET_2

# Create RDS instance
aws rds create-db-instance \
 --db-instance-identifier codex-ml-db \
 --db-instance-class db.t3.small \
 --engine postgres \
 --engine-version 14.7 \
 --master-username codex_admin \
 --master-user-password "$(openssl rand -base64 32)" \
 --allocated-storage 100 \
 --db-subnet-group-name codex-ml-subnet \
 --vpc-security-group-ids $SG_ID \
 --multi-az \
 --backup-retention-period 30 \
 --copy-tags-to-snapshot \
 --storage-encrypted \
 --kms-key-id arn:aws:kms:us-east-1:123456789:key/12345678-1234-1234-1234-123456789012

# Wait for database to be available
aws rds wait db-instance-available \
 --db-instance-identifier codex-ml-db
```

### 8. Create ElastiCache Redis

```bash
# Create cache subnet group
aws elasticache create-cache-subnet-group \
 --cache-subnet-group-name codex-ml-cache \
 --cache-subnet-group-description "Cache for Codex ML" \
 --subnet-ids $SUBNET_1 $SUBNET_2

# Create Redis cluster
aws elasticache create-replication-group \
 --replication-group-description "Redis cache for Codex ML" \
 --engine redis \
 --engine-version 7.0 \
 --cache-node-type cache.t3.micro \
 --num-cache-clusters 2 \
 --automatic-failover-enabled \
 --cache-subnet-group-name codex-ml-cache \
 --security-group-ids $SG_ID \
 --at-rest-encryption-enabled \
 --transit-encryption-enabled
```

### 9. Create ECS Task Definition

```bash
# Save task definition to file
cat > task-definition.json <<'EOF'
{
 "family": "codex-ml",
 "networkMode": "awsvpc",
 "requiresCompatibilities": ["FARGATE"],
 "cpu": "1024",
 "memory": "2048",
 "containerDefinitions": [
 {
 "name": "codex-ml",
 "image": "REPO_URI:1.0.0",
 "portMappings": [
 {
 "containerPort": 8000,
 "protocol": "tcp"
 }
 ],
 "environment": [
 {
 "name": "ENVIRONMENT",
 "value": "production"
 },
 {
 "name": "DATABASE_URL",
 "value": "******DB_ENDPOINT:5432/codex"
 },
 {
 "name": "REDIS_URL",
 "value": "redis://REDIS_ENDPOINT:6379/0"
 },
 {
 "name": "LOG_LEVEL",
 "value": "INFO"
 }
 ],
 "secrets": [
 {
 "name": "DATABASE_PASSWORD",
 "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789:secret:codex/db-password"
 },
 {
 "name": "API_KEY",
 "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789:secret:codex/api-key"
 }
 ],
 "logConfiguration": {
 "logDriver": "awslogs",
 "options": {
 "awslogs-group": "/ecs/codex-ml",
 "awslogs-region": "us-east-1",
 "awslogs-stream-prefix": "ecs"
 }
 },
 "healthCheck": {
 "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
 "interval": 30,
 "timeout": 5,
 "retries": 3,
 "startPeriod": 60
 }
 }
 ],
 "executionRoleArn": "arn:aws:iam::123456789:role/ecsTaskExecutionRole",
 "taskRoleArn": "arn:aws:iam::123456789:role/ecsTaskRole"
}
EOF

# Replace placeholders
sed -i "s|REPO_URI|$REPO_URI|g" task-definition.json
sed -i "s|DB_ENDPOINT|codex-ml-db.c123456789.us-east-1.rds.amazonaws.com|g" task-definition.json
sed -i "s|REDIS_ENDPOINT|codex-ml.c123456789.ng.0001.use1.cache.amazonaws.com|g" task-definition.json

# Register task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json
```

### 10. Create ECS Service

```bash
# Create CloudWatch log group
aws logs create-log-group --log-group-name /ecs/codex-ml

# Create service
aws ecs create-service \
 --cluster codex-ml-prod \
 --service-name codex-ml-service \
 --task-definition codex-ml:1 \
 --desired-count 2 \
 --launch-type FARGATE \
 --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_1,$SUBNET_2],securityGroups=[$SG_ID],assignPublicIp=DISABLED}" \
 --load-balancers targetGroupArn=$TG_ARN,containerName=codex-ml,containerPort=8000 \
 --deployment-configuration "minimumHealthyPercent=100,maximumPercent=200" \
 --enable-ecs-managed-tags
```

---

## Load Balancing

### Multi-Region Setup

```bash
# Create Route 53 health check
aws route53 create-health-check \
 --caller-reference $(date +%s) \
 --health-check-config IPAddress=$ALB_DNS,Port=80,Type=HTTP,ResourcePath=/health

# Create Route 53 record with geolocation routing
# (Requires Route 53 hosted zone setup)
```

### Sticky Sessions

```bash
# Enable sticky sessions for target group
aws elbv2 modify-target-group-attributes \
 --target-group-arn $TG_ARN \
 --attributes \
 Key=stickiness.enabled,Value=true \
 Key=stickiness.type,Value=lb_cookie \
 Key=stickiness.lb_cookie.duration_seconds,Value=86400
```

---

## Auto-Scaling Configuration

### Service Auto-Scaling

```bash
# Register scalable target
aws application-autoscaling register-scalable-target \
 --service-namespace ecs \
 --resource-id service/codex-ml-prod/codex-ml-service \
 --scalable-dimension ecs:service:DesiredCount \
 --min-capacity 2 \
 --max-capacity 10

# Create scaling policy for CPU
aws application-autoscaling put-scaling-policy \
 --policy-name codex-ml-cpu-scaling \
 --service-namespace ecs \
 --resource-id service/codex-ml-prod/codex-ml-service \
 --scalable-dimension ecs:service:DesiredCount \
 --policy-type TargetTrackingScaling \
 --target-tracking-scaling-policy-configuration '{
 "TargetValue": 70.0,
 "PredefinedMetricSpecification": {
 "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
 },
 "ScaleOutCooldown": 60,
 "ScaleInCooldown": 300
 }'

# Create scaling policy for memory
aws application-autoscaling put-scaling-policy \
 --policy-name codex-ml-memory-scaling \
 --service-namespace ecs \
 --resource-id service/codex-ml-prod/codex-ml-service \
 --scalable-dimension ecs:service:DesiredCount \
 --policy-type TargetTrackingScaling \
 --target-tracking-scaling-policy-configuration '{
 "TargetValue": 80.0,
 "PredefinedMetricSpecification": {
 "PredefinedMetricType": "ECSServiceAverageMemoryUtilization"
 },
 "ScaleOutCooldown": 60,
 "ScaleInCooldown": 300
 }'
```

---

## Monitoring & Logging

### CloudWatch Setup

```bash
# Enable detailed monitoring
aws ec2 monitor-instances --instance-ids $(aws ec2 describe-instances \
 --filters "Name=tag:Application,Values=codex-ml" \
 --query 'Reservations[*].Instances[*].InstanceId' \
 --output text)

# Create CloudWatch alarms
aws cloudwatch put-metric-alarm \
 --alarm-name codex-ml-high-cpu \
 --alarm-description "Alert when CPU > 80%" \
 --metric-name CPUUtilization \
 --namespace AWS/ECS \
 --statistic Average \
 --period 300 \
 --threshold 80 \
 --comparison-operator GreaterThanThreshold \
 --evaluation-periods 2

aws cloudwatch put-metric-alarm \
 --alarm-name codex-ml-high-memory \
 --alarm-description "Alert when memory > 85%" \
 --metric-name MemoryUtilization \
 --namespace AWS/ECS \
 --statistic Average \
 --period 300 \
 --threshold 85 \
 --comparison-operator GreaterThanThreshold \
 --evaluation-periods 2

# Create dashboard
aws cloudwatch put-dashboard \
 --dashboard-name codex-ml-prod \
 --dashboard-body file://dashboard.json
```

### Logging Configuration

```bash
# Create log group if not exists
aws logs create-log-group --log-group-name /ecs/codex-ml 2>/dev/null

# Set retention
aws logs put-retention-policy \
 --log-group-name /ecs/codex-ml \
 --retention-in-days 30

# Create log filters for errors
aws logs put-metric-filter \
 --log-group-name /ecs/codex-ml \
 --filter-name error-count \
 --filter-pattern "[ERROR]" \
 --metric-transformations metricName=ErrorCount,metricValue=1

# Verify logs are flowing
aws logs tail /ecs/codex-ml --follow
```

---

## Troubleshooting

### Common Issues

#### 1. Service Not Starting

```bash
# Check service status
aws ecs describe-services \
 --cluster codex-ml-prod \
 --services codex-ml-service

# Check task logs
TASK_ID=$(aws ecs list-tasks \
 --cluster codex-ml-prod \
 --service-name codex-ml-service \
 --query 'taskArns[0]' \
 --output text | cut -d'/' -f3)

aws logs tail /ecs/codex-ml --follow --task $TASK_ID
```

#### 2. Unhealthy Targets in ALB

```bash
# Check target health
aws elbv2 describe-target-health \
 --target-group-arn $TG_ARN

# Check container logs
aws ecs describe-tasks \
 --cluster codex-ml-prod \
 --tasks <task-arn> \
 --query 'tasks[0].containers[0].lastStatus'

# Test health endpoint manually
curl -v http://$ALB_DNS/health
```

#### 3. Database Connection Issues

```bash
# Test database connectivity
aws rds describe-db-instances \
 --db-instance-identifier codex-ml-db \
 --query 'DBInstances[0].Endpoint'

# Check security groups
aws ec2 describe-security-groups \
 --group-ids $SG_ID \
 --query 'SecurityGroups[0].IpPermissions'

# Test connection from ECS task
aws ecs execute-command \
 --cluster codex-ml-prod \
 --task <task-id> \
 --container codex-ml \
 --interactive \
 --command "/bin/bash"
# Then: psql ******host:5432/db
```

---

## Cost Optimization

### Reserved Instances

```bash
# Get savings plans recommendations
aws ce get-savings-plans-purchase-recommendation \
 --savings-plans-type COMPUTE_SP \
 --lookback-period THIRTY_DAYS \
 --term-in-years ONE_YEAR

# Purchase reservation if cost-effective
```

### Spot Instances

```bash
# Update capacity providers to use Spot
aws ecs create-capacity-provider \
 --name codex-ml-spot \
 --auto-scaling-group-provider autoScalingGroupArn=arn:...,managedScaling={status=ENABLED,targetCapacity=80,minimumScalingStepSize=1,maximumScalingStepSize=1000}

# Use Spot in service
aws ecs update-service \
 --cluster codex-ml-prod \
 --service codex-ml-service \
 --capacity-provider-strategy capacityProvider=FARGATE_SPOT,weight=70 capacityProvider=FARGATE,weight=30
```

---

## Rollback Procedures

```bash
# Rollback to previous task definition
PREV_VERSION=$((CURRENT_VERSION - 1))

aws ecs update-service \
 --cluster codex-ml-prod \
 --service codex-ml-service \
 --task-definition codex-ml:$PREV_VERSION

# Verify rollback
aws ecs describe-services \
 --cluster codex-ml-prod \
 --services codex-ml-service \
 --query 'services[0].taskDefinition'
```

---

## Production Readiness Checklist

- [ ] VPC configured with proper subnets
- [ ] Security groups configured with least privilege
- [ ] RDS instance in Multi-AZ with encryption
- [ ] ElastiCache Redis configured with high availability
- [ ] ALB configured with health checks
- [ ] CloudWatch logs configured with retention
- [ ] Alarms configured for CPU/memory/errors
- [ ] Auto-scaling policies configured
- [ ] Backup procedures documented
- [ ] Disaster recovery plan tested
- [ ] SSL/TLS certificates installed
- [ ] IAM roles with minimal permissions
- [ ] Secrets stored in Secrets Manager
- [ ] Cost monitoring configured

---

**Next Steps**:
1. Run deployment checklist before production
2. Set up monitoring dashboards
3. Configure log aggregation
4. Conduct disaster recovery drill
5. Schedule regular backup tests


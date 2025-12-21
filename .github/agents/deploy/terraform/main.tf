terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}

variable "environment" { type = string }
variable "aws_region" { type = string, default = "us-east-1" }
variable "github_app_id" { type = string, sensitive = true }
variable "github_webhook_secret" { type = string, sensitive = true }

provider "aws" { region = var.aws_region }

resource "aws_s3_bucket" "metrics" {
  bucket = "codex-reviewer-${var.environment}"
}

resource "aws_iam_role" "lambda" {
  name = "codex-reviewer-${var.environment}"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{ Action = "sts:AssumeRole", Effect = "Allow", Principal = { Service = "lambda.amazonaws.com" }}]
  })
}

resource "aws_lambda_function" "agent" {
  function_name = "codex-reviewer-${var.environment}"
  role = aws_iam_role.lambda.arn
  handler = "main.handler"
  runtime = "python3.11"
  filename = "lambda.zip"
}

output "webhook_url" { value = "https://example.com/webhook" }

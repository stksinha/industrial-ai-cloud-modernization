# terraform/main.tf
# Improved Industrial AI Cloud Modernization Configuration

tf
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  # Backend configuration for remote state storage
  backend "s3" {
    bucket         = "industrial-ai-tfstate"
    key            = "terraform/main.tfstate"
    region         = "eu-west-2"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}

provider "aws" {
  region = var.region

  default_tags {
    tags = merge(
      var.project_tags,
      {
        Environment = var.environment
        ManagedBy   = "Terraform"
        CreatedAt   = timestamp()
      }
    )
  }
}

# 1. Create a VPC for Industrial Security with Enhanced Configuration
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name   = "${var.cluster_name}-vpc"
  cidr   = var.vpc_cidr
  azs    = var.azs

  private_subnets = var.private_subnets
  public_subnets  = var.public_subnets

  # Enable NAT Gateway for secure outbound traffic from private subnets
  enable_nat_gateway = true
  single_nat_gateway = false # Use one NAT per AZ for high availability

  # Enable DNS settings for EKS compatibility
  enable_dns_hostnames = true
  enable_dns_support   = true

  # Enable VPC Flow Logs for security monitoring
  enable_flow_log                      = true
  create_flow_log_cloudwatch_iam_role  = true
  create_flow_log_cloudwatch_log_group = true

  tags = var.project_tags
}

# 2. Create the EKS Cluster with Best Practices
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = var.cluster_name
  cluster_version = var.cluster_version

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  # Enable cluster encryption with AWS KMS for enhanced security
  cluster_encryption_config = {
    provider_key_arn = aws_kms_key.eks.arn
    resources        = ["secrets"]
  }

  # Configure EKS managed node groups with best practices
  eks_managed_node_groups = {
    general = {
      name            = "${var.cluster_name}-general-ng"
      desired_size    = var.node_desired_size
      min_size        = var.node_min_size
      max_size        = var.node_max_size
      instance_types  = var.node_instance_types
      capacity_type   = "ON_DEMAND"
      ami_type        = "AL2_x86_64" # Amazon Linux 2

      # Node labeling for better scheduling
      labels = {
        Environment = var.environment
        NodeGroup   = "general"
      }

      tags = merge(
        var.project_tags,
        {
          NodeGroup = "general"
        }
      )

      # Block device configuration for optimal storage
      block_device_mappings = {
        xvda = {
          device_name = "/dev/xvda"
          ebs = {
            volume_size           = 50
            volume_type           = "gp3"
            iops                  = 3000
            throughput            = 125
            delete_on_termination = true
            encrypted             = true
          }
        }
      }
    }
  }

  # Enable cluster logging for better observability
  cluster_enabled_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]

  # Configure IRSA (IAM Roles for Service Accounts)
  enable_irsa = true

  tags = var.project_tags
}

# Create KMS key for EKS cluster encryption
resource "aws_kms_key" "eks" {
  description             = "KMS key for ${var.cluster_name} EKS cluster encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = merge(
    var.project_tags,
    {
      Name = "${var.cluster_name}-eks-key"
    }
  )
}

resource "aws_kms_alias" "eks" {
  name          = "alias/${var.cluster_name}-eks"
  target_key_id = aws_kms_key.eks.key_id
}
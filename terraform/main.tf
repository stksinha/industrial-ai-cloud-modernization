# terraform/main.tf

provider "aws" {
  region = "eu-west-2" # London 
}

# 1. Create a VPC for Industrial Security
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  name    = "industrial-vpc"
  cidr    = "10.0.0.0/16"

  azs             = ["eu-west-2a", "eu-west-2b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway = true # Required for private nodes to reach the internet
}

# 2. Create the EKS Cluster (Your CKA Validation)
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  cluster_name    = "industrial-ai-cluster"
  cluster_version = "1.29"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  eks_managed_node_groups = {
    general = {
      desired_size = 2
      min_size     = 1
      max_size     = 3
      instance_types = ["t3.medium"]
    }
  }
}

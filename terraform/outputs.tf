# Output values for referencing Terraform resources

# VPC Outputs
output "vpc_id" {
  description = "The ID of the VPC"
  value       = module.vpc.vpc_id
}

output "vpc_cidr_block" {
  description = "The CIDR block of the VPC"
  value       = module.vpc.vpc_cidr_block
}

output "private_subnets" {
  description = "List of IDs of private subnets"
  value       = module.vpc.private_subnets
}

output "public_subnets" {
  description = "List of IDs of public subnets"
  value       = module.vpc.public_subnets
}

output "nat_gateway_ids" {
  description = "List of NAT Gateway IDs"
  value       = module.vpc.natgw_ids
}

output "nat_gateway_public_ips" {
  description = "List of public Elastic IPs created for NAT Gateways"
  value       = module.vpc.nat_public_ips
}

# EKS Cluster Outputs
output "cluster_name" {
  description = "The name of the EKS cluster"
  value       = module.eks.cluster_name
}

output "cluster_arn" {
  description = "The Amazon Resource Name (ARN) of the cluster"
  value       = module.eks.cluster_arn
}

output "cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = module.eks.cluster_endpoint
}

output "cluster_version" {
  description = "The Kubernetes server version for the cluster"
  value       = module.eks.cluster_version
}

output "cluster_certificate_authority_data" {
  description = "Base64 encoded certificate data required to communicate with the cluster"
  value       = module.eks.cluster_certificate_authority_data
  sensitive   = true
}

output "cluster_security_group_id" {
  description = "Security group ID attached to the EKS cluster"
  value       = module.eks.cluster_security_group_id
}

# Node Group Outputs
output "eks_managed_node_groups" {
  description = "EKS managed node group outputs"
  value       = module.eks.eks_managed_node_groups
}

# KMS Key Outputs
output "kms_key_id" {
  description = "The KMS key ID used for EKS cluster encryption"
  value       = aws_kms_key.eks.key_id
}

output "kms_key_arn" {
  description = "The ARN of the KMS key used for EKS cluster encryption"
  value       = aws_kms_key.eks.arn
}

# IRSA Configuration
output "oidc_provider_arn" {
  description = "ARN of the OIDC provider for IRSA"
  value       = module.eks.oidc_provider_arn
}
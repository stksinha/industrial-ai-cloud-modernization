variable "region" {
  description = "The region in which to deploy resources."
  type        = string
}

variable "vpc_cidr" {
  description = "The CIDR block for the VPC."
  type        = string
}

variable "azs" {
  description = "The availability zones for the deployment."
  type        = list(string)
}

variable "private_subnets" {
  description = "List of private subnets."
  type        = list(string)
}

variable "public_subnets" {
  description = "List of public subnets."
  type        = list(string)
}

variable "cluster_name" {
  description = "The name of the cluster."
  type        = string
}

variable "cluster_version" {
  description = "The version of the cluster."
  type        = string
}

variable "node_desired_size" {
  description = "The desired number of nodes in the cluster."
  type        = number
}

variable "node_min_size" {
  description = "The minimum number of nodes in the cluster."
  type        = number
}

variable "node_max_size" {
  description = "The maximum number of nodes in the cluster."
  type        = number
}

variable "node_instance_types" {
  description = "The instance types for the cluster nodes."
  type        = list(string)
}

variable "environment" {
  description = "The environment for the deployment (e.g., dev, stage, prod)."
  type        = string
}

variable "project_tags" {
  description = "Tags for the project."
  type        = map(string)
}
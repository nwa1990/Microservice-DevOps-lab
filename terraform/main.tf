terraform {
  backend "s3" {
    bucket         = "my-terraform-state-bucket"
    key            = "dev/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

module "network" {
  source   = "./modules/network"
  vpc_cidr = var.vpc_cidr
  environment = "dev"
}

module "eks" {
  source          = "./modules/eks"
  cluster_name    = var.cluster_name
  vpc_id          = module.network.vpc_id
  subnet_ids      = module.network.private_subnet_ids
}

module "iam" {
  source        = "./modules/iam"
  cluster_name  = var.cluster_name
}

output "cluster_name" {
  value = module.eks.cluster_name
}

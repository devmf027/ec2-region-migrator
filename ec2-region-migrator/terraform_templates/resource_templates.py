vpc_module_template = """
# AWS Availability Zones Datasource
data "aws_availability_zones" "available" {
  #state = "available"
}

# Create VPC Terraform Module
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "5.1.2"

  # VPC Basic Details
  name            = var.vpc_name
  cidr            = var.vpc_cidr_block
  azs             = data.aws_availability_zones.available.names
  public_subnets  = var.vpc_public_subnets


  # VPC DNS Parameters
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags     = var.vpc_tags

  # Instances launched into the Public subnet should be assigned a public IP address.
  map_public_ip_on_launch = true
}
"""

vpc_variables_template = """
# VPC Input Variables

# VPC Name
variable "vpc_name" {
  description = "VPC Name"
  type        = string
  default     = "vpc-%(index)s"
}

# VPC CIDR Block
variable "vpc_cidr_block" {
  description = "VPC CIDR Block"
  type        = string
  default     = "%(CidrBlock)s"
}

# VPC Public Subnets
variable "vpc_public_subnets" {
  description = "VPC Public Subnets"
  type        = list(string)
  default     = %(PublicCidrBlock)s
}

# VPC Public Tags
variable "vpc_tags" {
  description = "VPC Tags"
  type        = map(string)
  default     = %(Tags)s
}
"""

vpc_auto_tfvars_template = """
# VPC Variables
vpc_name                               = "vpc-%(index)s"
vpc_cidr_block                         = "%(CidrBlock)s"
vpc_public_subnets                     = %(PublicCidrBlock)s
vpc_tags                               = %(Tags)s
"""

generic_variables_template = """
# Input Variables
# AWS Region
variable "aws_region" {
  description = "Region in which AWS Resources to be created"
  type        = string
  default     = "%(Region)s"
}
"""

terraform_tfvars_template = """
# Generic Variables
aws_region       = "%(Region)s"
"""

versions_template = """
# Terraform Block
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = ">= 4.65"
    }
  }
}

# Provider Block
provider "aws" {
  region = var.aws_region
  # profile = "default"
}
"""

security_group_resource_template = """
resource "aws_security_group" "security_group_%(index)s" {
  description = %(Description)s
  vpc_id      = module.vpc.vpc_id

  %(IngressRules)s
  %(EgressRules)s

  tags = %(Tags)s
}
"""

ingress_rule_template = """
  ingress {
    description      = %(Description)s
    from_port        = %(FromPort)s
    to_port          = %(ToPort)s
    protocol         = %(Protocol)s
    cidr_blocks      = %(CidrBlocks)s
    ipv6_cidr_blocks = %(Ipv6CidrBlocks)s
  }
"""

egress_rule_template = """
  egress {
    description      = %(Description)s
    from_port        = %(FromPort)s
    to_port          = %(ToPort)s
    protocol         = %(Protocol)s
    cidr_blocks      = %(CidrBlocks)s
    ipv6_cidr_blocks = %(Ipv6CidrBlocks)s
  }
"""

ec2_instance_module_template = """
module "ec2_instance_%(index)s" {
  source  = "terraform-aws-modules/ec2-instance/aws"
  version = "5.5.0"

  name          = "instance-%(index)s"
  ami           = "%(ImageId)s"
  instance_type = "%(InstanceType)s"

  subnet_id              = module.vpc.public_subnets[0]
  vpc_security_group_ids = %(SecurityGroupIds)s

  tags = %(Tags)s
}
"""

eip_resource_template = """
# Create Elastic IP for Instance-%(index)s
resource "aws_eip" "instance_eip-%(index)s" {
  instance   = module.ec2_instance_%(index)s.id
  domain     = "vpc"
  depends_on = [module.ec2_instance_%(index)s, module.vpc]
}
"""

terraform_backend_template = """
terraform {
  backend "s3" {
    bucket         = "%(bucket)s"
    key            = "%(vpcName)s/%(key)s"
    region         = "%(region)s"
    encrypt        = true
    dynamodb_table = "%(dynamodb_table)s"
  }
}
"""

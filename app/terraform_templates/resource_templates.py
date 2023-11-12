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
  default     = "vpc-%(index)d"
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
  type        = list(string)
  default     = %(Tags)s
}
"""

vpc_auto_tfvars_template = """
# VPC Variables
vpc_name                               = "vpc-%(index)d"
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
resource "aws_security_group" "allow_tls" {
  name        = %(GroupName)s
  description = %(Description)s
  vpc_id      = %(VpcId)s

  ingress {
    description      = %(Description)s
    from_port        = %(IngressFromPort)s
    to_port          = %(IngressToPort)s
    protocol         = %(IngressProtocol)s
    cidr_blocks      = %(IngressCidrIp)s
    ipv6_cidr_blocks = %(IngressCidrIpv6)s
  }

  egress {
    from_port        = %(EgressFromPort)s
    to_port          = %(EgressToPort)s
    protocol         = %(EgressProtocol)s
    cidr_blocks      = %(EgressCidrIp)s
    ipv6_cidr_blocks = %(EgressCidrIpv6)s
  }

  tags = {
    Name = %(Tags)s
  }
}
"""

ec2_instance_module_template = """
module "ec2_instance_%(index)d" {
  source  = "terraform-aws-modules/ec2-instance/aws"
  version = "5.5.0"

  name          = "$instance-%(index)d"
  ami           = "%(ImageId)s"
  instance_type = "%(InstanceType)s"

  subnet_id              = %(CidrBlock)s
  vpc_security_group_ids = [module.public_web_server_sg.security_group_id]

  tags = %(Tags)s
}
"""



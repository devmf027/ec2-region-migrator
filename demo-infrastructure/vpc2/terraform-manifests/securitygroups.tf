# AWS EC2 Security Group Terraform Module
# Security Group for Public Bastion Host

module "public_bastion_sg" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "5.1.0"

  name        = "${local.name}-public-bastion-sg"
  description = "Security group with SSH port open for everybody (IPv4 CIDR), egress all open"
  vpc_id      = module.vpc.vpc_id

  # Ingress rules & CIDR block
  ingress_rules       = ["ssh-tcp"]
  ingress_cidr_blocks = ["0.0.0.0/0"]

  # Egress rules all-all open
  egress_rules = ["all-all"]
  tags         = local.common_tags
}

module "public_web_server_sg" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "5.1.0"

  name        = "${local.name}-public-web-server-sg"
  description = "Security group with SSH port open for everybody (IPv4 CIDR), egress all open"
  vpc_id      = module.vpc.vpc_id

  # Ingress rules & CIDR block
  ingress_rules       = ["https-443-tcp"]
  ingress_cidr_blocks = ["0.0.0.0/0"]

  # Egress rules all-all open
  egress_rules = ["all-all"]
  tags         = local.common_tags
}
# AWS EC2 Instance Terraform Module
# Bastion Host - EC2 Instance that will be created in VPC Public Subnet
module "ec2_public_bastion" {
  source  = "terraform-aws-modules/ec2-instance/aws"
  version = "5.5.0"
  count = 2
  name          = "${local.name}-bastion-host-${count.index}"
  ami           = data.aws_ami.amzlinux2.id
  instance_type = "t2.nano"

  subnet_id              = module.vpc.public_subnets[0]
  vpc_security_group_ids = [module.public_bastion_sg.security_group_id]

  tags = local.common_tags
}

module "ec2_public_web_server" {
  source  = "terraform-aws-modules/ec2-instance/aws"
  version = "5.5.0"

  name          = "${local.name}-web-server"
  ami           = data.aws_ami.amzlinux2.id
  instance_type = "t2.micro"

  subnet_id              = module.vpc.public_subnets[1]
  vpc_security_group_ids = [module.public_web_server_sg.security_group_id]

  tags = local.common_tags
}
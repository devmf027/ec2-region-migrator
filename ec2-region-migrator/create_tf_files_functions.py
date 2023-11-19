import os
import json
from ipaddress import ip_network
import terraform_templates.resource_templates as var


def create_vpc_module(vpc_module_template, index):
    """
    Create a Terraform module for VPC configuration.

    :param vpc_module_template: str
        The Terraform template for the VPC module.

    :param index: int
        The index of the VPC module.

    :return: None
    """
    output_directory = os.path.join(
        os.path.dirname(__file__), '..', "terraform")
    vpc_directory = os.path.join(output_directory, f"vpc-{index}")
    os.makedirs(vpc_directory, exist_ok=True)
    output_file_path = os.path.join(vpc_directory, "vpc-module.tf")
    append_data_to_file(output_file_path, vpc_module_template)


def create_tf_file(vpc_name, filename, vpc_variables_template, args={}):
    """
    Create a Terraform variables file with the provided arguments.

    :param vpc_name: str
        The name of the VPC.

    :param filename: str
        The name of the Terraform variables file.

    :param vpc_variables_template: str
        The Terraform template for variables.

    :param args: dict
        The arguments to fill the placeholders in the template.

    :return: None
    """
    output_directory = os.path.join(
        os.path.dirname(__file__), '..', "terraform")
    vpc_directory = os.path.join(output_directory, vpc_name)
    formatted_template = vpc_variables_template % args
    output_file_path = os.path.join(vpc_directory, filename)
    append_data_to_file(
        output_file_path, formatted_template.replace("'", "\""))


def json_file_to_dict(file_location):
    """
    Read a JSON file and convert it to a dictionary.

    :param file_location: str
        The path to the JSON file.

    :return: dict
        The dictionary containing the JSON data, or None if there was an error.
    """
    try:
        with open(file_location, 'r') as file:
            # Use json.load to read the JSON file and convert it to a dictionary
            data_dict = json.load(file)
            return data_dict
    except FileNotFoundError:
        print(f"File not found: {file_location}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON decoding error: {e}")
        return None


def append_data_to_file(file_path, data):
    """
    Append data to a file.

    :param file_path: str
        The path to the file.

    :param data: str
        The data to be appended to the file.

    :return: None
    """
    try:
        with open(file_path, 'a') as file:
            # Append the data and add a newline character
            file.write(data + '\n')
        print(f"Data appended to {file_path} successfully.")
    except Exception as e:
        print(f"Error appending data to {file_path}: {e}")


def format_tags(tag_list):
    """
    Format a list of tags into a Terraform-compatible format.

    :param tag_list: list of dict
        A list of dictionaries containing Key-Value pairs for tags.

    :return: str
        The formatted tags as a string.
    """
    formatted_tags = []
    for tag in tag_list:
        key = tag.get("Key", "")
        value = tag.get("Value", "")
        formatted_tag = f'{key} = "{value}"'
        formatted_tags.append(formatted_tag)
    return "{" + ", ".join(formatted_tags) + "}"


def extract_vpc_info(vpc_info):
    public_cidr_blocks = [subnet_info['CidrBlock']
                          for subnet_info in vpc_info['Subnets'].values()]

    vpc_var_args = {
        "index": vpc_info['VpcIndex'],
        "CidrBlock": vpc_info['CidrBlock'],
        "PublicCidrBlock": public_cidr_blocks,
        "Tags": format_tags(vpc_info.get('Tags', []))
    }

    return vpc_var_args


def extract_ec2_instance_info(instance_info, subnet_info, instance_index, sg_ids):
    ec2_args = {
        "index": instance_index,
        "ImageId": instance_info['ImageId'],
        "InstanceType": instance_info['InstanceType'],
        "CidrBlock": f'"{subnet_info["CidrBlock"]}"',
        "SecurityGroupIds": sg_ids,  
        "Tags": format_tags(instance_info.get('Tags', []))
    }
    return ec2_args


def format_sg_rules(rules, template):
    """Format a list of security group rules for Terraform configuration."""
    formatted_rules = []
    for rule in rules:
        # Check and set default for FromPort and ToPort, replace empty strings with 0
        from_port = rule.get("FromPort")
        from_port = 0 if from_port == '' else from_port if from_port is not None else 0

        to_port = rule.get("ToPort")
        to_port = 0 if to_port == '' else to_port if to_port is not None else 0

        formatted_rule = template % {
            "Description": f'"{rule.get("Description", "")}"',
            "FromPort": from_port,
            "ToPort": to_port,
            "Protocol": f'"{rule.get("IpProtocol", "")}"',
            "CidrBlocks": json.dumps([ip_range.get("CidrIp", "") for ip_range in rule.get("IpRanges", [])]),
            "Ipv6CidrBlocks": json.dumps([ip_range.get("Ipv6CidrBlock", "") for ip_range in rule.get("Ipv6Ranges", [])])
        }
        formatted_rules.append(formatted_rule)
    return ''.join(formatted_rules)


def extract_security_group_info(sg_info, index):
    """Extract and format security group information for Terraform."""
    ingress_rules = format_sg_rules(sg_info.get(
        "IpPermissions", []), var.ingress_rule_template)
    egress_rules = format_sg_rules(sg_info.get(
        "IpPermissionsEgress", []), var.egress_rule_template)

    sg_args = {
        "index": index,
        "GroupName": f'"{sg_info.get("Id", "")}"',
        "Description": '"Security Group created from migration script"',
        "VpcId": f'"{sg_info.get("VpcId", "")}"',
        "IngressRules": ingress_rules,
        "EgressRules": egress_rules,
        "Tags": format_tags(sg_info.get("Tags", []))
    }
    return sg_args


def get_destination_region():
    region = os.getenv("DESTINATION_REGION")
    region_arg = {
        "Region": region
    }
    return region_arg

def get_backend_config():
    """
    Retrieves backend configuration details from environment variables.

    :return: list
        List containing the S3 bucket name, key, and DynamoDB table name.
    """
    bucket_name = os.getenv("BUCKET_NAME")
    key = os.getenv("KEY")
    dynamodb_table = os.getenv("DYNAMODB_TABLE")

    return [bucket_name, key, dynamodb_table]

def format_terraform_backend_args(vpc_name, bucket, key, region, dynamodb_table):
    """
    
    Format the arguments for the Terraform backend configuration.

    :param vpc_name: str
        The name of the VPC.

    :param bucket: str
        The name of the S3 bucket for the Terraform backend.

    :param key: str
        The key (path) in the S3 bucket where the Terraform state file will be stored.

    :param region: str
        The AWS region for the S3 bucket.

    :param dynamodb_table: str
        The name of the DynamoDB table for state locking.

    :return: dict
        Formatted arguments for the Terraform backend configuration.
    """
    return {
        "bucket": bucket,
        "vpcName": vpc_name,
        "key": key,
        "region": region,
        "dynamodb_table": dynamodb_table
    }
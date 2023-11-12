import os
import json
from ipaddress import ip_network
import terraform_templates.resource_templates as var

TERRAFORM_DIR = "terraform"


def create_vpc_module(vpc_module_template, index):
    """
    Create a Terraform module for VPC configuration.

    :param vpc_module_template: str
        The Terraform template for the VPC module.

    :param index: int
        The index of the VPC module.

    :return: None
    """
    vpc_directory = os.path.join(TERRAFORM_DIR, f"vpc-{index}")
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
    vpc_directory = os.path.join(TERRAFORM_DIR, vpc_name)
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


def find_vpc_subnets(subnets, vpc_cidr):
    vpc_subnets = []
    vpc_network = ip_network(vpc_cidr)
    for subnet_info in subnets.values():
        subnet_network = ip_network(subnet_info['CidrBlock'])
        if subnet_network.subnet_of(vpc_network):
            vpc_subnets.append(subnet_info['CidrBlock'])
    return vpc_subnets


def extract_vpc_info(data):
    vpc_var_args_list = []
    index = 1

    for vpc_info in data['vpcs'].values():
        vpc_var_args = {
            "index": index,
            "CidrBlock": vpc_info['CidrBlock'],
            "PublicCidrBlock": find_vpc_subnets(data['subnets'], vpc_info['CidrBlock']),
            "Tags": format_tags(vpc_info.get('Tags', []))
        }
        vpc_var_args_list.append(vpc_var_args)
        index += 1

    return vpc_var_args_list


def group_security_groups_by_vpc(security_groups):
    """Group security groups by VPC ID."""
    grouped = {}
    for sg_id, sg_info in security_groups.items():
        vpc_id = sg_info['VpcId']
        grouped.setdefault(vpc_id, []).append((sg_id, sg_info))
    return grouped


def extract_security_group_info(grouped_security_groups):
    sg_resources = {}

    for vpc_id, sg_list in grouped_security_groups.items():
        resources = []
        for sg_id, sg_info in sg_list:
            ingress = format_sg_rules(sg_info.get('IpPermissions', []))
            egress = format_sg_rules(sg_info.get('IpPermissionsEgress', []))
            tags = format_tags(sg_info.get('Tags', []))
            group_name = sg_info.get('GroupName', sg_id)  # Assuming GroupName is not available

            sg_resource = security_group_resource_template % {
                "GroupName": f'"{group_name}"',
                "Description": f'"{sg_info.get("Description", "Security Group")}"',
                "VpcId": f'"{vpc_id}"',
                "IngressRules": ingress,
                "EgressRules": egress,
                "Tags": tags
            }
            resources.append(sg_resource)

        sg_resources[vpc_id] = "\n".join(resources)

    return sg_resources
    

def get_destination_region():
    region = os.getenv("DESTINATION_REGION")
    region_arg = {
        "Region": region
    }
    return region_arg

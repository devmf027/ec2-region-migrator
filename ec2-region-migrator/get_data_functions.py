import os
import sys
import time
from datetime import datetime
import json
import boto3
from botocore.exceptions import ClientError



def get_ec2_instance_data(instance_id):
    """
    Retrieve information about an EC2 instance by its ID using Boto3.

    :param instance_id: The ID of the EC2 instance to retrieve information for.
    :returns: A dictionary containing information about the specified EC2 instance.
    """

    ec2 = boto3.client("ec2")
    response = ec2.describe_instances(InstanceIds=[instance_id])
    return response


def get_vpc_data(vpc_id):
    """
    Retrieve information about a VPC by its ID using Boto3.

    :param vpc_id: The ID of the VPC to retrieve information for.
    :returns: A dictionary containing information about the specified VPC.
    """
    ec2 = boto3.client("ec2")
    response = ec2.describe_vpcs(VpcIds=[vpc_id])
    return response


def get_security_group_data(group_id):
    """
    Retrieve information about a security group by its ID using Boto3.

    :param group_id: The ID of the security group to retrieve information for.
    :returns: A dictionary containing information about the specified security group.
    """
    ec2 = boto3.client("ec2")
    response = ec2.describe_security_groups(GroupIds=[group_id])
    return response


def get_subnet_data(subnet_id):
    """
    Retrieve information about a subnet by its ID using Boto3.

    :param subnet_id: The ID of the subnet to retrieve information for.
    :returns: A dictionary containing information about the specified subnet.
    """
    ec2 = boto3.client("ec2")
    response = ec2.describe_subnets(SubnetIds=[subnet_id])
    return response


def extract_instance_info(ec2_data):
    """
    Extract and structure EC2 information from the AWS API response.

    This function takes the output of the `get_ec2_instance_data` function and extracts specific information
    to create a dictionary with the EC2 instance ID as the key and relevant data as values.

    :param ec2_data: The AWS API response from describe EC2 instance.
    :returns: A dictionary with EC2 instance ID as the key and relevant data as values.
    """
    ec2_instance_info = {}

    if "Reservations" in ec2_data:
        for reservation in ec2_data["Reservations"]:
            for instance in reservation["Instances"]:
                instance_id = instance["InstanceId"]

                # Extract the security group IDs from the SecurityGroups list
                security_group_ids = [sg["GroupId"]
                                      for sg in instance.get("SecurityGroups", [])]

                ec2_instance_info[instance_id] = {
                    "InstanceType": instance["InstanceType"],
                    "VpcId": instance["VpcId"],
                    "SubnetId": instance.get("SubnetId", ""),
                    "PrivateIpAddress": instance.get("PrivateIpAddress", ""),
                    "SecurityGroups": security_group_ids,
                    "Tags": instance.get("Tags", []),

                }

    return ec2_instance_info


def extract_vpc_info(vpc_data):
    """
    Extract and structure VPC information from the AWS API response.

    :param vpc_data: The AWS API response for describe VPC information.
    :returns: A dictionary with VPC ID as the key and relevant data as values.
    """
    vpc_info = {}

    if "Vpcs" in vpc_data:
        for vpc in vpc_data["Vpcs"]:
            vpc_id = vpc["VpcId"]
            vpc_info[vpc_id] = {
                "CidrBlock": vpc.get("CidrBlock", ""),
                "Tags": vpc.get("Tags", [])
            }

    return vpc_info


def extract_subnet_info(subnet_data):
    """
    Extract and structure subnet information from the AWS API response.

    :param subnet_data: The AWS API response for subnet information.
    :returns: A dictionary with Subnet ID as the key and relevant data as values.
    """
    subnet_info = {}

    if "Subnets" in subnet_data:
        for subnet in subnet_data["Subnets"]:
            subnet_id = subnet["SubnetId"]
            subnet_info[subnet_id] = {
                "AvailabilityZone": subnet.get("AvailabilityZone", ""),
                "CidrBlock": subnet.get("CidrBlock", ""),
                "VpcId": subnet.get("VpcId", ""),
                "Tags": subnet.get("Tags", [])
            }

    return subnet_info


def extract_security_group_info(security_group_data):
    """
    Extract and structure security group information from the AWS API response.

    :param security_group_data: The AWS API response for security group information.
    :returns: A dictionary with Security Group ID as the key and relevant data as values.
    """
    security_group_info = {}

    if "SecurityGroups" in security_group_data:
        for sg in security_group_data["SecurityGroups"]:
            sg_id = sg["GroupId"]
            vpc_id = sg.get("VpcId")
            security_group_info[sg_id] = {
                "VpcId": vpc_id,
                "IpPermissions": [],
                "IpPermissionsEgress": [],
                "Tags": sg.get("Tags", [])
            }

            # Extract ingress rules
            for ingress_rule in sg.get("IpPermissions", []):
                ingress_info = {
                    "FromPort": ingress_rule.get("FromPort", ""),
                    "IpProtocol": ingress_rule.get("IpProtocol", ""),
                    "IpRanges": [{"CidrIp": ip_range.get("CidrIp", ""),
                                  "Description": ip_range.get("Description", "")}
                                 for ip_range in ingress_rule.get("IpRanges", [])],
                    "ToPort": ingress_rule.get("ToPort", "")
                }
                security_group_info[sg_id]["IpPermissions"].append(
                    ingress_info)

            # Extract egress rules
            for egress_rule in sg.get("IpPermissionsEgress", []):
                egress_info = {
                    "FromPort": egress_rule.get("FromPort", ""),
                    "IpProtocol": egress_rule.get("IpProtocol", ""),
                    "IpRanges": [{"CidrIp": ip_range.get("CidrIp", ""),
                                  "Description": ip_range.get("Description", "")}
                                 for ip_range in egress_rule.get("IpRanges", [])],
                    "ToPort": egress_rule.get("ToPort", "")
                }
                security_group_info[sg_id]["IpPermissionsEgress"].append(
                    egress_info)

    return security_group_info


def extract_ec2_resource_info(ec2_instance_ids):
    """
    Get information about EC2 instances, VPCs, subnets, and security groups for a list of EC2 instance IDs.

    :param ec2_instance_ids: A list of EC2 instance IDs.
    :returns: A dictionary containing information about EC2 instances, VPCs, subnets, and security groups.
    """
    ec2_instance_info = {}
    vpc_info = {}
    subnet_info = {}
    security_group_info = {}

    # Single set to store already queried IDs for VPCs, subnets, and security groups
    queried_ids = set()

    for instance_id in ec2_instance_ids:
        # Get data for each EC2 instance
        ec2_data = get_ec2_instance_data(instance_id)
        instance_info = extract_instance_info(ec2_data)
        ec2_instance_info.update(instance_info)
        save_to_audit_file(instance_id, "ec2-instance", ec2_data)

        # Get and process VPC ID
        vpc_id = instance_info[instance_id]["VpcId"]
        if vpc_id not in queried_ids:
            vpc_data = get_vpc_data(vpc_id)
            vpc_extracted_info = extract_vpc_info(vpc_data)
            vpc_info.update(vpc_extracted_info)
            queried_ids.add(vpc_id)
            save_to_audit_file(vpc_id, "vpc", vpc_data)

        # Get and process Subnet ID
        subnet_id = instance_info[instance_id]["SubnetId"]
        if subnet_id not in queried_ids:
            subnet_data = get_subnet_data(subnet_id)
            subnet_extracted_info = extract_subnet_info(subnet_data)
            subnet_info.update(subnet_extracted_info)
            queried_ids.add(subnet_id)
            save_to_audit_file(subnet_id, "subnet", subnet_data)

        # Get and process Security Group IDs
        sg_ids = instance_info[instance_id]["SecurityGroups"]
        for sg_id in sg_ids:
            if sg_id not in queried_ids:
                sg_data = get_security_group_data(sg_id)
                sg_extracted_info = extract_security_group_info(sg_data)
                security_group_info.update(sg_extracted_info)
                queried_ids.add(sg_id)
                save_to_audit_file(sg_id, "security-group", sg_data)

    resource_info = {
        "ec2_instances": ec2_instance_info,
        "vpcs": vpc_info,
        "subnets": subnet_info,
        "security_groups": security_group_info
    }

    return resource_info


def format_vpc_info(vpc_id, vpc_data):
    """
    Formats the VPC information.

    Args:
    vpc_id (str): The ID of the VPC.
    vpc_data (dict): The VPC data containing CidrBlock and Tags.

    Returns:
    dict: Formatted VPC information.
    """
    return {
        "VpcIndex": vpc_id,
        "CidrBlock": vpc_data["CidrBlock"],
        "Tags": vpc_data.get("Tags", []),
        "Subnets": {}
    }


def format_subnet_info(subnet_id, subnet_data):
    """
    Formats the subnet information.

    Args:
    subnet_id (str): The ID of the subnet.
    subnet_data (dict): The subnet data containing AvailabilityZone, CidrBlock, and Tags.

    Returns:
    dict: Formatted subnet information.
    """
    return {
        "AvailabilityZone": subnet_data["AvailabilityZone"],
        "CidrBlock": subnet_data["CidrBlock"],
        "Tags": subnet_data.get("Tags", []),
        "EC2Instances": {}
    }


def format_security_group_info(sg_id, security_groups):
    """
    Formats the security group information.

    Args:
    sg_id (str): The ID of the security group.
    security_groups (dict): The security groups data.

    Returns:
    dict: Formatted security group information, or None if the security group is not found.
    """
    sg_data = security_groups.get(sg_id)
    if sg_data:
        return {
            "Id": sg_id,
            "VpcId": sg_data.get("VpcId", ""),
            "IpPermissions": sg_data.get("IpPermissions", []),
            "IpPermissionsEgress": sg_data.get("IpPermissionsEgress", []),
            "Tags": sg_data.get("Tags", [])
        }
    return None


def format_ec2_instance_info(instance_id, instance_data, security_groups):
    """
    Formats the EC2 instance information.

    Args:
    instance_id (str): The ID of the EC2 instance.
    instance_data (dict): The data of the EC2 instance containing InstanceType, PrivateIpAddress, etc.
    security_groups (dict): The security groups data.

    Returns:
    dict: Formatted EC2 instance information.
    """
    security_groups_details = [format_security_group_info(
        sg_id, security_groups) for sg_id in instance_data.get("SecurityGroups", []) if sg_id in security_groups]
    return {
        "InstanceType": instance_data["InstanceType"],
        "PrivateIpAddress": instance_data["PrivateIpAddress"],
        "Tags": instance_data.get("Tags", []),
        "SecurityGroupsDetails": security_groups_details,
        "ImageId": instance_data["ImageId"]
    }


def format_ec2_resource_info(resource_info):
    """
    Formats the entire EC2 resource information including VPCs, subnets, EC2 instances, and security groups.

    Args:
    resource_info (dict): The raw resource data containing VPCs, subnets, EC2 instances, and security groups.

    Returns:
    dict: A dictionary containing formatted information of all resources.
    """
    formatted_info = {}
    vpc_number = 1
    # Iterate over VPCs
    for vpc_id, vpc_data in resource_info['vpcs'].items():
        vpc_info = format_vpc_info(vpc_number, vpc_data)

        # Find subnets associated with this VPC
        for subnet_id, subnet_data in resource_info['subnets'].items():
            if subnet_data['VpcId'] == vpc_id:
                subnet_info = format_subnet_info(subnet_id, subnet_data)

                # Find EC2 instances in this subnet
                for instance_id, instance_data in resource_info['ec2_instances'].items():
                    if instance_data['SubnetId'] == subnet_id:
                        instance_info = format_ec2_instance_info(
                            instance_id, instance_data, resource_info['security_groups'])
                        subnet_info["EC2Instances"][instance_id] = instance_info

                vpc_info["Subnets"][subnet_id] = subnet_info

        vpc_number += 1
        formatted_info[vpc_id] = vpc_info

    save_to_audit_file("", "formatted", formatted_info)

    return formatted_info


def save_to_audit_file(resource_id, resource_type, data):
    """
    Save data to a JSON file in the audit directory with a timestamp.

    This function takes resource ID, resource type, and data as input and saves the data to a JSON file in the audit directory.
    The file name is constructed using the resource ID, type, and a timestamp.

    :param resource_id: The ID of the AWS resource.
    :param resource_type: The type of the AWS resource (e.g., "ec2", "vpc", "security_group").
    :param data: The data to be saved to the JSON file.
    :returns: None
    """
    # Get the current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Construct the file path with resource ID, type, and timestamp
    file_path = os.path.join(os.path.dirname(
        __file__), "..", "audit", f"{resource_type}_{resource_id}_{timestamp}.json")

    # Create the directory if it doesn"t exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Save the data to the JSON file
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4, default=str)


def create_instance_image(instance_id, image_name):
    """
    Create an AMI from an existing EC2 instance.

    :param instance_id: The ID of the EC2 instance.
    :param image_name: The name for the new AMI.
    :return: The ID of the created AMI if successful, None otherwise.
    """
    ec2_client = boto3.client('ec2')
    response = ec2_client.create_image(InstanceId=instance_id, Name=image_name)
    response["InstanceId"] = instance_id
    save_to_audit_file(response["ImageId"], 'ami', response)
    return response


def copy_instance_image(image_id, image_name, source_region, destination_region):
    """
    Copy an AMI to a different region.
    :param image_id: str
        The ID of the AMI to copy.
    :param image_name: str
        The name for the copied AMI.
    :param source_region: str
        The region where the source AMI is located.
    :param destination_region: str
        The destination region to copy the AMI to.
    :return: str
        The ID of the copied AMI if successful, None otherwise.
    """
    ec2_client = boto3.client('ec2', region_name=destination_region)
    response = ec2_client.copy_image(
        Description='',
        Name=image_name,
        SourceImageId=image_id,
        SourceRegion=source_region
    )
    # Optionally save to audit file or perform other actions
    save_to_audit_file(response["ImageId"], 'copied_ami', response)
    return response


def add_image_id_to_instances(data, image_data_list):
    """
    Add ImageId to EC2 instances in the provided data dictionary by InstanceId.

    :param data:
        The data dictionary containing information about EC2 resources.

    :param image_data_list:
        A list of dictionaries containing ImageId and InstanceId.

    :return: None
    """
    ec2_instances = data.get("ec2_instances", {})
    for image_info in image_data_list:
        instance_id = image_info.get("InstanceId")
        if instance_id in ec2_instances:
            ec2_instances[instance_id]["ImageId"] = image_info.get("ImageId")


def get_ec2_instance_ids_from_args():
    """
    Get EC2 instance IDs from command-line arguments and return them as a list.

    Returns:
        list: A list of EC2 instance IDs.
    """
    # Check if at least one argument (EC2 instance ID) is provided
    if len(sys.argv) < 2:
        print(
            "Usage: python your_script.py <EC2_INSTANCE_ID1> [<EC2_INSTANCE_ID2> ...]")
        sys.exit(1)

    # Extract EC2 instance IDs from command-line arguments (skip the first argument)
    ec2_instance_ids = sys.argv[1:]
    return ec2_instance_ids


def wait_for_image_availability(image_id, region):
    """
    Check if the AMI with the given ImageId is available in the specified region
    and wait for it to become available if it's not already.

    :param image_id: str
        The ID of the AMI.
    :param region: str
        The AWS region to check in.
    """
    try:
        ec2_client = boto3.client('ec2', region_name=region)
        max_tries = 40
        sleep_time = 30
        print("Copying AMIs to the desired region")
        for attempt in range(max_tries):
            response = ec2_client.describe_images(ImageIds=[image_id])
            if response['Images']:
                image_state = response['Images'][0]['State']
                print(
                    f"Attempt {attempt + 1}: Image {image_id} is in '{image_state}' state.")

                if image_state == 'available':
                    print(f"Image {image_id} is now available.")
                    return
                else:
                    time.sleep(sleep_time)
            else:
                print(f"No image found with ID: {image_id}")
                return

        print(
            f"Image {image_id} did not become available after {max_tries} attempts.")

    except ClientError as e:
        print(f"An error occurred: {e}")

import os
from datetime import datetime
import json
import boto3


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


def get_ec2_resource_info(ec2_instance_ids):
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



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

    ec2 = boto3.client('ec2')
    response = ec2.describe_instances(InstanceIds=[instance_id])
    return response


def get_vpc_data(vpc_id):
    """
    Retrieve information about a VPC by its ID using Boto3.

    :param vpc_id: The ID of the VPC to retrieve information for.
    :returns: A dictionary containing information about the specified VPC.
    """
    ec2 = boto3.client('ec2')
    response = ec2.describe_vpcs(VpcIds=[vpc_id])
    return response


def get_security_group_data(group_id):
    """
    Retrieve information about a security group by its ID using Boto3.

    :param group_id: The ID of the security group to retrieve information for.
    :returns: A dictionary containing information about the specified security group.
    """
    ec2 = boto3.client('ec2')
    response = ec2.describe_security_groups(GroupIds=[group_id])
    return response


def get_subnet_data(subnet_id):
    """
    Retrieve information about a subnet by its ID using Boto3.

    :param subnet_id: The ID of the subnet to retrieve information for.
    :returns: A dictionary containing information about the specified subnet.
    """
    ec2 = boto3.client('ec2')
    response = ec2.describe_subnets(SubnetIds=[subnet_id])
    return response


def extract_ec2_info(ec2_data):
    """
    Extract and structure EC2 information from the AWS API response.

    This function takes the output of the `get_ec2_instance_data` function and extracts specific information
    to create a dictionary with the EC2 instance ID as the key and relevant data as values.

    :param ec2_data: The AWS API response for an EC2 instance.
    :returns: A dictionary with EC2 instance ID as the key and relevant data as values.
    """
    ec2_info = {}

    if 'Reservations' in ec2_data:
        for reservation in ec2_data['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']

                # Extract the security group IDs from the SecurityGroups list
                security_group_ids = [sg['GroupId']
                                      for sg in instance.get('SecurityGroups', [])]

                ec2_info[instance_id] = {
                    'ec2_name': instance.get('KeyName', ''),
                    'ec2_type': instance['InstanceType'],
                    'vpc_id': instance['VpcId'],
                    'subnet_cidr': instance.get('SubnetId', ''),
                    'security_group_id': security_group_ids,
                    'tags_of_ec2': instance.get('Tags', [])
                }

    return ec2_info


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
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    # Construct the file path with resource ID, type, and timestamp
    file_path = f"audit/{resource_type}_{resource_id}_{timestamp}.json"

    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Save the data to the JSON file
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4, default=str)
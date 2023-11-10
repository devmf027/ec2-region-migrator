import os
from datetime import datetime
import boto3
import json
from get_data_functions import (
    get_ec2_instance_data,
    extract_ec2_info,
    get_vpc_data,
    get_subnet_data,
    get_security_group_data,
    save_to_audit_file
)

# Example usage of functions
if __name__ == "__main__":
    # Get EC2 instance data
    ec2_instance_id = 'i-035e67de49dbf522a'
    ec2_data = get_ec2_instance_data(ec2_instance_id)

    # Extract information from the EC2 data
    ec2_info = extract_ec2_info(ec2_data)

    # Get VPC, security group, and subnet data from the ec2_info dictionary
    vpc_id = ec2_info[ec2_instance_id]['vpc_id']
    security_group_ids = ec2_info[ec2_instance_id]['security_group_id']
    subnet_id = ec2_info[ec2_instance_id]['subnet_cidr']

    # Retrieve VPC and subnet data
    vpc_data = get_vpc_data(vpc_id)
    subnet_data = get_subnet_data(subnet_id)

    # Retrieve security group data for all associated security groups
    security_group_data = {}
    for sg_id in security_group_ids:
        sg_data = get_security_group_data(sg_id)
        security_group_data[sg_id] = sg_data

    # Save VPC and subnet information to JSON files in the 'audit' directory
    save_to_audit_file(ec2_instance_id, 'ec2_instance', ec2_data)
    save_to_audit_file(vpc_id, 'vpc', vpc_data)
    save_to_audit_file(subnet_id, 'subnet', subnet_data)

    # Save security group information to JSON files in the 'audit' directory
    for sg_id, sg_data in security_group_data.items():
        save_to_audit_file(sg_id, 'security_group', sg_data)

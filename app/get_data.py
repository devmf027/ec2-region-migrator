import os
from datetime import datetime
import boto3
import json
import get_data_functions as data

def main():
    ec2_instance_ids = ["i-06b4ace9aaa0fa133", "i-06daf60c18b3f6177", "i-065dcd30980f2de55"]
    ami_list = []

    # Creates an Ami for each instance in the list
    for id in ec2_instance_ids:
        ami_list.append(data.create_instance_image(id, id))
        
    # Now, call the get_ec2_resource_info function to get additional resource info
    resource_info = data.get_ec2_resource_info(ec2_instance_ids)

    # Adds imageid to the corresponding ec2 instance
    data.add_image_id_to_instances(resource_info, ami_list)

    # Save all of the infrastructure info to file
    data.save_to_audit_file("", "resources", resource_info)

if __name__ == "__main__":
    main()

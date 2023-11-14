import os
from datetime import datetime
import boto3
import json
from time import sleep
import get_data_functions as data

DESTINATION_REGION = os.getenv("DESTINATION_REGION")
AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION")

def main():
    ec2_instance_ids = data.get_ec2_instance_ids_from_args()
    ami_list = []

    # Creates an Ami for each instance in the list
    for instance_id in ec2_instance_ids:
        response = ami_list.append(data.create_instance_image(instance_id, instance_id))
    
    # Wait for the availability of the new created AMIs
    sleep(120)

    # Copies each Ami to destination region
    for ami in ami_list:
        response = data.copy_instance_image(ami["ImageId"], ami["InstanceId"], AWS_DEFAULT_REGION, DESTINATION_REGION)
        ami["ImageId"] = response["ImageId"]
   
    # Now, call the extract_ec2_resource_info function to get additional resource info
    resource_info = data.extract_ec2_resource_info(ID_LIST)

    # Adds imageid to the corresponding ec2 instance
    data.add_image_id_to_instances(resource_info, ami_list)

    # Formats the resources information in a hierarchical format
    data.format_ec2_resource_info(resource_info)

    # Waits for the copied AMIs to be available
    for ami in ami_list:
        data.wait_for_image_availability(ami["ImageId"], DESTINATION_REGION)

    

if __name__ == "__main__":
    main()

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
        
    sleep(90)
    # Copies each Ami to destination region
    for ami in ami_list:
        response = data.copy_instance_image(ami["ImageId"], ami["InstanceId"], AWS_DEFAULT_REGION, DESTINATION_REGION)
        ami["ImageId"] = response["ImageId"]
   
    # Now, call the get_ec2_resource_info function to get additional resource info
    resource_info = data.get_ec2_resource_info(ec2_instance_ids)

    # Adds imageid to the corresponding ec2 instance
    data.add_image_id_to_instances(resource_info, ami_list)

    # Formats the resources information in a hierarchical format
    data.format_ec2_resource_info(resource_info)

    # Save all of the infrastructure info to file
    data.save_to_audit_file("", "resources", resource_info)

    # data.copy_instance_image("ami-01dc71c2e4542deed", "i-0b6ad7b625a49bf25", AWS_DEFAULT_REGION, DESTINATION_REGION)


    

if __name__ == "__main__":
    main()

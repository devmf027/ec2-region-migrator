import os
import create_tf_files_functions as tf
import terraform_templates.resource_templates as var

DESTINATION_REGION = tf.get_destination_region()
BUCKET_NAME, KEY, DYNAMODB_TABLE = tf.get_backend_config()

def main():
    # Define the directory containing the JSON files
    audit_directory = os.path.join(os.path.dirname(__file__), '..', 'audit')

    # Get a list of all files in the audit directory
    files_in_audit = os.listdir(audit_directory)
    
    # Filter the list to include only files that start with "resources"
    resources_files = [file for file in files_in_audit if file.startswith("formatted")]
    file_location = os.path.join(audit_directory, *resources_files)
        
    # Load the JSON file as a dictionary
    data_dict = tf.json_file_to_dict(file_location)
    
    
    # Iterate over each VPC in the data dictionary
    vpc_number = 1
    for vpc_id, vpc_data in data_dict.items():
        vpc_args = tf.extract_vpc_info(vpc_data)
        tf.create_vpc_module(var.vpc_module_template, vpc_args["index"])
        vpc_name = f"vpc-{vpc_args['index']}"

        # Check if any of the required arguments are absent or empty
        if not all([vpc_name, BUCKET_NAME, KEY, DESTINATION_REGION["Region"], DYNAMODB_TABLE]):
            print("One or more required arguments are missing or invalid. Skipping backend configuration.")
        else:
            try:
                # Format the arguments for the Terraform backend configuration
                backend_args = tf.format_terraform_backend_args(vpc_name, BUCKET_NAME, KEY, DESTINATION_REGION["Region"], DYNAMODB_TABLE)
                
                # Call the function to create the Terraform backend configuration file
                # Assuming create_tf_file is a function that takes these arguments
                tf.create_tf_file(vpc_name, "versions.tf", var.terraform_backend_template, backend_args)

            except KeyError as e:
                print(f"Missing argument in backend arguments: {e}")
            except Exception as e:
                print(f"An error occurred: {e}")
        # Call the function to create the VPC related files

        tf.create_tf_file(vpc_name, "vpc-variabels.tf", var.vpc_variables_template, vpc_args)
        tf.create_tf_file(vpc_name, "vpc.auto.tfvars", var.vpc_auto_tfvars_template, vpc_args)
        tf.create_tf_file(vpc_name, "generic-variables.tf", var.generic_variables_template, DESTINATION_REGION)
        tf.create_tf_file(vpc_name, "terraform.tfvars", var.terraform_tfvars_template, DESTINATION_REGION)
        tf.create_tf_file(vpc_name, "versions.tf", var.versions_template)

        ec2_instance_index = 1
        unique_security_groups = {}

        # First, collect unique security groups and associated instances
        for subnet_id, subnet_data in vpc_data['Subnets'].items():
            for instance_id, instance_data in subnet_data['EC2Instances'].items():
                for sg_detail in instance_data['SecurityGroupsDetails']:
                    sg_id = sg_detail['Id']
                    if sg_id not in unique_security_groups:
                        unique_security_groups[sg_id] = {"details": sg_detail, "instances": []}
                    unique_security_groups[sg_id]["instances"].append(ec2_instance_index)
                ec2_instance_index += 1

        # Then, generate security group configurations and assign indexes
        sg_index = 1
        for sg_id, sg_info in unique_security_groups.items():
            sg_args = tf.extract_security_group_info(sg_info["details"], sg_index)
            tf.create_tf_file(vpc_name, "security-groups.tf", var.security_group_resource_template, sg_args)
            # Assign the index to the security group
            unique_security_groups[sg_id]['index'] = sg_index
            sg_index += 1

        # Reset instance index for EC2 instance creation
        ec2_instance_index = 1

        # Finally, create EC2 instances configurations
        for subnet_id, subnet_data in vpc_data['Subnets'].items():
            for instance_id, instance_data in subnet_data['EC2Instances'].items():
                # Construct the security group IDs using the assigned indexes
                sg_ids = [f"aws_security_group.security_group_{unique_security_groups[sg['Id']]['index']}.id" for sg in instance_data['SecurityGroupsDetails']]
                ec2_args = tf.extract_ec2_instance_info(instance_data, subnet_data, ec2_instance_index, sg_ids)
                tf.create_tf_file(vpc_name, "ec2-instances.tf", var.ec2_instance_module_template, ec2_args)
                tf.create_tf_file(vpc_name, "eip-resources.tf", var.eip_resource_template, {"index": ec2_instance_index})
                ec2_instance_index += 1

                  

if __name__ == "__main__":
    main()
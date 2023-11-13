import os
import create_tf_files_functions as tf
import terraform_templates.resource_templates as var

DESTINATION_REGION = tf.get_destination_region()


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
    for vpc_id, vpc_data in data_dict.items():
        vpc_args = tf.extract_vpc_info(vpc_data)
        print(vpc_args)
        tf.create_vpc_module(var.vpc_module_template, vpc_args["index"])
        vpc_name = f"vpc-{vpc_args['index']}"

        # Call the function to create the VPC variables file
        tf.create_tf_file(vpc_name, "vpc-variabels.tf", var.vpc_variables_template, vpc_args)

        # Call the function to create the VPC auto.tfvars file
        tf.create_tf_file(vpc_name, "vpc.auto.tfvars", var.vpc_auto_tfvars_template, vpc_args)

        # Call the function to create generic variables file
        tf.create_tf_file(vpc_name, "generic-variables.tf", var.generic_variables_template, DESTINATION_REGION)

        # Call the function to create terraform.tfvars file
        tf.create_tf_file(vpc_name, "terraform.tfvars", var.terraform_tfvars_template, DESTINATION_REGION)

        # Call the function to create version.tf file
        tf.create_tf_file(vpc_name, "versions.tf", var.versions_template)

        ec2_instance_index = 1
        ec2_instances_tf_content = ""

        for subnet_id, subnet_data in vpc_data['Subnets'].items():
            for instance_id, instance_data in subnet_data['EC2Instances'].items():
                ec2_args = tf.extract_ec2_instance_info(instance_data, subnet_data, ec2_instance_index)
                
                # Call the function to create ec2-instances.tf file
                tf.create_tf_file(vpc_name, "ec2-instances.tf", var.ec2_instance_module_template, ec2_args)
                # Call the function to create eip-resources.tf file
                tf.create_tf_file(vpc_name, "eip-resources.tf", var.eip_resource_template, {"index": ec2_instance_index})
                ec2_instance_index += 1

        
        
     

if __name__ == "__main__":
    main()
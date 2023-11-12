import os
import create_tf_files_functions as tf
import terraform_templates.resource_templates as var

DESTINATION_REGION = tf.get_destination_region()

# Define the directory containing the JSON files
audit_directory = "audit"

def main():
    # Get a list of all files in the audit directory
    files_in_audit = os.listdir(audit_directory)
    
    # Filter the list to include only files that start with "resources"
    resources_files = [file for file in files_in_audit if file.startswith("resources")]
    file_location = os.path.join(audit_directory, *resources_files)
        
    # Load the JSON file as a dictionary
    data_dict = tf.json_file_to_dict(file_location)
    
    vpc_args_list = tf.extract_vpc_info(data_dict)
    
    # Create vpc directories and files for each vpc
    for vpc_args in vpc_args_list:
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

    print(tf.group_security_groups_by_vpc(data_dict['security_groups']))

if __name__ == "__main__":
    main()
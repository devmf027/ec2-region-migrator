# ec2-region-migrator

Project for automating the migration of EC2 instances between regions in AWS.

## Project Description

The "ec2-region-migrator" is a Python application that facilitates the migration of EC2 instances from one AWS region to another. It retrieves essential information about your EC2 instances, VPC, security groups, and other related data using the Boto3 library, and then generates Terraform configuration files to recreate the infrastructure in a different region. This project aims to simplify the process of migrating your EC2 resources between AWS regions while ensuring data integrity and configuration continuity.

### Features and Functionality

- Fetches critical EC2 instance information, VPC and subnet details, security group configurations, and tags.
- Converts retrieved data into variables for Terraform configuration.
- Generates Terraform files to recreate the infrastructure in a target AWS region.
- Maintains audit records in JSON format for EC2 instances, security groups, and VPCs.

## Table of Contents (Optional)

- [How to Install and Run the Project](#how-to-install-and-run-the-project)
- [How to Use the Project](#how-to-use-the-project)

## How to Install and Run the Project

### Prerequisites

- A Debian-based Linux system.
- Sudo privileges on your system.
- Access to AWS services with necessary permissions.

### Installation Steps

1. **Clone the Repository**: Clone this repository to your local machine using Git (or download the ZIP file and extract it).

   ```bash
   git clone https://github.com/devmf027/ec2-region-migrator
   cd ec2-region-migrator

## How to Use the Project

This project is designed to automate the migration of AWS EC2 instances from one region to another. It uses Python scripts to gather data from AWS and generate Terraform files for the migration process. Follow these steps to use the project:

1. **Initial Setup with `init.sh`**:
   - Run the `init.sh` script to set up your environment. This script will:
     - Check if Python 3 and pip3 are installed and install them if they're not.
     - Install the necessary Python dependencies listed in `requirements.txt`.
   - To run the script, open a terminal in the project directory and execute:

     ```bash
     ./init.sh
     ```

   - This script may ask for your sudo password to install the required packages.

2. **Configure AWS Credentials**:
   - During the execution of `init.sh`, you will be prompted to enter your AWS Access Key ID, Secret Access Key, default region, and destination region. These credentials are necessary for the script to access and interact with your AWS account.

3. **Provide EC2 Instance IDs**:
   - You will need to input the EC2 instance IDs that you wish to migrate. Make sure these IDs are from the instances in your source AWS region.

4. **Running Migration Scripts**:
   - After setting up the environment and AWS credentials, the `init.sh` script will automatically execute the `execute_migration.sh` script located in the `scripts` directory.
   - The `execute_migration.sh` script handles the core migration process, which includes:
     - Running Python scripts to gather information about the specified EC2 instances.
     - Generating Terraform files necessary for migrating the instances to the target AWS region.

5. **Manual Execution of Migration**:
   - If you need to run the migration process separately (after the initial setup), navigate to the `scripts` directory and run the `execute_migration.sh` script:

     ```bash
     cd scripts
     ./execute_migration.sh
     ```

6. **Customization and Configuration**:
   - Modify the Terraform files under `demo-infrastructure` if you need to customize the migration process.
   - You can also manually set or export AWS credentials in your shell if required.

## Using the Demo-Infrastructure Directory

The `demo-infrastructure` directory in this project contains Terraform manifests that are intended for setting up demo aws basic ec2 resources for trial purposes. Here's how you can use this directory:

1. **Directory Structure**:
   - The `demo-infrastructure` directory is organized into subdirectories for each virtual private cloud (VPC) that you are working with (e.g., `vpc1`, `vpc2`).
   - Each VPC subdirectory contains its own set of Terraform manifests (`*.tf` files) which define the infrastructure resources to be created in that VPC.

2. **Terraform Manifests**:
   - Inside each VPC subdirectory, you'll find Terraform files like `ec2instances.tf`, `securitygroups.tf`, and `vpc-module.tf`. These files contain the Terraform code to define your AWS infrastructure components.
   - `terraform.tfvars` and `vpc.auto.tfvars` are used for setting variables specific to your environment and requirements.

3. **Initializing Terraform**:
   - Before you can apply the Terraform configurations, navigate to the relevant VPC subdirectory and initialize Terraform using the following command:

     ```bash
     terraform init
     ```

   - This command will initialize your Terraform workspace, which includes downloading any necessary Terraform providers and modules.

4. **Applying Terraform Configuration**:
   - To create the infrastructure in a AWS region (specified in terraform.tfvars), run:

     ```bash
     terraform apply
     ```

   - This command will show a plan of what Terraform intends to do and ask for your confirmation before proceeding.
   - Review the plan carefully to ensure it aligns with your intended changes.

### Important Notes

- Familiarize yourself with Terraform's workflow and syntax if you are new to Terraform. Mistakes in Terraform files can lead to unintended changes in your AWS infrastructure.
- Always back up your current Terraform state and configuration files before making any significant changes.
- The `demo-infrastructure` directory is a crucial part of the migration process; handle it with the understanding that it directly affects your cloud infrastructure.

### Note

- If the aws credentials are already set, uncomment '# profile = "default"' in versions.tf otherwise set them as environment variables
- Ensure that the AWS credentials provided have the necessary permissions to perform actions on EC2 instances, VPCs, and other related services.
- The project is structured to be user-friendly, but a basic understanding of AWS services and Terraform is beneficial for custom configurations and troubleshooting.

## Credits

- [Dariel Mizrachi](https://github.com/devmf027) - Project Lead and Developer

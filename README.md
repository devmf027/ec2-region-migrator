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
- [Contributing](#contributing)
- [License](#license)

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

### Note

- Ensure that the AWS credentials provided have the necessary permissions to perform actions on EC2 instances, VPCs, and other related services.
- The project is structured to be user-friendly, but a basic understanding of AWS services and Terraform is beneficial for custom configurations and troubleshooting.

## Contributing

We welcome contributions from the community. If you have any ideas, bug fixes, or new features to propose, please follow these steps:

1. Open an issue to discuss your proposed changes.
2. Fork the repository and create a new branch for your feature or bug fix.
3. Make your changes, ensuring they adhere to the project's coding standards.
4. Test your changes thoroughly.
5. Create a pull request with a clear description of your changes.

Please make sure to update or add tests as necessary and ensure your code is well-documented.

## Credits

- [Dariel Mizrachi](https://github.com/devmf027) - Project Lead and Developer

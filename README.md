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

[Provide instructions here on how to install and run your project. Include any dependencies and steps necessary to set up the development environment.]

## How to Use the Project

[Provide detailed instructions on how to use your project. Include examples, configuration settings, and any authentication requirements if applicable.]

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

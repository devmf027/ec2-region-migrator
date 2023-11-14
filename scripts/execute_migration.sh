#!/bin/bash

# Prompt the user for AWS key ID
read -p "Enter AWS Access Key ID: " AWS_KEY_ID

# Prompt the user for AWS secret key (hidden input for security)
read -s -p "Enter AWS Secret Access Key: " AWS_SECRET_KEY
echo  # This echo statement adds a new line after hidden input

# Prompt the user for AWS default region
read -p "Enter AWS Default Region: " AWS_DEFAULT_REGION

# Prompt the user for destination region
read -p "Enter Destination Region: " DESTINATION_REGION

# Prompt the user for Terraform backend S3 bucket name
read -p "Enter Terraform Backend S3 Bucket Name: " BUCKET_NAME

# Prompt the user for Terraform backend key
read -p "Enter Terraform Backend Key: " KEY

# Prompt the user for DynamoDB table name for Terraform state locking
read -p "Enter DynamoDB Table Name for Terraform State Locking: " DYNAMODB_TABLE

# Set the environment variables for AWS configuration
export AWS_ACCESS_KEY_ID="$AWS_KEY_ID"
export AWS_SECRET_ACCESS_KEY="$AWS_SECRET_KEY"
export AWS_DEFAULT_REGION="$AWS_DEFAULT_REGION"
export DESTINATION_REGION="$DESTINATION_REGION"

# Set the environment variables for Terraform backend configuration
export BUCKET_NAME="$BUCKET_NAME"
export KEY="$KEY"
export DYNAMODB_TABLE="$DYNAMODB_TABLE"

echo "AWS and Terraform backend environment variables set successfully."

# Prompt the user for the list of EC2 instance IDs
read -p "Enter a list of EC2 instance IDs separated by whitespace: " INSTANCE_IDS
echo

# Display a summary of the environment variables set
echo "Environment variables set:"
echo "AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID"
echo "AWS_SECRET_ACCESS_KEY=**********"  # Masking secret key for security
echo "AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION"
echo "DESTINATION_REGION=$DESTINATION_REGION"
echo "BUCKET_NAME=$BUCKET_NAME"
echo "KEY=$KEY"
echo "DYNAMODB_TABLE=$DYNAMODB_TABLE"
echo "EC2 Instance IDs: $INSTANCE_IDS"
echo

# Notify user about the Python script execution for getting data
echo "Running Python script to process EC2 instance IDs..."
# Pass the list of instance IDs to a Python script for processing
python3 -E ../ec2-region-migrator/get_data.py $INSTANCE_IDS

# Notify user about the second Python script execution for creating Terraform files
echo "Running Python script to create Terraform files..."
# Pass the list of instance IDs to another Python script for creating Terraform files
python3 -E ../ec2-region-migrator/create_tf_files.py $INSTANCE_IDS

# Navigate to the terraform directory
cd ../terraform

# Iterate over each VPC directory and execute Terraform commands
for vpc_dir in vpc-*; do
    if [ -d "$vpc_dir" ]; then
        echo "Processing $vpc_dir..."

        # Navigate into the VPC directory
        cd "$vpc_dir"

        # Run Terraform commands
        echo "Running 'terraform init' in $vpc_dir..."
        terraform init

        echo "Running 'terraform fmt' in $vpc_dir..."
        terraform fmt

        echo "Running 'terraform validate' in $vpc_dir..."
        terraform validate

        echo "Running 'terraform apply --auto-approve' in $vpc_dir..."
        terraform apply --auto-approve

        # Navigate back to the terraform directory
        cd ..

        echo "$vpc_dir processed."
    fi
done

# Navigate back to the scripts directory
cd ../scripts

echo "Terraform process completed for all VPCs."

echo "Script execution completed."

#!/bin/bash

# Function to check if a command exists
command_exists() {
    type "$1" &> /dev/null 
}

# Update package list and install Python 3 and pip if they are not installed
if ! command_exists python3; then
    echo "Python 3 is not installed. Installing Python 3..."
    sudo apt-get update
    sudo apt-get install -y python3
fi

if ! command_exists pip3; then
    echo "pip3 is not installed. Installing pip3..."
    sudo apt-get install -y python3-pip
fi

# Install Python dependencies from requirements.txt
if [ -f "requirements.txt" ]; then
    echo "Installing Python dependencies from requirements.txt..."
    pip3 install -r requirements.txt
else
    echo "requirements.txt not found. Skipping Python dependencies installation."
fi

# Check if the execute_migration.sh script exists
if [ -f "scripts/execute_migration.sh" ]; then
    echo "Running execute_migration.sh..."
    # Navigate to the directory containing the execute_migration.sh script
    cd scripts
    # Run the execute_migration.sh script
    ./execute_migration.sh
    # Navigate back to the root directory
    cd ..
else
    echo "Error: execute_migration.sh script not found in the 'scripts' directory."
    exit 1
fi



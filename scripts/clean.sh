#!/bin/bash

# Change pwd to the directory where the script resides
cd $(cd $(dirname "$0") && pwd)  

# Define the directories
AUDIT_DIR="../audit"
TERRAFORM_DIR="../terraform"

# Function to delete all files except dummy.md in a given directory
clean_directory() {
    local dir=$1
    echo "Cleaning $dir..."

    # Find all files and directories except dummy.md and delete them
    find "$dir" -mindepth 1 ! -name "dummy.md" -exec rm -rf {} +
}

# Clean the specified directories
clean_directory "$AUDIT_DIR"
clean_directory "$TERRAFORM_DIR"

echo "Cleanup completed."

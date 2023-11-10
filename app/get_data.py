import os
from datetime import datetime
import boto3
import json
from get_data_functions import (
    get_ec2_instance_data,
    extract_ec2_info,
    get_vpc_data,
    get_subnet_data,
    get_security_group_data,
    save_to_audit_file
)



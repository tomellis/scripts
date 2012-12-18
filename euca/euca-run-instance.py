#!/usr/bin/python

# Simple script to start an instances via ec2-api
# Author: olivier.renault@eucalyptus.com

import boto
from boto.ec2.regioninfo import RegionInfo

# Credentials
access_key="access-key"
secret_key="secret-key"
ec2_host="x.x.x.x"

# Setup connection to Eucalyptus
conn = boto.connect_ec2(aws_access_key_id=access_key,
                        aws_secret_access_key=secret_key,
                        is_secure=False,
                        region=RegionInfo(name="eucalyptus", endpoint=ec2_host),
                        port=8773,
                        path="/services/Eucalyptus")

# Run commands
conn.run_instances('emi-XXXXXXXX', key_name='test',
        instance_type='m1.large',
        security_groups=['default'])

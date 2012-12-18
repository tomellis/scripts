#!/usr/bin/python

# Simple script to start an instances via ec2-api
# Author: olivier.renault@eucalyptus.com

import boto
from boto.ec2.regioninfo import RegionInfo

# Credentials
access_key="access-key"
secret_key="secret-key"
ec2_host="x.x.x.x"
api_version="2009-11-30"


# Setup connection to Eucalyptus
conn = boto.connect_ec2(aws_access_key_id=access_key,
                        aws_secret_access_key=secret_key,
                        is_secure=False,
                        region=RegionInfo(name="eucalyptus", endpoint=ec2_host),
                        port=8773,
                        path="/services/Eucalyptus")
conn.APIVersion = api_version
# Run commands
emi=conn.get_all_images()
print emi

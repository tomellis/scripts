#!/usr/bin/python

# Simple example to list all S3 buckets
#
# Software License Agreement (BSD License)
#
# Copyright (c) 2012, Eucalyptus Systems, Inc.
# All rights reserved.
#
# Redistribution and use of this software in source and binary forms, with or
# without modification, are permitted provided that the following conditions
# are met:
#
#   Redistributions of source code must retain the above
#   copyright notice, this list of conditions and the
#   following disclaimer.
#
#   Redistributions in binary form must reproduce the above
#   copyright notice, this list of conditions and the
#   following disclaimer in the documentation and/or other
#   materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# Author: Tom Ellis <tom.ellis@eucalyptus.com>

import boto
from boto.s3.connection import OrdinaryCallingFormat

# Credentials
access_key="access-key"
secret_key="secret-key"
s3_host="x.x.x.x"

# Setup connection to Walrus
conn = boto.connect_s3(aws_access_key_id=access_key,
                       aws_secret_access_key=secret_key,
                       is_secure=False,
                       host=s3_host,
                       port=8773,
                       path="/services/Walrus",
                       calling_format=OrdinaryCallingFormat()) 

# Run commands
buckets = conn.get_all_buckets()
for b in buckets:
    print b.name

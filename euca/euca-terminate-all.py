#!/usr/bin/python

# Terminate all instances via ec2-api
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
instances = conn.get_all_instances()
print instances
for reserv in instances:
    for inst in reserv.instances:
        if inst.state == u'running':
            print "Terminating instance %s" % inst
            inst.terminate()
        if inst.state == u'terminated':
            print "Cleaning up previously terminated instance %s" % inst
            inst.terminate()

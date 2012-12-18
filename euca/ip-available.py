#!/usr/bin/python

# Simple script to report instance number / instance type running on cloud
# Author: olivier.renault@eucalyptus.com

import boto
from boto.ec2.regioninfo import RegionInfo
import collectd
from collections import defaultdict

def count_sorted_list_items(items):
    """
    :param items: sorted iterable of items to count
    :type items: sorted iterable

    :returns: generator of (item,count) tuples
    :rtype: generator
    """
    if not items:
        return
    elif len(items) == 1:
        yield (items[0], 1)
        return
    prev_item = items[0]
    count = 1
    for item in items[1:]:
        if prev_item == item:
            count += 1
        else:
            yield (prev_item, count)
            count = 1
            prev_item = item
    yield (item, count)
    return

def count_unsorted_list_items(items):
    """
    :param items: iterable of hashable items to count
    :type items: iterable

    :returns: dict of counts like Py2.7 Counter
    :rtype: dict
    """
    counts = defaultdict(int)
    for item in items:
        counts[item] += 1
    return dict(counts)

def display_zones(zones):
    status=[]
    for zone in zones:
        zone_string = '%s\t%s' % (zone.name, zone.state)
	words = zone_string.split()
        if len(words) == 3:
           cluster=words[0]
        if len(words) == 8:
#           status =  words[1], int(words[2]), int(words[4])
	   status.append([words[1], int(words[2]), int(words[4]), cluster])
#    print status
    return status
#           for word in words:
               # prints each word on a line
#               print (word[2] )
#        print zone_string

# Credentials
access_key="access-key"
secret_key="secret-key"
clc_host="x.x.x.x"
api_version="2009-11-30"

# Initialize connection to Eucalyptus
#def euca_connect(clc_host, access_key, secret_key, api_version):
conn = boto.connect_ec2(aws_access_key_id=access_key,
                        aws_secret_access_key=secret_key,
                        is_secure=False,
                        region=RegionInfo(name="eucalyptus", endpoint=clc_host),
                        port=8773,
                        path="/services/Eucalyptus")

conn.APIVersion = api_version
#return (conn)

MAX_IP=0
FREE_IP=0
for ips in conn.get_all_addresses():
   print ips
   if ips.instance_id == 'nobody':
       FREE_IP = FREE_IP + 1 

   MAX_IP = MAX_IP + 1
print FREE_IP
print MAX_IP
"""
zones = conn.get_all_zones('verbose')
status = display_zones(zones)
print status[0]
print status[0][1]
print len(status)

# Grab instance information
#def gather_instance_info(connection):
type=[]
image=[]

#for reservation in connection.get_all_instances():
for reservation in conn.get_all_instances():
   print (len(reservation.instances) - 1)
   for i in range(len(reservation.instances)):
       if reservation.instances[i].state == 'running':
           type.append(reservation.instances[i].instance_type)
           image.append(reservation.instances[i].image_id)

#print "m1.small  :", info.count('m1.small')
#print "c1.medium :", info.count('c1.medium')
#print "m1.large  :", info.count('m1.large')
#print "m1.xlarge :", info.count('m1.xlarge')
#print "c1.xlarge :", info.count('c1.xlarge')
print image
image=count_unsorted_list_items(image)
print image
print type
type=count_unsorted_list_items(type)
print type

if not 'm1.xlarge' in type:
    type['m1.xlarge'] = 0
for i in type.keys():
    print i 
    print type[i]
print type

#def read(data):
#  euca_connect

"""

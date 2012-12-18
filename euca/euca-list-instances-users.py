#!/usr/bin/python

# List which instances are owned by which users
# Author: olivier.renault@eucalyptus.com

import boto
from boto.ec2.regioninfo import RegionInfo

# Credentials
access_key="access-key"
secret_key="secret-key"
ec2_host="x.x.x.x"
api_version="2009-11-30"

import euca2ools.commands.euca.describeinstances
import euca2ools.commands.euare.listaccounts
import euca2ools.utils
import prettytable

if __name__ == '__main__':
    la = euca2ools.commands.euare.listaccounts.ListAccounts()
    accts = {}
    response = la.main()
    for acct in response.Accounts:
        accts[acct['AccountId']] = acct['AccountName']

    di = euca2ools.commands.euca.describeinstances.DescribeInstances()
    di.instance=['verbose']
    res = di.main()
    fields = ('id','reservation','owner','status',
             'network', 'key', 'type')
    pt = prettytable.PrettyTable(fields)
    for r in res:
        for i in r.instances:
            net = '%s %s' % (i.private_ip_address, i.ip_address)
            pt.add_row([i.id, r.id,
                       accts[r.owner_id], i.state,
                       net, i.key_name, i.instance_type])

    pt.printt()



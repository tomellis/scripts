#!/usr/bin/python

#
# euca_generate_report.py
# Command-line utility to generate Eucalyptus usage reports
# and upload them to a Walrus/S3 Bucket to give similar behaviour
# to Amazon's "Programmatic Billing Access" feature.
#
# Author: Tim Gerla <tim.gerla@eucalyptus.com>
#         Tom Ellis <tom.ellis@eucalyptus.com>
#

import sys
import time 
import subprocess
from optparse import OptionParser
import boto
from boto.s3.connection import OrdinaryCallingFormat
from boto.s3.key import Key
import os
from os.path import basename

# Enable debug logging
import logging
#logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)

# S3 Connection parameters
s3_host="x.x.x.x"
access_key="access-key"
secret_key="secret-key"

# Parse options
parser = OptionParser()

parser.add_option("-t", "--type", dest = "report_type", 
	help = "type of report: instance, storage, or s3")
parser.add_option("-p", "--password", dest = "admin_pwd",
	help = "cloud eucalyptus/admin password")
parser.add_option("-b", "--begin", dest = "begin_date",
	help = "begin date (mm/dd/yyyy)")
parser.add_option("-e", "--end", dest = "end_date",
	help = "end date (mm/dd/yyyy)")
parser.add_option("-g", "--groupBy", dest = "group_by", default = "none",
	help = "group by: zone, cluster, account, user, or none (default: none)")
parser.add_option("-c", "--criterion", dest = "criterion", default = "account",
	help = "report criterion: zone, cluster, account, user (default: account)")
parser.add_option("-f", "--format", dest = "format", default = "csv",
	help = "report format: html, csv, or pdf (default: csv)")
parser.add_option("-o", "--output", dest = "output_file",
	help = "output filename and key name inside walrus bucket")
parser.add_option("--bucket", dest = "bucket_name", default = "billing-reports",
        help = "bucket name to upload report to (default: billing-reports)")

(options, args) = parser.parse_args()

if options.report_type not in ('instance', 'storage', 's3'):
	print "%s is not a valid report type. Valid report types: instance, storage, s3" % options.report_type 
	parser.print_help()
	sys.exit(1)

if options.format not in ('html', 'csv', 'pdf'):
	print "%s is not a valid output format. Valid output formats: html, csv, pdf (default: csv)" % options.format
	parser.print_help()
	sys.exit(1)

if options.criterion not in ('zone', 'cluster', 'account', 'user'):
	print "%s is not a valid report critieron. Valid report criteria: zone, cluster, account, user (default: account)" % options.criterion
	parser.print_help()
	sys.exit(1)

if options.group_by not in ('zone', 'cluster', 'account', 'user', 'none'):
	print "%s is not a valid report grouping. Valid report grouping: zone, cluster, account, user, none (default: none)" % options.group_by
	parser.print_help()
	sys.exit(1)

if not options.output_file:
	print "You must specify an output file."
	parser.print_help()
	sys.exit(1)

if options.begin_date is None or options.end_date is None:
	print "You must provide a begin and end date."
	parser.print_help()
	sys.exit(1)

beginDate = "%d" % (time.mktime(time.strptime(options.begin_date, "%m/%d/%Y")) * 1000)
endDate = "%d" % (time.mktime(time.strptime(options.end_date, "%m/%d/%Y")) * 1000)

url = "https://localhost:8443/loginservlet?adminPw=%s" % options.admin_pwd
p = subprocess.Popen(['curl', '-sk', url], stdout = subprocess.PIPE)
session_id, err = p.communicate()
if "Incorrect admin password" in session_id:
	print "Server reported incorrect admin password, please verify"
	sys.exit(1)

logging.info("Using session ID: %s", (session_id))

url = "https://localhost:8443/reportservlet?session=" + session_id + \
	"&type=" + options.report_type + \
	"&page=0&format=" + options.format + \
	"&flush=false" + \
	"&start=" + beginDate + \
	"&end=" + endDate + \
	"&criterion=" + options.criterion + \
	"&groupByCriterion=" + options.group_by

logging.info("Using request URL: %s" % (url))

subprocess.call(['curl', '-sko', options.output_file, url])
logging.info("Report generated and saved to %s" % (options.output_file))

# Start s3 connection to Walrus
s3_conn = boto.connect_s3(aws_access_key_id=access_key,
                       aws_secret_access_key=secret_key,
                       is_secure=False,
                       host=s3_host,
                       port=8773,
                       path="/services/Walrus",
                       calling_format=OrdinaryCallingFormat())
# Try to connect or create bucket
try:
  logging.info("Trying to connect to existing bucket...")
  bucket = s3_conn.get_bucket(options.bucket_name)
except Exception, e:
  logging.info("Couldn't find existing bucket. Trying to create a new one...")
  bucket = s3_conn.create_bucket(options.bucket_name)

# Strip extension from filename and use as keyname
k = Key(bucket)
file_basename = basename(options.output_file)
k.key = file_basename
# Upload
logging.info("Uploading report")
k.set_contents_from_filename(options.output_file)

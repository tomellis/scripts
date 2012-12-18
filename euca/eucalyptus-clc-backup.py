#!/usr/bin/python

# Backup and restore a Eucalyptus Cloud Controller DB & Keys
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

import sys
import time
import os
from optparse import OptionParser
import logging

prog_name = sys.argv[0]
date_fmt = time.strftime('%Y-%m-%d-%H%M')
date = time.strftime('%Y-%m-%d')
backup_dir = "/tmp/backup"
backup_subdir = backup_dir + "/" + date
backup_file = backup_subdir + "/eucalyptus-pg_dumpall-" + date_fmt + ".sql"

# Database settings
db_port = "8777"
db_user = "root"
db_dir = "/var/lib/eucalyptus/db/data"
db_socket = db_dir + "/.s.PGSQL." + db_port
pg_dumpall_path = "/usr/bin/pg_dumpall"

# Enable debug logging
logger = logging.getLogger('euca-clc-backup')
logging.basicConfig(format='%(asctime)s:%(filename)s:%(levelname)s: %(message)s', level=logging.DEBUG)

def get_args():
    # Parse options
    parser = OptionParser()
    parser.add_option("-b", "--backup", dest="backup",
            default=None, help="Backup CLC DB & Keys to given filename")
    parser.add_option("-r", "--restore", dest="restore",
            default=None, help="Restore CLC DB & Keys from given filename")
    (options, args) = parser.parse_args()
    if not options.backup and not options.restore:
        logger.critical("Please specify a file to backup or restore from")
        sys.exit(1)
    return options

if __name__ == "__main__":

    # is the db running? socket should exist
    if not os.path.exists(db_socket):
        logging.critical("PostgreSQL database not running. Please start eucalyptus-cloud.")
        sys.exit(1)

    # does pg_dumpall exist?
    if not os.path.isfile(pg_dumpall_path):
        logging.critical("pg_dumpall does not exist at: %s", (pg_dumpall_path))
        sys.exit(1)

    # does the backup dir exist? create it
    if not os.path.exists(backup_dir):
        logging.warn("Backup directory %s does not exist, creating...", (pg_dumpall_path))
        os.mkdir(backup_dir)

##########
# Backup #
##########

# Trying...
# 1. pg_dumpall
# 2. pg_dump each eucalyptus db
# 3. db dir backup
# 4. Eucalyptus keys dir

    # Create a subdir for today
    if not os.path.exists(backup_subdir):
        os.mkdir(backup_subdir)

    # Run a pg_dumpall dump
    logging.info("Running pg_dumpall backup")
    dump_all="nice -n 19 pg_dumpall -h%s -p%s -U%s -f%s" % (db_dir, db_port, db_user, backup_file)
    os.popen(dump_all)
    logging.info("pg_dumpall complete: %s", (backup_file))

    # List of individual databases in postgres 
    database_list = "psql -U%s -d%s -p%s -h%s --tuples-only -c 'select datname from pg_database' | grep -E -v '(template0|template1|^$)'" % (db_user, "postgres", db_port, db_dir)

    # Dump only global objects (roles and tablespaces) which include system grants
    system_grants = "pg_dumpall -h%s -p%s -U%s -g > %s/system.%s.gz" % (db_dir, db_port, db_user, backup_subdir, date_fmt)

    logging.info("Backing up global objects")
    os.popen(system_grants)

    logging.info("Running pg_dump on each database")
    for base in os.popen(database_list).readlines():
        base = base.strip()
        filename = "%s/%s-%s.sql" % (backup_subdir, base, date)
        dump_cmd = "nice -n 19 pg_dump -C -F c -U%s -p%s -h%s %s > %s" % (db_user, db_port, db_dir, base, filename) 
        logging.debug("Running pg_dump on %s", (base))
        os.popen(dump_cmd)

    logging.info("Backup complete")


#### 
# Restore
####
# run euca_conf --initialize
#start_db="/usr/pgsql-9.1/bin/pg_ctl start -w -s -D/var/lib/eucalyptus/db/data -o '-h0.0.0.0/0 -p8777 -i'"
# restore pgdumps
# restore keys
#stop_db="/usr/pgsql-9.1/bin/pg_ctl stop -D/var/lib/eucalyptus/db/data"
# start eucalyptus-cloud

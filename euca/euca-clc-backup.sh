#!/bin/sh

# Backup and restore a Eucalyptus Cloud Controller DB & Keys
#
# Software License Agreement (BSD License)
#
# Copyright (c) 2013, Eucalyptus Systems, Inc.
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


# Database Options
DBPORT="8777"
DBUSER="root"
DBDIR="/var/lib/eucalyptus/db/data"
DBSOCKET="${DBDIR}/.s.PGSQL.${DBPORT}"
DATE="`date +%Y%m%d%H%M`"
DUMPDIR="/var/lib/eucalyptus/backups/"
DUMPFILE="${DUMPDIR}/eucalyptus-database-${DATE}.sql"
TEMPFILE="`mktemp`"
KEYSDIR="/var/lib/eucalyptus/keys"
KEYSFILE="${DUMPDIR}/eucalyptus-keysdir-${DATE}.tgz"

backup() {
    if ! test -S "$DBSOCKET"; then
        exit 0
    fi
    if ! pg_dumpall -c -o -h ${DBDIR} -p ${DBPORT} -U ${DBUSER} -f ${TEMPFILE} >/dev/null 2>&1; then
            echo "Failed to backup Eucalyptus database: pg_dumpall failed" 1>&2
            rm -f "$TEMPFILE"
            exit 1
    fi
    if ! tar -czvf ${KEYSFILE} ${KEYSDIR} >/dev/null 2>&1; then
            echo "Failed to backup Eucalyptus keys: tar failed" 1>&2
            exit 1
    fi
    if ! install -m 600 -o root -g root "$TEMPFILE" "$DUMPFILE" >/dev/null 2>&1; then
            echo "Failed to backup Eucalyptus database: Copying of $TEMPFILE to $DUMPFILE failed" 1>&2
            rm -f "$TEMPFILE"
            exit 1
    fi
    rm -f "$TEMPFILE"
}
 
restore() {
    # Stop CLC service
    /etc/init.d/eucalyptus-cloud stop

    # Remove old db dir
    rm /var/lib/eucalyptus/db -rf

    # Initialise new db structure
    euca_conf --initialize

    # Start Eucalyptus PostgreSQL DB
    su eucalyptus -c "/usr/pgsql-9.1/bin/pg_ctl start -w -s -D${DBDIR} -o '-h0.0.0.0/0 -p${DBPORT} -i'"

    # Restore Backup
    psql -U ${DBUSER} -d postgres -p ${DBPORT} -h ${DBDIR} -f $1

    # Restore keys
    tar -xvf $2 -C /

    # Stop Eucalyptus PostgreSQL DB
    su eucalyptus -c "/usr/pgsql-9.1/bin/pg_ctl stop -D${DBDIR}"

    # Start CLC
    /etc/init.d/eucalyptus-cloud start
}

if [ "$1" = "backup" ]; then
  backup
elif [ "$1" = "restore" ]; then
  if [ $# = 3 ]; then
    restore $2 $3
  else
    echo "Please specify full path of pg_dumpall sql file and keys dir backup"
  fi
else
  echo "
  clc backup - manage backup of Eucalyptus CLC DB backup
  
  USAGE:
  
  ./euca-clc-backup.sh backup - take a full backup of the db 
  ./euca-clc-backup.sh restore sqldump keystarfile - restore db from sql file and
    keys directory contents from tar file
  "
fi

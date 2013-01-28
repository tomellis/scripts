#!/bin/sh

# Eucalyptus CLC Backup & Restore script
# - includes DB & Keys

# Database Options
DBPORT="8777"
DBUSER="root"
DBDIR="/var/lib/eucalyptus/db/data"
DBSOCKET="${DBDIR}/.s.PGSQL.${DBPORT}"
DATE="`date +%Y%m%d%H%M`"
DUMPDIR="/var/lib/eucalyptus/dbdumps/postgresql"
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

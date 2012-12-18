#!/bin/bash
TODAYS_DATE=`date +%m/%d/%Y`
START_DATE=`date +%m/01/%Y`
DATE=`date +%d%m%Y`
PASS="i3d2012@"
/usr/local/sbin/euca_generate_report.py -t instance -p ${PASS} -b ${START_DATE} -e ${TODAYS_DATE} -f csv -g account -o /var/tmp/instance-report-${DATE}
/usr/local/sbin/euca_generate_report.py -t storage -p ${PASS} -b ${START_DATE} -e ${TODAYS_DATE} -f csv -g account -o /var/tmp/storage-report-${DATE}
/usr/local/sbin/euca_generate_report.py -t s3 -p ${PASS} -b ${START_DATE} -e ${TODAYS_DATE} -f csv -g account -o /var/tmp/s3-report-${DATE}
rm -rf /var/tmp/instance-report* /var/tmp/storage-report* /var/tmp/s3-report*

#!/bin/bash
TODAYS_DATE=`date +%m/%d/%Y`
START_DATE=`date +%m/01/%Y`
DATE=`date +%d%m%Y`
PASS="password"
/usr/local/sbin/euca_generate_report.py -t instance -p ${PASS} -b ${START_DATE} -e ${TODAYS_DATE} -f csv -g account -o instance-report-${DATE}
/usr/local/sbin/euca_generate_report.py -t storage -p ${PASS} -b ${START_DATE} -e ${TODAYS_DATE} -f csv -g account -o storage-report-${DATE}
/usr/local/sbin/euca_generate_report.py -t s3 -p ${PASS} -b ${START_DATE} -e ${TODAYS_DATE} -f csv -g account -o s3-report-${DATE}

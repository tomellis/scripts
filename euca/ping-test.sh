#!/bin/bash

for i in `cat ips`; do
  RETVAL=0
  ping -c1 -W 2 $i 1>/dev/null 2>&1
  RETVAL=$?
  if [ $RETVAL -eq 0 ]; then
    echo "$i - OK" 1>/dev/nill 2>&1
  else
    echo "$i failed." | tee -a broken-instances.log
  fi
done

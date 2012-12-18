#!/bin/bash -x
EMI="emi-XXXXXXX"
GROUP_NAME="20"

while [ $GROUP_NAME -lt 30 ]; do
  echo "Adding a new group, ${GROUP_NAME}"
  euca-add-group -d ${GROUP_NAME} ${GROUP_NAME}
  euca-authorize -P icmp -t -1:-1 -s 0.0.0.0/0 ${GROUP_NAME}
  euca-authorize -P tcp -p 22 -s 0.0.0.0/0 ${GROUP_NAME}

  echo "Entering run-instances loop..."  
  i="0"
  while [ $i -lt 2 ]; do
    echo "Running 10 instances on cluster1...."
    euca-run-instances -k cloudadmin -t m1.small -n 10 -z cluster1 -g ${GROUP_NAME} ${EMI}
    #sleep 3m
    echo "Running 10 instances on cluster2...."
    euca-run-instances -k cloudadmin -t m1.small -n 10 -z cluster2 -g ${GROUP_NAME} ${EMI}
    #sleep 3m
    i=$[$i+1]
  done
  GROUP_NAME=$[$GROUP_NAME+1]
done

echo "Done."

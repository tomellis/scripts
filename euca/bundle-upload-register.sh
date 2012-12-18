#!/bin/bash
#
# Copyright (C) 2011
# Olivier Renault <monoliv@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# * Tue Jan 03 2012 Olivier Renault <monoliv@gmail.com> - 0.1
# - initial script



if ( ! getopts "k:r:i:b:" opt); then
	echo "Usage: `basename $0` options (-k kernel_file) (-r ramdisk_file) (-i image_file) (-b bucket)";
	exit $E_OPTERROR;
fi


while getopts "k:r:i:b:" opt; do
  case $opt in
    k)
      echo "-k was triggered, Parameter: $OPTARG" >&2
      KERNEL=$OPTARG
      ;;
    r)
      echo "-r was triggered, Parameter: $OPTARG" >&2
      RAMDISK=$OPTARG
      ;;
    i)
      echo "-i was triggered, Parameter: $OPTARG" >&2
      IMAGE=$OPTARG
      ;;
    b)
      echo "-b was triggered, Parameter: $OPTARG" >&2
      BUCKET=$OPTARG
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      exit 1
      ;;
  esac
done

# Register Kernel
MANIFEST=`euca-bundle-image --kernel=true -i $KERNEL | grep "Generating" | awk '{print $NF}'`
XML=`euca-upload-bundle -b $BUCKET -m $MANIFEST | grep "Uploaded" | awk '{print $NF}'`
EKI=`euca-register --kernel=true -a x86_64 $XML | awk '{print $NF}'`


# Register Ramdisk
MANIFEST=`euca-bundle-image --ramdisk=true -i $RAMDISK | grep "Generating" | awk '{print $NF}'`
XML=`euca-upload-bundle -b $BUCKET -m $MANIFEST | grep "Uploaded" | awk '{print $NF}'`
ERI=`euca-register --ramdisk=true  -a x86_64 $XML | awk '{print $NF}'`


# Register Image
MANIFEST=`euca-bundle-image --kernel=$EKI --ramdisk=$ERI -i $IMAGE | grep "Generating" | awk '{print $NF}'`
XML=`euca-upload-bundle -b $BUCKET -m $MANIFEST | grep "Uploaded" | awk '{print $NF}'`
EMI=`euca-register --ramdisk=$ERI --kernel=$EKI -a x86_64 $XML | awk '{print $NF}'`

echo $EMI


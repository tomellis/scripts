#!/bin/sh 
# 
# Copyright (C) 2011 Eucalyptus Systems, Inc.
#
# Copies an EMI from one Eucalyptus cloud to another.
#
# This script takes several input parameters:
#
# -s <path to the source cloud eucarc>
# -d <path to the destination cloud eucarc>
# <emi>
#
# optional parameters:
#
# -m <new manifest name>
# -b <new bucket name>
# -f
#
# (if these aren't specified, the name from the source cloud will be re-used)
# 
# The "-f" parameter forces a re-copy even if the image exists on the
# destination cloud already.
#
# The last parameter is the emi (or eki/eri) to be copied.
#
# If the referenced EMI is a Linux image and has an associated kernel
# and ramdisk, the script will attempt to copy the kernel and ramdisk
# too. If it's a Windows image, or if you specify an eki or eri, it
# won't try to do anything more than just the image specified.
# 
# It requires one external utility, the XML::XPath module. This is
# available from various places but probably the most convenient is from
# http://repoforge.org/use/ for RHEL/CentOS.
#

TMP=/tmp

usage() {
	echo "Usage: $0 -s <source eucarc> -d <destination eucarc> [-b <new bucket name> -m <new manifest name> -f] <emi-xxxxxxxx to copy>"
	echo "Optional parameters to rename the image at the destination: -b <new bucket name> -m <new manifest name>"
	echo "Force re-upload if image already exists on destination cloud: -f"
	exit 1
}

bail () {
	echo $1
	exit 1
}

trim() { echo $1; }

FORCE=0
while getopts "s:d:e:b:m:f" flag
do
	case $flag in
		s)
			SOURCE_EUCARC=$OPTARG
			shift $((OPTIND-1)); OPTIND=1
			;;
		d)
			DEST_EUCARC=$OPTARG
			shift $((OPTIND-1)); OPTIND=1
			;;
		b)	
			NEW_BUCKET=$OPTARG
			shift $((OPTIND-1)); OPTIND=1
                        ;;
		m)
			NEW_MANIFEST=$OPTARG
			shift $((OPTIND-1)); OPTIND=1
                        ;;
		f)
			FORCE=1
                        shift $((OPTIND-1)); OPTIND=1
			;;
		?)
			usage
			;;
	esac
done

EMI=$1

if [ -z $SOURCE_EUCARC ] ; then
	echo "Source cloud credentials must be specified (eucarc file)"
	usage
fi
if [ ! -f $SOURCE_EUCARC ] ; then
	echo Source cloud credentials at $SOURCE_EUCARC not found
	usage
fi
if [ -z $DEST_EUCARC ] ; then
	echo "Destination cloud credentials must be specified (eucarc file)"
	usage
fi
if [ ! -f $DEST_EUCARC ] ; then
	echo Destination cloud credentials at $DEST_EUCARC not found
	usage
fi

function load_describe_images () {
	. $DEST_EUCARC
	euca-describe-images > /tmp/euca-di-dest.txt
	. $SOURCE_EUCARC
	euca-describe-images > /tmp/euca-di-source.txt
}

function get_emi_info () {
	if [ -z "$1" ]; then
		echo You must specify an image ID.
		exit 1
	fi

	. $SOURCE_EUCARC 

	image_info=$(cat /tmp/euca-di-source.txt | grep -P "IMAGE\s+$1")

	if [ -z "$image_info" ] ; then
		echo Image $1 not found on source cloud.
		exit 1
	fi

	manifest=$(echo "$image_info" | cut -f 3)
	type=$(echo "$image_info" | cut -f 9)
	platform=$(echo "$image_info" | cut -f 12)

	echo "EMI: $1 (manifest: $manifest, type: $type, platform: $platform)"

	if [ $platform = "linux" ]; then
		eki=$(trim $(echo "$image_info" | cut -f 10))
		eri=$(trim $(echo "$image_info" | cut -f 11))
	fi

	bucket=$(echo "$manifest" | cut -d / -f 1)
	xml=$(echo "$manifest" | cut -d / -f 2)
	echo "Bucket: $bucket"
}

function copy_image () {
	local emi=$1
	shift
	local manifest=$1
	shift
	local bucket=$1
	shift
	local xml=$1
	shift
	local eki=$1
	shift
	local eri=$1

	# check for existence of this image already on the destination cloud
        image_info=$(cat /tmp/euca-di-dest.txt | grep "$manifest")	
	if [ -n "$image_info" -a "$FORCE" != "1" ]; then
		echo "Image $manifest already found on destination cloud, skipping."
		new_emi=$(echo $image_info | awk '{print $2}')
		return
	fi	

	. $SOURCE_EUCARC

	echo "Downloading $emi ($manifest) from source cloud..."
	if [ ! -f $TMP/$xml ]; then
		euca-download-bundle -d $TMP -b $bucket || bail "Error downloading bundle from source cloud"
	else
		echo "$TMP/$xml already exists, assuming already downloaded."
	fi

	echo "Unbundling $EMI..."
	euca-unbundle -d $TMP -m $TMP/$xml || bail "Error unbundling image; check source cloud credentials"

	image_filename=$(cat $TMP/$xml | xpath manifest/image/name 2> /dev/null | sed 's/<name>//g' | sed 's/<\/name>//g')

	. $DEST_EUCARC
	echo "Rebundling $image_filename"
	destdir=$(mktemp -d -p $TMP)

	# handle a renamed bucket
	if [ -n "$NEW_BUCKET" ]; then
		bucket=$NEW_BUCKET
	fi

	# only allow a manifest to be renamed if it's not an eki or an eri
	if [ -n "$NEW_MANIFEST" -a "$eri" != "true" -a "$eki" != "true"  ]; then
		mv $TMP/$image_filename $TMP/$NEW_MANIFEST
		image_filename=$NEW_MANIFEST
		xml="$NEW_MANIFEST".manifest.xml
	fi

	bundle_command="euca-bundle-image -d $destdir -i $TMP/$image_filename"

	if [ "$eki" != "false" -a -n "$eki" ]; then
		bundle_command="$bundle_command --kernel $eki"
	fi

	if [ "$eri" != "false" -a -n "$eri" ]; then
		bundle_command="$bundle_command --ramdisk $eri"
	fi

	eval $bundle_command || bail "Error bundling image"

	target_manifest=$(echo $destdir/*.manifest.xml)
	echo "New manifest: $target_manifest"
	euca-upload-bundle -b $bucket -m $target_manifest || bail "Error uploading bundle to destination cloud"

	new_emi=$(euca-register $bucket/$xml)
	if [ $? != 0 ]; then
		echo "Problem registering image: $new_emi"
	else
		new_emi=$(echo $new_emi | awk '{print $2}')
		echo "Image $bucket/$xml ($emi) copied to target cloud, new EMI ID is $new_emi"
	fi
}

load_describe_images

get_emi_info $EMI
emi_manifest=$manifest
emi_type=$type
emi_platform=$platform
emi_bucket=$bucket
emi_xml=$xml
emi_eki=$eki
emi_eri=$eri

# for Linux images that may have an associated EKI or ERI
if [ $emi_platform = "linux" -a $emi_type = "machine" ]; then
	if [ -n "$emi_eki" ]; then
		echo "EMI has an associated EKI ($emi_eki) -- considering that for copying too."
		get_emi_info $emi_eki
		copy_image $emi_eki $manifest $bucket $xml true false
		emi_eki=$new_emi
	else
		echo "Note: EMI does not have an associated EKI, will use the default EKI on the destination cloud."
	fi

	if [ -n "$emi_eri" ]; then
		echo "EMI has an associated ERI ($emi_eki) -- copying that too."
		get_emi_info $emi_eri
		copy_image $emi_eri $manifest $bucket $xml false true
		emi_eri=$new_emi
        else
                echo "Note: EMI does not have an associated ERI, will use the default ERI on the destination cloud."
	fi

	copy_image $EMI $emi_manifest $emi_bucket $emi_xml $emi_eki $emi_eri

# for Windows images or EKI/ERIs
else
	copy_image $EMI $emi_manifest $emi_bucket $emi_xml false false
fi


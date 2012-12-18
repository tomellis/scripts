#!/usr/bin/python
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

import optparse
import os


def parse_args():
    # Parse argument provided on command line and check validity
    parser = optparse.OptionParser()
    parser.add_option("--kernel", type="string", dest="kernel", 
                      help="Kernel file")
    parser.add_option("--ramdisk", type="string", dest="ramdisk",
                      help="Ramdisk File")
    parser.add_option("--image", type="string", dest="image",
                      help="Image File")
    parser.add_option("--key", type="string", dest="key",
                      help="Key to use")
    (options, args) = parser.parse_args()
    return options

def bundle_image(file,type):

def main():
    # Check if conf file and read
    options = parse_args()
    bundle_image(options.kernel,"kernel")

if __name__ == "__main__":
    main()


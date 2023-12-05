#!/usr/bin/env python
import os
import sys
import argparse
from subprocess import run
sys.path.append("/opt/flockpocket/")

# parse the script arguments
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--full', action='store_true', dest='full')
args = parser.parse_args()

# find the directory of this file
curr_dir = os.path.dirname(os.path.realpath(__file__))

# Misc Install
print("installing (miscellaneous)...")
command = "%s/misc_install.sh" % curr_dir
if args.full:
    command += ' -f'
code = run(command.split()).returncode

# Package Install
print("installing packages...")
command = "%s/packages.py" % curr_dir
if args.full:
    command += ' -f'
code = run(command.split()).returncode
if (code):
    sys.exit(code)

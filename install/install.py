#!/usr/bin/env python
import os
import sys
import argparse
from subprocess import getstatusoutput, run
sys.path.append("/opt/flockpocket/")
from common import linux

# parse the script arguments
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--full', action='store_true', dest='full')
parser.add_argument('--skip-snmp-optimization', action='store_true', dest='skip_snmp_optimization',
                    help="Building net-snmp-5.8 from source takes time, but supports more simultaneous connections")
args = parser.parse_args()

# find the linux distrobution name
distro = linux.distro()
release = linux.release()[0]
print("OS Type: %s %s" % (distro, release))

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
if args.skip_snmp_optimization:
    command += ' --skip-snmp-optimization'
code = run(command.split()).returncode
if (code):
    sys.exit(code)

if distro != "docker":
    # for first install
    if args.full:
        command = "%s/postgres.install.py" % curr_dir
        code = run(command.split()).returncode

    # Postgres Configure
    print("configuring postgres...")
    command = "%s/postgres.py" % curr_dir
    code = run(command.split()).returncode

    # Restart postgresql
    if distro in ['ubuntu', 'debian', 'raspbian']:
        svc_name = "postgresql"
    else:
        # fancy command to extract the postgres version number
        (code, result) = getstatusoutput("psql -V | egrep -o '[0-9]{1,}\.[0-9]{1,}'")
        svc_name = "postgresql-%s" % int(float(result))

    command = 'service %s restart' % svc_name
    (code, result) = getstatusoutput(command)

# nginx configure
if args.full and distro != 'docker':
    print("configuring nginx...")
    command = "%s/nginx.py" % curr_dir
    code = run(command.split()).returncode

# Startup Scripts
if distro in ['ubuntu', 'debian']:
    print("adding to system startup...")
    command = "cp %s/files/flockpocket /etc/init.d/" % curr_dir
    code = run(command.split()).returncode
    command = "update-rc.d flockpocket defaults"
    code = run(command.split()).returncode

# Init DB
if distro not in ['docker']:
    print("initialize database...")
    command = "%s/init_db.sh 2> /dev/null" % curr_dir
    code = run(command.split()).returncode

    command = "%s/create_users.py" % curr_dir
    code = run(command.split()).returncode

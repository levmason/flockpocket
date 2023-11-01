#!/usr/bin/env python
from __future__ import division
import os, sys, re
import string, random
from subprocess import getstatusoutput, run, PIPE
sys.path.append("/opt/flockpocket")
from common import root_config as cfg
from common import linux
from common import textIO
import apt
import yum

postgres_version = 16
distro = linux.distro()
release = linux.release()[0]

command = "which psql"
(code, result) = getstatusoutput(command)

if code == 0:
    print("postgresql already installed!")
else:
    if distro in ['ubuntu', 'debian', 'raspbian']:
        command = "lsb_release -cs"
        (code, release_str) = getstatusoutput(command)

        #
        # add postgres sources
        with open ('/etc/apt/sources.list.d/pgdg.list', 'wb') as f:
            f.write(('deb http://apt.postgresql.org/pub/repos/apt/ %s-pgdg main\n' % release_str).encode())

        command = "wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -"
        (code, result) = getstatusoutput(command)

        #
        # Install the packages
        apt_packages = [
            'postgresql-%s' % postgres_version,
            'postgresql-contrib-%s' % postgres_version,
            'postgresql-server-dev-%s' % postgres_version,
        ]

        apt.update()

        # loop through the apt packages
        for pkg in apt_packages:
            try:
                apt.install(pkg)
            except:
                print(textIO.warning("%s failed to install :-(" % pkg))
                sys.exit(code)

    elif distro in ['centos']:
        # add the postgres repository
        pkg = 'https://download.postgresql.org/pub/repos/yum/reporpms/EL-7-x86_64/pgdg-redhat-repo-latest.noarch.rpm'
        yum.install(pkg, quiet=True)

        #
        # Install the packages
        yum_packages = [
            'postgresql%s' % postgres_version,
            'postgresql%s-contrib' % postgres_version,
            'postgresql%s-devel' % postgres_version,
            'postgresql%s-server' % postgres_version,
        ]

        yum.update()

        # loop through the apt packages
        for pkg in yum_packages:
            try:
                yum.install(pkg)
            except:
                print(textIO.warning("%s failed to install :-(" % pkg))
                sys.exit(code)

        # run the initdb
        command = '`find / -name postgresql*-setup | head -n1` initdb'
        (code, result) = getstatusoutput(command)
        # configure to run at startup
        command = 'systemctl enable postgresql-%s' % postgres_version
        (code, result) = getstatusoutput(command)
        # start the service
        command = 'service postgresql-%s restart' % postgres_version
        (code, result) = getstatusoutput(command)

# find the database password
if not cfg.db_password:
    length = 16
    chars = string.ascii_lowercase + string.digits
    cfg.db_password = ''.join(random.choice(chars) for x in range(length))

    # write the password into the root config
    filepath = "/etc/%s/%s.conf" % (cfg.tool_name, cfg.tool_name)
    with open (filepath, "r") as f:
        cfg_txt = f.read()
        cfg_txt += "db_password: %s\n" % cfg.db_password

    with open (filepath, "w") as f:
        f.write(cfg_txt)

#
# init the database
def psql_run (command, db = None, required = True):
    if db:
        db_arg = "-d %s" % db
    else:
        db_arg = ""

    command = "runuser -l postgres -c \"psql -qAt %s -c \\\"%s\\\"\"" % (db_arg, command)
    try:
        result = run(command, shell=True, check=True, stdout=PIPE, stderr=PIPE, stdin=PIPE).stdout.decode()
    except Exception as e:
        if required:
            print(textIO.error(e))
        return

    return result

print("Creating database user...")
psql_run("CREATE USER %s WITH PASSWORD '%s'" % (cfg.db_username, cfg.db_password), required = False)
psql_run("ALTER USER %s WITH PASSWORD '%s'" % (cfg.db_username, cfg.db_password))
psql_run("ALTER USER %s WITH SUPERUSER" % cfg.db_username)

print("Creating the database...")
psql_run("CREATE DATABASE flockpocket OWNER %s" % cfg.db_username, required = False)
psql_run("ALTER DATABASE flockpocket OWNER TO %s" % cfg.db_username)

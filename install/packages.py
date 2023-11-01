#!/usr/bin/env python
from __future__ import division, print_function
import sys, os
import argparse
from subprocess import getstatusoutput, run, PIPE
sys.path.append("/opt/flockpocket/")
from common import linux
from common import textIO
import apt
import yum

# parse the script arguments
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--full', action='store_true', dest='full')
args = parser.parse_args()

# find the linux distrobution name
distro = linux.distro()
release = linux.release()[0]

# find the directory of this file
install_dir = os.path.dirname(os.path.realpath(__file__))

# keep track of packages that fail to install
failed = []

try:
    if distro in ['ubuntu', 'debian', 'raspbian', 'docker']:
        apt.update()

        # find the correct requirements file
        req_path = "%s/requirements/apt_requirements.%s_%s.txt" % (install_dir, distro, release)
        if not os.path.exists(req_path):
            req_path = "%s/requirements/apt_requirements.%s.txt" % (install_dir, distro)

        # loop through the apt packages
        with open(req_path, 'r') as f:
            apt_packages = f.read().splitlines()
            for pkg in apt_packages:
                try:
                    apt.install(pkg)
                except:
                    failed.append(('apt', pkg))
                    if not textIO.prompt(textIO.warning("Package installation failed! Continue package installation?")):
                        sys.exit(1)

        apt.cleanup()
    elif distro in ['centos', 'redhat']:
        yum.update()

        # set the yum options
        yum_cmd = 'yum -q -y'
        # loop through the yum packages
        with open("%s/requirements/yum_requirements.txt" % install_dir, 'r') as f:
            yum_packages = f.read().splitlines()
            for pkg in yum_packages:
                try:
                    yum.install(pkg)
                except:
                    failed.append(('yum', pkg))
                    if not textIO.prompt(textIO.warning("Package installation failed! Continue package installation?")):
                        sys.exit(1)

    # loop through the pip packages
    with open("%s/requirements/pip_requirements.txt" % install_dir, 'r') as f:
        pip_packages = f.read().splitlines()
        for pkg in pip_packages:
            print("(pip) Installing %s" % pkg)
            command = 'pip install %s' % pkg
            if '==' not in pkg:
                command += " --upgrade"
            (code, result) = getstatusoutput(command)
            if code != 0:
                failed.append(('pip', pkg))
                print(textIO.fail("[ERROR]"))
                print(textIO.fail(result))
                if not textIO.prompt(textIO.warning("Package installation failed! Continue package installation?")):
                    sys.exit(1)

    if failed:
        text = "---------- Failed Packages ----------\n"
        for x, pkg in failed:
            text += "(%s) %s\n" % (x, pkg)
        text += "-------------------------------------\n"
        print(textIO.fail(text))

except KeyboardInterrupt:
    sys.exit(1)



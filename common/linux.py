import os
from subprocess import getstatusoutput

os_release = {}

# try to pull platform detials
command = "cat /etc/os-release"
(code, result) = getstatusoutput(command)
for line in result.splitlines():
    try:
        key, val = line.split("=")
        os_release[key.lower()] = val.lower().strip("\"")
    except: continue

def distro ():
    if os.environ.get("DOCKER"):
        return "docker"
    else:
        return os_release['id']

def release ():
    return [int(x) for x in os_release['version_id'].split('.')]

def get_system_timezone ():
    command = 'cat /etc/timezone'
    (code, result) = getstatusoutput(command)
    return result

#!/usr/bin/env python
import os, sys, re
from subprocess import getstatusoutput, run, PIPE
sys.path.append("/opt/flockpocket")
from common import root_config as cfg

# find the directory of this file
install_dir = os.path.dirname(os.path.realpath(__file__))
project_dir = os.path.dirname(install_dir)

# remove all existing nginx configs
command = "rm -f /etc/nginx/sites-enabled/*"
run(command, shell=True, stderr=PIPE)
command = "rm -f /etc/nginx/conf.d/*"
run(command, shell=True, stderr=PIPE)

# determine the nginx version (and nginx corresponding config file)
command = "nginx -v 2>&1 | grep -oE [0-9.]+"
(code, result) = getstatusoutput(command)
nginx_conf = 'flockpocket.conf'

# set the daphne bind variable
if cfg.daphne_port:
    daphne_bind = "0.0.0.0:%s" % cfg.daphne_port
else:
    daphne_bind = "unix:%s" % (cfg.daphne_socket or cfg.get_sockfile('daphne'))

# build the nginx configs (using config variables)
filepath = "%s/server/nginx/%s" % (project_dir, nginx_conf)
with open (filepath, "r") as f:
    cfg = f.read()
    # replace the bind variables
    cfg = re.sub(r'{daphne_bind}', daphne_bind, cfg)

# write the config file into the nginx directory
filepath = "/etc/nginx/conf.d/%s" % nginx_conf
with open (filepath, "w") as f:
    f.write(cfg)

# find the nginx user
command = "egrep -o 'user\s+.+;' /etc/nginx/nginx.conf | egrep -o '[^ ;]+' | tail -n1"
(code, nginx_user) = getstatusoutput(command)
# add the flockpocket group
command = "usermod -a -G flockpocket %s" % nginx_user
run(command.split())

# restart nginx
command = "flockpocket nginx restart"
run(command.split())

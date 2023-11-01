#!/usr/bin/env python
from __future__ import division
from psutil import virtual_memory
from subprocess import getstatusoutput
import re

#
# find the config file
for x in ['etc', 'var']:
    (code, result) = getstatusoutput('find /%s/ -name postgresql.conf' % x)
    filepath_l = result.splitlines()
    if filepath_l: break

for filepath in filepath_l:
    #
    # find the new values
    mem = virtual_memory().total // (1024 * 1024)
    max_connections = 512
    shared_buffers = int(mem / 4)
    effective_cache_size = int(mem * 3/4)

    #
    # edit the file
    with open (filepath, "r") as f:
        cfg = f.read()
        cfg = re.sub(r'\n[#\s*]?(max_connections\s+=\s+)[0-9]+', '\n\g<1>%s' % max_connections, cfg)
        cfg = re.sub(r'\n[#\s*]?(shared_buffers\s+=\s+)[0-9]+\w+', '\n\g<1>%sMB' % shared_buffers, cfg)
        cfg = re.sub(r'\n[#\s*]?(effective_cache_size\s+=\s+)[0-9]+\w+', '\n\g<1>%sMB' % effective_cache_size, cfg)

    with open (filepath, "w") as f:
        f.write(cfg)

#
# edit the authentication method in pg_hba.conf
(code, result) = getstatusoutput('find / -name pg_hba.conf')
filepath_l = result.splitlines()

for filepath in filepath_l:
    try:
        # edit the file
        with open (filepath, "r") as f:
            cfg = f.read()
            cfg = re.sub(r'\n[#\s*]?(host\s+all\s+all.*)ident', '\n\g<1>md5', cfg)

        with open (filepath, "w") as f:
            f.write(cfg)
    except: pass

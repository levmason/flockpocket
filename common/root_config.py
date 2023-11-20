import os
import yaml
from common import linux

tool_name = "flockpocket"
proj_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
cfg_file = "/etc/%s/%s.conf" % (tool_name, tool_name)

if linux.distro() == "docker":
    db_host = 'db'
    redis_host = 'redis'
else:
    redis_host = db_host = 'localhost'


# Root Config Options
opts = {
    # django
    'django_secret_key': '',
    'db_name': 'flockpocket',
    'db_username': "flockpocket",
    'db_password': None,
    'db_host': db_host,
    'db_port': 5432,
    'daphne_port': None,
    'daphne_socket': None,
    'debug': False,
    # redis
    'redis_host': redis_host,
    'redis_port': 6379,
    'redis_username': None,
    'redis_password': None,
    # email
    'email_host': None,
    'email_port': None,
    'email_user': None,
    'email_password': None,
    'email_from': None,
    # misc
    'sub_url': '',
    'timezone': linux.get_system_timezone()
}


# import the tool config
try:
    with open (cfg_file) as f:
        _config_d = yaml.full_load(f.read()) or {}
except:
    _config_d = {}

#
# init root globals from flockpocket.conf
config_d = {}
for key, value in opts.items():
    config_d[key] = globals()[key] = _config_d.get(key, value)

# string conversion map
eval_map = ['True', 'False']

#
# overwrite root globals with linux env
for key, value in config_d.items():
    opt = "FLOCKPOCKET_%s" % key.upper()
    val = os.environ.get(opt, value)
    if val in eval_map:
        val = eval(val)

    config_d[key] = globals()[key] = val

def get_logfile (name):
    return '/var/log/%s/%s.log' % (tool_name, name)

def get_pidfile (name):
    return '/run/%s/%s.pid' % (tool_name, name)

def get_sockfile (name):
    return '/run/%s/%s.sock' % (tool_name, name)

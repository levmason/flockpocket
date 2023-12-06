import os
from common import linux

tool_name = "flockpocket"
proj_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# Root Config Options
opts = {
    'domain_name': '',
    # django
    'django_secret_key': '',
    'postgres_name': 'flockpocket',
    'postgres_username': "flockpocket",
    'postgres_password': None,
    'postgres_host': 'db',
    'postgres_port': 5432,
    'daphne_port': 8086,
    'debug': False,
    # redis
    'redis_host': 'redis',
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

# string conversion map
eval_map = ['True', 'False']

# overwrite root globals with linux environment variables
config_d = {}
for key, value in opts.items():
    opt = key.upper()
    val = os.environ.get(opt, value)
    if val in eval_map:
        val = eval(val)

    config_d[key] = globals()[key] = val

# file locations
def get_logfile (name):
    return '/var/log/%s/%s.log' % (tool_name, name)

def get_pidfile (name):
    return '/run/%s/%s.pid' % (tool_name, name)

def get_sockfile (name):
    return '/run/%s/%s.sock' % (tool_name, name)

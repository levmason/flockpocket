"""
File: config.py
Class: config

The config class is meant to handle the overall configuration and variables
shared between the different modules.
"""

import os, traceback
import uuid

from .RedisWrapper import aioRedisWrapper
from common.models import User as User_db
from user.User import User

from . import linux
from . import root_config as root
from . import logger as log
from . import aio

# Globals (from root)
tool_name = root.tool_name
tool_version = "1.00"
pid = os.getpid()
proj_dir = root.proj_dir
storage_dir = f"{proj_dir}/storage"
chat_dir = f"{storage_dir}/chat"
get_logfile = root.get_logfile
get_pidfile = root.get_pidfile
get_sockfile = root.get_sockfile
profile_pic_dir = "%s/static/profile_pics/" % proj_dir

# make the directories
if not os.path.exists(chat_dir):
    os.makedirs(chat_dir)

services = [
    'builder',
    'daphne',
    'datastore',
]

# Globals
initialized = False
redis = None
distro = linux.distro()
release = linux.release()[0]
config = {}
user_d = {}
log_dir = "/var/log/flockpocket/"
# invite hold time (days)
invite_timeout = 2

def init_config ():
    # init root globals
    for key, value in root.opts.items():
        globals()[key] = root.config_d.get(key, value)

async def init ():
    global redis, user_d, initialized

    if not initialized:
        initialized = True
        redis = await init_redis()

        try:
            user_d = await init_user_d()
        except Exception as e:
            log.debug(traceback.format_exc())

#
# User
async def init_user_d ():
    global user_d

    user_d = {}
    async for user_db in User_db.objects.all():
        user = User(user_db)
        user_d[user_db.id] = user

    return user_d

async def update_user (user_db):
    # see if the user already exists
    user = await get_user(user_db.id)
    user.update(user_db)
    user_dict = user.as_dict()

    task_l = []
    for usr_id, usr in user_d.items():
        task_l.append(usr.push_user(user_dict))

    await aio.gather(task_l)

async def get_user (user_id, user_db = None):
    if isinstance(user_id, str):
        user_id = uuid.UUID(user_id)

    user = user_d.get(user_id)
    if not user:
        if not user_db:
            user_db = await User_db.objects.aget(pk=user_id)

        user_d[user_id] = user = User(user_db)

    return user

# interface to redis
async def init_redis ():
    redis = aioRedisWrapper(host=root.redis_host,
                            port=root.redis_port,
                            username=root.redis_username,
                            password=root.redis_password)
    await redis.connect()
    return redis

import time
import aioredis
from . import config as cfg
from . import logger as log
from . import utility
from . import crypto

def pfx (x):
    """ add the tool name prefix """
    if isinstance(x, list):
        return [pfx(i) for i in x]
    else:
        if x.startswith(cfg.tool_name):
            return x
        else:
            return '.'.join([cfg.tool_name, x])

class RedisWrapper (object):
    def __init__ (self, host = "", port = "", username = "", password = ""):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def connect (self):
        self.redis = redis.StrictRedis(host=self.host,
                                       port=self.port,
                                       username=self.username,
                                       password=self.password)

    def set (self, key, value, secure=False, ex=None):
        # encode
        value = crypto.encode(value, secure=secure)
        # set
        self.redis.set(pfx(key), value, ex=ex)

    def get (self, key, default=None, secure=False):
        # get
        value = self.redis.get(pfx(key))
        # decode
        value = crypto.decode(value, secure=secure)

        return value if value is not None else default

    def delete (self, key):
        self.redis.delete(pfx(key))

    def publish (self, channel, value):
        # encode
        value = crypto.encode(value)
        # set
        self.redis.publish(pfx(channel), value)

    def subscribe (self, channel):
        sub = self.redis.pubsub(ignore_subscribe_messages=True)
        sub.subscribe(pfx(channel))
        return sub

    def psubscribe (self, channel):
        sub = self.redis.pubsub(ignore_subscribe_messages=True)
        sub.psubscribe(pfx(channel))
        return sub

    def unsubscribe (self, sub, channel):
        sub.unsubscribe(pfx(channel))

    def get_message (self, sub, timeout=1):
        msg = sub.get_message(timeout=timeout)
        if msg is not None:
            data = crypto.decode(msg.get('data'))
            channel = msg.get('channel').decode()
            return channel, data
        else:
            return None, None

    def wait_for (self, sub, timeout=10.0):
        t1 = time.time()
        while True:
            # first the subscribe message will come
            msg = sub.get_message(timeout=1)
            if msg:
                sub.close()
                return crypto.decode(msg['data'])
            if time.time() - t1 > timeout:
                break

    def query (self, channel, query, timeout=10):
        key = hash("%s%s" % (time.time(), cfg.pid))
        channel = "%s.%X" % (channel, key)

        try:
            sub = self.subscribe("response.%s" % channel)
            self.publish(channel, query)
            response = self.wait_for(sub, timeout=timeout)
        finally:
            sub.close()

        return response

    def respond (self, channel, value):
        channel = channel.replace(cfg.tool_name, "%s.response" % cfg.tool_name)
        self.publish(channel, value)

    def ds_query (self, query, timeout=10):
        return self.query('datastore', query, timeout=timeout)

    def ds_push (self, query):
        self.publish('datastore', query)

    def poller_query (self, query, timeout=10):
        return self.query('poller', query, timeout=timeout)

    def poller_push (self, query):
        self.publish('poller', query)

class aioRedisWrapper (object):
    def __init__ (self, host = "", port = "", username = "", password = "", socket_connect_timeout=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.socket_connect_timeout = socket_connect_timeout

    async def connect (self):
        self.redis = await aioredis.StrictRedis(host=self.host,
                                                port=self.port,
                                                username=self.username,
                                                password=self.password,
                                                socket_connect_timeout=self.socket_connect_timeout)

    async def set (self, key, value, secure=False, ex=None):
        # encode
        value = crypto.encode(value, secure=secure)
        # set
        await self.redis.set(pfx(key), value, ex=ex)

    async def get (self, key, default=None, secure=False):
        # get
        value = await self.redis.get(pfx(key))
        # decode
        value = crypto.decode(value, secure=secure)

        return value if value is not None else default

    async def delete (self, key):
        await self.redis.delete(pfx(key))

    async def publish (self, channel, value):
        # encode
        value = crypto.encode(value)
        # set
        await self.redis.publish(pfx(channel), value)
        # return the size of the data
        return len(value)

    async def subscribe (self, channel):
        sub = self.redis.pubsub(ignore_subscribe_messages=True)
        await sub.subscribe(pfx(channel))
        return sub

    async def psubscribe (self, channel):
        sub = self.redis.pubsub(ignore_subscribe_messages=True)
        await sub.psubscribe(pfx(channel))
        return sub

    async def unsubscribe (self, sub, channel):
        await sub.unsubscribe(pfx(channel))

    async def subcount (self, channel):
        return (await self.redis.pubsub_numsub(pfx(channel)))[0][1]

    async def get_message (self, sub, timeout=1):
        msg = await sub.get_message(timeout=timeout)
        if msg is not None:
            data = crypto.decode(msg.get('data'))
            channel = msg.get('channel').decode()
            return channel, data
        else:
            return None, None

    async def wait_for (self, sub, timeout=10.0):
        t1 = time.time()
        while True:
            # first the subscribe message will come
            msg = await sub.get_message(timeout=1)
            if msg:
                await sub.close()
                return crypto.decode(msg['data'])
            if time.time() - t1 > timeout:
                break

    async def query (self, channel, query, timeout=10):
        key = hash("%s%s" % (time.time(), cfg.pid))
        channel = "%s.%X" % (channel, key)

        try:
            sub = await self.subscribe("response.%s" % channel)
            await self.publish(channel, query)
            response = await self.wait_for(sub, timeout=timeout)
        finally:
            await sub.close()

        return response

    async def respond (self, channel, value):
        channel = channel.replace(cfg.tool_name, "%s.response" % cfg.tool_name)
        await self.publish(channel, value)

    async def ds_query (self, query, timeout=10):
        return await self.query('datastore', query, timeout=timeout)

    async def ds_push (self, query):
        return await self.publish('datastore', query)

    async def poller_query (self, query, timeout=10):
        return await self.query('poller', query, timeout=timeout)

    async def poller_push (self, query):
        return await self.publish('poller', query)

    async def handle_push (self, query):
        return await self.publish('handle', query)

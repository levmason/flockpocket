import time
import traceback
import uuid
from common import config as cfg
from common import logger as log
from common import aio
from .ChatDatastore import ChatDatastore

class DatastoreDaemon():
    def __init__(self):
        self.name = "datastore"
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  cfg.get_pidfile(self.name)
        self.pidfile_timeout = 1
        self.interrupt = False

    def run(self):
        # start the asyncio loop
        aio.run(self.initialize())

    def terminate(self, signal_number, stack_frame):
        self.interrupt = True

    async def initialize (self):
        # Levy: delete all the threads in the DB
        #log.debug("removing threads...")
        #from common.models import ChatThread as ChatThread_db
        #await ChatThread_db.objects.all().adelete();

        # initialize the chat handler
        self.chat = ChatDatastore()
        # subscribe to data
        self.sub = await cfg.redis.psubscribe('%s*' % self.name)
        # start the message handler
        await self.handler()
        # gracefully stop the chat handlers
        await self.chat.stop()

    async def handler (self):
        while not self.interrupt:
            try:
                channel, data = await cfg.redis.get_message(self.sub)
                if data is not None:
                    aio.create_task(self.process_query(channel, data))
            except Exception as e:
                log.debug(traceback.format_exc())

    async def process_query (self, channel, query):

        for name, options in query.items():
            # find the query handler
            try:
                fn = getattr(self, name)
                response = await fn(**options)

                if not channel.endswith(self.name):
                    await self.respond(channel, response)
            except Exception as e:
                log.debug("Can't process query: %s\n%s" % (name, e))
                log.debug(traceback.format_exc())

    async def respond (self, channel, response):
        await cfg.redis.respond(channel, response)

    #
    # Chat Threads
    #
    async def get_thread_history (self, thread_id = None):
        thread_id = uuid.UUID(thread_id)
        return await self.chat.get_history(thread_id)

    async def store_message (self, thread_id = None, message = None):
        thread_id = uuid.UUID(thread_id)
        await self.chat.add_message(thread_id, message)

    async def like_message (self, thread_id = None, user_id = None, message_idx = None):
        thread_id = uuid.UUID(thread_id)
        await self.chat.like_message(thread_id, user_id, message_idx)

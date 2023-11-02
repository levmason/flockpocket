import time
import traceback
import uuid
from common import config as cfg
from common import logger as log
from common import aio
from chat.ChatHandler import ChatHandler

class DatastoreDaemon():
    chat = ChatHandler()

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
        self.chat = ChatHandler()
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
        # get the query type
        query_type = query.get('name').lower()

        # find the query handler
        try:
            fn = getattr(self, query_type)
            t1 = time.time()
            response = await fn(query.get('options', {}))
            t2 = time.time()
            #log.debug("Query/%s took: %sms" % (query_type, int(1000*(t2-t1))))

            if not channel.endswith(self.name):
                await self.respond(channel, response)
        except Exception as e:
            log.debug("Can't process query: %s\n%s" % (query_type, e))
            log.debug(traceback.format_exc())

    async def respond (self, channel, response):
        await cfg.redis.respond(channel, response)

    #
    # Chat Threads
    #
    async def get_thread_history (self, opt):
        thread_id = uuid.UUID(opt['thread_id'])
        return await self.chat.read_thread(thread_id)

    async def store_message (self, opt):
        thread_id = uuid.UUID(opt['thread_id'])
        thread = await self.chat.get_thread(thread_id)
        if thread:
            await thread.add_message(opt['message'])
        else:
            log.debug(f"Can't find thread {thread_id}")

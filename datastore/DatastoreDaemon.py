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
                    aio.create_task(self.handle_message(channel, data))
            except Exception as e:
                log.debug(traceback.format_exc())

    async def handle_message (self, channel, message):
        """Handles the message"""

        # find all tasks
        task_l = []
        for name, options in message.items():
            # Finds the correct API handler function
            if '.' in name:
                module_name, fn_name = name.split(".")
                module = getattr(self, module_name)
                fn = getattr(module, fn_name)
            else:
                fn = getattr(self, name)

            # queue the handler function (the ** converts the dictionary into keyword arguments)
            task_l.append(fn(**options))

        # execute tasks
        results = await aio.gather(task_l)

        # handle responses
        for r in results:
            # if there's an error, raise it
            if isinstance(r, Exception):
                await self.error(str(r))
                # debug the error
                try:
                    raise r
                except:
                    log.debug("Error in handler:\n%s" % traceback.format_exc())
            elif r and not channel.endswith(self.name):
                # If there's a response, then send it to the browser
                await self.respond(channel, r)

    async def respond (self, channel, response):
        await cfg.redis.respond(channel, response)

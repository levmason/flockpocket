import time
import json
import uuid
import traceback
from channels.generic.websocket import AsyncWebsocketConsumer

from common import config as cfg
from common import logger as log
from common import utility
from common import aio
from common.models import User as User_db
from user.User import User
from user import utility as user_utility
from .chat.ChatHandler import ChatHandler

class FlockConsumer(AsyncWebsocketConsumer):
    async def connect (self):
        """ What to run when a new connection is received """

        user_db = self.scope['user']

        if user_db.is_authenticated:
            await self.accept()
            self.user = await cfg.get_user(user_db.id, user_db = user_db)
            self.user.socket_l.append(self)
            self.chat = ChatHandler(self.user)

    async def disconnect (self, close_code):
        """ What to run when a connection is lost """
        self.user.socket_l.remove(self)

    async def respond (self, data):
        """ Respond to the browser """

        # Formats the data
        if not isinstance(data, str):
            data = json.dumps(data)

        # Sends the data
        await self.send(text_data=data)

    async def error (self, message):
        """What to do when there is an error"""
        await self.respond({
            "error": message
        })

    async def receive (self, text_data):
        """ What do do when we receive a message """
        # Formats the message
        message = json.loads(text_data)
        if isinstance(message, str):
            message = {message: {}}

        # Starts a new task to handle the message
        aio.create_task(self.handle_message(message))

    async def handle_message (self, message):
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
            # if there's an error, report it
            if isinstance(r, Exception):
                await self.error(str(r))
                # debug the error
                try:
                    raise r
                except:
                    log.debug("Error in handler:\n%s" % traceback.format_exc())
            elif r:
                # If there's a response, then send it to the browser
                await self.respond(r)

    async def ui_config (self):
        return {
            'ui_config': {
                'user_id': str(self.user.id),
                'user_d': {str(x):y.as_dict() for x,y in cfg.user_d.items() if y.is_active},
                'thread_d': await self.chat.get_threads(),
            }
        }


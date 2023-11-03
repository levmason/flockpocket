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
from common.models import ChatThread as ChatThread_db
from user.User import User
from user import utility as user_utility
from chat.ChatHandler import ChatHandler

class FlockConsumer(AsyncWebsocketConsumer):
    chat = ChatHandler()

    async def connect (self):
        """ What to run when a new connection is received """

        user_db = self.scope['user']

        if user_db.is_authenticated:
            await self.accept()
            self.user = await cfg.get_user(user_db.id, user_db = user_db)
            self.user.socket_l.append(self)

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
                module = getattr(self, module)
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
                'thread_d': self.user.thread_d,
            }
        }

    async def typing (self, thread_id = None, clear = False):
        thread = await self.chat.get_thread(thread_id)
        if thread:
            await thread.typing(self.user, clear)

    async def message (self, thread_id = None, to_user_id = None, text = None):
        if to_user_id:
            to_user = await cfg.get_user(to_user_id)
            thread_id = user_utility.merge_uuid(self.user.id, to_user.id)
        else:
            thread_id = uuid.UUID(thread_id)
            to_user = None

        thread = await self.chat.get_thread(thread_id)

        if not thread and to_user:
            label = "{user}"
            members = [self.user.db_entry, to_user.db_entry]
            thread = await self.chat.create_thread(label, members, thread_id)

        if thread:
            await thread.send_message(self.user, text)

    async def thread (self, thread_id = None, user_id = None):
        if user_id:
            thread_id = user_utility.merge_uuid(self.user.id, user_id)
        else:
            thread_id = uuid.UUID(thread_id)

        thread = await self.chat.get_thread(thread_id)
        if thread:
            history = await thread.read_from_datastore()
        else:
            history = []

        if thread:
            return {"thread": history}

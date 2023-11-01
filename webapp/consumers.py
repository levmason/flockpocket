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
            message = {
                'name': message,
                'options': {}
                }

        # Starts a new task to handle the message
        aio.create_task(self.handle_message(message))

    async def handle_message (self, message):
        """Handles the message"""

        # Finds the correct API handler function
        api_fn_name = message["name"]
        api_fn = getattr(self, api_fn_name)

        # Extracts the options from the query
        options = message.get("options", {})

        try:
            # Run the API handler function (the ** converts the dictionary into keyword arguments)
            response = await api_fn(**options)

            # If there's a response, then send it to the browser
            if response:
                await self.respond(response)

        except Exception as e:
            log.debug(traceback.format_exc())
            await self.error(str(e))

    async def ui_config (self):
        return {
            'name': 'ui_config',
            'options': {
                'user_id': str(self.user.id),
                'user_d': {str(x):y.as_dict() for x,y in cfg.user_d.items() if y.is_active},
                'thread_d': self.user.thread_d,
            }
        }

    async def threads (self):
        thread_d = {}
        async for thread in ChatThread_db.objects.filter(members__id=self.user.id):
            label = thread.label
            if label == "{user}":
                for member in thread.members.all():
                    if member.id != self.user.id:
                        label = f"{member.first_name} {member.last_name}"

            thread_d[str(thread.id)] = {
                "label": label
            }

        return thread_d

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
            return {
                "name": "thread",
                "options": history,
            }

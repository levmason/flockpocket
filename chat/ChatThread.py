import time
import uuid
import aiofiles
from common import config as cfg
from common import crypto
from common import logger as log

class ChatThread:
    def __init__(self, db_entry = None):
        self.db_entry = db_entry
        self.id = db_entry.id
        self.label = db_entry.label
        self.path = f"{cfg.chat_dir}/{self.id}"
        self.timestamp = 0
        self.user_l = []
        self.message_l = None

    async def set_users (self):
        async for user_db in self.db_entry.members.all():
            user = await cfg.get_user(user_db.id)
            self.user_l.append(user)

    def make_message (self, from_user, text):
        return {
            'timestamp': time.time(),
            'user': str(from_user.id),
            'text': text
        }

    async def send_message (self, from_user, text):
        # create the message object
        message = self.make_message(from_user, text)

        # send the message to the datastore
        await self.push_to_datastore(message)

        # set the thread timestamp
        self.timestamp = message['timestamp']

        for user in self.user_l:
            await user.push_message(self, message)

    async def typing (self, typing_user, clear):
        """ send <user> typing notifications to users """
        for user in self.user_l:
            await user.push_typing(self, typing_user, clear)

    #
    # Interface to the datastore
    #
    async def push_to_datastore (self, message):
        await cfg.redis.ds_push({
            "name": "store_message",
            "options": {
                'thread_id': str(self.id),
                'message': message
            }
        })

    async def read_from_datastore (self):
        query = {
            'name': 'get_thread_history',
            'options': {
                'thread_id': str(self.id)
            }
        }
        return await cfg.redis.ds_query(query)

    #
    # Datastore functions
    #
    async def add_message (self, message):
        """ add a message to the history cache """

        if self.message_l is None:
            await self.read()

        self.message_l.append(message)

    async def get_history (self):
        """ get the chat history (disk or cache) """

        if self.message_l is None:
            await self.read()

        return self.message_l

    async def write (self):
        """ write the chat history to the disk """

        data = crypto.encode(self.message_l)
        async with aiofiles.open(self.path, "wb") as f:
            await f.write(data)

    async def read (self):
        """ read the chat history from the disk """

        self.message_l = []

        t1 = time.time()
        try:
            async with aiofiles.open(self.path, "rb") as f:
                data = await f.read()
        except FileNotFoundError:
            return

        t2 = time.time()
        if (t2-t1) > 1:
            log.debug("thread get took: %s" % (t2-t1))

        # decode the data
        data = crypto.decode(data)
        self.message_l = data

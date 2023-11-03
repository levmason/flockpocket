import time
from common import config as cfg
from common import logger as log

class ChatThread:
    def __init__(self, db_entry = None):
        self.db_entry = db_entry
        self.id = db_entry.id
        self.label = db_entry.label
        self.timestamp = 0
        self.user_l = []

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
    async def push_to_datastore (self, message):
        """ push message to the datastore """

        await cfg.redis.ds_push({
            "store_message": {
                'thread_id': str(self.id),
                'message': message
            }
        })

    async def read_from_datastore (self):
        """ read message history from datastore """

        query = {
            'get_thread_history': {
                'thread_id': str(self.id)
            }
        }
        return await cfg.redis.ds_query(query)

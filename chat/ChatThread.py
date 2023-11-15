import time
from common import config as cfg
from common import logger as log

class ChatThread:
    def __init__(self, user, config):
        self.user = user
        for key, val in config.items():
            setattr(self, key, val)

    async def init (self):
        self.user_s = [await cfg.get_user(x) for x in self.user_l]
        if self.type == 0:
            self.other_user = [x for x in self.user_s if x is not self.user][0]

    def as_dict (self):
        ret_d = {
            'type': self.type,
            'id': self.id,
            'user_l': list(self.user_s),
            'label': self.label,
            'timestamp': self.timestamp,
        }

        if self.other_user:
            ret_d['user'] = str(self.other_user.id)
            ret_d['label'] = f"{self.other_user.first_name} {self.other_user.last_name}"

    async def alert_users (self):
        for user in self.user_s:
            await user.push_thread(self)

    def make_message (self, from_user, text):
        now = time.time()
        self.timestamp = now
        return {
            'timestamp': now,
            'user': str(from_user.id),
            'text': text
        }

    async def send_message (self, from_user, text):
        # create the message object
        message = self.make_message(from_user, text)

        # send to other user sessions
        for user in self.user_s:
            await user.push_message(self, message)

        # send the message to the datastore
        await cfg.redis.ds_push({
            "chat.add_message": {
                'thread_id': self.id,
                'message': message
            }
        })

    async def send_like (self, from_user, message_idx):
        # set the thread timestamp
        self.timestamp = time.time()

        # send to other user sessions
        for user in self.user_s:
            await user.push_like(self, self.timestamp, from_user, message_idx)

        # send the message to the datastore
        await cfg.redis.ds_push({
            "chat.like_message": {
                'thread_id': self.id,
                'timestamp': self.timestamp,
                'user_id': str(from_user.id),
                'message_idx': message_idx
            }
        })

    async def typing (self, typing_user, clear):
        """
        send chat typing notifications to users
        """
        for user in self.user_s:
            await user.push_typing(self, typing_user, clear)

    async def read_history_from_datastore (self):
        """ read message history from datastore """

        return await cfg.redis.ds_query({
            'chat.get_history': {
                'thread_id': self.id
            }
        })

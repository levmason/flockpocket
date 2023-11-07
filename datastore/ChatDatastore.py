import aiofiles

from common import config as cfg
from common import logger as log
from common import crypto

class ChatDatastore:
    def __init__(self):
        # thread cache
        self.thread_d = {}

    async def stop (self):
        for thread_id in self.thread_d.keys():
            await self.write(thread_id)

    async def add_message (self, thread_id, message):
        """ add a message to the history cache """

        thread = self.thread_d.get(thread_id)
        if not thread:
            thread = self.thread_d[thread_id] = await self.read(thread_id)

        thread.append(message)

    async def like_message (self, thread_id, user_id, message_idx):
        thread = self.thread_d.get(thread_id)
        message = thread[message_idx]

        if 'like_l' not in message:
            message['like_l'] = []

        if user_id in message['like_l']:
            message['like_l'].remove(user_id);
        else:
            message['like_l'].append(user_id);

    async def get_history (self, thread_id):
        """ get the chat history (disk or cache) """

        history = self.thread_d.get(thread_id)
        if history is None:
            self.thread_d[thread_id] = await self.read(thread_id)

        return self.thread_d.get(thread_id)

    async def write (self, thread_id):
        """ write the chat history to the disk """

        # find the filepath
        path = f"{cfg.chat_dir}/{thread_id}"
        message_l = self.thread_d[thread_id]
        data = crypto.encode(message_l)
        async with aiofiles.open(path, "wb") as f:
            await f.write(data)

    async def read (self, thread_id):
        """ read the chat history from the disk """

        # find the filepath
        path = f"{cfg.chat_dir}/{thread_id}"

        try:
            async with aiofiles.open(path, "rb") as f:
                data = await f.read()
            # decode the data
            return crypto.decode(data)
        except FileNotFoundError: pass

        return []


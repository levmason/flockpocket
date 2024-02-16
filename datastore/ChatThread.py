import aiofiles
from common import crypto
from common import config as cfg
from common import utility

class ChatThread:
    def __init__(self, db_entry = None):
        self.db_entry = db_entry
        self.id = str(db_entry.id)
        self.type = db_entry.type
        self.label = db_entry.label
        self.length = db_entry.length
        self.seen = db_entry.seen
        self.timestamp = utility.datetime_to_epoch(db_entry.timestamp)
        self.user_s = set()
        self.key = None
        self.message_l = None

    def as_dict (self):
        return {
            'type': self.type,
            'id': self.id,
            'user_l': list(self.user_s),
            'label': self.label,
            'timestamp': self.timestamp,
            'length': self.length,
            'seen': self.seen,
        }

    async def init (self):
        # set the user list
        async for user_db in self.db_entry.members.all():
            self.user_s.add(str(user_db.id))

        # set the key (for user type)
        if self.type == 0:
            self.key = '/'.join(sorted(self.user_s))

    async def add_message (self, message):
        history = await self.get_history()
        self.timestamp = message['timestamp']
        history.append(message)
        # increase the thread length
        self.length += 1
        # auto see
        await self.seen_message(message['user'], self.length)

    async def like_message (self, timestamp, user_id, message_idx):
        # update the timestamp
        self.timestamp = timestamp

        message = self.message_l[message_idx]

        if 'like_l' not in message:
            message['like_l'] = []

        if user_id in message['like_l']:
            message['like_l'].remove(user_id)
        else:
            message['like_l'].append(user_id)

    async def seen_message (self, user_id, message_idx):
        self.seen[user_id] = message_idx

    async def get_history (self):
        """ get the chat history (disk or cache) """

        if self.message_l is None:
            self.message_l = await self.read_history()

        # set the length
        self.length = len(self.message_l)

        return self.message_l

    async def read_history (self):
        """ read the chat history from the disk """

        # find the filepath
        path = f"{cfg.chat_dir}/{self.id}"

        try:
            async with aiofiles.open(path, "rb") as f:
                data = await f.read()
            # decode the data
            return crypto.decode(data)
        except FileNotFoundError: pass

        return []

    async def write_history (self):
        """ write the chat history to the disk """

        if self.message_l is not None:
            # find the filepath
            path = f"{cfg.chat_dir}/{self.id}"
            data = crypto.encode(self.message_l)
            async with aiofiles.open(path, "wb") as f:
                await f.write(data)

    async def stop (self):
        """ elegant shutdown """

        await self.write_history()

        self.db_entry.length = self.length
        timestamp_dt = utility.epoch_to_datetime(self.timestamp)
        if timestamp_dt != self.db_entry.timestamp:
            self.db_entry.timestamp = timestamp_dt

        await self.db_entry.asave()

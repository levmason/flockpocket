

from common.models import ChatThread as ChatThread_db
from .ChatThread import ChatThread

class ChatDatastore:
    def __init__(self):
        # thread cache
        self.thread_d = {}
        self.user_thread_d = {}

    async def init (self):
        async for thread_db in ChatThread_db.objects.all():
            await self.add_thread(thread_db)

    async def add_thread (self, thread_db):
        """ Add a thread to the cache """

        thread = ChatThread(thread_db)
        await thread.init()
        self.thread_d[str(thread.id)] = thread
        if thread.type == 0:
            self.user_thread_d[thread.key] = thread

        return thread

    async def stop (self):
        """ gracefully shutdown the (writing everything """

        for thread_id, thread in self.thread_d.items():
            await thread.stop()

    async def get_threads_for_user (self, user_id):
        """ get all threads for a specified user """

        thread_d = {}
        for thread_id, thread in self.thread_d.items():
            if user_id in thread.user_s:
                thread_d[thread_id] = thread.as_dict()

        return thread_d

    async def create_thread (self, label = "", members = [], type = 0):
        """ create a new thread """

        # make sure there aren't redundant members
        if len(members) > len(set(members)):
            return

        thread_db = await ChatThread_db.objects.acreate(
            type = type,
            label = label,
        )

        await thread_db.members.aset(members)
        await thread_db.asave()

        thread = await self.add_thread(thread_db)
        return thread.as_dict()

    async def add_message (self, thread_id, message):
        """ add a message to the history cache """
        thread = self.thread_d.get(thread_id)
        await thread.add_message(message)

    async def seen_message (self, thread_id, user_id, message_idx):
        """ track when a user seees a message """
        thread = self.thread_d.get(thread_id)
        await thread.seen_message(user_id, message_idx)

    async def like_message (self, thread_id, timestamp, user_id, message_idx):
        """ like a message """
        thread = self.thread_d.get(thread_id)
        await thread.like_message(timestamp, user_id, message_idx)

    async def get_history (self, thread_id):
        """ get the chat history (disk or cache) """

        thread = self.thread_d.get(thread_id)
        return await thread.get_history()

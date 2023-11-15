import uuid
import aiofiles

from django.core.exceptions import ObjectDoesNotExist

from common import config as cfg
from common import logger as log
from common import crypto
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

    #
    # threads
    async def get_threads_for_user (self, user_id):
        """ get all threads for a specified user """

        thread_d = {}
        log.debug(user_id)
        for thread_id, thread in self.thread_d.items():
            if user_id in thread.user_s:
                thread_d[thread_id] = thread.as_dict()

        return thread_d

    # async def get_thread (self, thread_id, thread_db = None):
    #     """ Retrieve thread details from the database or cache """

    #     # check the cache
    #     thread = self.thread_d.get(thread_id)
    #     if not thread:
    #         if not thread_db:
    #             # see if we have one in the database
    #             try:
    #                 thread_db = await ChatThread_db.objects.aget(pk=uuid.UUID(thread_id))
    #             except ObjectDoesNotExist:
    #                 thread_db = None

    #         # initialize the handler object
    #         if thread_db:
    #             thread = ChatThread(thread_db)
    #             await thread.init()
    #             self.cache(thread)

    #     return thread

    # async def get_user_thread (self, users, create=False):
    #     """ Get a user thread """

    #     log.debug("get_user_thread")
    #     key = '/'.join(sorted(users))

    #     # check the cache
    #     thread = self.user_thread_d.get(key)
    #     if not thread:
    #         log.debug("NOOOOOO")
    #         users = [uuid.UUID(x) for x in users]
    #         # see if we have one in the database

    #         # match a user:user thread
    #         qs = ChatThread_db.objects.filter(type=0)
    #         # match both users
    #         qs = qs.filter(members__id=users[0]).filter(members__id=users[1])
    #         async for thread_db in qs:
    #             thread = ChatThread(thread_db)
    #             await thread.init()
    #             self.cache(thread)
    #             # there should only be one
    #             break

    #         # initialize the handler object
    #         if not thread and create:
    #             thread = await self.create_thread("", members=users)

    #     return thread.as_dict()

    async def create_thread (self, label = "", members = [], type = 0):

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

    #
    # messages
    async def add_message (self, thread_id, message):
        """ add a message to the history cache """
        thread = self.thread_d.get(thread_id)
        await thread.add_message(message)

    async def like_message (self, thread_id, timestamp, user_id, message_idx):
        """ like a message """
        thread = self.thread_d.get(thread_id)
        await thread.like_message(timestamp, user_id, message_idx)

    async def get_history (self, thread_id):
        """ get the chat history (disk or cache) """

        thread = self.thread_d.get(thread_id)
        return await thread.get_history()

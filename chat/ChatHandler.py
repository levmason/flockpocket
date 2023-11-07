import uuid
from django.core.exceptions import ObjectDoesNotExist

from user import utility as user_utility
from common import logger as log
from common import config as cfg

from common.models import ChatThread as ChatThread_db
from .ChatThread import ChatThread

class ChatHandler:
    def __init__(self, user):
        self.user = user
        self.user_thread_d = {}

    async def get_thread (self, thread_id):
        """ Retrieve thread details from the database or cache """

        # check the cache
        thread = cfg.thread_d.get(thread_id)
        if not thread:
            # see if we have one in the database
            try:
                thread_db = await ChatThread_db.objects.aget(pk=thread_id)
            except ObjectDoesNotExist:
                thread_db = None

            # initialize the handler object
            if thread_db:
                cfg.thread_d[thread_id] = thread = ChatThread(thread_db)
                await thread.set_users()

        return thread

    async def get_user_thread (self, user_id, create=False):
        """ Get a user thread """

        # check the cache
        thread = self.user_thread_d.get(user_id)
        if not thread:
            user = await cfg.get_user(user_id)

            # see if we have one in the database
            thread_db = None
            for thread_id, entry in cfg.thread_d.items():
                if entry.db_entry.type == 0 and entry.user_s == {self.user, user}:
                    thread = entry
                    break

            # initialize the handler object
            if not thread and create:
                thread = await self.create_thread("", user=user)

        return thread

    async def create_thread (self, label = "", members = None, user = None):
        if user:
            members = [self.user.db_entry, user.db_entry]
            type = 0
        else:
            type = 1

        # make sure there aren't redundant members
        if len(members) > len(set(members)):
            return

        thread_db = await ChatThread_db.objects.acreate(
            type = type,
            label = label,
        )

        await thread_db.members.aset(members)
        await thread_db.asave()

        thread = ChatThread(thread_db)
        await thread.set_users()
        await thread.alert_users()

        # remember
        cfg.thread_d[thread_db.id] = thread
        if user:
            self.user_thread_d[user.id] = thread

        return thread

    async def get_thread_history (self, thread_id = None, user_id = None):
        """ get the thread history from the datastore """

        history = []

        if thread_id:
            thread_id = uuid.UUID(thread_id)
        if user_id:
            user_id = uuid.UUID(user_id)

        # get the thread
        if user_id:
            thread = await self.get_user_thread(user_id)
        else:
            thread = await self.get_thread(thread_id)

        # read the chat history
        if thread:
            history = await thread.read_from_datastore()

        if thread:
            return {
                "thread": {
                    'id': str(thread.id),
                    'message_l': history
                }
            }

    async def send_typing (self, thread_id = None, clear = False):
        """ send the typing indicator signal """

        thread = await self.get_thread(thread_id)
        if thread:
            await thread.typing(self.user, clear)

    async def send_like (self, thread_id = None, message_idx = None):

        thread = await self.get_thread(thread_id)
        if thread:
            await thread.send_like(self.user, message_idx)

    async def send_message (self, thread_id = None, user_id = None, text = None):
        """ send a new message """

        if user_id:
            user_id = uuid.UUID(user_id)
            thread = await self.get_user_thread(user_id, create=True)
        else:
            thread_id = uuid.UUID(thread_id)
            thread = await self.get_thread(thread_id)

        if thread:
            await thread.send_message(self.user, text)

from django.core.exceptions import ObjectDoesNotExist

from common.models import ChatThread as ChatThread_db
from user import utility as user_utility
from common import logger as log
from common import config as cfg

from .ChatThread import ChatThread

class ChatHandler:
    def __init__(self):
        # thread cache
        self.thread_d = {}

    async def get_thread (self, thread_id):
        """ Retrieve thread details from the database or cache """

        # check the cache
        thread = self.thread_d.get(thread_id)
        if not thread:
            # see if we have one in the database
            try:
                thread_db = await ChatThread_db.objects.aget(pk=thread_id)
            except ObjectDoesNotExist:
                thread_db = None

            # initialize the handler object
            if thread_db:
                self.thread_d[thread_id] = thread = ChatThread(thread_db)
                await thread.set_users()

        return thread

    async def create_thread (self, label, members, id=None):
        try:
            # make sure there aren't redundant members
            if len(members) > len(set(members)):
                return

            thread_db = await ChatThread_db.objects.acreate(
                id = id,
                label = label,
            )

            await thread_db.members.aset(members)
            await thread_db.asave()

            self.thread_d[id] = thread = ChatThread(thread_db)
            await thread.set_users()

            for user in thread.user_l:
                user.add_thread(thread)
                entry = user.thread_d[str(thread.id)]
                await user.push({
                    "name": "new_thread",
                    "options": {
                        "id": str(thread.id),
                        "label": entry['label'],
                    }
                })

            return thread
        except Exception as e:
            log.debug(e)

    async def read_thread (self, thread_id):
        thread = await self.get_thread(thread_id)
        return await thread.get_history()

    async def stop (self):
        for thread_id, thread in self.thread_d.items():
            await thread.write()

    #
    # Websocket handler functions
    #

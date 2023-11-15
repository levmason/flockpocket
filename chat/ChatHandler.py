from common import logger as log
from common import config as cfg

from .ChatThread import ChatThread

class ChatHandler:

    def __init__(self, user):
        self.user = user
        self.thread_d = {}
        self.user_thread_d = {}

    async def add_thread (self, thread_cfg):
        thread = ChatThread(self.user, thread_cfg)
        await thread.init()

        self.thread_d[thread.id] = thread
        if thread.other_user:
            self.user_thread_d[str(thread.other_user.id)] = thread

    async def get_thread (self, thread_id = None):
        """ Retrieve thread details from the database or cache """
        # check the cache
        thread = self.thread_d.get(thread_id)
        if not thread:
            # see if we have one in the datastore
            thread_cfg = await cfg.redis.ds_query({
                'chat.get_thread': {
                    'thread_id': str(thread_id),
                }
            })

            # initialize the handler object
            if thread_cfg:
                self.thread_d[thread_id] = thread = ChatThread(thread_cfg)
                await thread.init()

        return thread

    async def get_user_thread (self, user_id = None, create=False):
        """ Get a user thread """

        users = [str(self.user.id), str(user_id)]
        key = '/'.join(sorted(users))

        # check the cache
        thread = self.user_thread_d.get(key)
        if not thread:
            # see if we have one in the datastore
            thread_cfg = await cfg.redis.ds_query({
                'chat.get_user_thread': {
                    'users': users,
                    'create': create
                }
            })

            # initialize the handler object
            if thread_cfg:
                self.thread_d[thread_cfg['id']] = thread = ChatThread(thread_cfg)
                await thread.init()
                if thread_cfg.get('created'):
                    log.debug("CREATED")
                    await thread.alert_users()

        return thread

    async def get_thread_history (self, thread_id = None, user_id = None):
        """ get the thread history from the datastore """

        # get the thread
        if user_id:
            thread = await self.get_user_thread(user_id)
        else:
            thread = await self.get_thread(thread_id)

        if thread:
            # read the chat history
            return {
                "thread": {
                    'id': str(thread.id),
                    'message_l': await thread.read_history_from_datastore()
                }
            }

    async def get_threads_for_user (self):
        thread_d = await cfg.redis.ds_query({
            'chat.get_threads_for_user': {
                'user_id': str(self.user.id)
            }
        })

        # for user threads, remove the other user
        for thread_id, thread_cfg in thread_d.items():
            await self.add_thread(thread_cfg)

        return [x.as_dict() for x in self.thread_d]

    async def send_message (self, thread_id = None, user_id = None, text = None):
        """ send a new message """

        if user_id:
            thread = self.user_thread_d[user_id]
        else:
            thread = self.thread_d[thread_id]

        if thread:
            await thread.send_message(self.user, text)

    async def send_typing (self, thread_id = None, clear = False):
        """ send the typing indicator signal """

        if user_id:
            thread = self.user_thread_d[user_id]
        else:
            thread = self.thread_d[thread_id]

        if thread:
            await thread.typing(self.user, clear)

    async def send_like (self, thread_id = None, message_idx = None):

        thread = self.thread_d[thread_id]
        if thread:
            await thread.send_like(self.user, message_idx)

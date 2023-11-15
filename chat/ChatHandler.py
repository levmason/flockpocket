from common import logger as log
from common import config as cfg

from .ChatThread import ChatThread

class ChatHandler:

    def __init__(self, user):
        self.user = user
        self.thread_d = {}
        self.user_thread_d = {}

    def as_dict (self):
        return {x:y.as_dict() for x,y in self.thread_d.items()}

    async def add_thread (self, thread_cfg):
        thread = ChatThread(self.user, thread_cfg)
        await thread.init()

        self.thread_d[thread.id] = thread
        if thread.other_user:
            self.user_thread_d[str(thread.other_user.id)] = thread

        return thread

    async def get_thread_history (self, thread_id = None):
        """ get the thread history from the datastore """

        # get the thread
        thread = self.thread_d.get(thread_id)

        if thread:
            # read the chat history
            return {
                "thread": {
                    'id': thread_id,
                    'message_l': await thread.read_history_from_datastore()
                }
            }

    async def get_threads (self):
        """
        Ask the datastore for all of the threads including this user
        """

        thread_d = await cfg.redis.ds_query({
            'chat.get_threads_for_user': {
                'user_id': str(self.user.id)
            }
        })

        # for user threads, remove the other user
        for thread_id, thread_cfg in thread_d.items():
            await self.add_thread(thread_cfg)

        return self.as_dict()

    async def send_message (self, thread_id = None, user_id = None, text = None):
        """ send a new message """

        if thread_id:
            thread = self.thread_d.get(thread_id)
        elif user_id:
            # automatically create a user thread
            thread_cfg = await cfg.redis.ds_query({
                'chat.create_thread': {
                    'label': "",
                    'members': [str(self.user.id), user_id],
                    'type': 0,
                }
            })
            thread = await self.add_thread(thread_cfg)

            # send the new thread to user sessions
            for user in thread.user_s:
                await user.push_thread(thread_cfg)

        # send the message
        if thread:
            await thread.send_message(self.user, text)

    async def send_typing (self, thread_id = None, clear = False):
        """ send the typing indicator signal """

        thread = self.thread_d.get(thread_id)
        if thread:
            await thread.typing(self.user, clear)

    async def send_like (self, thread_id = None, message_idx = None):

        thread = self.thread_d.get(thread_id)
        if thread:
            await thread.send_like(self.user, message_idx)

from common.models import ChatThread as ChatThread_db
from chat.ChatThread import ChatThread
from common import aio
from common import logger as log
from common import config as cfg

class User:
    fields = ['id', 'email', 'first_name', 'last_name', 'is_active', 'details']

    def __init__(self, db_entry):
        self.socket_l = []
        self.thread_d = {}
        self.update(db_entry)

    def update (self, db_entry):
        self.db_entry = db_entry

        for field in self.fields:
            val = getattr(db_entry, field)
            setattr(self, field, val)

    def as_dict (self):
        ret = {
            'id': str(self.id),
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": f"{self.first_name} {self.last_name}",
        }
        ret.update(self.details)
        return ret

    async def push (self, msg):
        task_l = []
        for socket in self.socket_l:
            task_l.append(socket.respond(msg))

        await aio.gather(task_l)

    async def add_thread (self, thread, push=True):
        user_id = None
        if thread.db_entry.type == 0:
            for user in thread.user_s:
                if user is not self:
                    user_id = str(user.id)
                    break

        entry = {
            "id": str(thread.id),
            "user": user_id,
            "label": thread.label,
        }

        # add to our dict
        self.thread_d[str(thread.id)] = entry

    def get_threads (self):
        for id, entry in self.thread_d.items():
            entry['timestamp'] = cfg.get_thread(id).timestamp;

        return self.thread_d

    async def push_thread (self, thread):
        await self.push({
            "new_thread": self.thread_d[str(thread.id)]
        })

    #
    # Websockets push functions
    async def push_typing (self, thread, user, clear):
        if user is not self:
            await self.push(
                {
                    "typing": {
                        "thread": str(thread.id),
                        "user": str(user.id),
                        "clear": clear,
                    }
                }
            )

    async def push_like (self, thread, user, message_idx):
        await self.push(
            {
                "like": {
                    "thread": str(thread.id),
                    "user": str(user.id),
                    "message_idx": message_idx,
                }
            }
        )

    async def push_message (self, thread, message):
        await self.push(
            {
                "message": {
                    'message': message,
                    'thread': str(thread.id)
                }
            }
        )

    async def push_user (self, user):
        await self.push(
            {
                "user": user
            }
        )

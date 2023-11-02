from common.models import ChatThread as ChatThread_db
from chat.ChatThread import ChatThread
from common import aio
from common import logger as log

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

    async def get_threads (self):
        self.thread_d = {}
        async for thread_db in ChatThread_db.objects.filter(members__id=self.id):
            thread = ChatThread(thread_db)
            await thread.set_users()
            self.add_thread(thread)

    def add_thread (self, thread):
        label = thread.label
        if label == "{user}":
            for user in thread.user_l:
                if user is not self:
                    label = f"{user.first_name} {user.last_name}"

        self.thread_d[str(thread.id)] = {
            "id": str(thread.id),
            "label": label
        }

    #
    # Websockets push functions
    async def push_message (self, message):
        await self.push(
            {
                "name": "message",
                "options": message
            }
        )

    async def push_user (self, user):
        await self.push(
            {
                "name": "user",
                "options": user
            }
        )

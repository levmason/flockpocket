from common import aio
from common import logger as log
from common import config as cfg

from common.apns_push_notifications import pushiOSMessage

class User:
    fields = ['id', 'email', 'first_name', 'last_name', 'is_active', 'details', 'ios_push_notification_token']

    def __init__(self, db_entry):
        self.socket_l = []
        self.update(db_entry)
        self.active = False

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
            "active": self.active,
        }
        ret.update(self.details)
        return ret

    def check_active (self):
        """ check if this user is active on any of it's sockets """
        return any([x.active for x in self.socket_l])

    def add_household_link (self, other_user, relationship):
        pass

    async def push (self, msg):
        """ push messages to all websocket sessions """

        task_l = []
        for socket in self.socket_l:
            task_l.append(socket.respond(msg))

        await aio.gather(task_l)

    #
    # Websockets push functions
    async def push_thread (self, thread_cfg):
        for socket in self.socket_l:
            thread = await socket.chat.add_thread(thread_cfg)

        await self.push({
            "new_thread": thread.as_dict()
        })

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

    async def push_like (self, thread, timestamp, user, message_idx):
        await self.push(
            {
                "like": {
                    "thread": str(thread.id),
                    "timestamp": timestamp,
                    "user": str(user.id),
                    "message_idx": message_idx,
                }
            }
        )

    async def push_seen (self, thread, user, message_idx):
        if user is not self:
            await self.push(
                {
                    "seen": {
                        "thread": str(thread.id),
                        "user": str(user.id),
                        "message_idx": message_idx,
                    }
                }
            )

    async def push_message (self, thread, message):
        if self.ios_push_notification_token != "":
            pushiOSMessage(
                push_token=self.ios_push_notification_token,
                message=message,
                thread=thread
            )

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

    async def push_active (self, user_id, active):
        await self.push(
            {
                "active": {
                    'user_id': user_id,
                    "active": active
                }
            }
        )

from datetime import timedelta
from django.utils import timezone

from common import aio
from common import config as cfg
from common import logger as log
from common.PeriodicTask import PeriodicTask
from common.models import Invite as Invite_db

class UserManager:
    def __init__(self):
        self.task_l = []
        self.task_cfg = {
            'purge_invites': {
                'interval': 600,
            },
        }

    async def start (self):
        # start all the periodic tasks
        for name, t in self.task_cfg.items():
            action = getattr(self, name)
            name = "datastore/%s" % name
            task = PeriodicTask(name=name,
                                interval=t.get('interval'),
                                action=action)
            await task.start(t.get('delay'), t.get('start_time'))
            self.task_l.append(task)


    async def stop (self):
        # stop all periodic tasks
        stop_l = [task.stop() for task in self.task_l]
        # stop all datastores
        stop_l += [db.stop() for db in self.db_d.values()]

        await aio.gather(stop_l)

    async def purge_invites (self):
        cutoff = timezone.now() - timedelta(cfg.invite_timeout)
        await Invite_db.objects.filter(timestamp__lt=cutoff).adelete()

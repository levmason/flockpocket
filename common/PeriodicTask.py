import time
import asyncio
from . import logger as log

class PeriodicTask(object):
    def __init__ (self, name, interval, action, args=(), kwargs={}, concurrent=False, quiet=False):
        self.name = name # task name
        self.interval = interval # The period interval
        self.timestamp = 0 # The timestamp for the current run
        self.next_timestamp = 0 # The timestamp for the next run
        self.action = action # function ptr
        self.args = args # function arguments
        self.kwargs = kwargs # keyword arguments
        self.task = None # keep track of the task so we can cancel it
        self.concurrent = concurrent
        self.quiet = quiet
        self.iterations = 0
        self.missed_iterations = 0
        self.max_timer = 0 # time the periodic function

    async def start (self, delay=None, start_time=None):
        """ Start the periodic task """

        now = time.time()
        if start_time and start_time > now:
            delay = start_time - now

        self.task = asyncio.create_task(self.periodic(delay))

    async def stop (self):
        """ Stop the periodic task """
        self.task.cancel()

    async def periodic (self, delay = None):
        """
        This is the function that's run periodically. It schedules the next
        occurence and then runs the desired action function.
        """

        # wait to start
        if delay:
            await asyncio.sleep(delay)
        self.next_timestamp = time.time()

        while True:
            self.timestamp = self.next_timestamp
            self.next_timestamp += self.interval

            #
            # run the action
            if self.concurrent:
                asyncio.create_task(self.run_action())
            else:
                await self.run_action()
            self.iterations += 1

            #
            # schedule next iteration
            delay = self.next_timestamp - time.time()
            if delay > 0:
                await asyncio.sleep(delay)
            else:
                if not self.quiet:
                    await log.warning("PeriodicTask %s is late! (%s seconds)" % (self.name, delay * -1), "system")

    async def run_action (self):
        try:
            start_time = time.time()
            await self.action(*self.args, **self.kwargs)
            self.max_timer = max(self.max_timer, time.time() - start_time)
        except Exception as e:
            await log.exception("Action failed for PeriodicTask: %s" % self.name, "system")

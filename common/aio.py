import asyncio
from twisted.internet import reactor
from . import config as cfg
from . import logger as log

# we use the reactor loop
loop = reactor._asyncioEventloop

def run (coroutine):
    """ run a async application """
    coroutine = run_wrapper(coroutine)
    loop.run_until_complete(coroutine)

def create_task (coro):
    return asyncio.create_task(coro)

async def run_wrapper(coroutine):
    """ helper for running async application """
    await cfg.init()
    await coroutine

async def gather (coro_l, concurrent = None):
    if concurrent:
        task_l = []
        pending_s = set()
        for coro in coro_l:
            # run the task
            task = asyncio.create_task(coro)
            # add to pending list
            pending_s.add(task)
            # track the task_l
            task_l.append(task)

            if len(pending_s) == concurrent:
                completed_s, pending_s = await asyncio.wait(pending_s, return_when=asyncio.FIRST_COMPLETED)

        # wait for the remainder
        if pending_s:
            await asyncio.wait(pending_s, return_when=asyncio.ALL_COMPLETED)

        # gather the results
        results = []
        for task in task_l:
            try:
                result = task.result()
            except Exception as e:
                result = e
            results.append(result)

    else:
        results = await asyncio.gather(*coro_l, return_exceptions=True)

    return results

def find_fds (obj):
    l = dir(obj)
    for attr_name in l:
        try:
            attr = getattr(obj, attr_name)
            for a in ['fileno', 'i', 'o']:
                if hasattr(attr, a):
                    val = getattr(attr, a)
                    try:
                        val = val()
                    except: pass

                    print('/'.join([str(obj), attr_name, a, str(val)]))
        except Exception as e: pass

def get_fds ():
    fds = [
        loop._internal_fds,
        loop._selector.fileno(),
        loop._ssock.fileno(),
        loop._csock.fileno(),
        reactor.waker.i,
        reactor.waker.o,
    ]

    return fds

"""
This is a HACK because I can't get the twisted stuff to work in asyncio
"""
def set_ex (exception, err):
    exception['Error'] = err.getErrorMessage()

async def as_future (d):
    exception = {}
    # if we don't add this errback, then it never returns on failure
    d.addErrback(lambda x: set_ex(exception, x))

    response = await d.asFuture(loop)
    if exception:
        raise Exception(exception.get('Error'))

    return response

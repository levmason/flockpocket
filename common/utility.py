"""
File: utility.py

This module is used to house functions that are shared between other modules.
"""

import time
import datetime
import pytz
from django.utils import timezone
import json
from subprocess import getstatusoutput


from . import config as cfg
from . import logger as log

#
# Epoch/Datetime conversions
#epoch = datetime.datetime.fromtimestamp(0, pytz.UTC)
def datetime_to_epoch (dt, local=False, as_int=True):
    if local:
        ret = time.mktime(dt.timetuple())
    else:
        ret = dt.timestamp()

    if as_int:
        return int(ret)
    else:
        return ret

def epoch_to_datetime (ts, local=False, aware=True):
    if local:
        return datetime.datetime.fromtimestamp(ts, timezone.get_default_timezone())
    elif aware:
        return datetime.datetime.fromtimestamp(ts, pytz.UTC)
    else:
        return datetime.datetime.fromtimestamp(ts)

#
# Datetime fns
def datetime_same_hour (dt1, dt2):
    try:
        return (datetime_to_hour(dt1) == datetime_to_hour(dt2))
    except:
        return None

def datetime_to_hour (dt, next=False):
    ret = dt.replace(minute=0, second=0, microsecond=0)
    if next and ret != dt:
        ret += datetime.timedelta(0, 3600)
    return ret

def datetime_to_day (dt, next=False):
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)

#
# Epoch fns
def epoch_same_hour (ts1, ts2):
    try:
        return (epoch_to_hour(ts1) == epoch_to_hour(ts2))
    except:
        return None

def epoch_same_day (ts1, ts2):
    return (epoch_to_day(ts1) == epoch_to_day(ts2))

def epoch_to_hour (ts, next=False):
    ret = (ts//3600) * 3600
    if next and ret != ts:
        ret += 3600
    return ret

def epoch_to_day (ts, next=False):
    ret = (ts//86400) * 86400
    if next and ret != ts:
        ret += 86400
    return ret

def epoch_delta_str (ts1, ts2):
    """
    This function takes in a time string (sometime in the future),
    and returns the time delta between NOW and that time.
    (used to show time remaining on reservations)
    """

    WEEK = 604800
    DAY = 86400
    HOUR = 3600
    MINUTE = 60

    delta = ts2 - ts1

    weeks = delta / WEEK
    days = delta / DAY
    hours = delta / HOUR
    minutes = delta / MINUTE

    ret = ""
    if weeks >= 2:
        ret += "%.1f weeks" % weeks
    elif days >= 2:
        ret += "%.01f days" % days
    elif hours >= 1:
        ret += "%.1f hrs" % hours
    else:
        ret += "%.1f mins" % minutes

    return ret

def get_build_date ():
    # so we can do this from any directory
    git_args = "--git-dir=%s/.git --work-tree=%s/" % (cfg.proj_dir, cfg.proj_dir)

    # get the commit date
    command = "git %s show -s --format=%%ct" % git_args
    (code, result) = getstatusoutput(command)

    try:
        ret = int(result)
    except:
        ret = 0

    return ret


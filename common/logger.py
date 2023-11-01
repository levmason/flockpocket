import os
import logging

from . import config as cfg

logger = None
fh = None
log_file = None
signal = False

# remember previous settings
prev_filename = None
prev_debug_lvl = None

def init (filename = None, debug_lvl="critical", sync=True):
    global logger, fh

    debug_lvl = eval("logging." + debug_lvl.upper())

    # init the log directory
    log_dir = cfg.log_dir
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file = "%s/%s" % (log_dir, filename)

    # create logger
    #logger = logging.getLogger("main")
    logger = logging.getLogger("asyncio")


    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    # create formatter
    fmt = logging.Formatter(fmt = "%(asctime)s\t%(levelname)s/%(module)s\t%(message)s",
                            datefmt = "%Y-%m-%d_%H:%M:%S")

    #
    # create file handler
    fh = logging.handlers.RotatingFileHandler(log_file,
                                              maxBytes=100*1024,
                                              backupCount=5)
    # set log level
    fh.setLevel(logging.DEBUG)
    # add formatter to handler
    fh.setFormatter(fmt)
    # add handler to logger
    logger.addHandler(fh)


    #
    # create console handler
    ch = logging.StreamHandler()
    # set log level
    ch.setLevel(debug_lvl)
    # add handler to logger
    logger.addHandler(ch)

def debug (message):
    logger.debug(message)

def info (message):
    logger.info(message)

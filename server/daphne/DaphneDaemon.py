import os
import subprocess

from common import logger as log
from common import config as cfg

class DaphneDaemon():
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  cfg.get_pidfile('daphne')
        self.logfile = cfg.get_logfile('daphne')
        self.pidfile_timeout = 1
        self.interrupt = False
        self.app_name = "%s.asgi:application" % cfg.tool_name
        self.port = cfg.daphne_port

        bind = " -b 0.0.0.0 -p %s" % self.port

        self.app_args = (
            ''
            #+ "--root-path %s" % proj_dir
            + bind
            + " --websocket_timeout -1"
            #+ " --access-log %s" % self.logfile
            + " --verbosity 0"
            + " %s" % self.app_name
        )

    def run(self):
        try:
            os.environ["PYTHONPATH"] = cfg.proj_dir
            command = "daphne %s" % self.app_args
            log.debug(command)
            result = subprocess.run(
                command.split(),
                capture_output = True,
                text = True,
            )
            # show output
            if result.stdout:
                log.debug(result.stdout)
            if result.stderr:
                log.debug(result.stderr)
        except Exception as e:
            log.debug("error: %s" % e)

    def terminate(self, signal_number, stack_frame):
        (code, result) = subprocess.getstatusoutput("pkill -KILL daphne")
        self.interrupt = True


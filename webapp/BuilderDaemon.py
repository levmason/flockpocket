import time
import traceback
from subprocess import run
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from common import \
    config as cfg, \
    logger as log

class BuilderDaemon():
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.logfile = cfg.get_logfile('builder')
        self.pidfile_path =  cfg.get_pidfile('builder')
        self.pidfile_timeout = 1
        self.interrupt = False

    def run(self):
        watcher = CodeWatcher()
        observer = Observer()
        observer.schedule(watcher, "%s/webapp/" % cfg.proj_dir, recursive=True)
        try:
            observer.start()
            while not self.interrupt:
                time.sleep(1)
        except Exception as e:
            print(traceback.format_exc())
        finally:
            try:
                observer.stop()
            except:
                log.debug("exception in builder shutdown")
                log.debug(traceback.format_exc())

    def terminate(self, signal_number, stack_frame):
        self.interrupt = True

class CodeWatcher(FileSystemEventHandler):
    def __init__(self):
        self.builder_path = "%s/webapp" % cfg.proj_dir
        self.builder_command = "bash %s/build.sh -q" % self.builder_path

    def build (self):
        output = run(self.builder_command.split(), cwd=self.builder_path, capture_output=True)

    def on_modified (self, e):
        if not e.is_directory:
            self.build()


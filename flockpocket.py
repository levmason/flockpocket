#!/usr/bin/env python
"""
This file handles all CLI inputs
"""
import time
import os, sys
# initialize django
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flockpocket.settings")
# levy hack for strange import problem?
os.environ["PYTHON_EGG_CACHE"] = "/tmp/.python-eggs/"
django.setup()
from django.db import connection
from django.contrib.auth.models import User
import shutil, traceback
import time
from datetime import datetime
import argparse
import subprocess
from subprocess import getstatusoutput, Popen, PIPE
import re
import json
import yaml

import lockfile
import signal

from pkg.daemon import runner
from common import \
    utility, \
    aio, \
    textIO, \
    logger as log, \
    config as cfg

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

def OK (string):
    return OKGREEN + string + ENDC

def Fail (string):
    return FAIL + string + ENDC

def usage (command=None):
    """
    Return the usage string.

    The string will differ depending on the command.
    """
    # find the command argument, if one was entered
    if not command:
        try:
            command = args.command
        except NameError:
            pass

    # alter the usage message based on the command argument
    if command in ['stop', 'start', 'restart', 'kill']:
        return (
            "Usage: %s <action> [daemon]\n" % cfg.tool_name +
            "\n"
            "Description:\n"
            "    This command allows you to control %s daemons.\n" % cfg.tool_name +
            "\n"
            "Options:\n"
            "    <action>                  Options: start | stop | restart | kill\n"
            "    [daemon]                  Options: %s\n" % ' | '.join(cfg.services) +
            "                              Default: all\n"
            "                              Mutiple daemons can be chosen using commas...\n"
            "                              Example: start poller,db\n"
        )
    elif command == "log":
        return (
            "Usage: %s %s <log_file>\n" % (cfg.tool_name, command) +
            "\n"
            "Description:\n"
            "    This command will display the latest log file for a specified daemon.\n"
            "\n"
            "Options:\n"
            "    <log_file>                Options: %s | nugget_test | termserver\n" % ' | '.join(cfg.services) +
            "                              Default: poller\n"
            "    -t,--tail                 Watch the tail of the file.\n"
            "    -c,--clear                Clears all the associated log files.\n"
            )
    elif command == "install":
        return (
            "\n"
            "Usage: {0} {1} [opt]\n"
            "\n"
            "Description:\n"
            "    This will install {0} components/dependencies. If [opt]\n"
            "    isn't specified, the standard install will run, otherwise the\n"
            "    specific componant will be installed.\n"
            "\n"
            "Options:\n"
            "    [opt]       Currently only 'pmacct'\n"
            .format(cfg.tool_name, command))
    elif command == "update":
        return (
            "\n"
            "Usage: {0} {1}\n"
            "\n"
            "Description:\n"
            "    Update the {0} tool to the latest version.\n"
            "\n"
            "Options:\n"
            "    -l,--local      If updating from a local repo, give the path (otherwise origin is used)\n"
            "    -i,--install    Install the tool after updating\n"
            "    -r,--restart    Restart the tool after updating\n"
            "\n"
            "Examples:\n"
            "    {0} {1} -ir\n"
            .format(cfg.tool_name, command))
    else:
        return (
            "usage: {0} <command> [options]\n"
            "For detailed help about commands, try '{0} <command> --help'\n"
            "\n"
            "Daemon Control\n"
            "    <action> [daemon]             Actions = start | stop | restart | kill\n"
            "Logs\n"
            "    log <opt>                     Display {0} log files.\n"
            "Other\n"
            "    status                        Show up/down status of {0} services\n"
            "    update                        Download the latest code\n"
            "    install [opt]                 Install {0} components\n"
            "    clear_config                  Clear all {0} configurations\n"
            "    clear_logs                    Clear all {0} logs\n"
            "    clear_data                    Clear all {0} data\n"
            "    clear_db                      Clear all {0} data/configs/passwords (everything)\n"
            "\n"
            "Universal Options:\n"
            "    --help                        Show help information\n"
            "    --version                     Show version information\n"
            .format(cfg.tool_name))

def usage_exit (string="", err_code=0):
    """
    Print usage information, then exit.

    Args:
        string -- the error string (reason for exiting)
    """

    if string:
        sys.stderr.write("\n%s\n\n" % string)
        err_code = 1

    print(usage())
    sys.exit(err_code)

def clear_config ():
    if textIO.prompt("This will delete all current configs! Continue?"):
        cfg.clear_config()

def clear_logs ():
    if textIO.prompt("This will delete all %s logs! Continue?" % cfg.tool_name):
        cfg.db.clear_logs()

def clear_data ():
    if textIO.prompt("This will delete all %s data! Continue?" % cfg.tool_name):
        cfg.db.clear_data()

def clear_db ():
    if textIO.prompt("This will delete all %s configs/data! Continue?" % cfg.tool_name):
        cfg.db.clear_db()

def update ():
    git_args = "--git-dir=%s/.git --work-tree=%s/" % (cfg.proj_dir, cfg.proj_dir)

    # get the build_date
    build_date_A = utility.get_build_date()

    # see if we're updating from a local repo
    if args.repo:
        # see if it's a tar file
        if '.tar' not in args.repo.lower():
            repo = args.repo
        else:
            repo_tmp_dir = '/tmp/.flockpocket.repo/'

            # we'll need to extract the tar file
            if args.repo.lower().endswith(".tar.gz"):
                tar_args = '-xzf'
            elif args.repo.lower().endswith(".tar"):
                tar_args = '-xf'
            else:
                print("File type not supported (must be .tar or .tar.gz)")
                return

            # clean the directory
            shutil.rmtree(repo_tmp_dir, ignore_errors=True)
            os.makedirs(repo_tmp_dir)

            # extract the tar file
            command = 'tar %s %s -C %s' % (tar_args, args.repo, repo_tmp_dir)
            (code, result) = getstatusoutput(command)
            if code:
                print(result)
                return

            # find the repo directory
            command = "dirname `find %s -name .git | head -n 1`" % repo_tmp_dir
            (code, result) = getstatusoutput(command)
            if code:
                print(result)
                return

            repo = result

        fetch_command = 'git %s fetch %s' % (git_args, repo)
        reset_command = 'git %s reset --hard FETCH_HEAD' % git_args
    else:
        fetch_command = 'git %s fetch origin' % git_args
        reset_command = 'git %s reset --hard origin/v3' % git_args

    # fetch
    (code, result) = getstatusoutput(fetch_command)
    if code:
        print(result)
        return

    # reset head
    (code, result) = getstatusoutput(reset_command)
    if code:
        print(result)
        return

    # get the build date
    build_date_B = utility.get_build_date()

    # did we update?
    if build_date_A != build_date_B:
        print("Update Successful :)")
    else:
        print("No Updates Found :(")
        return

    # set the permissions
    command = '%s/install/misc_install.sh' % cfg.proj_dir
    subprocess.call(command.split())

    # install
    if args.install:
        command = '%s/install/install.py' % cfg.proj_dir
        subprocess.call(command.split())

    # restart
    if args.restart:
        command = '%s restart' % cfg.tool_name
        subprocess.call(command.split())

install_d = {}

def install ():
    name = args.option
    if name:
        try:
            script_name = install_d[name]
        except KeyError:
            script_name = name + '.sh'

        command = "%s/install/%s" % (cfg.proj_dir, script_name)
    elif args.full:
        command = '%s/install/install.py -f' % cfg.proj_dir
    else:
        command = '%s/install/install.py' % cfg.proj_dir

    subprocess.call(command.split())

def status ():
    # check if services are running
    l = sorted(cfg.services)
    for d in l:
        if getattr(cfg, "%s_enabled" % d, True):
            sys.stdout.write("%s: " % d)
            if daemon_is_running(d):
                print(OK("UP"))
            else:
                print(Fail("DOWN"))

def service_handler (action = None, services = cfg.services):
    action = action or args.command
    if args.option:
        services = args.option.split(',') or services

    if len(services) == 1:
        service = services[0]

        # handle the "server" alias
        if service == 'server':
            service = "daphne"

        daemon_handler(action=action, service=service)

        if action in ["start", "restart"] and args.tail:
            show_log(service)

        return

    # informative output
    output_str = "%sing services..." % action.capitalize()
    output_str = output_str.replace("toping", "topping")
    print(output_str)

    # for each service
    for service in services:
        is_running = daemon_is_running(service)
        if (getattr(cfg, "%s_enabled" % service, True) and
            ((action == "kill" and is_running) or
             (action == "stop" and is_running) or
             (action == "start" and not is_running) or
             (action == "restart"))):

            print("    %s" % (service))
            command = '%s %s %s' % (cfg.tool_name, action, service)
            Popen(command.split(), stdout=PIPE, stderr=PIPE)

def postgresql_handler (action = None):
    if not action:
        action = args.command

    # informative output
    output_str = "%sing postgresql..." % action.capitalize()
    output_str = output_str.replace("toping", "topping")
    print(output_str)

    if cfg.distro in ['ubuntu', 'debian']:
        svc_name = "postgresql"
    else:
        # fancy command to extract the postgres version number
        (code, result) = getstatusoutput("psql -V | egrep -o '[0-9]{1,}\.[0-9]{1,}'")
        svc_name = "postgresql-%s" % result

    command = 'service %s %s' % (svc_name, action)
    subprocess.call(command.split())

def daemon_is_running (daemon_name):
    (code, result) = getstatusoutput('ps -p `cat %s`' % cfg.get_pidfile(daemon_name))
    return code == 0

def daemon_handler (action = None, service = None):
    action = action or args.command

    if action == "restart":
        (code, result) = getstatusoutput("%s stop %s" %
                                         (cfg.tool_name, service))
        (code, result) = getstatusoutput("%s start %s" %
                                         (cfg.tool_name, service))
    elif action == "kill":
        (code, result) = getstatusoutput("pkill -9 -f '%s (start|stop|restart) %s'" %
                                         (cfg.tool_name, service))
    else:
        log.debug("%s %s" % (service, action))

        start_daemon(service)

def start_daemon (service):
    from server.daphne.DaphneDaemon import DaphneDaemon
    from datastore.DatastoreDaemon import DatastoreDaemon

    # find FDs to preserve into the daemon
    files_preserve = []
    # the logging file
    files_preserve.append(log.fh.stream)
    # Twisted/Asyncio FDs
    files_preserve += aio.get_fds()

    # need to treat the subcommand as the first argument
    if len(sys.argv) > 2:
        sys.argv = sys.argv[1:]
        # swap the first two args
        sys.argv[0], sys.argv[1] = sys.argv[1], sys.argv[0]

    try:

        # can't carry the connection into daemon mode
        connection.close()
    except Exception as e:
        print(e)


    app = locals()['%sDaemon' % service.capitalize()]()
    daemon_runner = runner.DaemonRunner(app)
    daemon_runner.daemon_context.files_preserve=files_preserve
    daemon_runner.daemon_context.signal_map = {
        signal.SIGTTIN: None,
        signal.SIGTTOU: None,
        signal.SIGTSTP: None,
        signal.SIGTERM: app.terminate,
        }
    try:
        daemon_runner.do_action()
    except runner.DaemonRunnerStopFailureError as e:
        if "PID" not in str(e):
            print(e)
        sys.exit (-1)
    except lockfile.LockTimeout as e:
        print("%s already running" % service)
        sys.exit (-1)

def show_log (daemon_name = None):
    daemon_name = args.option

    if args.clear:
        clear_log(daemon_name)

    filepath = "%s/%s.log" % (cfg.log_dir, daemon_name)

    if args.tail:
        command = 'stty size'
        (code, result) = getstatusoutput(command)
        rows, cols = result.split()
        command = 'tail -f -n%s %s' % (int(rows) - 4, filepath)
        subprocess.call(command, shell=True)
    else:
        with open (filepath, "r") as f:
            print(f.read())

def clear_log (daemon_name = None):
    if not daemon_name:
        daemon_name = args.device_name or "poller"

    log_regex = re.compile(f"{daemon_name}\.log.*")

    # delete all log files that match the "daemon_name.log.*" pattern
    for file in os.listdir(cfg.log_dir):
        # clear file, but don't delete it if it is the main log file
        if file == f"{daemon_name}.log":
            with open(os.path.join(cfg.log_dir, file), "w") as f:
                pass

        # delete the log file entirely if it isn't the main log file
        elif log_regex.search(file):
            os.remove(os.path.join(cfg.log_dir, file))

def build_parser ():
    """
    Build the ArgumentParser tree.

    The parser will change depending on the command.
    """

    parser = argparse.ArgumentParser(usage=usage(), conflict_handler='resolve', add_help=False)
    parser.add_argument('-h', '--help', action='store_true', dest='help')
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('-d', '--debug', action='store', dest="debug_lvl", default="critical")
    parser.add_argument('command', nargs='?', default=None)
    parser.add_argument('option', nargs='?', default=None)

    # stop here and figure out the subcommand
    (args, leftover) = parser.parse_known_args()

    # check for invalid command
    if args.command and args.command not in commands.keys():
        usage_exit("Invalid Command: %s" % args.command)

    # check for help flag
    if args.help or not args.command:
        print(usage(args.command))
        sys.exit()

    command = args.command
    parser.usage = usage(command)

    if command in ["update"]:
        parser.add_argument("-i", "--install",
                            action="store_true", dest="install")
        parser.add_argument("-r", "--restart",
                            action="store_true", dest="restart")

    if command in ["update"]:
        parser.add_argument("-l", "--local",
                            action="store", dest="repo")

    if command in ["install"]:
        parser.add_argument("-f", "--full",
                            action="store_true", dest="full")

    if command in ['log', 'start', 'restart']:
        parser.add_argument("-t", "--tail",
                            action="store_true")
        parser.add_argument("-c", "--clear",
                            action="store_true")

    args = parser.parse_args()
    return args

def test ():
    """ function for testing random functionality  """

    print(str(datetime.utcnow()))
    #aio.run(main())

##
# GLOBALS
##
VERSION = str(utility.epoch_to_datetime(utility.get_build_date()).date())

commands = {
    'clear_config' : clear_config,
    'clear_data' : clear_data,
    'clear_logs' : clear_logs,
    'clear_db' : clear_db,
    'log' : show_log,
    'update' : update,
    'install' : install,
    'kill' : service_handler,
    'stop' : service_handler,
    'start' : service_handler,
    'restart' : service_handler,
    'postgresql' : postgresql_handler,
    'status': status,
    'test': test
    }

# initialize the configuration module
try:
    cfg.init_config()
except Exception as e:
    print("\nError: Problem initializing config!")
    print(traceback.format_exc())

# build the parser
args = build_parser()

# initialize the logger
log_name = "flockpocket.log"
try:
    if args.command in ["start", "stop", "kill", "restart"] and args.option in cfg.services:
        log_name = "%s.log" % args.option
except: pass

try:
    log.init(log_name, args.debug_lvl)
except Exception as e:
    print("\nError: Problem initializing logger!")
    print(traceback.format_exc())

# find the command function
command_fn = commands[args.command]

try:
    # run the command!
    command_fn()
except KeyboardInterrupt:
    print('')
    sys.exit()
except Exception as e:
#    print(sys.exc_info()[0]
    print(traceback.format_exc())
#    print(e)
    sys.exit()

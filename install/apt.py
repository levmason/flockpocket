from subprocess import run, PIPE
from common import textIO

# set the apt-get options
cmd='apt-get -q -o Acquire::ForceIPv4=true -y --fix-missing --allow-unauthenticated'

def update ():
    command = '%s update' % cmd
    result = run(command.split(), stdout=PIPE, stderr=PIPE)

def install (pkg, quiet=False):
    print("(apt) Installing %s" % pkg)
    command = '%s install %s' % (cmd, pkg)
    try:
        result = run(command.split(), stdout=PIPE, stderr=PIPE)
        result.check_returncode()
    except Exception as e:
        if not quiet:
            text = '**** ERROR ****\n%s' % result.stderr
            print(textIO.fail(textIO.indent(text, 4)))
        raise

def cleanup ():
    command = '%s autoclean; %s clean; %s autoremove' % (cmd, cmd, cmd)
    result = run(command.split(), stdout=PIPE, stderr=PIPE)

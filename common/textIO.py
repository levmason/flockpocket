def prompt (string):
    """Prompt the user with a yes/no question"""

    answer = input(string + " [y/n]: ")

    if answer.lower() == 'y':
        return True
    elif answer.lower() == 'n':
        return False
    else:
        return prompt(string)

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

def warning (string):
    return("%s%s%s" % (WARNING, string, ENDC))
def error (string):
    return("%s%s%s" % (FAIL, string, ENDC))
def fail (string):
    return("%s%s%s" % (FAIL, string, ENDC))
def success (string):
    return("%s%s%s" % (OKGREEN, string, ENDC))

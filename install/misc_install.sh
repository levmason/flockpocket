#!/bin/bash
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
PRJ_DIR=`dirname "$DIR"`
CFG_DIR=/etc/flockpocket/
LOG_DIR=/var/log/flockpocket/
PID_DIR=/run/flockpocket/

# check for -f argument
FULL=false
for arg in "$@"
do
    if [ "$arg" == "-f" ]
    then
	FULL=true
    fi
done

if $FULL; then
    # create the flockpocket user
    useradd -m -s /bin/bash flockpocket -g flockpocket 2> /dev/null
    # create the flockpocket group
    groupadd flockpocket 2> /dev/null
    # create the user for CLI commands
    useradd -m -s flockpocket 2> /dev/null
fi

#
# flockpocket dir permissions
# change the group owner
chown -R flockpocket:flockpocket $PRJ_DIR 2> /dev/null
# set the permissions (remove all other)
chmod -R o-rwx,g+rw $PRJ_DIR 2> /dev/null

# permissions for nginx
chmod u+rwX,go+rwX,o-w $PRJ_DIR # levy: maybe this conflicts with the above?
chmod -R u+rwX,go+rwX,o-w $PRJ_DIR/static/

if $FULL; then
    #
    # root config
    mkdir -p $CFG_DIR
    # copy the default config (no overwrite)
    cp -n $DIR/files/flockpocket.conf $CFG_DIR
    # change the group owner
    chown -R flockpocket:flockpocket $CFG_DIR
    # set the permissions
    chmod -R o-rwx $CFG_DIR

    #
    # pids
    mkdir -p $PID_DIR
    # change the group owner
    chown -R flockpocket:flockpocket $PID_DIR
    # set the permissions
    chmod -R u+rw,g+rw,o=r $PID_DIR
    # Add to the tmpfiles.d
    cp -f $DIR/files/tmpfiles.d/flockpocket.conf /usr/lib/tmpfiles.d/

    #
    # logs
    mkdir -p $LOG_DIR
    # change the group owner
    chown -R flockpocket:flockpocket $LOG_DIR
    # set the permissions
    chmod -R u+rw,g+rw,o=r $LOG_DIR
    chmod g+s $LOG_DIR

    # set the binary symlink
    ln -sf $PRJ_DIR/flockpocket.py /usr/local/bin/flockpocket
fi
exit 0

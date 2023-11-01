#!/bin/bash
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
PRJ_DIR="$(dirname $DIR)"

$PRJ_DIR/install/init_db.sh
$PRJ_DIR/install/create_users.py
flockpocket start $@
tail -f /dev/null
flockpocket stop $@

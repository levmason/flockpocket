#!/bin/bash

# check for -r argument
root=false
for arg in "$@"
do
    if [ "$arg" == "-r" ]
    then
	root=true
    fi
done

if $root
then
    docker exec -it -u root flockpocket /bin/bash
else
    docker exec -it flockpocket /bin/bash
fi

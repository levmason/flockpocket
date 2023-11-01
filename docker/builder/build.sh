#!/bin/bash

# set the default config file
config_file=./flockpocket.conf

# read the options
while test $# -gt 0; do
    case "$1" in
	-h|--help)
	    echo "./install.sh  [options]"
	    echo " "
	    echo "options:"
	    echo "-h, --help                show brief help"
	    echo "-c, --config              specify the flockpocket config file"
	    exit 0
	    ;;
	-c|--config)
	    shift
	    config_file=$1
	    ;;
	*)
	    break
	    ;;
    esac
done

# copy in the config file
cp $config_file .flockpocket.conf

# read the config file (all options will be exposed as bash variables)
eval $(sed -e 's/FLOCKPOCKET_//g' $config_file)

# write the nginx config
sed -e "s/{daphne_bind}/flockpocket:$DAPHNE_PORT/g;" ../../server/nginx/flockpocket.conf > ./.nginx.conf

# add the postgres env variables
db_username=${DB_USERNAME:=flockpocket}
if [ -z ${DB_PASSWORD} ];
then
    echo "DB_PASSWORD must be set in the Flockpocket config file!"
    exit
fi
rm .postgres.conf 2> /dev/null
echo POSTGRES_USER=$DB_USERNAME >> .postgres.conf
echo POSTGRES_PASSWORD=$DB_PASSWORD >> .postgres.conf

docker-compose build --build-arg http_proxy=$http_proxy --build-arg https_proxy=$https_proxy flockpocket

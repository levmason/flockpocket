#!/bin/bash

# make the migrations
/opt/flockpocket/manage.py makemigrations
# apply the migrations
while ! /opt/flockpocket/manage.py migrate; do
    echo "Database Initialization Failed!"
    sleep 5
    echo "Trying again..."
done

export DJANGO_SETTINGS_MODULE=flockpocket.settings
export PYTHONPATH=/opt/flockpocket/

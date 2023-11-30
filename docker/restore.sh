#!/bin/bash

if [ $# -eq 0 ]
  then
      echo "Filepath required!"
      exit 1
fi

docker exec -i flockpocket_db pg_restore -U flockpocket -ec --if-exists -d flockpocket < $1

#!/bin/bash

docker exec flockpocket_db pg_dump -U flockpocket -Fc flockpocket > flock.bkp

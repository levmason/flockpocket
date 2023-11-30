#!/bin/bash
docker-compose build flockpocket
docker tag builder_flockpocket levmason/flockpocket:latest

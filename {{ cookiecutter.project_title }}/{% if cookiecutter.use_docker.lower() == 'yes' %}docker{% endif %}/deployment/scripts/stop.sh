#!/bin/bash

docker-compose -f docker/deployment/app.yml stop

echo "stop.sh: All Done..."

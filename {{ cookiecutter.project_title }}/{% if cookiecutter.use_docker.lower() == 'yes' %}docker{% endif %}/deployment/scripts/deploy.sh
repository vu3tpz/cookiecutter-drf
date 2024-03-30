#!/bin/bash

# init necessary services
./docker/deployment/scripts/init.sh

# stop running services, if any
./docker/deployment/scripts/stop.sh

# re-run the necessary services
./docker/deployment/scripts/up.sh

echo "deploy.sh: All Done..."

#!/bin/bash

docker-compose -f docker/deployment/app.yml up -d

echo "up.sh: All Done..."

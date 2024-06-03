#!/bin/bash

# Stop all running containers
docker stop $(docker ps -a -q)

# Remove all containers
docker rm $(docker ps -a -q)

# Remove all docker images
docker rmi $(docker images -q)

# # Navigate to your docker-compose file directory
# cd /home/eragoh/Projects/RSWW-mikroserwisy/

# # Rebuild and recreate services
# docker-compose up --build -d

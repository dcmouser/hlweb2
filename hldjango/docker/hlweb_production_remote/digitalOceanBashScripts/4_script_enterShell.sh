#!/bin/bash

# Get the first running container ID
CONTAINER_ID=$(docker ps -q | head -n 1)

# Check if we got a container ID
if [ -z "$CONTAINER_ID" ]; then
    echo "No running Docker containers found."
    exit 1
fi

# Launch an interactive shell
docker exec -it "$CONTAINER_ID" sh
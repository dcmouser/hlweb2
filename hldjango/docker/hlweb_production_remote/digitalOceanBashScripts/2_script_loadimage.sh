#!/bin/sh
docker load --input hlweb_production_remote.tar
docker images
echo "RUN: docker compose up &"
echo "Delete with: docker image rm OLDIMAGEID"

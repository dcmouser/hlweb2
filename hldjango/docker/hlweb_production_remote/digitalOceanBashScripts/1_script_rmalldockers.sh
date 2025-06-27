#!/bin/sh
ids=$(docker ps -a -q)
for id in $ids
do
  echo "$id"
  docker stop $id && docker rm $id
done

# really delete all
docker system prune --all --force
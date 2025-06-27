del hlweb_production_remote.tar
docker compose build --no-cache
docker image save -o hlweb_production_remote.tar jreichler/hlweb_production_remote
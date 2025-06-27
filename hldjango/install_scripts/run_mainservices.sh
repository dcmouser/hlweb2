#!/bin/bash

# see https://docs.docker.com/config/containers/multi-service_container/


# what webserver port to use when running builtin or waitress server (nginx and gunicorn use their own config files)
#WEBSERVER_PORT_STANDALONE=8000
WEBSERVER_PORT_STANDALONE=80



# switch into code directory?
cd /code



# now some preliminary steps we run EVERY TIME the container launches

# Preliminary step 1: run databsae migrate in case we have updated code and local database needs updating
python ./manage.py makemigrations  --noinput
python ./manage.py migrate  --noinput

# Preliminary step 2: ensure there is a superuser with simple login
python ./manage.py initGameGroupAndPermission
python ./manage.py initSiteGadminGroupAndPermission
python ./manage.py verifyOrAddInsecureTestingSuperuser


# NEW attempt to generate certbot real certificates
if [ "$JR_RUN_CERTBOT" == "disable" ]
then
	echo "Skipping letsencrypt certificate request because it has been disabled in docker mainservices script for testing."
fi



# NEW attempt to generate certbot real certificates
if [ "$JR_RUN_CERTBOT" == "standalone" ]
then
	chmod +x /install_scripts/generate_ssl_certbot_standalone.sh;
	/install_scripts/generate_ssl_certbot_standalone.sh
fi




# NOTE: JR_DJANGO_WEBSERVER is set in the Dockerfile for this image

# collect static unless builtin debug mode
if [ "$JR_DJANGO_WEBSERVER" != "devbuiltin" ] || [ "$JR_DJANGO_DEBUG" != "true" ]
then
    # to prep for possible use of static files server
    python ./manage.py collectstatic --noinput
fi


if [ "$JR_DJANGO_WEBSERVER" == "devbuiltin" ]
then
    # start django web server (process 1)
    # ATTN: TODO: change this to production web server
    #python ./manage.py runserver 0.0.0.0:8000 &
    python ./manage.py runserver_local 0.0.0.0:$WEBSERVER_PORT_STANDALONE &

elif [ "$JR_DJANGO_WEBSERVER" == "waitress" ]
then
    #python ./manage.py runserver_waitress 0.0.0.0 8000 &
    python ./manage.py runserver_waitress 0.0.0.0 $WEBSERVER_PORT_STANDALONE &

elif [ "$JR_DJANGO_WEBSERVER" == "gunicorn" ]
then
    gunicorn --config python:hldjango.wsgi_gunicorn_config_standalone hldjango.wsgi:application &

elif [ "$JR_DJANGO_WEBSERVER" == "nginx" ]
then
    # first we need to run gunicorn
    gunicorn --config python:hldjango.wsgi_gunicorn_config_nginxhelper hldjango.wsgi:application &
    # then nginx to proxy requests to gunicorn or serve statics on its own
    nginx -c /code/hldjango/nginx_config.conf -t
    nginx -c /code/hldjango/nginx_config.conf &

else
    echo "No value specified for environmental variable 'JR_DJANGO_WEBSERVER'."
    exit 1
fi




# NEW attempt to generate certbot real certificates
if [ "$JR_RUN_CERTBOT" == "runningweb" ]
then
	chmod +x /install_scripts/generate_ssl_certbot_running.sh;
	/install_scripts/generate_ssl_certbot_running.sh
fi





# start huey queued exectution process (process 2)
python ./manage.py run_huey &

# Wait for any process to exit
wait -n

# back out to main dir?
cd ..

# ATTN: for debugging we can have it NOT exit and stay running on error
echo "ATTN!"
echo "ATTN: DEBUG - Leaving container running even after a mainprocess exited.."
echo "ATTN!"
sleep 9999999999 & wait

# Exit with status of process that exited first
exit $?

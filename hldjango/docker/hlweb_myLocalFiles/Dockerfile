# PRIOR TO 10/25/24 was ARG PYTHON_VERSION=3.12.3
ARG PYTHON_VERSION=3.12.7
FROM python:${PYTHON_VERSION}


# choose which settings to use and any overrides
ENV DJANGO_SETTINGS_MODULE=hldjango.settingsdir.production_docker
#
#ENV JR_DJANGO_WEBSERVER=devbuiltin
#ENV JR_DJANGO_WHITENOISE=false
#ENV JR_DJANGO_DEBUG=false
#ENV JR_DJANGO_WEBSERVER=waitress
#ENV JR_DJANGO_WHITENOISE=true
#ENV JR_DJANGO_DEBUG=false
#ENV JR_DJANGO_WEBSERVER=gunicorn
#ENV JR_DJANGO_WHITENOISE=true
#ENV JR_DJANGO_DEBUG=false
#
ENV JR_DJANGO_WEBSERVER=nginx
ENV JR_DJANGO_WHITENOISE=false
ENV JR_DJANGO_DEBUG=false
#
ENV JR_RUN_CERTBOT=standalone



LABEL maintainer = "jesse reichler <jessereichler@gmail.com>"
LABEL description = "A casebook pdf builder tool for New York Noir"

# DOCKER BUILD NOTE: rebuild with: docker compose build --no-cache ; then: docker compose up ; or build container with: docker create


# python environment vars
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# copy files (mock files)
COPY install_scripts /install_scripts
COPY code /code
COPY deploy/jrlogs /jrlogs
COPY deploy/db /db
COPY deploy/media /media
COPY deploy/static /static
COPY deploy/botaccess /botaccess
COPY deploy/etc /etc

# copy requirements into install_scripts
COPY requirements.txt /install_scripts

# go into install_scripts directory
WORKDIR /install_scripts

# pip update, etc.
RUN chmod +x ./pip_install.sh; ./pip_install.sh

# main apt installs
RUN chmod +x ./apt_install.sh; ./apt_install.sh

# 6/28/24 create ssl cert and key
RUN chmod +x ./generate_ssl.sh; ./generate_ssl.sh

# 6/27/24 install nginx production quality server
RUN chmod +x ./apt_install_nginx.sh; ./apt_install_nginx.sh

# tex-live
RUN chmod +x ./texlive_install.sh; ./texlive_install.sh

# step out of install_scripts?
WORKDIR /



# ATTN: JR - Add path to find pdflatex bin for texlive 
# ATTN: *IMPORTANT* The directory we add to path is in the install directory specified in the file .\textlive.profile
ENV PATH="${PATH}:/opt/texlive/bin/x86_64-linux"


# EXPOSING PORTS tip: See also the compose file
# expose to nginx
EXPOSE 80
# https
EXPOSE 443
# expose 8000 to gunicorn (not needed in nginx setup since IT does the forwarding?)
#EXPOSE 8000

CMD /install_scripts/run_mainservices.sh

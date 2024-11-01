# PRIOR TO 10/25/24 was ARG PYTHON_VERSION=3.12.3
ARG PYTHON_VERSION=3.12.7
FROM python:${PYTHON_VERSION}


# choose which settings to use and any overrides
ENV DJANGO_SETTINGS_MODULE=hldjango.settingsdir.personal_docker
#
#ENV JR_DJANGO_WEBSERVER=devbuiltin
#ENV JR_DJANGO_WHITENOISE=false
#ENV JR_DJANGO_DEBUG=true
#ENV JR_DJANGO_WEBSERVER=waitress
#ENV JR_DJANGO_WHITENOISE=true
#ENV JR_DJANGO_DEBUG=false
ENV JR_DJANGO_WEBSERVER=gunicorn
ENV JR_DJANGO_WHITENOISE=true
ENV JR_DJANGO_DEBUG=true


LABEL maintainer = "jesse reichler <jessereichler@gmail.com>"
LABEL description = "A casebook pdf builder tool for New York Noir (High & Low)"

# DOCKER BUILD NOTE: rebuild with: docker compose build --no-cache ; then launch with: docker compose up ; or build container with: docker create


# python environment vars
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# copy files (mock files)
COPY install_scripts /install_scripts
COPY code /code
COPY mock/jrlogs /jrlogs
COPY mock/db /db
COPY mock/media /media
COPY mock/static /static
COPY mock/botaccess /botaccess
COPY mock/etc /etc

# copy requirements into install_scripts
COPY requirements.txt /install_scripts

# go into install_scripts directory
WORKDIR /install_scripts

# pip update, etc.
RUN chmod +x ./pip_install.sh; ./pip_install.sh

# main apt installs
RUN chmod +x ./apt_install.sh; ./apt_install.sh

# tex-live
RUN chmod +x ./texlive_install.sh; ./texlive_install.sh

# step out of install_scripts?
WORKDIR /



# ATTN: JR - Add path to find pdflatex bin for texlive 
# ATTN: *IMPORTANT* The directory we add to path is in the install directory specified in the file .\textlive.profile
ENV PATH="${PATH}:/opt/texlive/bin/x86_64-linux"


# EXPOSING PORTS tip: See also the compose file
# expose web port
EXPOSE 80
# we dont use 8000 anymore
#EXPOSE 8000


CMD /install_scripts/run_mainservices.sh

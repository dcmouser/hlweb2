#!/usr/bin/env sh

# update packages
apt-get update

apt --ys install tzdata

# certificate authorities for openssl?
# see https://serverfault.com/questions/639837/openssl-s-client-shows-alert-certificate-unknown-but-all-server-certificates-app
apt --yes install ca-certificates

# certbot new way to generate ssl keys?
apt --yes install certbot

# graphviz
apt --yes install graphviz

# popper tools for pdf to image converstion (this may not be needed..)
apt --yes install poppler-utils

# imagemagick for image manipulation utility functionality
apt --yes install libjpeg-dev libpng-dev libtiff-dev
apt-get update
apt --yes install imagemagick

#!/usr/bin/env sh
# Note that this only gets run once when BUILDING the docker image, NOT on every instantiation/mount of the docker image (the way our letsencrypt gets run)

echo "---------------------------------------------------------------------------"
echo "Running openssl certificate generation.."

# switch into code directory?
#cd /code/hldjango
# NEW, trying to put this in a dedicated
mkdir -p /ssl
cd /

#DOMAIN='newyorknoirgame.com'
#DOMAIN='nycnoirgame.com'
#DOMAIN='nycnoir.org'
DOMAIN='nynoir.org'

# generate the ssl key
echo "Generating ssl certificate for $DOMAIN in $PWD/ssl/ ..."
openssl req -x509 -newkey rsa:2048 -sha256 -days 3650 -nodes -keyout ssl/$DOMAIN.key -out ssl/$DOMAIN.crt -subj "/CN=$DOMAIN" -addext "subjectAltName=DNS:$DOMAIN,DNS:*.$DOMAIN,IP:0.0.0.0"

# now we copy over where our letsencrypt certbot files would be; hopefully the wrong extensions wont confuse it
echo "Copying openssl self-signed keys in place of certbox letsencrypt keys until that bot runs"
cp /ssl/$DOMAIN.crt /ssl/fullchain.pem
cp /ssl/$DOMAIN.key /ssl/privkey.pem

echo "---------------------------------------------------------------------------"



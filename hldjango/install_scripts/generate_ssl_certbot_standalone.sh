#!/usr/bin/env sh

echo "---------------------------------------------------------------------------"
echo "Running certbot script to generate ssl keys using letsencrypt and certbot (standalone.sh).."

# switch into code directory?
#cd /code/hldjango
# NEW, trying to put this in a dedicated


#DOMAIN='newyorknoirgame.com'
#DOMAIN='nycnoirgame.com'
DOMAIN='nycnoir.org'



# generate the ssl keys using letsencrypt / certbot
# see https://eff-certbot.readthedocs.io/en/stable/using.html#certbot-command-line-options
echo "Invoking (standalone) letsencrypt certbot for $DOMAIN ..."

# using server currently running
#certbot certonly --webroot --webroot-path /botaccess/ --email jessereichler@gmail.com --keep-until-expiring --agree-tos --no-eff-email -n -d $DOMAIN -d www.$DOMAIN

# using standalone web server (must be run BEFORE our local nginx, etc.)
certbot certonly --standalone --email jessereichler@gmail.com --keep-until-expiring --agree-tos --no-eff-email -n -d $DOMAIN -d www.$DOMAIN -v

# copy to /ssl where our web server looks for it
echo "Copying letsencrypt keys to /ssl"
mkdir -p /ssl
cp -r -L /etc/letsencrypt/live/$DOMAIN/fullchain.pem /ssl
cp -r -L /etc/letsencrypt/live/$DOMAIN/privkey.pem /ssl

echo "---------------------------------------------------------------------------"

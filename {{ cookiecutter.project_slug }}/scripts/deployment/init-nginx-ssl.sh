#!/bin/bash

# Init the app's deployment strategy, nginx and certbot runs on the OS level
# and they proxy to the given port where the docker will be running

# default values
default_domain="example.com"
default_port="8000"
default_email="email@mailinator.com"

# template variable for domain
read -r -p "Domain [$default_domain]: " domain && domain=${domain:-"$default_domain"}
# template variable for which port to proxy
read -r -p "Proxy to Port [$default_port]: " proxy_port && proxy_port=${proxy_port:-"$default_port"}
# email address to register for ssl certificate
read -r -p "Email for registration [$default_email]: " email_address && email_address=${email_address:-"$default_email"}

# reinstall nginx
if [ "$1" == "--reset-nginx" ]; then
    echo "Removing and reinstalling nginx & related settings"
    sudo apt update -y
    sudo apt purge nginx nginx-common -y
    sudo apt autoremove -y
    sudo apt install nginx nginx-common -y
fi

# configurations for the script
nginx_conf_template="$PWD/docker/deployment/conf/nginx-ssl.conf" # specify the location of the template file
media_root="$PWD/apps/media/"                                    # the file path where media is present
static_root="$PWD/staticfiles/"                                  # the file path where media is present
current_directory="$(basename "$PWD")"                           # name of the current directory
nginx_conf_file="$current_directory.conf"                        # nginx.conf file with directory name
nginx_conf_directory="/etc/nginx/sites-enabled"                  # directory where nginx configurations are stored

# replace necessary variables in nginx_conf_template
echo "Generating nginx conf file"
sed -e " \
s|{domain}|$domain|g; \
s|{proxy_port}|$proxy_port|g; \
s|{media_root}|$media_root|g; \
s|{static_root}|$static_root|g; \
" "$nginx_conf_template" >"$nginx_conf_file"

# move the generated configuration file to the nginx directory
echo "Moving nginx configuration file to necessary directory"
sudo mv "$nginx_conf_file" "$nginx_conf_directory/$nginx_conf_file"

# getting SSL cerificate
echo "Installing certbot for SSL certificate"
sudo apt install certbot python3-certbot-nginx -y
echo "Getting SSL certificate"
eval "sudo certbot --nginx -d $domain --email $email_address"
sudo certbot renew --dry-run

# update firewall
echo "Updating firewall settings"
sudo ufw allow 'Nginx Full'
sudo ufw delete allow 'Nginx HTTP'

# restart nginx
echo "Restarting nginx"
sudo systemctl restart nginx

echo "All done"

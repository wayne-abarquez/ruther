#!/usr/bin/env bash

sudo rm /etc/nginx/sites-enabled/default
sudo rm /etc/nginx/sites-available/ruther
sudo rm /etc/nginx/sites-enabled/ruther
sudo cp conf/local/nginx.conf /etc/nginx/sites-available/ruther
sudo ln -s /etc/nginx/sites-available/ruther /etc/nginx/sites-enabled/ruther
sudo /etc/init.d/nginx start

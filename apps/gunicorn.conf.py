bind = '127.0.0.1:8000'
accesslog='/var/www/ruther/logs/gunicorn-access.log'
errorlog='/var/www/ruther/logs/gunicorn-error.log'
workers=4
preload=True

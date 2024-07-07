#!/bin/sh
touch /var/log/cron.log
printenv | grep -Ev 'BASHOPTS|BASH_VERSINFO|EUID|PPID|SHELLOPTS|UID|LANG|PWD|GPG_KEY|_=' >> /etc/environment
env > /etc/environment
echo "SHELL=/bin/bash" > /etc/cron.d/parsing

echo "*/5 * * * * /usr/local/bin/python3 /app/manage.py parsing >> /app/parsing_log/server.log 2>&1" >> /etc/cron.d/parsing
service cron start
crontab /etc/cron.d/parsing
python manage.py makemigrations --no-input
python manage.py migrate --no-input
python manage.py createbotuser
python manage.py runserver 0.0.0.0:8000

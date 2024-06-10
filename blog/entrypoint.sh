#!/bin/sh
touch /var/log/cron.log
printenv | grep -Ev 'BASHOPTS|BASH_VERSINFO|EUID|PPID|SHELLOPTS|UID|LANG|PWD|GPG_KEY|_=' >> /etc/environment

python manage.py crontab remove
python manage.py crontab add
service cron start
python manage.py makemigrations --no-input
python manage.py migrate --no-input
python manage.py createbotuser
python manage.py runserver 0.0.0.0:8000

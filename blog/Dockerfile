FROM python:3.10-slim

# prevents python buffering stdout and stderr
ENV PYTHONUNBUFFERED 1

# prevents python from writing .pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update && apt-get install -y \
    chromium-driver \
    chromium

# Set the environment variable for Chromium
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_BIN=/usr/bin/chromedriver

WORKDIR /app

RUN apt-get update \
    && apt-get install -y cron

COPY ./requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app/
RUN chmod a+rwx ./parsing_log



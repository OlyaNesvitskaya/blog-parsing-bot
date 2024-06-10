FROM python:3.10-slim

# prevents python buffering stdout and stderr
ENV PYTHONUNBUFFERED 1

# prevents python from writing .pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1

# sets up the working directory for any RUN, CMD, ENTRYPOINT, COPY and ADD instructions
WORKDIR /app

# install dependencies

RUN apt-get update \
    && apt-get install -y cron
COPY ./requirements.txt /app/
RUN pip install -r requirements.txt


# copies files and directories from current directory to WORKDIR
COPY . /app/



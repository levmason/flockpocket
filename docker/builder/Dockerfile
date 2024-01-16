# pull the base image
FROM python:3.9-slim-buster as baseimage

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY install/requirements/pip_requirements.txt requirements.txt
RUN apt-get update && apt-get install git procps python3-psycopg2 -y
RUN pip3 install -r requirements.txt

FROM baseimage
RUN mkdir -p /opt/flockpocket
WORKDIR /opt/flockpocket
COPY . /opt/flockpocket

# create the user
RUN useradd -m -s /bin/bash flockpocket

# install
ARG DOCKER=true
RUN python /opt/flockpocket/install/install.py -f

# switch user
USER flockpocket

# pull the base image
FROM python:3.9-slim-buster

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

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

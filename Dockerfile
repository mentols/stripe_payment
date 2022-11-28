FROM python:3.9-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install --no-install-recommends

RUN pip3 install --upgrade pip
COPY . .

RUN pip3 install -r ./requirements.txt

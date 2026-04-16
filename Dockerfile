FROM python:3.13-slim

WORKDIR /app

COPY . .

# FIX ENV
RUN dos2unix .env | sed -i 's/\r$//' .env

# TUNA
# Install req
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*
# Install tuna
RUN curl -sSLf https://get.tuna.am | sh

# network bridge fix
RUN apt-get update -y
RUN apt-get install bridge-utils

RUN [ "pip", "install", "--no-cache-dir", "-r", "requirements.txt" ]

ENTRYPOINT [ "python", "bot/main.py" ]

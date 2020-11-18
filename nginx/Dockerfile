FROM nginx:latest

ENV APP_PATH /var/www/html

WORKDIR $APP_PATH

RUN apt update \
    && apt-get update \
    && apt-get install --yes --no-install-recommends \
      openssl \
      certbot \
      vim \
      less \
      curl \
      net-tools \
      iputils-ping \
      procps \
      cron \
    && rm -rf /var/lib/apt/lists/*


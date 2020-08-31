FROM alpine:3.12.0

RUN apk --update-cache add \
    musl \
    linux-headers \
    gcc \
    g++ \
    make \
    gfortran \
    openblas-dev \
    python3 \
    python3-dev
    openjdk11-jre-headless \
    vim \
    less \
    curl \
    && rm -rf /var/cache/apk/*

RUN pip3 install --upgrade pip

COPY requirements.txt /tmp

RUN pip3 install -r requirements.txt

COPY wait-for-h2.sh /wait-for-h2.sh
RUN chmod +x /wait-for-h2.sh

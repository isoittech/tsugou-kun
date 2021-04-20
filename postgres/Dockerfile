FROM postgres:11.4-alpine

MAINTAINER isoittech

USER postgres
RUN /etc/init.d/postgresql start &&\
    echo "host all  all    0.0.0.0/0  trust" >> /var/lib/postgresql/data/pg_hba.conf


FROM docker.io/postgres:17

RUN apt-get update \
    && apt-get install -y gnupg wget \
    && wget --quiet -O - https://packagecloud.io/timescale/timescaledb/gpgkey | apt-key add - \
    && echo "deb https://packagecloud.io/timescale/timescaledb/debian/ stretch main" > /etc/apt/sources.list.d/timescaledb.list \
    && apt-get update \
    && apt-get install -y timescaledb-postgresql-17 \
    && rm -rf /var/lib/apt/lists/*

# Optionally, configure shared_preload_libraries
RUN echo "shared_preload_libraries = 'timescaledb'" >> /var/lib/postgresql/data/postgresql.conf

# TODO
# Need to enable the extension in the database later.

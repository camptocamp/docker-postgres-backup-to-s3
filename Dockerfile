FROM postgres:9.6

ENV \
  AWS_ACCESS_KEY_ID \
  AWS_SECRET_ACCESS_KEY \
  AWS_S3_BUCKET \
  PGHOST \
  PGUSER \
  PGPASSWORD \
  PGDATABASE

RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install -y awscli \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

COPY docker-entrypoint.sh /

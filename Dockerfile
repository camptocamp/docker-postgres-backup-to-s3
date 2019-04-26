FROM postgres:10.3

ENV \
  AWS_ACCESS_KEY_ID \
  AWS_DEFAULT_REGION \
  AWS_SECRET_ACCESS_KEY \
  AWS_S3_BUCKET \
  PGHOST \
  PGUSER \
  PGPASSWORD \
  PGDATABASE

RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install -y python-pip curl pv \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* \
  && pip install awscli

COPY docker-entrypoint.sh /

ENTRYPOINT ["/docker-entrypoint.sh"]

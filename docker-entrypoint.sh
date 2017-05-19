#!/bin/sh

pg_dump -Fc | gzip -9 | aws s3 cp - "s3://${AWS_S3_BUCKET}/postgres.${PGDATABASE}.dump.gz"

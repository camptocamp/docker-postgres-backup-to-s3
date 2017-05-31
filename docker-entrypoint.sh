#!/bin/bash

pg_dump -Fc | aws s3 cp - "s3://${AWS_S3_BUCKET}/postgres.${PGDATABASE}.$(date +%Y%m%d-%H%M).dump"

statuses=("${PIPESTATUS[@]}")
pg_dump_status=${statuses[0]}
echo "pg_dump exited with status: ${pg_dump_status}"
aws_status=${statuses[1]}
echo "aws exited with status: ${aws_status}"

stats=$(aws s3 ls --summarize --recursive "${AWS_S3_BUCKET}")
objects=$(sed -n '/ *Total Objects: / s///p' <<<"${stats}")
echo "Total Objects in bucket: ${objects}"

size=$(sed -n '/ *Total Size: / s///p' <<<"${stats}")
echo "Total Size of bucket: ${size}"

if [ ! -z "${PUSHGATEWAY_URL}" ]; then
  echo "Sending metrics to ${PUSHGATEWAY_URL}"
  cat <<EOF | curl --data-binary @- "${PUSHGATEWAY_URL}/metrics/job/postgres_s3_backup/database/${PGDATABASE}"
# TYPE postgres_s3_backup counter
postgres_s3_backup{what="pg_dump_status"} ${pg_dump_status}
postgres_s3_backup{what="aws_status"} ${aws_status}
postgres_s3_backup{what="total_objects"} ${objects}
postgres_s3_backup{what="total_size"} ${size}
EOF
fi

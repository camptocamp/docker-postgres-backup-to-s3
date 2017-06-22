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

  if getent hosts rancher-metadata >/dev/null; then
    instance=$(curl http://rancher-metadata/latest/self/container/name)
  else
    instance=$(hostname -f)
  fi

  cat <<EOF | curl --data-binary @- "${PUSHGATEWAY_URL}/metrics/job/postgres_s3_backup/instance/${instance}/database/${PGDATABASE}"
# TYPE postgres_s3_backup_pgDumpStatus gauge
postgres_s3_backup_pgDumpStatus ${pg_dump_status}
# TYPE postgres_s3_backup_awsStatus gauge
postgres_s3_backup_awsStatus ${aws_status}
# TYPE postgres_s3_backup_totalObjects gauge
postgres_s3_backup_totalObjects ${objects}
# TYPE postgres_s3_backup_totalSize gauge
postgres_s3_backup_totalSize ${size}
# TYPE postgres_s3_backup endTime counter
postgres_s3_backup_endTime $(date +%s)
EOF
fi

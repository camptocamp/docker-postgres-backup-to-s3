#!/bin/bash

list_databases() {
  databases=$(psql -t -A -c "SELECT datname FROM pg_database WHERE datistemplate IS FALSE AND datname !~ ('$BLACKLISTED_DATABASES')")
}

backup_database() {
  echo "[*] Backuping ${PGDATABASE}"
  backup_start_time=$(date +%s)
  pg_dump -Fc -v | pv -i 10 -F "%t %r %b" | aws s3 cp - "s3://${AWS_S3_BUCKET}/postgres.${PGDATABASE}.$(date +%Y%m%d-%H%M).dump"

  statuses=("${PIPESTATUS[@]}")
  pg_dump_status=${statuses[0]}
  echo "pg_dump exited with status: ${pg_dump_status}"
  aws_status=${statuses[2]}
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

    cat <<EOF | curl -s --data-binary @- "${PUSHGATEWAY_URL}/metrics/job/postgres_s3_backup/instance/${instance}/database/${PGDATABASE}"
# TYPE postgres_s3_backup_pg_dump_status gauge
postgres_s3_backup_pg_dump_status ${pg_dump_status}
# TYPE postgres_s3_backup_aws_status gauge
postgres_s3_backup_aws_status ${aws_status}
# TYPE postgres_s3_backup_total_objects gauge
postgres_s3_backup_total_objects ${objects}
# TYPE postgres_s3_backup_total_size gauge
postgres_s3_backup_total_size ${size}
# TYPE postgres_s3_backup_start_time gauge
postgres_s3_backup_start_time ${backup_start_time}
# TYPE postgres_s3_backup_end_time gauge
postgres_s3_backup_end_time $(date +%s)
EOF
fi
}

# the dumps are big (130GB) and S3 limits to 10000 chunks => increase the chunk size
aws configure set default.s3.multipart_chunksize 32MB
if [ -z "$PGDATABASE" ]; then
  list_databases
  for PGDATABASE in ${databases[@]}; do
    backup_database
  done
else
  backup_database
fi

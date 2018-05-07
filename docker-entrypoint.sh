#!/bin/bash

list_databases() {
  blacklisted_databases=$(echo "$BLACKLISTED_DATABASES" | sed -e "s/,/'&'/g" -e "s/^/\'/" -e "s/$/'/")
  databases=$(psql -t -A -c "SELECT datname FROM pg_database WHERE datname not in ($blacklisted_databases)")
}

backup_database() {
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

    cat <<EOF | curl -s --data-binary @- "${PUSHGATEWAY_URL}/metrics/job/postgres_s3_backup/instance/${instance}/database/${PGDATABASE}"
# TYPE postgres_s3_backup_pg_dump_status gauge
postgres_s3_backup_pg_dump_status ${pg_dump_status}
# TYPE postgres_s3_backup_aws_status gauge
postgres_s3_backup_aws_status ${aws_status}
# TYPE postgres_s3_backup_total_objects gauge
postgres_s3_backup_total_objects ${objects}
# TYPE postgres_s3_backup_total_size gauge
postgres_s3_backup_total_size ${size}
# TYPE postgres_s3_backup_end_time counter
postgres_s3_backup_end_time $(date +%s)
EOF
fi
}

list_databases

for PGDATABASE in ${databases[@]}; do
  echo "[*] Backuping ${PGDATABASE}"
  backup_database
done

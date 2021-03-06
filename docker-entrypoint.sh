#!/bin/bash

list_databases() {
  list_databases_query='SELECT datname FROM pg_database WHERE datistemplate IS FALSE'
  BLACKLISTED_DATABASES="'""$BLACKLISTED_DATABASES""'"
  if [ -z "$BLACKLISTED_DATABASES" ]; then
    databases=$(psql -t -A -c "$list_databases_query")
  else
    databases=$(psql -t -A -c "$list_databases_query AND datname !~ ($BLACKLISTED_DATABASES)")
  fi
}

backup_database() {
  echo "[*] Backing up ${PGDATABASE}"
  backup_start_time=$(date +%s)
  pg_dump -Fc -v -d ${PGDATABASE} | pv -i 10 -F "%t %r %b" | tee >(wc -c > /tmp/last_size) | aws s3 cp - "s3://${AWS_S3_BUCKET}/postgres.${PGDATABASE}.$(date +%Y%m%d-%H%M).dump"

  statuses=("${PIPESTATUS[@]}")
  last_size=$(cat /tmp/last_size)
  pg_dump_status=${statuses[0]}
  echo "pg_dump exited with status: ${pg_dump_status}"
  aws_status=${statuses[3]}
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
# TYPE postgres_s3_backup_last_size gauge
postgres_s3_backup_last_size ${last_size}
# TYPE postgres_s3_backup_start_time gauge
postgres_s3_backup_start_time ${backup_start_time}
# TYPE postgres_s3_backup_end_time gauge
postgres_s3_backup_end_time $(date +%s)
EOF
fi
}

# the dumps are big (130GB) and S3 limits to 10000 chunks => increase the chunk size
aws configure set default.s3.multipart_chunksize ${AWS_MULTIPART_CHUNKSIZE:-"32MB"}
if [ -z "$PGDATABASE" ]; then
  list_databases
  for PGDATABASE in ${databases[@]}; do
    backup_database
  done
else
  backup_database
fi

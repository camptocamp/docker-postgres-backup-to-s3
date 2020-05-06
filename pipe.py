from subprocess import Popen, PIPE
import os

import boto3
from prometheus_client import start_http_server
from prometheus_client import Gauge, Counter

# Prometheus exporter configuration
PROMETHEUS_EXPORTER_PORT = 9352
start_http_server(PROMETHEUS_EXPORTER_PORT)

bytes_read = Counter('bytes_read', 'Total bytes reads from input')
bytes_write = Counter('bytes_write', 'Total bytes uploaded to object storage')
metrics1 = Gauge('walg_basebackup_count',
                 'Remote Basebackups count')
metrics1.set(123)


# Buffer configuration
BUFFER_SIZE = 10 * 1024 * 1024
BUFFER = bytearray(BUFFER_SIZE)

# Target configuration
AWS_ENDPOINT = 'http://localhost:9000'
AWS_ACCESS_KEY = 'AKIAACCESSKEY'
AWS_SECRET_KEY = 'SECRETSECRET'
AWS_BUCKET = 'postgres-to-s3'
AWS_OBJECT_KEY = 'IMG_20200326_091927876.jpg'
AWS_MULTIPART_UPLOAD_ID = 'postgres-to-s3-IMG_20200326_091927876.jpg'

AWS_TARGET = {'Bucket': AWS_BUCKET, 'Key': AWS_OBJECT_KEY}
client = boto3.client('s3',
                      endpoint_url=AWS_ENDPOINT,
                      aws_access_key_id=AWS_ACCESS_KEY,
                      aws_secret_access_key=AWS_SECRET_KEY)

multipart_upload = client.create_multipart_upload(**AWS_TARGET)

input_cmd = "cat /home/jacroute/git/github.com/camptocamp/docker-postgres-backup-to-s3/data"

print("%s --> S3" % input_cmd)
bytes_written = 0
with Popen(input_cmd.split(), stdout=PIPE, stderr=PIPE) as input:
    part_number = 1
    parts = []
    while True:

        # Retrieve data from input in the buffer
        bytes_read = input.stdout.readinto(BUFFER)

        if bytes_read == 0:
            break

        # Push buffer to object storage
        res = client.upload_part(**AWS_TARGET,
                                 UploadId=multipart_upload['UploadId'],
                                 PartNumber=part_number,
                                 Body=BUFFER if bytes_read == BUFFER_SIZE else BUFFER[0:bytes_read],
                                 ContentLength=bytes_read)

        print(res)
        parts.append({'ETag': res['ETag'], 'PartNumber': part_number})
        bytes_written += bytes_read
        print('Write %s bytes' % bytes_read)

        part_number += 1
    if input.poll() is not None:
        res = client.complete_multipart_upload(**AWS_TARGET,
                                               MultipartUpload={'Parts': parts},
                                               UploadId=multipart_upload['UploadId'])
        print(res)
        print("%s bytes written" % bytes_written)

print("Done")

from subprocess import Popen, PIPE
import os

import boto3
from prometheus_client import start_http_server
from prometheus_client import Gauge, Counter

#
# Configuration
#

# Prometheus exporter configuration
PROMETHEUS_EXPORTER_PORT = 9352

# Source configuration
os.environ["PGHOST"] = "postgres"
os.environ["PGHOST"] = "localhost"
os.environ["PGDATABASE"] = "postgres"
os.environ["PGUSER"] = "postgres"
os.environ["PGPASSWORD"] = "pgpass"

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


# Start and configure prometheus exporter
start_http_server(PROMETHEUS_EXPORTER_PORT)

total_bytes_read = Counter('total_bytes_read',
                           'Total bytes reads from input')
current_bytes_read = Gauge('current_bytes_read',
                           'Bytes reads from input for current transfer')
total_bytes_write = Counter('total_bytes_write',
                            'Total bytes uploaded to object storage')
current_bytes_write = Gauge('current_bytes_write',
                            'Bytes uploaded to object storage for current transfer')
part_count = Gauge('part_count', 'Part of the Multipart upload uploaded')

# Start S3 client
AWS_TARGET = {'Bucket': AWS_BUCKET, 'Key': AWS_OBJECT_KEY}
client = boto3.client('s3',
                      endpoint_url=AWS_ENDPOINT,
                      aws_access_key_id=AWS_ACCESS_KEY,
                      aws_secret_access_key=AWS_SECRET_KEY)

multipart_upload = client.create_multipart_upload(**AWS_TARGET)

input_cmd = 'pg_dump -Fc -v -d %s' % os.environ['PGDATABASE']

print("%s --> S3" % input_cmd)
current_bytes_read.set(0)
current_bytes_write.set(0)

with Popen(input_cmd.split(), stdout=PIPE, stderr=PIPE) as input:
    part_number = 1
    part_count.set(part_number)
    parts = []
    while True:

        # Retrieve data from input in the buffer
        bytes_read = input.stdout.readinto(BUFFER)
        current_bytes_read.inc(bytes_read)
        total_bytes_read.inc(bytes_read)

        if bytes_read == 0:
            break

        # Push buffer to object storage
        res = client.upload_part(**AWS_TARGET,
                                 UploadId=multipart_upload['UploadId'],
                                 PartNumber=part_number,
                                 Body=BUFFER if bytes_read == BUFFER_SIZE
                                 else BUFFER[0:bytes_read])

        print(res)
        parts.append({'ETag': res['ETag'], 'PartNumber': part_number})
        current_bytes_write.inc(bytes_read)
        total_bytes_write.inc(bytes_read)
        print('Write %s bytes' % bytes_read)

        part_number += 1
        part_count.set(part_number)
    if input.poll() is not None:
        if current_bytes_write._value.get() == 0 or input.returncode != 0:
            client.abort_multipart_upload(**AWS_TARGET,
                                          UploadId=multipart_upload['UploadId'])
            raise Exception('Error: no data transfered or error on pg_dump: %s'
                            % input.stderr.read())
        else:
            res = client.complete_multipart_upload(**AWS_TARGET,
                                                   MultipartUpload={'Parts': parts},
                                                   UploadId=multipart_upload['UploadId'])
        print(res)
        print("%s bytes written" % current_bytes_write._value.get())
    else:
        raise Exception("Read of input finished but process is not finished, should not happen")

print("Done")

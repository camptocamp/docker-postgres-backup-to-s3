import os

import boto3

from pg253.configuration import Configuration


class ClientS3:
    def __init__(self, key):

        self.client = boto3.client('s3',
                                   endpoint_url=os.environ[Configuration.AWS_ENDPOINT],
                                   aws_access_key_id=os.environ[Configuration.AWS_ACCESS_KEY_ID],
                                   aws_secret_access_key=os.environ[Configuration.AWS_SECRET_ACCESS_KEY])

        self.target = {'Bucket': os.environ[Configuration.AWS_S3_BUCKET],
                       'Key': key}
        multipart_upload = self.client.create_multipart_upload(**self.target)
        self.upload_id = multipart_upload['UploadId']
        self.part_count = 1
        self.parts = []

    def getPart(self):
        return self.part_count

    def uploadPart(self, body, size, buffer_size):
        res = self.client.upload_part(**self.target,
                                      UploadId=self.upload_id,
                                      PartNumber=self.part_count,
                                      Body=body if size == buffer_size
                                      else body[0:size])

        print(res)
        self.parts.append({'ETag': res['ETag'], 'PartNumber': self.part_count})
        self.part_count += 1

    def abort(self):
        res = self.client.abort_multipart_upload(**self.target,
                                                 UploadId=self.upload_id)
        print(res)

    def complete(self):
        res = self.client.complete_multipart_upload(**self.target,
                                                    MultipartUpload={'Parts': self.parts},
                                                    UploadId=self.upload_id)
        print(res)

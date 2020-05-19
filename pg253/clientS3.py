import boto3


class ClientS3:
    def __init__(self, config, key):
        self.client = boto3.client('s3',
                                   endpoint_url=config.aws_endpoint,
                                   aws_access_key_id=config.aws_access_key_id,
                                   aws_secret_access_key=config.aws_secret_access_key)

        self.target = {'Bucket': config.aws_s3_bucket,
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
        return res

    def abort(self):
        res = self.client.abort_multipart_upload(**self.target,
                                                 UploadId=self.upload_id)
        print(res)

    def complete(self):
        res = self.client.complete_multipart_upload(**self.target,
                                                    MultipartUpload={'Parts': self.parts},
                                                    UploadId=self.upload_id)
        return res

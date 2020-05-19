import boto3


class ClientS3:
    def __init__(self, config):
        self.config = config
        self.client = boto3.client('s3',
                                   endpoint_url=config.aws_endpoint,
                                   aws_access_key_id=config.aws_access_key_id,
                                   aws_secret_access_key=config.aws_secret_access_key)

    def createMultipartUpload(self, key):
        return Upload(self.client, self.config.aws_s3_bucket, key)

    def listContent(self, prefix):

        continuation_token = None
        marker = None
        fetch_method = "V2"
        while True:
            s3_args = {
                "Bucket": self.config.aws_s3_bucket,
                "Prefix": prefix,
            }
            if fetch_method == "V2" and continuation_token:
                s3_args["ContinuationToken"] = continuation_token
            if fetch_method == "V1" and marker:
                s3_args["Marker"] = marker

            # Fetch results by on method
            if fetch_method == "V1":
                response = self.client.list_objects(**s3_args)
            elif fetch_method == "V2":
                response = self.client.list_objects_v2(**s3_args)
            else:
                raise Exception("Invalid fetch method")

            # Check if pagination is broken in V2
            if (fetch_method == "V2" and response.get("IsTruncated")
                    and "NextContinuationToken" not in response):
                # Fallback to list_object() V1 if NextContinuationToken
                # is not in response
                print("Pagination broken, falling back to list_object V1")
                fetch_method = "V1"
                response = self.client.list_objects(**s3_args)

            for item in response.get("Contents", []):
                yield item['Key'].replace(prefix,'')

            if response.get("IsTruncated"):
                if fetch_method == "V1":
                    marker = response.get('NextMarker')
                elif fetch_method == "V2":
                    continuation_token = response["NextContinuationToken"]
                else:
                    raise Exception("Invalid fetch method")
            else:
                break





class Upload:

    def __init__(self, client, bucket, key):
        self.client = client
        self.target = {'Bucket': bucket,
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

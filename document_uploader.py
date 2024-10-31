import boto3
from botocore.exceptions import NoCredentialsError, ClientError

class DocumentUploader:
    def __init__(self, bucket_name, region, access_key, secret_key):
        self.bucket_name = bucket_name
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
        )

    def upload_file(self, file_obj, file_name):
        try:
            self.s3_client.upload_fileobj(file_obj, self.bucket_name, file_name)
            return f"https://{self.bucket_name}.s3.{self.s3_client.meta.region_name}.amazonaws.com/{file_name}"
        except (NoCredentialsError, ClientError) as e:
            raise Exception("Could not upload file to S3.") from e 
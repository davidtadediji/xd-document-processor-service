import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from app.utils.logger import logger


class DocumentUploader:
    def __init__(self, bucket_name, region, access_key, secret_key):
        self.bucket_name = bucket_name
        self.region_name = region
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=self.region_name,
        )

    def upload_file(self, file_content: bytes, file_name: str) -> str:
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name, Key=file_name, Body=file_content
            )
            file_url = f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{file_name}"
            logger.debug(f"File uploaded to S3: {file_url}")
            return file_url
        except (NoCredentialsError, ClientError) as e:
            logger.error(f"S3 upload error: {e}")
            raise Exception("Could not upload file to S3.") from e

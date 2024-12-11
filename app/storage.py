import boto3
import secrets

AWS_ACCESS_KEY = "your_access_key"
AWS_SECRET_KEY = "your_secret_key"
S3_BUCKET = "your_bucket_name"
S3_REGION = "your_region"

def upload_to_s3(content: str, filename: str) -> str:
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=S3_REGION,
    )
    object_name = f"texts/{filename}"
    s3_client.put_object(Bucket=S3_BUCKET, Key=object_name, Body=content)
    return f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{object_name}"

def generate_short_key(length: int = 8) -> str:
    return secrets.token_urlsafe(length)[:length]

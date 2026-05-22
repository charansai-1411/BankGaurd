import os
import boto3
from botocore.config import Config

def get_r2_client():
    """
    Returns boto3 S3 client targeted at Cloudflare R2 storage endpoint.
    """
    endpoint_url = os.getenv("R2_ENDPOINT_URL", "")
    access_key = os.getenv("R2_ACCESS_KEY_ID", "")
    secret_key = os.getenv("R2_SECRET_ACCESS_KEY", "")
    
    # Strip quotes
    if endpoint_url.startswith('"') and endpoint_url.endswith('"'):
        endpoint_url = endpoint_url[1:-1]
    if access_key.startswith('"') and access_key.endswith('"'):
        access_key = access_key[1:-1]
    if secret_key.startswith('"') and secret_key.endswith('"'):
        secret_key = secret_key[1:-1]
        
    return boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(signature_version="s3v4"),
        region_name="auto"
    )

def upload_file_to_r2(local_path: str, r2_key: str) -> str:
    """
    Uploads a local file to R2 bucket and returns its pre-signed reference URL.
    """
    bucket_name = os.getenv("R2_BUCKET_NAME", "bankguard")
    if bucket_name.startswith('"') and bucket_name.endswith('"'):
        bucket_name = bucket_name[1:-1]
        
    client = get_r2_client()
    
    # Upload the file
    client.upload_file(local_path, bucket_name, r2_key)
    
    # Generate a signed URL for retrieval (valid for 7 days = 604800 seconds)
    url = client.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": bucket_name, "Key": r2_key},
        ExpiresIn=604800
    )
    return url


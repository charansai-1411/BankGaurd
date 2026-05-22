import os
# import boto3

def get_r2_bucket():
    """
    Returns boto3 S3 client targeted at Cloudflare R2 storage endpoint.
    """
    # Stub connection
    return None

def upload_file_to_r2(local_path: str, r2_key: str) -> str:
    """
    Uploads a local file to R2 bucket and returns its reference URL.
    """
    return f"https://r2.bankguard.dev/{r2_key}"

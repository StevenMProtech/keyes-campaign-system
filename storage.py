"""
Secure file storage using DigitalOcean Spaces (S3-compatible)
"""
import os
import boto3
from botocore.client import Config
from datetime import datetime

# Initialize S3 client for DigitalOcean Spaces
def get_spaces_client():
    """Get configured boto3 client for DigitalOcean Spaces"""
    session = boto3.session.Session()
    client = session.client('s3',
        region_name=os.environ.get('SPACES_REGION', 'nyc3'),
        endpoint_url=f"https://{os.environ.get('SPACES_REGION', 'nyc3')}.digitaloceanspaces.com",
        aws_access_key_id=os.environ.get('SPACES_KEY'),
        aws_secret_access_key=os.environ.get('SPACES_SECRET'),
        config=Config(signature_version='s3v4')
    )
    return client

def upload_file_to_spaces(file_obj, filename):
    """
    Upload a file to DigitalOcean Spaces
    
    Args:
        file_obj: File object or path to upload
        filename: Name to save as in Spaces
    
    Returns:
        dict: {'success': bool, 'key': str, 'message': str}
    """
    try:
        client = get_spaces_client()
        bucket = os.environ.get('SPACES_BUCKET')
        
        # Add timestamp to filename to avoid conflicts
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        key = f"client-data/{timestamp}_{filename}"
        
        # Upload with server-side encryption
        client.upload_fileobj(
            file_obj,
            bucket,
            key,
            ExtraArgs={
                'ACL': 'private',  # Private file
                'ServerSideEncryption': 'AES256'  # Encryption at rest
            }
        )
        
        return {
            'success': True,
            'key': key,
            'message': f'File uploaded successfully: {key}'
        }
    except Exception as e:
        return {
            'success': False,
            'key': None,
            'message': f'Upload failed: {str(e)}'
        }

def download_file_from_spaces(key, local_path):
    """
    Download a file from DigitalOcean Spaces
    
    Args:
        key: File key in Spaces
        local_path: Local path to save file
    
    Returns:
        dict: {'success': bool, 'path': str, 'message': str}
    """
    try:
        client = get_spaces_client()
        bucket = os.environ.get('SPACES_BUCKET')
        
        client.download_file(bucket, key, local_path)
        
        return {
            'success': True,
            'path': local_path,
            'message': f'File downloaded successfully to {local_path}'
        }
    except Exception as e:
        return {
            'success': False,
            'path': None,
            'message': f'Download failed: {str(e)}'
        }

def list_files_in_spaces(prefix='client-data/'):
    """
    List all files in Spaces with given prefix
    
    Args:
        prefix: Folder prefix to filter files
    
    Returns:
        list: List of file objects with keys and metadata
    """
    try:
        client = get_spaces_client()
        bucket = os.environ.get('SPACES_BUCKET')
        
        response = client.list_objects_v2(Bucket=bucket, Prefix=prefix)
        
        if 'Contents' not in response:
            return []
        
        files = []
        for obj in response['Contents']:
            files.append({
                'key': obj['Key'],
                'size': obj['Size'],
                'last_modified': obj['LastModified'],
                'filename': obj['Key'].split('/')[-1]
            })
        
        return files
    except Exception as e:
        print(f"Error listing files: {str(e)}")
        return []

def delete_file_from_spaces(key):
    """
    Delete a file from DigitalOcean Spaces
    
    Args:
        key: File key to delete
    
    Returns:
        dict: {'success': bool, 'message': str}
    """
    try:
        client = get_spaces_client()
        bucket = os.environ.get('SPACES_BUCKET')
        
        client.delete_object(Bucket=bucket, Key=key)
        
        return {
            'success': True,
            'message': f'File deleted successfully: {key}'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Delete failed: {str(e)}'
        }

def get_file_url(key, expiration=3600):
    """
    Generate a presigned URL for temporary file access
    
    Args:
        key: File key in Spaces
        expiration: URL expiration time in seconds (default 1 hour)
    
    Returns:
        str: Presigned URL or None if failed
    """
    try:
        client = get_spaces_client()
        bucket = os.environ.get('SPACES_BUCKET')
        
        url = client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket, 'Key': key},
            ExpiresIn=expiration
        )
        
        return url
    except Exception as e:
        print(f"Error generating URL: {str(e)}")
        return None


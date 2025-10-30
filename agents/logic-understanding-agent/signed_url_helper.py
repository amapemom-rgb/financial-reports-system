"""
Helper functions for generating signed URLs using IAM signBlob API

This module provides IAM-based signed URL generation for Cloud Run environments
where service account private keys are not available.

Session 20: Bug #2 Fix - Manual signed URL generation using IAM API
"""
import base64
import datetime
import hashlib
from typing import Dict
from urllib.parse import quote
import requests
import google.auth
from google.auth.transport import requests as google_requests


def generate_signed_url_v4(
    bucket_name: str,
    blob_name: str,
    service_account_email: str,
    expiration_minutes: int = 15,
    http_method: str = "PUT",
    content_type: str = "application/octet-stream"
) -> str:
    """Generate a v4 signed URL using IAM signBlob API
    
    This function manually constructs a signed URL by:
    1. Building the canonical request
    2. Signing it using IAM signBlob API
    3. Constructing the final signed URL
    
    Args:
        bucket_name: GCS bucket name
        blob_name: Object path in bucket
        service_account_email: Service account email for signing
        expiration_minutes: URL expiration time in minutes
        http_method: HTTP method (GET, PUT, POST, etc.)
        content_type: Content-Type header value
        
    Returns:
        Signed URL string
        
    Raises:
        Exception: If signing fails
    """
    # Get credentials
    credentials, project_id = google.auth.default()
    auth_request = google_requests.Request()
    credentials.refresh(auth_request)
    
    # Calculate expiration timestamp
    now = datetime.datetime.utcnow()
    expiration = now + datetime.timedelta(minutes=expiration_minutes)
    expiration_timestamp = int(expiration.timestamp())
    
    # Format date strings
    datestamp = now.strftime('%Y%m%d')
    timestamp = now.strftime('%Y%m%dT%H%M%SZ')
    
    # Credential scope
    credential_scope = f"{datestamp}/auto/storage/goog4_request"
    credential = f"{service_account_email}/{credential_scope}"
    
    # Canonical headers
    canonical_headers = f"host:storage.googleapis.com\n"
    if content_type:
        canonical_headers += f"content-type:{content_type}\n"
    
    signed_headers = "host"
    if content_type:
        signed_headers += ";content-type"
    
    # Query parameters
    query_params = {
        'X-Goog-Algorithm': 'GOOG4-RSA-SHA256',
        'X-Goog-Credential': credential,
        'X-Goog-Date': timestamp,
        'X-Goog-Expires': str(expiration_minutes * 60),
        'X-Goog-SignedHeaders': signed_headers,
    }
    
    # Canonical query string
    canonical_query_string = '&'.join([
        f"{quote(key, safe='')}={quote(str(value), safe='')}"
        for key, value in sorted(query_params.items())
    ])
    
    # Canonical request
    canonical_request = '\n'.join([
        http_method,
        f"/{blob_name}",
        canonical_query_string,
        canonical_headers,
        signed_headers,
        'UNSIGNED-PAYLOAD'
    ])
    
    # String to sign
    canonical_request_hash = hashlib.sha256(canonical_request.encode()).hexdigest()
    string_to_sign = '\n'.join([
        'GOOG4-RSA-SHA256',
        timestamp,
        credential_scope,
        canonical_request_hash
    ])
    
    # Sign using IAM API
    iam_endpoint = f"https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/{service_account_email}:signBlob"
    
    headers = {
        'Authorization': f'Bearer {credentials.token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'payload': base64.b64encode(string_to_sign.encode()).decode()
    }
    
    response = requests.post(iam_endpoint, json=payload, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"IAM signBlob failed: {response.status_code} - {response.text}")
    
    signature = response.json()['signedBlob']
    
    # Construct final URL
    base_url = f"https://storage.googleapis.com/{bucket_name}/{blob_name}"
    final_url = f"{base_url}?{canonical_query_string}&X-Goog-Signature={signature}"
    
    return final_url

"""
Upload handlers for signed URL file upload (Session 20: Bug #2 Fix)

This module provides endpoints for secure file uploads using the Signed URL pattern.
"""
import os
import uuid
import logging
from datetime import timedelta
from typing import Optional
from fastapi import HTTPException
from pydantic import BaseModel
from google.cloud import storage

logger = logging.getLogger(__name__)

# Configuration
PROJECT_ID = os.getenv("PROJECT_ID", "financial-reports-ai-2024")
REPORTS_BUCKET = os.getenv("REPORTS_BUCKET", "financial-reports-ai-2024-reports")

# Initialize Cloud Storage client
try:
    storage_client = storage.Client(project=PROJECT_ID)
    storage_bucket = storage_client.bucket(REPORTS_BUCKET)
    logger.info(f"✅ Storage client initialized for bucket: {REPORTS_BUCKET}")
except Exception as e:
    logger.error(f"❌ Failed to initialize Storage client: {e}")
    storage_client = None
    storage_bucket = None


# Request/Response Models
class SignedUrlRequest(BaseModel):
    """Request model for signed URL generation"""
    filename: str
    content_type: Optional[str] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class SignedUrlResponse(BaseModel):
    """Response model for signed URL"""
    upload_url: str
    file_id: str
    file_path: str
    expires_in_minutes: int = 15


class UploadCompleteRequest(BaseModel):
    """Request model for upload completion notification"""
    file_id: str
    file_path: str


# Endpoint Handlers
async def generate_signed_url(request: SignedUrlRequest) -> SignedUrlResponse:
    """Generate signed URL for direct client upload to GCS
    
    This function implements the Signed URL Pattern for secure file uploads:
    1. Client requests signed URL
    2. Server generates temporary URL (valid 15 minutes)
    3. Client uploads file directly to GCS using PUT
    4. Client notifies server via /upload/complete
    
    Session 20: Bug #2 Fix - Enable secure file upload from browser
    """
    try:
        if not storage_client or not storage_bucket:
            raise HTTPException(
                status_code=503,
                detail="Storage service unavailable"
            )
        
        # Validate file type
        allowed_extensions = ['.xlsx', '.xls', '.csv']
        file_ext = os.path.splitext(request.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Generate unique file ID and path
        file_id = f"{uuid.uuid4().hex}_{request.filename}"
        file_path = f"reports/{file_id}"
        
        logger.info(f"Generating signed URL for: {file_path}")
        
        # Get blob reference
        blob = storage_bucket.blob(file_path)
        
        # Generate signed URL (valid for 15 minutes)
        signed_url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=15),
            method="PUT",
            content_type=request.content_type
        )
        
        logger.info(f"✅ Signed URL generated for: {file_path}")
        
        return SignedUrlResponse(
            upload_url=signed_url,
            file_id=file_id,
            file_path=file_path,
            expires_in_minutes=15
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to generate signed URL: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate signed URL: {str(e)}"
        )


async def upload_complete(request: UploadCompleteRequest) -> dict:
    """Verify that file upload completed successfully
    
    This function is called by the client after successfully uploading
    the file to GCS using the signed URL. It verifies that the file
    exists and is accessible.
    
    Session 20: Bug #2 Fix - Upload completion verification
    """
    try:
        if not storage_client or not storage_bucket:
            raise HTTPException(
                status_code=503,
                detail="Storage service unavailable"
            )
        
        logger.info(f"Verifying upload completion for: {request.file_path}")
        
        # Verify file exists
        blob = storage_bucket.blob(request.file_path)
        
        if not blob.exists():
            raise HTTPException(
                status_code=404,
                detail="File not found in storage. Upload may have failed."
            )
        
        # Get file metadata
        blob.reload()
        file_size = blob.size
        
        logger.info(f"✅ File upload verified: {request.file_path} ({file_size} bytes)")
        
        from datetime import datetime
        return {
            "status": "success",
            "message": "File upload completed and verified",
            "file_id": request.file_id,
            "file_path": request.file_path,
            "file_size_bytes": file_size,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Upload verification failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Upload verification failed: {str(e)}"
        )

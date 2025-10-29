# Session 20 Priority 1: Backend Changes for main.py

## Changes needed in `agents/logic-understanding-agent/main.py`

### 1. Update imports (line ~24)
```python
# OLD:
from google.cloud import secretmanager, firestore

# NEW:
from google.cloud import secretmanager, firestore, storage
```

### 2. Update datetime import (line ~7)
```python
# OLD:
from datetime import datetime

# NEW:
from datetime import datetime, timedelta
```

### 3. Add GCS bucket configuration (after line ~58, after REPORT_READER_URL)
```python
# GCS Configuration for file uploads (Session 20: Bug #2 Fix)
REPORTS_BUCKET = os.getenv("REPORTS_BUCKET", "financial-reports-ai-2024-reports")
```

### 4. Initialize Storage client (after line ~70, after Firestore initialization)
```python
# Initialize Cloud Storage client (Session 20: Bug #2 Fix)
try:
    storage_client = storage.Client(project=PROJECT_ID)
    storage_bucket = storage_client.bucket(REPORTS_BUCKET)
    logger.info(f"✅ Storage client initialized for bucket: {REPORTS_BUCKET}")
except Exception as e:
    logger.error(f"❌ Failed to initialize Storage client: {e}")
    storage_client = None
    storage_bucket = None
```

### 5. Add new Pydantic models (after AnalyzeSheetRequest class, around line ~190)
```python
class SignedUrlRequest(BaseModel):
    """Request model for signed URL generation (Session 20)"""
    filename: str
    content_type: Optional[str] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

class SignedUrlResponse(BaseModel):
    """Response model for signed URL (Session 20)"""
    upload_url: str
    file_id: str
    file_path: str
    expires_in_minutes: int = 15

class UploadCompleteRequest(BaseModel):
    """Request model for upload completion notification (Session 20)"""
    file_id: str
    file_path: str
```

### 6. Add new endpoints (after /regenerate endpoint, before /test-connection, around line ~820)
```python
@app.post("/upload/signed-url", response_model=SignedUrlResponse)
async def generate_signed_url(request: SignedUrlRequest):
    """Generate signed URL for direct client upload to GCS
    
    This endpoint implements the Signed URL Pattern for secure file uploads:
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

@app.post("/upload/complete")
async def upload_complete(request: UploadCompleteRequest):
    """Verify that file upload completed successfully
    
    This endpoint is called by the client after successfully uploading
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
```

### 7. Update /health endpoint (around line ~300)
Add to features list:
```python
"features": [
    "dynamic_prompts", 
    "secret_manager", 
    "user_feedback", 
    "regenerate", 
    "cors_enabled",
    "multi_sheet_intelligence",
    "report_reader_retry_logic",
    "firestore_retry_logic",
    "gemini_explicit_timeout",
    "signed_url_upload"  # NEW
]
```

---

## Verification after changes

Test the new endpoints:
```bash
# 1. Request signed URL
curl -X POST https://logic-understanding-agent-38390150695.us-central1.run.app/upload/signed-url \
  -H "Content-Type: application/json" \
  -d '{"filename": "test.xlsx", "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}'

# Should return:
# {
#   "upload_url": "https://storage.googleapis.com/...",
#   "file_id": "...",
#   "file_path": "reports/...",
#   "expires_in_minutes": 15
# }

# 2. Upload file using signed URL (from browser or curl)
# PUT request to upload_url with file content

# 3. Verify upload completion
curl -X POST https://logic-understanding-agent-38390150695.us-central1.run.app/upload/complete \
  -H "Content-Type: application/json" \
  -d '{"file_id": "...", "file_path": "reports/..."}'
```

---

## Next steps
After applying these changes:
1. Build Docker image: `v12-upload-fix`
2. Deploy to Cloud Run
3. Test endpoints
4. Move to Priority 2: Frontend updates
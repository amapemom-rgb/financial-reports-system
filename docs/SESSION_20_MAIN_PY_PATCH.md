# Session 20: Patch for main.py - Use IAM signBlob helper

## Changes Required

In `agents/logic-understanding-agent/main.py`, replace the `generate_signed_url_endpoint` function:

### FIND THIS (lines ~750-800):

```python
@app.post("/upload/signed-url", response_model=SignedUrlResponse)
async def generate_signed_url_endpoint(request: SignedUrlRequest):
    """Generate signed URL for direct client upload to GCS
    
    This endpoint implements the Signed URL Pattern for secure file uploads:
    1. Client requests signed URL
    2. Server generates temporary URL (valid 15 minutes)
    3. Client uploads file directly to GCS using PUT
    4. Client notifies server via /upload/complete
    
    Session 20: Bug #2 Fix - IAM-based signing using iam.Signer
    Uses IAM signBlob API instead of service account private key
    """
    try:
        if not storage_client or not storage_bucket:
            raise HTTPException(
                status_code=503,
                detail="Storage service unavailable"
            )
        
        if not service_account_email or not credentials:
            raise HTTPException(
                status_code=503,
                detail="Service account configuration unavailable"
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
        
        # 🎯 KEY FIX: Create IAM-based signer object
        # This uses the IAM signBlob API instead of requiring private key
        signing_credentials = iam.Signer(
            request=google_requests.Request(),
            credentials=credentials,  # default credentials from google.auth.default()
            service_account_email=service_account_email
        )
        
        # Generate signed URL with IAM signer
        signed_url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=15),
            method="PUT",
            content_type=request.content_type,
            credentials=signing_credentials  # 🎯 Pass IAM Signer here!
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
```

### REPLACE WITH THIS:

```python
@app.post("/upload/signed-url", response_model=SignedUrlResponse)
async def generate_signed_url_endpoint(request: SignedUrlRequest):
    """Generate signed URL for direct client upload to GCS
    
    This endpoint implements the Signed URL Pattern for secure file uploads:
    1. Client requests signed URL
    2. Server generates temporary URL (valid 15 minutes)
    3. Client uploads file directly to GCS using PUT
    4. Client notifies server via /upload/complete
    
    Session 20: Bug #2 Fix - Manual IAM signBlob API
    Uses IAM signBlob API directly instead of service account private key
    """
    try:
        if not storage_bucket:
            raise HTTPException(
                status_code=503,
                detail="Storage service unavailable"
            )
        
        if not service_account_email:
            raise HTTPException(
                status_code=503,
                detail="Service account configuration unavailable"
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
        blob_name = f"reports/{file_id}"
        
        logger.info(f"Generating signed URL for: {blob_name}")
        
        # Import helper function
        from signed_url_helper import generate_signed_url_v4
        
        # 🎯 FIXED: Use manual IAM signBlob implementation
        signed_url = generate_signed_url_v4(
            bucket_name=REPORTS_BUCKET,
            blob_name=blob_name,
            service_account_email=service_account_email,
            expiration_minutes=15,
            http_method="PUT",
            content_type=request.content_type
        )
        
        logger.info(f"✅ Signed URL generated for: {blob_name}")
        
        return SignedUrlResponse(
            upload_url=signed_url,
            file_id=file_id,
            file_path=blob_name,
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
```

### ALSO ADD THIS IMPORT at the top of main.py:

After line with `from google.auth.transport import requests as google_requests`, add:

```python
# Session 20: IAM signBlob helper
from signed_url_helper import generate_signed_url_v4
```

### REMOVE UNUSED IMPORTS:

Remove these lines (no longer needed):
```python
from google.auth import iam
```

## Summary

- ✅ Created `signed_url_helper.py` with manual IAM signBlob implementation
- ✅ Added dependencies: `google-auth` and `google-cloud-iam`
- ⏭️ **TODO:** Update `main.py` to use the helper function
- ⏭️ **TODO:** Rebuild and redeploy

## Quick Apply (manual):

```bash
cd agents/logic-understanding-agent

# Edit main.py and make the changes above
vim main.py

# Or use sed (be careful!):
# ... (commands to replace the function)
```

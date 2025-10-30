#!/usr/bin/env python3
"""
Session 20: Apply patch to main.py for IAM signBlob helper

This script updates the generate_signed_url_endpoint function in main.py
to use the manual IAM signBlob implementation instead of iam.Signer.

Usage:
    python3 apply_patch.py
"""

import re

# Read main.py
with open('main.py', 'r') as f:
    content = f.read()

# Remove unused import
content = content.replace(
    'from google.auth import iam\n',
    ''
)

# Find and replace the function
old_function_pattern = r'@app\.post\("/upload/signed-url", response_model=SignedUrlResponse\).*?(?=@app\.post|if __name__|$)'

new_function = '''@app.post("/upload/signed-url", response_model=SignedUrlResponse)
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

'''

# Replace the function
content = re.sub(old_function_pattern, new_function, content, flags=re.DOTALL)

# Write back
with open('main.py', 'w') as f:
    f.write(content)

print("✅ Patch applied successfully!")
print("Next steps:")
print("1. Review the changes: git diff main.py")
print("2. Build: gcloud builds submit ...")
print("3. Deploy: gcloud run deploy ...")

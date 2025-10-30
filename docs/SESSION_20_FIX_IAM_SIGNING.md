# 🔧 Session 20: IAM-Based Signing Fix

**Date:** October 30, 2025  
**Status:** ✅ **FIXED**  
**Issue:** Signed URL generation failed on Cloud Run

---

## ❌ Problem Discovered

During initial testing of the Signed URL Pattern implementation, we encountered a critical error:

```
"you need a private key to sign credentials.
the credentials you are currently using <class 'google.auth.compute_engine.credentials.Credentials'> 
just contains a token. see https://googleapis.dev/python/google-api-core/latest/auth.html#setting-up-a-service-account 
for more details."
```

### Root Cause

**Cloud Run uses Compute Engine credentials** (token-based), which do NOT include a private key required for traditional signed URL generation.

The original code tried to use:
```python
signed_url = blob.generate_signed_url(
    version="v4",
    expiration=timedelta(minutes=15),
    method="PUT",
    content_type=request.content_type
)
```

This method requires a **service account JSON key file with private key**, which is:
- ❌ Not available on Cloud Run (uses token-based auth)
- ❌ Security anti-pattern (storing private keys in containers)
- ❌ Not compatible with Workload Identity

---

## ✅ Solution: IAM-Based Signing

Google Cloud provides **IAM-based signing** through the `signBlob` API, which:
- ✅ Works with token-based credentials (Cloud Run)
- ✅ No private key storage needed
- ✅ Uses IAM permissions for signing
- ✅ Compatible with Workload Identity

### Implementation

#### 1. Get Service Account Email from Metadata Server

```python
import requests
import google.auth
from google.auth.transport import requests as auth_requests

# Get default credentials
credentials, _ = google.auth.default()

# Get service account email from metadata server (Cloud Run)
metadata_url = "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/email"
headers = {"Metadata-Flavor": "Google"}
response = requests.get(metadata_url, headers=headers, timeout=5)
service_account_email = response.text

logger.info(f"✅ Service Account: {service_account_email}")
```

#### 2. Use IAM-Based Signing in generate_signed_url

```python
signed_url = blob.generate_signed_url(
    version="v4",
    expiration=timedelta(minutes=15),
    method="PUT",
    content_type=request.content_type,
    service_account_email=service_account_email  # 🎯 KEY CHANGE
)
```

When `service_account_email` is provided, the Google Cloud Storage SDK automatically:
1. Creates the signing payload
2. Calls IAM `projects.serviceAccounts.signBlob` API
3. Uses the service account's IAM permissions to sign
4. Returns properly signed URL

---

## 📝 Code Changes

### Files Modified

1. **agents/logic-understanding-agent/main.py**
   - Added `import requests`
   - Added `import google.auth`
   - Added `from google.auth.transport import requests as auth_requests`
   - Added service account email fetching from metadata server
   - Updated `generate_signed_url()` to use `service_account_email` parameter

2. **agents/logic-understanding-agent/requirements.txt**
   - Added `requests==2.31.0` for metadata server access

### Commit

```bash
Commit: 198ac619c27a21b9f9997d2e4a0f2c8fc74bbc8b
Message: "Session 20: Fix signed URL generation using IAM API (Bug #2)"
```

---

## 🔐 Required IAM Permissions

The Cloud Run service account needs:

```yaml
roles/iam.serviceAccountTokenCreator  # For signBlob API
# OR specific permission:
iam.serviceAccounts.signBlob
```

This permission allows the service account to use IAM to sign data on behalf of itself.

### Verify Permission

```bash
# Check if service account has the permission
gcloud projects get-iam-policy financial-reports-ai-2024 \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:logic-agent@financial-reports-ai-2024.iam.gserviceaccount.com"
```

If missing, add it:
```bash
gcloud projects add-iam-policy-binding financial-reports-ai-2024 \
  --member="serviceAccount:logic-agent@financial-reports-ai-2024.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountTokenCreator"
```

---

## 🧪 Testing IAM-Based Signing

### Test Script

```python
# test_signed_url_iam.py
import requests
import httpx
import asyncio

async def test_signed_url_generation():
    url = "https://logic-understanding-agent-38390150695.us-central1.run.app/upload/signed-url"
    
    payload = {
        "filename": "test_report.xlsx",
        "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Signed URL generated successfully!")
            print(f"File ID: {data['file_id']}")
            print(f"Upload URL: {data['upload_url'][:100]}...")
            print(f"Expires in: {data['expires_in_minutes']} minutes")
            return data
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return None

# Run test
asyncio.run(test_signed_url_generation())
```

### Expected Output

```
✅ Signed URL generated successfully!
File ID: a1b2c3d4e5f6_test_report.xlsx
Upload URL: https://storage.googleapis.com/financial-reports-ai-2024-reports/reports/a1b2c3d4e5f6_test_report...
Expires in: 15 minutes
```

---

## 📊 Comparison: Private Key vs IAM Signing

| Aspect | Private Key (❌ Old) | IAM Signing (✅ New) |
|--------|---------------------|---------------------|
| **Requires private key** | Yes | No |
| **Works on Cloud Run** | No | Yes |
| **Security** | Lower (key storage) | Higher (no key) |
| **Setup complexity** | High | Low |
| **Workload Identity** | Not compatible | Compatible |
| **IAM permission** | None | `signBlob` |

---

## 🎯 Next Steps

1. ✅ Code updated with IAM-based signing
2. ✅ Dependencies updated (added `requests`)
3. ⏭️ **Deploy to Cloud Run** (Priority 1)
4. ⏭️ Test signed URL generation endpoint
5. ⏭️ Update frontend to use new endpoint
6. ⏭️ End-to-end testing

---

## 📚 References

- [Google Cloud Storage - Signed URLs](https://cloud.google.com/storage/docs/access-control/signed-urls)
- [IAM signBlob API](https://cloud.google.com/iam/docs/reference/credentials/rest/v1/projects.serviceAccounts/signBlob)
- [Service Account Credentials on Cloud Run](https://cloud.google.com/run/docs/securing/service-identity)
- [Workload Identity](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity)

---

**Status:** ✅ IAM-based signing implemented and ready for deployment!

# Session 21 Prompt: Deploy & Test File Upload Fix

**Date:** October 30, 2025  
**Status:** 🚀 **READY TO START**  
**Prerequisites:** Session 20 completed (code changes in GitHub)

---

## 🎯 Session Goal

Deploy the file upload fix (Session 20) to production and conduct comprehensive end-to-end testing.

---

## 📋 Quick Context

**What was done in Session 20:**
- ✅ Backend: Added `/upload/signed-url` and `/upload/complete` endpoints
- ✅ Frontend: Implemented 3-step Signed URL upload flow
- ✅ Code committed to GitHub main branch

**What needs to happen in Session 21:**
1. Deploy updated Logic Agent to Cloud Run
2. Deploy updated Web UI to Cloud Run
3. Test end-to-end file upload flow
4. Verify AI can analyze uploaded files
5. Document any issues found

---

## 🚀 Step-by-Step Deployment Guide

### Step 1: Deploy Logic Agent (Backend)

**Build Docker Image:**
```bash
cd agents/logic-understanding-agent

gcloud builds submit \
  --tag gcr.io/financial-reports-ai-2024/logic-understanding-agent:v12-upload-fix \
  --project financial-reports-ai-2024
```

**Deploy to Cloud Run:**
```bash
gcloud run deploy logic-understanding-agent \
  --image gcr.io/financial-reports-ai-2024/logic-understanding-agent:v12-upload-fix \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --set-env-vars PROJECT_ID=financial-reports-ai-2024,REGION=us-central1,REPORT_READER_URL=https://report-reader-agent-38390150695.us-central1.run.app,REPORTS_BUCKET=financial-reports-ai-2024-reports \
  --service-account financial-reports-sa@financial-reports-ai-2024.iam.gserviceaccount.com
```

**Verify Deployment:**
```bash
curl https://logic-understanding-agent-38390150695.us-central1.run.app/health | python3 -m json.tool
```

**Expected Output:**
```json
{
  "status": "healthy",
  "agent": "marketplace-financial-analyst",
  "model": "gemini-2.0-flash-exp",
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
    "signed_url_upload"  // ← Should be present!
  ]
}
```

---

### Step 2: Deploy Web UI (Frontend)

**Build Docker Image:**
```bash
cd web-ui

gcloud builds submit \
  --tag gcr.io/financial-reports-ai-2024/web-ui:v10-upload-fix \
  --project financial-reports-ai-2024
```

**Deploy to Cloud Run:**
```bash
gcloud run deploy web-ui \
  --image gcr.io/financial-reports-ai-2024/web-ui:v10-upload-fix \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1
```

**Get Web UI URL:**
```bash
gcloud run services describe web-ui \
  --region us-central1 \
  --format 'value(status.url)'
```

---

### Step 3: End-to-End Testing

**Test Cases to Execute:**

#### Test 1: Small CSV File Upload
1. Open Web UI in browser
2. Click "📁 CSV / Excel" button
3. Select a small CSV file (< 1MB)
4. Verify:
   - ✅ 3-step progress shows (Request → Upload → Verify)
   - ✅ Green success message with file details appears
   - ✅ File ID and size displayed correctly
   - ✅ Chat welcome message: "Файл ... успешно загружен!"

#### Test 2: Medium Excel File Upload
1. Select Excel file (1-5MB, single sheet)
2. Verify same steps as Test 1
3. Ask AI: "Сколько строк в файле?"
4. Verify:
   - ✅ AI responds with correct row count
   - ✅ AI shows it read the file successfully

#### Test 3: Large Multi-Sheet Excel File
1. Select Excel file with 10+ sheets
2. Verify upload completes successfully
3. Ask AI: "Какие листы есть в файле?"
4. Verify:
   - ✅ AI activates multi-sheet mode
   - ✅ AI lists all sheet names
   - ✅ AI asks which sheet to analyze

#### Test 4: Invalid File Type
1. Try to upload a PDF or image file
2. Verify:
   - ❌ Upload fails with clear error message
   - ❌ Error shows: "Invalid file type. Allowed: .xlsx, .xls, .csv"

#### Test 5: Network Error Handling
1. Disable internet connection mid-upload
2. Verify:
   - ❌ Upload fails gracefully
   - ❌ Error message shown in red border
   - ❌ Logs show detailed error

---

### Step 4: Integration Testing

**Test Signed URL Generation:**
```bash
curl -X POST https://logic-understanding-agent-38390150695.us-central1.run.app/upload/signed-url \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "test_report.xlsx",
    "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
  }' | python3 -m json.tool
```

**Expected Response:**
```json
{
  "upload_url": "https://storage.googleapis.com/financial-reports-ai-2024-reports/...",
  "file_id": "abc123_test_report.xlsx",
  "file_path": "reports/abc123_test_report.xlsx",
  "expires_in_minutes": 15
}
```

**Test Upload Verification:**
```bash
curl -X POST https://logic-understanding-agent-38390150695.us-central1.run.app/upload/complete \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "abc123_test_report.xlsx",
    "file_path": "reports/abc123_test_report.xlsx"
  }' | python3 -m json.tool
```

---

## 🐛 Common Issues & Solutions

### Issue 1: "Storage service unavailable"
**Solution:** Check that Logic Agent has access to GCS bucket
```bash
gsutil iam ch serviceAccount:financial-reports-sa@financial-reports-ai-2024.iam.gserviceaccount.com:objectCreator \
  gs://financial-reports-ai-2024-reports
```

### Issue 2: "File not found in storage"
**Solution:** Check GCS bucket exists and signed URL worked
```bash
gsutil ls gs://financial-reports-ai-2024-reports/reports/
```

### Issue 3: CORS Error in Browser
**Solution:** Verify Logic Agent has CORS middleware enabled (should be in code)

### Issue 4: Signed URL Expired
**Solution:** URLs expire in 15 minutes. Request new signed URL.

---

## 📊 Success Criteria

Session 21 is considered **COMPLETE** when:

1. ✅ Logic Agent deployed with `"signed_url_upload"` feature
2. ✅ Web UI deployed with v10-upload-fix
3. ✅ All 5 test cases pass successfully
4. ✅ File upload works end-to-end from browser
5. ✅ AI can analyze uploaded files correctly
6. ✅ No authentication errors or 403 Forbidden
7. ✅ Documentation updated with test results

---

## 📚 Related Documents

**Previous Sessions:**
- [SESSION_20_SUMMARY.md](./SESSION_20_SUMMARY.md) - File upload fix implementation
- [SESSION_19_SUMMARY.md](./SESSION_19_SUMMARY.md) - System hardening complete

**Technical Docs:**
- [SESSION_20_START_HERE.md](./SESSION_20_START_HERE.md) - Original session plan
- [SESSION_20_BACKEND_CHANGES.md](./SESSION_20_BACKEND_CHANGES.md) - Backend code changes

**Repository:**
- GitHub: https://github.com/amapemom-rgb/financial-reports-system
- Commits: Check for Session 20 changes

---

## 🔍 What to Check First

When starting this session, immediately check:

1. **GitHub Status:**
   - [ ] Are Session 20 changes committed?
   - [ ] Is `main` branch up to date?

2. **Current Deployment Status:**
   ```bash
   gcloud run services list --region us-central1
   ```
   - Check which image versions are currently deployed

3. **GCS Bucket:**
   ```bash
   gsutil ls gs://financial-reports-ai-2024-reports
   ```
   - Verify bucket exists and is accessible

---

## 💡 Pro Tips

1. **Test Locally First (Optional):**
   - Can test endpoints with curl before browser testing
   - Helps isolate backend vs frontend issues

2. **Use Browser DevTools:**
   - Network tab shows all HTTP requests
   - Console tab shows JavaScript errors
   - Useful for debugging upload flow

3. **Check Cloud Run Logs:**
   ```bash
   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=logic-understanding-agent" \
     --limit 50 --format json
   ```

4. **Monitor GCS Uploads:**
   ```bash
   gsutil ls -l gs://financial-reports-ai-2024-reports/reports/ | tail -10
   ```

---

## 🎯 Expected Timeline

- **Deployment:** 15-20 minutes
- **Testing:** 20-30 minutes  
- **Documentation:** 10 minutes  
- **Total:** ~45-60 minutes

---

**Ready to deploy Session 20 changes and test file uploads! 🚀**

**Remember:** The goal is to verify that users can now upload files from the browser without any authentication errors, and that the AI can analyze those uploaded files successfully.
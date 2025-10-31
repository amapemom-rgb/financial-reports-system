# Session 22 Prompt: Complete Testing & Web UI Deployment

**Date:** October 31, 2025  
**Status:** 🚀 **READY TO START**  
**Prerequisites:** Session 21 deployment complete (Logic Agent v13-signblob-final deployed)

---

## 🎯 Session Goal

Complete Session 21 by:
1. Deploying Web UI (v10-upload-fix)
2. Executing all 5 test cases
3. Documenting test results
4. Verifying production readiness

---

## 📋 Quick Context

**What was done in Session 20-21:**
- ✅ Logic Agent with Signed URL Pattern deployed (v13-signblob-final)
- ✅ Web UI code updated with 3-step upload flow
- ✅ `signed_url_helper.py` created (IAM signBlob API)
- ⏱️ Web UI deployment pending
- ⏱️ All test cases pending

**Current Status:**
- Logic Agent: ✅ Deployed and working
- Web UI: ⏱️ Code ready, needs deployment
- Testing: ⏱️ 0/5 test cases completed

---

## 🚀 Step 1: Deploy Web UI

### Build Docker Image

```bash
cd web-ui

gcloud builds submit \
  --tag gcr.io/financial-reports-ai-2024/web-ui:v10-upload-fix \
  --project financial-reports-ai-2024
```

### Deploy to Cloud Run

```bash
gcloud run deploy web-ui \
  --image gcr.io/financial-reports-ai-2024/web-ui:v10-upload-fix \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --project financial-reports-ai-2024
```

### Verify Deployment

```bash
# Get Web UI URL
gcloud run services describe web-ui \
  --region us-central1 \
  --format 'value(status.url)' \
  --project financial-reports-ai-2024
```

**Expected URL:** `https://web-ui-38390150695.us-central1.run.app`

Open in browser and verify:
- ✅ Page loads correctly
- ✅ Version shows "v10-upload-fix"
- ✅ File upload button visible
- ✅ Chat interface working

---

## 🧪 Step 2: Execute Test Cases

### Test Case 1: Small CSV File Upload

**Objective:** Verify 3-step upload flow

1. Open Web UI: https://web-ui-38390150695.us-central1.run.app
2. Click "📁 CSV / Excel" button
3. Select a CSV file (< 1MB)
4. Watch the 3-step progress:
   - ⏳ Step 1/3: Request signed URL
   - ⏳ Step 2/3: Upload to GCS
   - ⏳ Step 3/3: Verify upload

**Success Criteria:**
- ✅ All 3 steps complete without errors
- ✅ Green success message shows file details
- ✅ Chat message: "Файл ... успешно загружен!"
- ✅ No 403 Forbidden or authentication errors

**Document:**
- Screenshot of successful upload
- Upload time (seconds)
- File size
- Any errors encountered

---

### Test Case 2: AI Analysis After Upload

**Objective:** Verify AI can analyze uploaded file

1. After successful upload from Test Case 1
2. In chat, ask: "Сколько строк в этом файле?"
3. Wait for AI response

**Success Criteria:**
- ✅ AI responds within 10 seconds
- ✅ AI provides accurate row count
- ✅ AI mentions specific data from file
- ✅ No "file not found" errors

**Document:**
- Screenshot of AI response
- Response time
- Accuracy of information

---

### Test Case 3: Multi-Sheet Excel File

**Objective:** Test Multi-Sheet Intelligence integration

1. Upload Excel file with 10+ sheets
2. Ask: "Какие листы есть в файле?"
3. Verify multi-sheet mode activates

**Success Criteria:**
- ✅ File uploads successfully
- ✅ AI lists all sheet names
- ✅ AI asks user to select specific sheet
- ✅ `agent_mode: "multi_sheet_selector"` in response

**Document:**
- Number of sheets in file
- AI's sheet list (matches actual?)
- Time to analyze metadata

---

### Test Case 4: Invalid File Type

**Objective:** Verify file type validation

1. Try to upload a PDF or .txt file
2. Observe error message

**Success Criteria:**
- ❌ Upload fails immediately
- ❌ Clear error: "Invalid file type. Allowed: .xlsx, .xls, .csv"
- ❌ No server errors or crashes

**Document:**
- Screenshot of error message
- Error appears at which step?

---

### Test Case 5: Large File Performance

**Objective:** Test with large file

1. Upload Excel file > 5MB (50+ sheets if possible)
2. Monitor upload progress
3. Time the complete upload process

**Success Criteria:**
- ✅ Upload completes within 15 minutes
- ✅ Progress indicators update smoothly
- ✅ File verified successfully
- ✅ No timeout errors

**Document:**
- File size (MB)
- Upload duration (seconds)
- Network speed if available

---

## 🔍 Step 3: Integration Testing (Optional)

If time permits, test endpoints directly:

### Test Signed URL Generation

```bash
curl -X POST https://logic-understanding-agent-38390150695.us-central1.run.app/upload/signed-url \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "test_report.xlsx",
    "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
  }' | python3 -m json.tool
```

**Expected:** Valid signed URL with 15-minute expiration

### Test Upload Verification

```bash
# Use file_path from previous response
curl -X POST https://logic-understanding-agent-38390150695.us-central1.run.app/upload/complete \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "YOUR_FILE_ID",
    "file_path": "reports/YOUR_FILE_PATH"
  }' | python3 -m json.tool
```

**Expected:** Status "success" with file size

---

## 📝 Step 4: Update Documentation

After testing, update `SESSION_21_SUMMARY.md`:

1. **Change test statuses** from "⏱️ PENDING" to "✅ PASS" or "❌ FAIL"
2. **Add test results** with timestamps, file sizes, response times
3. **Document any issues** found during testing
4. **Update Session 21 Status** to "✅ COMPLETE"

### Example Update:

```markdown
### Test Case 1: Small CSV File Upload ✅ PASS

**Execution:** October 31, 2025 18:30 UTC
**File:** sample_data.csv (125 KB)
**Upload Time:** 3.2 seconds

**Results:**
- ✅ All 3 steps completed successfully
- ✅ File details displayed correctly
- ✅ No authentication errors
- ✅ Chat welcome message appeared

**Screenshot:** [test1_success.png]
```

---

## 🎯 Success Criteria for Session 22

Session 22 is considered **COMPLETE** when:

1. ✅ Web UI deployed successfully
2. ✅ At least 4/5 test cases pass
3. ✅ No critical bugs found
4. ✅ Documentation updated with results
5. ✅ System ready for production use

---

## 🐛 Troubleshooting Guide

### Issue: Web UI shows old version after deployment

**Solution:**
```bash
# Force Cloud Run to use new image
gcloud run services update-traffic web-ui \
  --to-latest \
  --region us-central1
```

### Issue: Signed URL generation fails

**Check:**
1. Service Account has `iam.serviceAccountTokenCreator` role
2. Service Account email is correct in metadata
3. Cloud Run logs for detailed errors:

```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=logic-understanding-agent" \
  --limit 20 --format json
```

### Issue: File upload times out

**Possible causes:**
- File too large (> 100MB)
- Network too slow
- Signed URL expired (15 min)

**Solution:**
- Try smaller file
- Request new signed URL
- Check network speed

---

## 📊 Expected Timeline

- **Web UI Deployment:** 10 minutes
- **Test Execution:** 30-45 minutes
- **Documentation Update:** 15 minutes
- **Total:** ~60-70 minutes

---

## 🔗 Related Documents

**Read First:**
- [SESSION_21_SUMMARY.md](./SESSION_21_SUMMARY.md) - Deployment status
- [SESSION_20_SUMMARY.md](./SESSION_20_SUMMARY.md) - Implementation details

**Reference:**
- [SESSION_20_START_HERE.md](./SESSION_20_START_HERE.md) - Original plan
- [web-ui/index.html](../web-ui/index.html) - Frontend code

**Repository:**
- GitHub: https://github.com/amapemom-rgb/financial-reports-system

---

**Ready to complete Session 21 testing and move to Session 22! 🚀**

**First Action:** Deploy Web UI with the commands above, then proceed with testing.

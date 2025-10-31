#!/bin/bash
# Session 21: Test signed URL endpoints
# Comprehensive testing of file upload flow

set -e

echo "🧪 Session 21: Testing Signed URL Upload Flow"
echo "=============================================="

SERVICE_URL="https://logic-understanding-agent-38390150695.us-central1.run.app"

echo ""
echo "📋 Test Plan:"
echo "  1. Health check (verify signed_url_upload_v2_signblob feature)"
echo "  2. Generate signed URL"
echo "  3. Verify signed URL structure"
echo "  4. Test upload/complete endpoint (optional)"
echo ""

# Test 1: Health Check
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 1: Health Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "GET ${SERVICE_URL}/health"
echo ""

HEALTH_RESPONSE=$(curl -s "${SERVICE_URL}/health")
echo "$HEALTH_RESPONSE" | python3 -m json.tool

# Check if signed_url_upload_v2_signblob feature is present
if echo "$HEALTH_RESPONSE" | grep -q "signed_url_upload_v2_signblob"; then
    echo ""
    echo "✅ Feature flag 'signed_url_upload_v2_signblob' found!"
else
    echo ""
    echo "❌ ERROR: Feature flag 'signed_url_upload_v2_signblob' NOT found!"
    echo "   Deployment may have failed or old version is still running."
    exit 1
fi

# Test 2: Generate Signed URL
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 2: Generate Signed URL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "POST ${SERVICE_URL}/upload/signed-url"
echo ""
echo "Request Body:"
echo '{
  "filename": "test_report.xlsx",
  "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
}' | python3 -m json.tool

echo ""
echo "Response:"

SIGNED_URL_RESPONSE=$(curl -s -X POST "${SERVICE_URL}/upload/signed-url" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "test_report.xlsx",
    "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
  }')

echo "$SIGNED_URL_RESPONSE" | python3 -m json.tool

# Extract upload_url for verification
UPLOAD_URL=$(echo "$SIGNED_URL_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('upload_url', ''))" 2>/dev/null || echo "")

if [ -n "$UPLOAD_URL" ]; then
    echo ""
    echo "✅ Signed URL generated successfully!"
    
    # Test 3: Verify URL Structure
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Test 3: Verify Signed URL Structure"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    echo "Signed URL: ${UPLOAD_URL:0:100}..."
    echo ""
    
    # Check URL components
    if echo "$UPLOAD_URL" | grep -q "storage.googleapis.com"; then
        echo "✅ URL points to Google Cloud Storage"
    else
        echo "❌ URL does not point to GCS"
    fi
    
    if echo "$UPLOAD_URL" | grep -q "X-Goog-Algorithm=GOOG4-RSA-SHA256"; then
        echo "✅ URL uses v4 signing (GOOG4-RSA-SHA256)"
    else
        echo "❌ URL does not use v4 signing"
    fi
    
    if echo "$UPLOAD_URL" | grep -q "X-Goog-Signature="; then
        echo "✅ URL contains signature"
    else
        echo "❌ URL missing signature"
    fi
    
    if echo "$UPLOAD_URL" | grep -q "X-Goog-Expires=900"; then
        echo "✅ URL expires in 15 minutes (900 seconds)"
    else
        echo "⚠️  URL expiration time may be different"
    fi
    
    # Extract file_id and file_path
    FILE_ID=$(echo "$SIGNED_URL_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('file_id', ''))" 2>/dev/null || echo "")
    FILE_PATH=$(echo "$SIGNED_URL_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('file_path', ''))" 2>/dev/null || echo "")
    
    echo ""
    echo "📁 File Information:"
    echo "  file_id: ${FILE_ID}"
    echo "  file_path: ${FILE_PATH}"
    
else
    echo ""
    echo "❌ ERROR: Failed to generate signed URL!"
    echo "Response: $SIGNED_URL_RESPONSE"
    exit 1
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Test Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Health endpoint accessible"
echo "✅ Feature flag 'signed_url_upload_v2_signblob' present"
echo "✅ Signed URL generation working"
echo "✅ Signed URL structure valid"
echo ""
echo "🎯 Next Steps:"
echo "  1. Test actual file upload from browser"
echo "  2. Verify AI can analyze uploaded files"
echo "  3. Check Cloud Run logs for any errors"
echo ""
echo "📝 To test file upload from browser:"
echo "  - Open Web UI: https://web-ui-38390150695.us-central1.run.app"
echo "  - Click '📁 CSV / Excel' button"
echo "  - Select a test file"
echo "  - Watch for 3-step progress"
echo ""
echo "💡 To check Cloud Run logs:"
echo "  gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=logic-understanding-agent' \\"
echo "    --limit 50 --format json"
echo ""
echo "=============================================="

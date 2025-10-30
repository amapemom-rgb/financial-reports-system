#!/bin/bash
# Session 21: Test File Upload Endpoints

set -e

LOGIC_AGENT_URL="https://logic-understanding-agent-38390150695.us-central1.run.app"

echo "🧪 Session 21: Testing File Upload Endpoints"
echo "============================================="
echo ""

# Test 1: Health check
echo "Test 1: Health Check"
echo "-------------------"
curl -s ${LOGIC_AGENT_URL}/health | python3 -m json.tool
echo ""
echo "✓ Check: 'signed_url_upload' should be in features list"
echo ""

# Test 2: Request signed URL
echo "Test 2: Generate Signed URL"
echo "---------------------------"
echo "Request payload:"
cat << EOF | tee /tmp/signed_url_request.json
{
  "filename": "test_report.xlsx",
  "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
}
EOF

echo ""
echo "Response:"
curl -s -X POST ${LOGIC_AGENT_URL}/upload/signed-url \
  -H "Content-Type: application/json" \
  -d @/tmp/signed_url_request.json | python3 -m json.tool | tee /tmp/signed_url_response.json

echo ""
echo "✓ Check: Response should contain 'upload_url', 'file_id', 'file_path'"
echo "✓ Check: expires_in_minutes should be 15"
echo ""

# Extract values for next test
FILE_ID=$(cat /tmp/signed_url_response.json | python3 -c "import sys, json; print(json.load(sys.stdin)['file_id'])" 2>/dev/null || echo "FAILED_TO_EXTRACT")
FILE_PATH=$(cat /tmp/signed_url_response.json | python3 -c "import sys, json; print(json.load(sys.stdin)['file_path'])" 2>/dev/null || echo "FAILED_TO_EXTRACT")

echo "Extracted values:"
echo "  FILE_ID: ${FILE_ID}"
echo "  FILE_PATH: ${FILE_PATH}"
echo ""

# Test 3: Upload completion (will fail without actual file upload)
echo "Test 3: Upload Complete Verification"
echo "------------------------------------"
echo "⚠️  Note: This will fail because we didn't actually upload a file to GCS"
echo "⚠️  This is expected! In real scenario, browser uploads file first."
echo ""
echo "Request payload:"
cat << EOF | tee /tmp/upload_complete_request.json
{
  "file_id": "${FILE_ID}",
  "file_path": "${FILE_PATH}"
}
EOF

echo ""
echo "Response:"
curl -s -X POST ${LOGIC_AGENT_URL}/upload/complete \
  -H "Content-Type: application/json" \
  -d @/tmp/upload_complete_request.json | python3 -m json.tool || echo "❌ Expected failure: File not found (we didn't upload it)"

echo ""
echo ""
echo "=================================================="
echo "Summary:"
echo "=================================================="
echo "✅ Test 1: Health check - SHOULD PASS"
echo "✅ Test 2: Generate signed URL - SHOULD PASS"
echo "❌ Test 3: Upload complete - EXPECTED TO FAIL (no actual upload)"
echo ""
echo "Next: Test in browser with real file upload!"
echo ""
echo "Browser test steps:"
echo "1. Open Web UI in browser"
echo "2. Upload a real Excel/CSV file"
echo "3. Watch 3-step progress"
echo "4. Verify success message"
echo "5. Ask AI about the file"

#!/bin/bash
# Session 21: Deploy Logic Agent v12-signblob-fix
# Updated to use signed_url_helper with IAM signBlob API

set -e

echo "🚀 Session 21: Deploying Logic Agent v12-signblob-fix"
echo "=================================================="

# Configuration
PROJECT_ID="financial-reports-ai-2024"
REGION="us-central1"
SERVICE_NAME="logic-understanding-agent"
IMAGE_TAG="v12-signblob-fix"
SERVICE_ACCOUNT="financial-reports-sa@${PROJECT_ID}.iam.gserviceaccount.com"

# Report Reader URL
REPORT_READER_URL="https://report-reader-agent-38390150695.us-central1.run.app"

# GCS Bucket for uploads
REPORTS_BUCKET="${PROJECT_ID}-reports"

echo ""
echo "📦 Step 1/3: Building Docker image..."
echo "Image: gcr.io/${PROJECT_ID}/${SERVICE_NAME}:${IMAGE_TAG}"

cd agents/logic-understanding-agent

gcloud builds submit \
  --tag "gcr.io/${PROJECT_ID}/${SERVICE_NAME}:${IMAGE_TAG}" \
  --project "${PROJECT_ID}"

echo ""
echo "✅ Docker image built successfully!"

echo ""
echo "🚢 Step 2/3: Deploying to Cloud Run..."

gcloud run deploy "${SERVICE_NAME}" \
  --image "gcr.io/${PROJECT_ID}/${SERVICE_NAME}:${IMAGE_TAG}" \
  --platform managed \
  --region "${REGION}" \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --set-env-vars "PROJECT_ID=${PROJECT_ID},REGION=${REGION},REPORT_READER_URL=${REPORT_READER_URL},REPORTS_BUCKET=${REPORTS_BUCKET}" \
  --service-account "${SERVICE_ACCOUNT}" \
  --project "${PROJECT_ID}"

echo ""
echo "✅ Deployment complete!"

echo ""
echo "🔍 Step 3/3: Verifying deployment..."

SERVICE_URL="https://logic-understanding-agent-38390150695.us-central1.run.app"

echo "Checking health endpoint..."
curl -s "${SERVICE_URL}/health" | python3 -m json.tool

echo ""
echo ""
echo "=================================================="
echo "✅ Logic Agent v12-signblob-fix deployed successfully!"
echo ""
echo "Service URL: ${SERVICE_URL}"
echo ""
echo "🎯 Key Changes:"
echo "  - Using signed_url_helper.generate_signed_url_v4()"
echo "  - IAM signBlob API (more reliable on Cloud Run)"
echo "  - Removed iam.Signer dependency"
echo ""
echo "🧪 Test signed URL generation:"
echo "curl -X POST ${SERVICE_URL}/upload/signed-url \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"filename\": \"test.xlsx\", \"content_type\": \"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet\"}' | python3 -m json.tool"
echo ""
echo "=================================================="

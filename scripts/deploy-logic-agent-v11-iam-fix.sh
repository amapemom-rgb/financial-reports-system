#!/bin/bash
# Session 20: Deploy Logic Agent with IAM-based signing fix
# Usage: ./scripts/deploy-logic-agent-v11-iam-fix.sh

set -e

PROJECT_ID="financial-reports-ai-2024"
REGION="us-central1"
SERVICE_NAME="logic-understanding-agent"
IMAGE_TAG="v11-iam-signing-fix"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:${IMAGE_TAG}"

echo "🚀 Deploying Logic Agent with IAM-based signing fix"
echo "=================================================="
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Service: ${SERVICE_NAME}"
echo "Image: ${IMAGE_NAME}"
echo ""

# Step 1: Build Docker image
echo "📦 Step 1/3: Building Docker image..."
gcloud builds submit --tag ${IMAGE_NAME} agents/logic-understanding-agent \
  --project=${PROJECT_ID} \
  --timeout=10m

echo "✅ Image built successfully"
echo ""

# Step 2: Deploy to Cloud Run
echo "🚀 Step 2/3: Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --set-env-vars PROJECT_ID=${PROJECT_ID},REGION=${REGION},REPORTS_BUCKET=${PROJECT_ID}-reports,REPORT_READER_URL=https://report-reader-agent-38390150695.us-central1.run.app \
  --project=${PROJECT_ID}

echo "✅ Service deployed successfully"
echo ""

# Step 3: Test deployment
echo "🧪 Step 3/3: Testing deployment..."
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
  --platform managed \
  --region ${REGION} \
  --project=${PROJECT_ID} \
  --format 'value(status.url)')

echo "Service URL: ${SERVICE_URL}"
echo ""

# Test health endpoint
echo "Testing /health endpoint..."
curl -s "${SERVICE_URL}/health" | python3 -m json.tool

echo ""
echo "✅ Health check passed"
echo ""

# Test signed-url endpoint
echo "Testing /upload/signed-url endpoint..."
curl -s -X POST "${SERVICE_URL}/upload/signed-url" \
  -H "Content-Type: application/json" \
  -d '{"filename": "test.xlsx", "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}' \
  | python3 -m json.tool

echo ""
echo "=================================================="
echo "✅ Deployment complete!"
echo ""
echo "Service URL: ${SERVICE_URL}"
echo "Image: ${IMAGE_NAME}"
echo ""
echo "Next steps:"
echo "1. Verify signed URL generation works"
echo "2. Update Web UI to use new endpoint"
echo "3. Test end-to-end file upload flow"

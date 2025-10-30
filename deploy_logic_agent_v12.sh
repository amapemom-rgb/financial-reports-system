#!/bin/bash
# Session 21: Deploy Logic Agent v12-upload-fix

set -e

PROJECT_ID="financial-reports-ai-2024"
REGION="us-central1"
SERVICE_NAME="logic-understanding-agent"
IMAGE_TAG="v12-upload-fix"
SERVICE_ACCOUNT="financial-reports-sa@${PROJECT_ID}.iam.gserviceaccount.com"

echo "🚀 Session 21: Deploying Logic Agent v12-upload-fix"
echo "=================================================="
echo ""

# Step 1: Build Docker image
echo "📦 Step 1/3: Building Docker image..."
cd agents/logic-understanding-agent

gcloud builds submit \
  --tag gcr.io/${PROJECT_ID}/${SERVICE_NAME}:${IMAGE_TAG} \
  --project ${PROJECT_ID}

echo "✅ Docker image built successfully!"
echo ""

# Step 2: Deploy to Cloud Run
echo "🚀 Step 2/3: Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image gcr.io/${PROJECT_ID}/${SERVICE_NAME}:${IMAGE_TAG} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --set-env-vars PROJECT_ID=${PROJECT_ID},REGION=${REGION},REPORT_READER_URL=https://report-reader-agent-38390150695.us-central1.run.app,REPORTS_BUCKET=${PROJECT_ID}-reports \
  --service-account ${SERVICE_ACCOUNT}

echo "✅ Deployed to Cloud Run successfully!"
echo ""

# Step 3: Verify deployment
echo "🔍 Step 3/3: Verifying deployment..."
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)')

echo "Service URL: ${SERVICE_URL}"
echo ""
echo "Testing /health endpoint..."
curl -s ${SERVICE_URL}/health | python3 -m json.tool

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Check that 'signed_url_upload' appears in features list above"
echo "2. Run deploy_web_ui_v10.sh to deploy frontend"
echo "3. Test file upload in browser"

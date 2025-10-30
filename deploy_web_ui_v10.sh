#!/bin/bash
# Session 21: Deploy Web UI v10-upload-fix

set -e

PROJECT_ID="financial-reports-ai-2024"
REGION="us-central1"
SERVICE_NAME="web-ui"
IMAGE_TAG="v10-upload-fix"

echo "🚀 Session 21: Deploying Web UI v10-upload-fix"
echo "=============================================="
echo ""

# Step 1: Build Docker image
echo "📦 Step 1/3: Building Docker image..."
cd web-ui

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
  --memory 512Mi \
  --cpu 1

echo "✅ Deployed to Cloud Run successfully!"
echo ""

# Step 3: Get service URL
echo "🔍 Step 3/3: Getting service URL..."
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)')

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "=================================================="
echo "Web UI URL: ${SERVICE_URL}"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Open the URL above in your browser"
echo "2. Click '📁 CSV / Excel' to upload a test file"
echo "3. Watch for 3-step progress: Request → Upload → Verify"
echo "4. Verify green success message with file details"
echo "5. Ask AI a question about the file"
echo ""
echo "Test checklist:"
echo "□ Small CSV file (< 1MB)"
echo "□ Medium Excel file (1-5MB)"
echo "□ Large multi-sheet Excel (10+ sheets)"
echo "□ Invalid file type (should fail gracefully)"
echo "□ Network error handling"

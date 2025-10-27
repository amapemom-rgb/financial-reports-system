#!/bin/bash
# Deploy Logic Agent v10-multisheet with Multi-Sheet Intelligence
# Session 15 - Improvement #3

set -e

echo "🚀 Deploying Logic Agent v10-multisheet..."
echo ""

PROJECT_ID="financial-reports-ai-2024"
REGION="us-central1"
SERVICE_NAME="logic-understanding-agent"
IMAGE_TAG="v10-multisheet"

cd agents/logic-understanding-agent

echo "📦 Step 1: Building Docker image..."
gcloud builds submit \
  --tag gcr.io/$PROJECT_ID/$SERVICE_NAME:$IMAGE_TAG \
  --project=$PROJECT_ID \
  --timeout=10m

echo ""
echo "🚢 Step 2: Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME:$IMAGE_TAG \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --service-account=financial-reports-sa@$PROJECT_ID.iam.gserviceaccount.com \
  --set-env-vars PROJECT_ID=$PROJECT_ID,REGION=$REGION \
  --min-instances=0 \
  --max-instances=10 \
  --memory=512Mi \
  --cpu=1 \
  --timeout=300 \
  --project=$PROJECT_ID

echo ""
echo "✅ Deployment complete!"
echo ""

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --region $REGION \
  --project $PROJECT_ID \
  --format="value(status.url)")

echo "🌐 Service URL: $SERVICE_URL"
echo ""

echo "🧪 Testing health endpoint..."
curl -s "$SERVICE_URL/health" | python3 -m json.tool

echo ""
echo "✅ Logic Agent v10-multisheet deployed successfully!"
echo ""
echo "Features:"
echo "  ✅ Dynamic Prompts (Secret Manager)"
echo "  ✅ User Feedback (Firestore)"
echo "  ✅ Regenerate"
echo "  ✅ CORS"
echo "  ✅ Multi-Sheet Intelligence (NEW)"

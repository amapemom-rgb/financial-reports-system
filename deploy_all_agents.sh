#!/bin/bash
# Deploy all 5 agents to Cloud Run
# Financial Reports System - Session 9

set -e  # Exit on error

PROJECT_ID="financial-reports-ai-2024"
REGION="us-central1"
REGISTRY="us-central1-docker.pkg.dev"
SERVICE_ACCOUNT="financial-reports-sa@financial-reports-ai-2024.iam.gserviceaccount.com"

echo "🚀 Starting deployment of all 5 agents to Cloud Run"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Step 1: Update Cloud Build trigger to use cloudbuild.yaml
echo "📝 Step 1: Updating Cloud Build trigger configuration..."
gcloud builds triggers update FRAI \
  --region=global \
  --build-config=cloudbuild.yaml \
  --project=$PROJECT_ID

echo "✅ Trigger updated to use cloudbuild.yaml"
echo ""

# Step 2: Run the build
echo "🔨 Step 2: Starting build for all 5 agents..."
echo "This will take approximately 10-15 minutes..."
BUILD_ID=$(gcloud builds triggers run FRAI \
  --branch=main \
  --region=global \
  --project=$PROJECT_ID \
  --format='value(metadata.build.id)')

echo "Build started with ID: $BUILD_ID"
echo "Streaming logs..."
echo ""

# Stream logs
gcloud builds log $BUILD_ID --stream --project=$PROJECT_ID

# Check build status
BUILD_STATUS=$(gcloud builds describe $BUILD_ID --project=$PROJECT_ID --format='value(status)')

if [ "$BUILD_STATUS" != "SUCCESS" ]; then
  echo "❌ Build failed with status: $BUILD_STATUS"
  exit 1
fi

echo ""
echo "✅ All Docker images built successfully!"
echo ""

# Step 3: Verify images in Artifact Registry
echo "🔍 Step 3: Verifying images in Artifact Registry..."
echo ""

gcloud artifacts docker images list \
  $REGISTRY/$PROJECT_ID/financial-reports \
  --include-tags \
  --project=$PROJECT_ID

echo ""
echo "✅ All images verified in Artifact Registry"
echo ""

# Step 4: Deploy to Cloud Run
echo "🚢 Step 4: Deploying all services to Cloud Run..."
echo ""

SERVICES=(
  "frontend-service"
  "orchestrator-agent"
  "report-reader-agent"
  "logic-understanding-agent"
  "visualization-agent"
)

for service in "${SERVICES[@]}"; do
  echo "Deploying $service..."
  
  gcloud run deploy $service \
    --image=$REGISTRY/$PROJECT_ID/financial-reports/$service:latest \
    --region=$REGION \
    --platform=managed \
    --service-account=$SERVICE_ACCOUNT \
    --allow-unauthenticated \
    --memory=2Gi \
    --cpu=2 \
    --timeout=300 \
    --max-instances=10 \
    --min-instances=0 \
    --project=$PROJECT_ID \
    --quiet
  
  echo "✅ $service deployed"
  echo ""
done

echo ""
echo "🎉 All services deployed successfully!"
echo ""
echo "📋 Service URLs:"
for service in "${SERVICES[@]}"; do
  URL=$(gcloud run services describe $service \
    --region=$REGION \
    --project=$PROJECT_ID \
    --format='value(status.url)')
  echo "  $service: $URL"
done

echo ""
echo "✅ Deployment complete!"

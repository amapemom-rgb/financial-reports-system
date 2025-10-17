#!/bin/bash
# Deploy Orchestrator Agent using Cloud Build

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🎯 Deploying Orchestrator Agent${NC}"
echo "=================================="
echo ""

PROJECT_ID="financial-reports-ai-2024"
REGION="us-central1"
SERVICE_NAME="orchestrator-agent"

# Step 1: Build and push image
echo -e "${YELLOW}🏗️  Building image with Cloud Build...${NC}"
gcloud builds submit \
    --tag=${REGION}-docker.pkg.dev/${PROJECT_ID}/financial-reports/${SERVICE_NAME}:latest \
    agents/${SERVICE_NAME} \
    --project=${PROJECT_ID}

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to build image${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Image built successfully${NC}"
echo ""

# Step 2: Deploy to Cloud Run
echo -e "${YELLOW}🚀 Deploying to Cloud Run...${NC}"

# Get other services URLs for env vars
REPORT_READER_URL=$(gcloud run services describe report-reader-agent --region=${REGION} --format="value(status.url)" 2>/dev/null || echo "")
LOGIC_AGENT_URL=$(gcloud run services describe logic-understanding-agent --region=${REGION} --format="value(status.url)" 2>/dev/null || echo "")
VISUALIZATION_URL=$(gcloud run services describe visualization-agent --region=${REGION} --format="value(status.url)" 2>/dev/null || echo "")

gcloud run deploy ${SERVICE_NAME} \
    --image=${REGION}-docker.pkg.dev/${PROJECT_ID}/financial-reports/${SERVICE_NAME}:latest \
    --region=${REGION} \
    --platform=managed \
    --memory=1Gi \
    --cpu=2 \
    --max-instances=10 \
    --timeout=900 \
    --no-allow-unauthenticated \
    --set-env-vars="PROJECT_ID=${PROJECT_ID},REGION=${REGION},PUBSUB_TOPIC=task-queue-topic,REPORT_READER_URL=${REPORT_READER_URL},LOGIC_AGENT_URL=${LOGIC_AGENT_URL},VISUALIZATION_URL=${VISUALIZATION_URL},DATABASE_URL=sqlite:///./orchestrator.db" \
    --service-account=financial-reports-sa@${PROJECT_ID}.iam.gserviceaccount.com \
    --project=${PROJECT_ID}

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to deploy service${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Orchestrator Agent deployed successfully!${NC}"
echo ""

# Step 3: Get service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format="value(status.url)")
echo "Service URL: ${SERVICE_URL}"
echo ""

# Step 4: Test health endpoint (with auth)
echo -e "${YELLOW}🔍 Testing health endpoint...${NC}"
TOKEN=$(gcloud auth print-identity-token)

HEALTH_RESPONSE=$(curl -s -H "Authorization: Bearer ${TOKEN}" ${SERVICE_URL}/health)
echo "Health check: ${HEALTH_RESPONSE}"
echo ""

if echo "${HEALTH_RESPONSE}" | grep -q "healthy"; then
    echo -e "${GREEN}✅ Service is healthy!${NC}"
else
    echo -e "${RED}⚠️  Service may not be healthy${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Deployment complete!${NC}"
echo ""
echo "All services:"
gcloud run services list --region=${REGION}

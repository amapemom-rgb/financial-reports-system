#!/bin/bash

# ==============================================================================
# Session 22: Deploy Web UI v10-upload-fix
# ==============================================================================
# This script deploys the updated Web UI with 3-step Signed URL upload flow
# ==============================================================================

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Session 22: Web UI Deployment${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Configuration
PROJECT_ID="financial-reports-ai-2024"
REGION="us-central1"
SERVICE_NAME="web-ui"
IMAGE_TAG="v10-upload-fix"
IMAGE_URL="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:${IMAGE_TAG}"

# Change to web-ui directory
cd "$(dirname "$0")/web-ui" || exit 1

echo -e "${YELLOW}📍 Current directory: $(pwd)${NC}"
echo ""

# ==============================================================================
# Step 1: Build Docker Image
# ==============================================================================
echo -e "${BLUE}Step 1/3: Building Docker image...${NC}"
echo -e "Image: ${IMAGE_URL}"
echo ""

gcloud builds submit \
  --tag "${IMAGE_URL}" \
  --project "${PROJECT_ID}" \
  --timeout=10m

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✅ Docker image built successfully!${NC}"
  echo ""
else
  echo -e "❌ Docker build failed!"
  exit 1
fi

# ==============================================================================
# Step 2: Deploy to Cloud Run
# ==============================================================================
echo -e "${BLUE}Step 2/3: Deploying to Cloud Run...${NC}"
echo -e "Service: ${SERVICE_NAME}"
echo -e "Region: ${REGION}"
echo ""

gcloud run deploy "${SERVICE_NAME}" \
  --image "${IMAGE_URL}" \
  --platform managed \
  --region "${REGION}" \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --timeout 60 \
  --project "${PROJECT_ID}"

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✅ Service deployed successfully!${NC}"
  echo ""
else
  echo -e "❌ Deployment failed!"
  exit 1
fi

# ==============================================================================
# Step 3: Verify Deployment
# ==============================================================================
echo -e "${BLUE}Step 3/3: Verifying deployment...${NC}"
echo ""

# Get service URL
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" \
  --region "${REGION}" \
  --project "${PROJECT_ID}" \
  --format 'value(status.url)')

echo -e "${GREEN}✅ Service URL: ${SERVICE_URL}${NC}"
echo ""

# Test health endpoint (basic check)
echo "Testing if service is accessible..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${SERVICE_URL}")

if [ "${HTTP_CODE}" = "200" ]; then
  echo -e "${GREEN}✅ Service is accessible (HTTP ${HTTP_CODE})${NC}"
else
  echo -e "${YELLOW}⚠️  Service returned HTTP ${HTTP_CODE}${NC}"
fi

echo ""

# ==============================================================================
# Summary
# ==============================================================================
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Deployment Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "Service:    ${GREEN}${SERVICE_NAME}${NC}"
echo -e "Version:    ${GREEN}${IMAGE_TAG}${NC}"
echo -e "Region:     ${GREEN}${REGION}${NC}"
echo -e "URL:        ${GREEN}${SERVICE_URL}${NC}"
echo ""
echo -e "${GREEN}✅ Web UI v10-upload-fix deployed successfully!${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Open Web UI in browser: ${SERVICE_URL}"
echo "2. Execute 5 test cases from SESSION_22_PROMPT.md"
echo "3. Document results in SESSION_21_SUMMARY.md"
echo ""
echo -e "${BLUE}========================================${NC}"

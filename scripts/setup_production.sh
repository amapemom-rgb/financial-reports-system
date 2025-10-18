#!/bin/bash
# Automated setup script for Financial Reports System
# This script sets up EVERYTHING automatically

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_ID="financial-reports-ai-2024"
REGION="us-central1"
REPO_OWNER="amapemom-rgb"
REPO_NAME="financial-reports-system"

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║   Financial Reports System - Automated Setup          ║"
echo "║   Full CI/CD with Cloud Build + Terraform             ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI not found. Install it first!${NC}"
    exit 1
fi

# Check if logged in
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo -e "${YELLOW}⚠️  Not logged in to gcloud. Running login...${NC}"
    gcloud auth login
fi

# Set project
echo -e "${YELLOW}🔧 Setting project: $PROJECT_ID${NC}"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo -e "${YELLOW}🔧 Enabling required Google Cloud APIs...${NC}"
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    containerregistry.googleapis.com \
    sourcerepo.googleapis.com \
    pubsub.googleapis.com \
    storage.googleapis.com \
    aiplatform.googleapis.com \
    secretmanager.googleapis.com

echo -e "${GREEN}✅ APIs enabled${NC}"

# Create Cloud Build trigger for web-ui
echo -e "${YELLOW}🔧 Creating Cloud Build trigger for Web UI...${NC}"

# Check if trigger already exists
if gcloud builds triggers list --format="value(name)" | grep -q "web-ui-deploy"; then
    echo -e "${BLUE}ℹ️  Trigger 'web-ui-deploy' already exists, skipping${NC}"
else
    gcloud builds triggers create github \
        --name="web-ui-deploy" \
        --repo-name="$REPO_NAME" \
        --repo-owner="$REPO_OWNER" \
        --branch-pattern="^main$" \
        --build-config="web-ui/cloudbuild.yaml" \
        --include-logs-with-status
    
    echo -e "${GREEN}✅ Cloud Build trigger created${NC}"
fi

# Build and deploy web-ui immediately
echo -e "${YELLOW}🚀 Building and deploying Web UI...${NC}"
gcloud builds submit ./web-ui \
    --config=./web-ui/cloudbuild.yaml \
    --project=$PROJECT_ID

echo -e "${GREEN}✅ Web UI deployed!${NC}"

# Get Web UI URL
WEB_UI_URL=$(gcloud run services describe web-ui \
    --region=$REGION \
    --format='value(status.url)')

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    🎉 SUCCESS!                         ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📍 Web UI URL:${NC}"
echo -e "${YELLOW}   $WEB_UI_URL${NC}"
echo ""
echo -e "${BLUE}🔐 Get auth token:${NC}"
echo -e "${YELLOW}   gcloud auth print-identity-token${NC}"
echo ""
echo -e "${BLUE}🚀 Next steps:${NC}"
echo "   1. Open the URL above in your browser"
echo "   2. Paste your auth token"
echo "   3. Start using the system!"
echo ""
echo -e "${GREEN}🎊 System is ready to use!${NC}"
echo ""

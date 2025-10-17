#!/bin/bash
# Complete deployment script

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🚀 Financial Reports System - Complete Deployment${NC}"
echo "==================================================="
echo ""

# Get project ID
read -p "Enter your GCP Project ID [financial-reports-ai-2024]: " PROJECT_ID
PROJECT_ID=${PROJECT_ID:-financial-reports-ai-2024}

read -p "Enter region [us-central1]: " REGION
REGION=${REGION:-us-central1}

echo ""
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo ""

read -p "Continue with deployment? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "Deployment cancelled."
    exit 0
fi

# Step 1: Set GCP project
echo ""
echo -e "${YELLOW}📋 Step 1: Setting GCP project...${NC}"
gcloud config set project $PROJECT_ID

# Step 2: Enable required APIs
echo ""
echo -e "${YELLOW}🔧 Step 2: Enabling required APIs...${NC}"
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    pubsub.googleapis.com \
    storage.googleapis.com \
    aiplatform.googleapis.com \
    sqladmin.googleapis.com \
    --project=$PROJECT_ID

# Step 3: Build and push Docker images
echo ""
echo -e "${YELLOW}🐳 Step 3: Building and pushing Docker images...${NC}"
chmod +x scripts/build_and_push.sh
./scripts/build_and_push.sh $PROJECT_ID $REGION

# Step 4: Initialize Terraform
echo ""
echo -e "${YELLOW}🏗️  Step 4: Initializing Terraform...${NC}"
cd terraform
terraform init

# Step 5: Plan Terraform
echo ""
echo -e "${YELLOW}📝 Step 5: Planning Terraform deployment...${NC}"
terraform plan -var="project_id=$PROJECT_ID" -var="region=$REGION"

# Step 6: Apply Terraform
echo ""
read -p "Apply Terraform changes? (yes/no): " APPLY_CONFIRM
if [ "$APPLY_CONFIRM" == "yes" ]; then
    echo -e "${YELLOW}🚀 Step 6: Applying Terraform...${NC}"
    terraform apply -var="project_id=$PROJECT_ID" -var="region=$REGION" -auto-approve
    
    echo ""
    echo -e "${GREEN}✅ Deployment Complete!${NC}"
    echo ""
    echo "📊 Outputs:"
    terraform output
    
    echo ""
    echo -e "${GREEN}🎉 Your Financial Reports System is now live!${NC}"
    echo ""
    echo "Frontend URL:"
    terraform output -raw frontend_url
    echo ""
else
    echo "Terraform apply skipped."
fi

cd ..

echo ""
echo "Deployment script finished."

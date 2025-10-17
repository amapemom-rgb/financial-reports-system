#!/bin/bash
# Deploy using Cloud Build (no local Docker required)

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🚀 Financial Reports System - Cloud Build Deployment${NC}"
echo "========================================================"
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

# Step 3: Create Artifact Registry repository
echo ""
echo -e "${YELLOW}📦 Step 3: Creating Artifact Registry repository...${NC}"
gcloud artifacts repositories create financial-reports \
    --repository-format=docker \
    --location=$REGION \
    --description="Financial Reports System Docker Images" \
    --project=$PROJECT_ID 2>/dev/null || echo "Repository already exists"

# Step 4: Build and push images using Cloud Build
echo ""
echo -e "${YELLOW}🏗️  Step 4: Building images with Cloud Build...${NC}"

SERVICES=(
    "frontend-service"
    "report-reader-agent"
    "logic-understanding-agent"
    "visualization-agent"
    "orchestrator-agent"
)

for SERVICE in "${SERVICES[@]}"; do
    echo ""
    echo -e "${YELLOW}Building $SERVICE...${NC}"
    
    gcloud builds submit \
        --tag=${REGION}-docker.pkg.dev/${PROJECT_ID}/financial-reports/${SERVICE}:latest \
        agents/${SERVICE} \
        --project=$PROJECT_ID
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Built and pushed $SERVICE${NC}"
    else
        echo -e "${RED}❌ Failed to build $SERVICE${NC}"
        exit 1
    fi
done

# Step 5: Initialize Terraform
echo ""
echo -e "${YELLOW}🏗️  Step 5: Initializing Terraform...${NC}"
cd terraform
terraform init

# Step 6: Plan Terraform
echo ""
echo -e "${YELLOW}📝 Step 6: Planning Terraform deployment...${NC}"
terraform plan -var="project_id=$PROJECT_ID" -var="region=$REGION"

# Step 7: Apply Terraform
echo ""
read -p "Apply Terraform changes? (yes/no): " APPLY_CONFIRM
if [ "$APPLY_CONFIRM" == "yes" ]; then
    echo -e "${YELLOW}🚀 Step 7: Applying Terraform...${NC}"
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

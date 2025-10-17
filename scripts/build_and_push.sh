#!/bin/bash
# Build and push Docker images to Google Artifact Registry

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🐳 Building and Pushing Docker Images${NC}"
echo "========================================"

# Configuration
PROJECT_ID="${1:-financial-reports-ai-2024}"
REGION="${2:-us-central1}"
REPOSITORY="financial-reports"

echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI not found. Please install it first.${NC}"
    exit 1
fi

# Authenticate
echo -e "${YELLOW}🔐 Authenticating with GCP...${NC}"
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# Create Artifact Registry repository if it doesn't exist
echo -e "${YELLOW}📦 Creating Artifact Registry repository...${NC}"
gcloud artifacts repositories create $REPOSITORY \
    --repository-format=docker \
    --location=$REGION \
    --description="Financial Reports System Docker Images" \
    --project=$PROJECT_ID || echo "Repository already exists"

# List of services
SERVICES=(
    "frontend-service"
    "report-reader-agent"
    "logic-understanding-agent"
    "visualization-agent"
    "orchestrator-agent"
)

# Build and push each service
for SERVICE in "${SERVICES[@]}"; do
    echo ""
    echo -e "${YELLOW}🔨 Building $SERVICE...${NC}"
    
    IMAGE_NAME="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${SERVICE}:latest"
    
    cd agents/${SERVICE}
    
    # Build image
    docker build -t $IMAGE_NAME .
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Built $SERVICE${NC}"
        
        # Push image
        echo -e "${YELLOW}📤 Pushing $SERVICE...${NC}"
        docker push $IMAGE_NAME
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Pushed $SERVICE${NC}"
        else
            echo -e "${RED}❌ Failed to push $SERVICE${NC}"
            exit 1
        fi
    else
        echo -e "${RED}❌ Failed to build $SERVICE${NC}"
        exit 1
    fi
    
    cd ../..
done

echo ""
echo -e "${GREEN}🎉 All images built and pushed successfully!${NC}"
echo ""
echo "Next steps:"
echo "  1. cd terraform"
echo "  2. terraform init"
echo "  3. terraform plan -var='project_id=$PROJECT_ID'"
echo "  4. terraform apply -var='project_id=$PROJECT_ID'"

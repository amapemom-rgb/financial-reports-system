#!/bin/bash
# Quick health check script for all services

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}🏥 Checking health of all services...${NC}"
echo ""

# Get token
TOKEN=$(gcloud auth print-identity-token)

if [ -z "$TOKEN" ]; then
    echo -e "${RED}❌ Failed to get auth token${NC}"
    exit 1
fi

# Services
declare -A SERVICES=(
    ["Frontend"]="https://frontend-service-38390150695.us-central1.run.app"
    ["Orchestrator"]="https://orchestrator-agent-38390150695.us-central1.run.app"
    ["Report Reader"]="https://report-reader-agent-38390150695.us-central1.run.app"
    ["Logic Agent"]="https://logic-understanding-agent-38390150695.us-central1.run.app"
    ["Visualization"]="https://visualization-agent-38390150695.us-central1.run.app"
)

all_healthy=true

for service in "${!SERVICES[@]}"; do
    url="${SERVICES[$service]}"
    
    printf "%-20s" "$service:"
    
    # Make request and capture both response and HTTP code
    temp_file=$(mktemp)
    http_code=$(curl -s -w "%{http_code}" -m 10 \
        -H "Authorization: Bearer $TOKEN" \
        -o "$temp_file" \
        "$url/health" 2>/dev/null)
    
    response=$(cat "$temp_file")
    rm -f "$temp_file"
    
    # Check result
    if [ "$http_code" = "200" ] && echo "$response" | grep -q "healthy"; then
        echo -e "${GREEN}✅ healthy${NC}"
    else
        echo -e "${RED}❌ unhealthy (HTTP $http_code)${NC}"
        all_healthy=false
        
        if [ "$1" = "-v" ] || [ "$1" = "--verbose" ]; then
            echo "   Response: $response"
        fi
    fi
done

echo ""

if [ "$all_healthy" = true ]; then
    echo -e "${GREEN}✅ All services are healthy!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some services are unhealthy${NC}"
    echo ""
    echo "Run with -v or --verbose for detailed output"
    exit 1
fi

#!/bin/bash
# Quick test to see if APIs are responding

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🔍 Проверка доступности API endpoints...${NC}"
echo ""

# Get token
echo "Получение токена..."
TOKEN=$(gcloud auth print-identity-token 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "❌ Не удалось получить токен. Запусти: gcloud auth login"
    exit 1
fi

echo -e "${GREEN}✅ Токен получен${NC}"
echo ""

# Frontend health
echo -e "${YELLOW}1. Frontend Service:${NC}"
echo "   URL: https://frontend-service-38390150695.us-central1.run.app"
curl -s -H "Authorization: Bearer $TOKEN" \
    https://frontend-service-38390150695.us-central1.run.app/health | jq
echo ""

# Frontend endpoints info
echo -e "${YELLOW}2. Доступные endpoints Frontend:${NC}"
curl -s -H "Authorization: Bearer $TOKEN" \
    https://frontend-service-38390150695.us-central1.run.app/ | jq
echo ""

echo -e "${GREEN}✅ API работают! Можно использовать через curl или Postman${NC}"
echo ""
echo "📝 Примеры использования:"
echo ""
echo "# Загрузить файл:"
echo "curl -X POST -H \"Authorization: Bearer \$TOKEN\" \\"
echo "  -F \"file=@/path/to/report.csv\" \\"
echo "  https://frontend-service-38390150695.us-central1.run.app/upload"
echo ""

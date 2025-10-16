#!/bin/bash
set -e

PROJECT_ID="financial-reports-ai-2024"
REGION="us-central1"
SERVICE_NAME="logic-understanding-agent"

echo "🚀 Деплой Logic Understanding Agent"
echo "===================================="
echo ""

cd agents/logic-understanding-agent

echo "📦 Сборка Docker образа..."
gcloud builds submit \
  --tag=$REGION-docker.pkg.dev/$PROJECT_ID/financial-reports-agents/$SERVICE_NAME:latest \
  --project=$PROJECT_ID

echo "🚀 Деплой в Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image=$REGION-docker.pkg.dev/$PROJECT_ID/financial-reports-agents/$SERVICE_NAME:latest \
  --platform=managed \
  --region=$REGION \
  --allow-unauthenticated \
  --set-env-vars="PROJECT_ID=$PROJECT_ID,REGION=$REGION" \
  --project=$PROJECT_ID

echo ""
echo "✅ Деплой завершен!"
echo ""

SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)' --project=$PROJECT_ID)
echo "🎉 AI Агент доступен: $SERVICE_URL"
echo ""
echo "Тест:"
echo "curl $SERVICE_URL/health"

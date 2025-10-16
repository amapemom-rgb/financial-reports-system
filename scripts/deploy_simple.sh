#!/bin/bash
set -e

PROJECT_ID="financial-reports-ai-2024"
REGION="us-central1"
SERVICE_NAME="frontend-service"

echo "🚀 Деплой Frontend Service в Cloud Run"
echo "======================================"
echo ""

# Сборка и деплой
cd agents/frontend-service

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
  --project=$PROJECT_ID

echo ""
echo "✅ Деплой завершен!"
echo ""
echo "Получаем URL..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)' --project=$PROJECT_ID)
echo "🎉 Сервис доступен: $SERVICE_URL"
echo ""
echo "Проверка:"
echo "curl $SERVICE_URL/health"

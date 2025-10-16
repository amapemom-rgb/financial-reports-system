#!/bin/bash
set -e

echo "🚀 Быстрый деплой Financial Reports System"
echo "=========================================="
echo ""

# Переменные
export PROJECT_ID="financial-reports-ai-2024"
export REGION="us-central1"
export GEMINI_API_KEY="AIzaSyADsLkWZiN8XhHXEaJws-sSbsUC8bAByr8"

echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# 1. Активация API
echo "1️⃣ Активация необходимых API..."
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  --project=$PROJECT_ID

echo "✅ API активированы"
echo ""

# 2. Создание Artifact Registry
echo "2️⃣ Создание Artifact Registry..."
if gcloud artifacts repositories describe financial-reports-agents --location=$REGION --project=$PROJECT_ID &>/dev/null; then
    echo "✅ Репозиторий уже существует"
else
    gcloud artifacts repositories create financial-reports-agents \
      --repository-format=docker \
      --location=$REGION \
      --description="Docker repository for financial reports agents" \
      --project=$PROJECT_ID
    echo "✅ Artifact Registry создан"
fi
echo ""

echo "🎉 Базовая настройка завершена!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Создание Docker образов (займет ~15-20 минут)"
echo "2. Деплой в Cloud Run"
echo "3. Настройка базы данных"
echo ""
echo "Готовы продолжить? (y/n)"

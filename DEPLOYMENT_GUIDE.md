# 🚀 GCP Deployment Guide

## ✅ Что готово

Terraform модули созданы и готовы:
- ✅ Cloud Run module
- ✅ Pub/Sub module
- ✅ Storage module
- ✅ Main terraform configuration
- ✅ Build & Push script
- ✅ Complete deployment script

---

## 📋 Предварительные требования

### 1. Установить Google Cloud SDK

```bash
# Mac
brew install --cask google-cloud-sdk

# Или скачать с https://cloud.google.com/sdk/docs/install
```

### 2. Установить Docker

```bash
# Проверь что Docker запущен
docker --version

# Если нет - установи Docker Desktop
# https://www.docker.com/products/docker-desktop
```

### 3. Установить Terraform

```bash
# Mac
brew install terraform

# Проверь
terraform --version
```

---

## 🎯 Деплой (Автоматический)

### Вариант 1: Полный автоматический деплой

```bash
cd /Users/sergejbykov/financial-reports-system

# Дай права на выполнение
chmod +x scripts/deploy_gcp.sh

# Запусти деплой
./scripts/deploy_gcp.sh
```

**Скрипт выполнит:**
1. Настройку GCP проекта
2. Включение нужных API
3. Сборку всех Docker образов
4. Загрузку в Container Registry
5. Terraform init/plan/apply
6. Деплой всех 5 агентов

**Время:** ~20-30 минут

---

## 🎯 Деплой (Пошаговый)

### Шаг 1: Настрой GCP

```bash
# Войди в GCP
gcloud auth login

# Установи проект
gcloud config set project financial-reports-ai-2024

# Создай проект если нет
# gcloud projects create financial-reports-ai-2024 --name="Financial Reports System"

# Включи биллинг (через веб-консоль)
# https://console.cloud.google.com/billing
```

### Шаг 2: Включи API

```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  pubsub.googleapis.com \
  storage.googleapis.com \
  aiplatform.googleapis.com
```

### Шаг 3: Собери и загрузи образы

```bash
cd /Users/sergejbykov/financial-reports-system

# Дай права
chmod +x scripts/build_and_push.sh

# Запусти
./scripts/build_and_push.sh financial-reports-ai-2024 us-central1
```

Это займёт **10-15 минут** (собираем 5 Docker образов)

### Шаг 4: Задеплой через Terraform

```bash
cd terraform

# Инициализируй
terraform init

# Проверь план
terraform plan -var="project_id=financial-reports-ai-2024"

# Задеплой
terraform apply -var="project_id=financial-reports-ai-2024" -auto-approve
```

Это займёт **5-10 минут**

### Шаг 5: Проверь результат

```bash
# Получи URLs сервисов
terraform output

# Проверь Frontend
curl $(terraform output -raw frontend_url)/health

# Проверь в консоли
gcloud run services list
```

---

## 💰 Стоимость

### Ожидаемые расходы:

**Dev окружение (минимальная нагрузка):**
- Cloud Run: $5-10/месяц
- Storage: $1-2/месяц
- Pub/Sub: $1-2/месяц
- Vertex AI: $10-20/месяц (за запросы к Gemini)
- **ИТОГО: ~$20-35/месяц**

**Production (средняя нагрузка):**
- Cloud Run: $50-100/месяц
- Storage: $10-20/месяц
- Pub/Sub: $10-20/месяц
- Vertex AI: $100-300/месяц
- **ИТОГО: ~$200-500/месяц**

---

## 🐛 Troubleshooting

### Проблема: Docker not found
```bash
# Установи Docker Desktop
brew install --cask docker
# Запусти Docker Desktop
```

### Проблема: Permission denied
```bash
# Дай права на скрипты
chmod +x scripts/*.sh
```

### Проблема: gcloud not found
```bash
# Установи gcloud SDK
brew install --cask google-cloud-sdk
```

### Проблема: Terraform apply failed
```bash
# Проверь что все API включены
gcloud services list --enabled

# Проверь что есть права
gcloud auth list
```

### Проблема: API not enabled
```bash
# Включи API вручную в консоли
# https://console.cloud.google.com/apis/library
```

---

## 🎯 После деплоя

### Проверь все сервисы:

```bash
# Frontend
curl https://frontend-service-xxx.run.app/health

# Orchestrator
curl https://orchestrator-agent-xxx.run.app/health

# Report Reader
curl https://report-reader-agent-xxx.run.app/health

# Logic Agent
curl https://logic-understanding-agent-xxx.run.app/health

# Visualization
curl https://visualization-agent-xxx.run.app/health
```

### Тестовый запрос:

```bash
FRONTEND_URL=$(cd terraform && terraform output -raw frontend_url)

curl -X POST $FRONTEND_URL/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Test analysis",
    "use_voice_response": false
  }'
```

---

## 📊 Мониторинг

### Cloud Console:
- **Cloud Run**: https://console.cloud.google.com/run
- **Logs**: https://console.cloud.google.com/logs
- **Monitoring**: https://console.cloud.google.com/monitoring

### Команды:

```bash
# Логи сервиса
gcloud run services logs read frontend-service --limit=50

# Метрики
gcloud run services describe frontend-service

# Статус
gcloud run services list
```

---

## 🗑️ Удаление (если нужно)

```bash
cd terraform

# Удали всё
terraform destroy -var="project_id=financial-reports-ai-2024" -auto-approve

# Или удали вручную
gcloud run services delete frontend-service --region=us-central1
gcloud run services delete orchestrator-agent --region=us-central1
# ... и так далее
```

---

## 🎊 Готово!

После успешного деплоя у тебя будет:

✅ 5 агентов в Cloud Run  
✅ Pub/Sub для коммуникации  
✅ Storage для файлов и графиков  
✅ Автоматический скейлинг  
✅ HTTPS endpoints  
✅ Мониторинг и логи  

**Проект готов к использованию! 🚀**

---

## 📝 Следующие шаги

1. **Настрой CI/CD** (GitHub Actions)
2. **Добавь мониторинг** (Cloud Monitoring dashboards)
3. **Настрой алерты** (email/Slack уведомления)
4. **Добавь кастомный домен** (если нужно)
5. **Настрой Cloud SQL** (вместо SQLite для Orchestrator)

---

**Удачи с деплоем! 🎉**

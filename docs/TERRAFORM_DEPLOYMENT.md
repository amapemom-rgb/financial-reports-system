# 🚀 Terraform Deployment Guide - Complete Setup

## 📋 Что создано

### ✅ Terraform Infrastructure (Complete)

**Основные файлы:**
- `terraform/main.tf` - главная конфигурация
- `terraform/variables.tf` - переменные
- `terraform/outputs.tf` - outputs с URLs сервисов
- `terraform/versions.tf` - версии провайдеров
- `terraform/terraform.tfvars.example` - пример конфигурации

**Модули:**
- `terraform/modules/cloud_build/` - Cloud Build триггеры (5 триггеров)
- `terraform/modules/cloud_run/` - Cloud Run сервисы (5 сервисов)
- `terraform/modules/storage/` - Cloud Storage бакеты
- `terraform/modules/pubsub/` - Pub/Sub топики и подписки
- `terraform/modules/iam/` - Service accounts и IAM политики

### ✅ Cloud Build Configurations

**Созданы:**
- `services/frontend-service/cloudbuild.yaml` + `Dockerfile` ✅
- `services/orchestrator-agent/cloudbuild.yaml` + `Dockerfile` ✅
- `services/report-reader-agent/cloudbuild.yaml` + `Dockerfile` ✅

**Нужно создать вручную (копируй из этого файла):**
- `services/logic-understanding-agent/cloudbuild.yaml` + `Dockerfile`
- `services/visualization-agent/cloudbuild.yaml` + `Dockerfile`

---

## 🎯 Полный Deployment Workflow

### Шаг 0: Создай недостающие файлы

#### services/logic-understanding-agent/cloudbuild.yaml
```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-t'
      - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_ARTIFACT_REPO}/logic-understanding-agent:${SHORT_SHA}'
      - '-t'
      - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_ARTIFACT_REPO}/logic-understanding-agent:latest'
      - '-f'
      - 'services/logic-understanding-agent/Dockerfile'
      - 'services/logic-understanding-agent'
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_ARTIFACT_REPO}/logic-understanding-agent:${SHORT_SHA}']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_ARTIFACT_REPO}/logic-understanding-agent:latest']
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'logic-understanding-agent'
      - '--image=${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_ARTIFACT_REPO}/logic-understanding-agent:${SHORT_SHA}'
      - '--region=${_REGION}'
      - '--platform=managed'
      - '--allow-unauthenticated'
      - '--memory=2Gi'
      - '--cpu=2'
      - '--timeout=300'
images:
  - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_ARTIFACT_REPO}/logic-understanding-agent:${SHORT_SHA}'
  - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_ARTIFACT_REPO}/logic-understanding-agent:latest'
substitutions:
  _REGION: us-central1
  _ARTIFACT_REPO: financial-reports
options:
  logging: CLOUD_LOGGING_ONLY
  machineType: 'E2_HIGHCPU_8'
```

#### services/logic-understanding-agent/Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc g++ && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--timeout-keep-alive", "300"]
```

#### services/visualization-agent/cloudbuild.yaml
```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-t'
      - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_ARTIFACT_REPO}/visualization-agent:${SHORT_SHA}'
      - '-t'
      - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_ARTIFACT_REPO}/visualization-agent:latest'
      - '-f'
      - 'services/visualization-agent/Dockerfile'
      - 'services/visualization-agent'
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_ARTIFACT_REPO}/visualization-agent:${SHORT_SHA}']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_ARTIFACT_REPO}/visualization-agent:latest']
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'visualization-agent'
      - '--image=${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_ARTIFACT_REPO}/visualization-agent:${SHORT_SHA}'
      - '--region=${_REGION}'
      - '--platform=managed'
      - '--allow-unauthenticated'
      - '--memory=1Gi'
      - '--cpu=1'
images:
  - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_ARTIFACT_REPO}/visualization-agent:${SHORT_SHA}'
  - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_ARTIFACT_REPO}/visualization-agent:latest'
substitutions:
  _REGION: us-central1
  _ARTIFACT_REPO: financial-reports
options:
  logging: CLOUD_LOGGING_ONLY
  machineType: 'E2_HIGHCPU_8'
```

#### services/visualization-agent/Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

---

### Шаг 1: GitHub OAuth Setup (один раз)

Следуй `docs/GITHUB_OAUTH_SETUP.md`:

```bash
# 1. Открой Cloud Console
open https://console.cloud.google.com/cloud-build/triggers

# 2. Connect Repository → GitHub → Authorize
# 3. Install Google Cloud Build в твой репозиторий
# 4. Получи connection ID:
gcloud builds connections list --region=us-central1

# Скопируй полный путь, например:
# projects/123456789/locations/global/connections/github-abcd1234
```

---

### Шаг 2: Настройка Terraform

```bash
cd /Users/sergejbykov/financial-reports-system/terraform

# Скопируй example
cp terraform.tfvars.example terraform.tfvars

# Отредактируй
nano terraform.tfvars
```

**Обнови в terraform.tfvars:**
```hcl
project_id = "financial-reports-ai-2024"
github_connection = "projects/YOUR_NUMBER/locations/global/connections/github-YOUR_ID"
```

---

### Шаг 3: Создай State Bucket

```bash
# Создай bucket для Terraform state
gsutil mb -p financial-reports-ai-2024 -l us-central1 gs://financial-reports-terraform-state

# Включи versioning
gsutil versioning set on gs://financial-reports-terraform-state
```

---

### Шаг 4: Запусти Terraform! 🚀

```bash
cd /Users/sergejbykov/financial-reports-system/terraform

# Инициализация
terraform init

# Просмотр изменений
terraform plan

# Применение (создаст ВСЁ!)
terraform apply

# Введи: yes
```

---

## ✅ Что создаст Terraform

### Cloud Build Triggers (5 шт)
- `frontend-service-deploy`
- `orchestrator-agent-deploy`
- `report-reader-agent-deploy`
- `logic-understanding-agent-deploy`
- `visualization-agent-deploy`

**Каждый триггер:**
- Срабатывает при push в main
- Только для изменений в своей папке `services/*/`
- Автоматически: build → push → deploy

### Cloud Run Services (5 шт)
- `frontend-service` (512Mi RAM, 1 CPU)
- `orchestrator-agent` (512Mi RAM, 1 CPU)
- `report-reader-agent` (1Gi RAM, 2 CPU)
- `logic-understanding-agent` (2Gi RAM, 2 CPU)
- `visualization-agent` (1Gi RAM, 1 CPU)

### Cloud Storage (2 бакета)
- `financial-reports-ai-2024-reports` (для отчетов, 90 дней retention)
- `financial-reports-ai-2024-charts` (для графиков, 30 дней retention)

### Pub/Sub (3 топика + подписки)
- `financial-reports-tasks` + subscription
- `financial-reports-results` + subscription
- `financial-reports-dead-letter` + subscription

### IAM
- Service Account: `financial-reports-sa@...`
- Cloud Build SA: `cloudbuild-deploy-sa@...`
- Все необходимые permissions

### Artifact Registry
- Repository: `financial-reports`
- Location: `us-central1`

---

## 🔄 После Terraform Apply

### Автоматический CI/CD процесс:

```
1. Разработчик → git push origin main
   ↓
2. GitHub → webhook → Cloud Build Trigger
   ↓
3. Cloud Build → читает cloudbuild.yaml
   ↓
4. Docker Build → создаёт образ
   ↓
5. Push to Artifact Registry
   ↓
6. Deploy to Cloud Run
   ↓
7. Готово! Новая версия работает ✅
```

---

## 🧪 Тестирование

### После успешного apply:

```bash
# Получи все URLs
terraform output

# Запусти интерактивный тест
cd /Users/sergejbykov/financial-reports-system
./scripts/interactive_demo.sh

# Выбери: 1 - Проверить здоровье всех сервисов
# Все должны показать: ✅ healthy
```

### Или вручную:

```bash
TOKEN=$(gcloud auth print-identity-token)

# Frontend
curl -H "Authorization: Bearer $TOKEN" \
  $(terraform output -raw frontend_url)/health

# Orchestrator
curl -H "Authorization: Bearer $TOKEN" \
  $(terraform output -raw orchestrator_url)/health

# И так далее для всех сервисов
```

---

## 🐛 Troubleshooting

### Ошибка: "Connection not found"
**Решение:** Проверь `github_connection` в `terraform.tfvars`
```bash
gcloud builds connections list --region=us-central1
```

### Ошибка: "Bucket already exists"
**Решение:** Удали старый bucket или используй другое имя
```bash
gsutil rm -r gs://financial-reports-terraform-state
```

### Cloud Build fails
**Решение:** Проверь, что все `cloudbuild.yaml` и `Dockerfile` созданы в каждом `services/*/`

### Service не деплоится
**Решение:** Проверь логи Cloud Build
```bash
gcloud builds list --limit=5
gcloud builds log BUILD_ID
```

---

## 📚 Дополнительные команды

```bash
# Удалить всё (осторожно!)
terraform destroy

# Обновить конфигурацию
terraform apply

# Посмотреть state
terraform show

# Список ресурсов
terraform state list

# Форматировать .tf файлы
terraform fmt -recursive

# Валидация
terraform validate
```

---

## 🎊 Финальный чеклист

- [ ] GitHub OAuth подключен
- [ ] `terraform.tfvars` настроен
- [ ] State bucket создан
- [ ] Все `cloudbuild.yaml` созданы (5 шт)
- [ ] Все `Dockerfile` созданы (5 шт)
- [ ] `terraform init` выполнен
- [ ] `terraform apply` выполнен успешно
- [ ] Все 5 сервисов healthy
- [ ] `interactive_demo.sh` работает

---

**🎉 После выполнения всех шагов - система полностью автоматизирована!**

**Каждый push в main → автоматический деплой → zero manual work!** ✨

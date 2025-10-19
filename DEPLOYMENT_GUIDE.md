# 🚀 Deployment Guide - Session 9
**Цель:** Собрать все 5 Docker образов и задеплоить в Cloud Run

---

## ✅ Предварительные требования

- [x] Cloud Build триггер "FRAI" настроен
- [x] Service Account с необходимыми permissions
- [x] Artifact Registry репозиторий создан
- [x] frontend-service образ уже собран (проверка работоспособности)

---

## 🎯 Вариант A: Автоматический Deploy (Рекомендуется!)

### Шаг 1: Запустить скрипт
```bash
# Скачать и запустить скрипт
chmod +x deploy_all_agents.sh
./deploy_all_agents.sh
```

Скрипт выполнит:
1. ✅ Обновит триггер на `cloudbuild.yaml`
2. 🔨 Запустит сборку всех 5 агентов (~10-15 минут)
3. 🔍 Проверит образы в Artifact Registry
4. 🚢 Задеплоит все сервисы в Cloud Run

### Ожидаемое время выполнения
- Обновление триггера: ~5 секунд
- Сборка образов: ~10-15 минут
- Deploy всех сервисов: ~5 минут
- **Общее время: ~20 минут**

---

## 🎯 Вариант B: Пошаговый Deploy (для контроля)

### Шаг 1: Обновить Cloud Build триггер
```bash
gcloud builds triggers update FRAI \
  --region=global \
  --build-config=cloudbuild.yaml \
  --project=financial-reports-ai-2024
```

### Шаг 2: Запустить сборку образов
```bash
# Вариант 2a: Через триггер
gcloud builds triggers run FRAI \
  --branch=main \
  --region=global \
  --project=financial-reports-ai-2024

# Вариант 2b: Через git push (проще!)
git add .
git commit -m "Build all 5 agents"
git push origin main
```

### Шаг 3: Мониторинг сборки
```bash
# Посмотреть последние builds
gcloud builds list --limit=1 --project=financial-reports-ai-2024

# Стримить логи build (замените BUILD_ID)
gcloud builds log <BUILD_ID> --stream
```

### Шаг 4: Проверить образы
```bash
gcloud artifacts docker images list \
  us-central1-docker.pkg.dev/financial-reports-ai-2024/financial-reports \
  --include-tags
```

Должно быть **5 образов**:
- ✅ frontend-service:latest
- ✅ orchestrator-agent:latest
- ✅ report-reader-agent:latest
- ✅ logic-understanding-agent:latest
- ✅ visualization-agent:latest

### Шаг 5: Deploy в Cloud Run
```bash
# Frontend Service
gcloud run deploy frontend-service \
  --image=us-central1-docker.pkg.dev/financial-reports-ai-2024/financial-reports/frontend-service:latest \
  --region=us-central1 \
  --allow-unauthenticated \
  --memory=2Gi \
  --cpu=2

# Orchestrator Agent
gcloud run deploy orchestrator-agent \
  --image=us-central1-docker.pkg.dev/financial-reports-ai-2024/financial-reports/orchestrator-agent:latest \
  --region=us-central1 \
  --allow-unauthenticated \
  --memory=2Gi \
  --cpu=2

# Report Reader Agent
gcloud run deploy report-reader-agent \
  --image=us-central1-docker.pkg.dev/financial-reports-ai-2024/financial-reports/report-reader-agent:latest \
  --region=us-central1 \
  --allow-unauthenticated \
  --memory=2Gi \
  --cpu=2

# Logic Understanding Agent
gcloud run deploy logic-understanding-agent \
  --image=us-central1-docker.pkg.dev/financial-reports-ai-2024/financial-reports/logic-understanding-agent:latest \
  --region=us-central1 \
  --allow-unauthenticated \
  --memory=2Gi \
  --cpu=2

# Visualization Agent
gcloud run deploy visualization-agent \
  --image=us-central1-docker.pkg.dev/financial-reports-ai-2024/financial-reports/visualization-agent:latest \
  --region=us-central1 \
  --allow-unauthenticated \
  --memory=2Gi \
  --cpu=2
```

---

## 🎯 Вариант C: Через Terraform

```bash
cd terraform
terraform plan
terraform apply
```

---

## 📊 Проверка результатов

### 1. Проверить Cloud Run сервисы
```bash
gcloud run services list --region=us-central1
```

Должно быть **5 сервисов** со статусом `Ready`.

### 2. Получить URLs всех сервисов
```bash
gcloud run services list \
  --region=us-central1 \
  --format='table(SERVICE,URL)' \
  --project=financial-reports-ai-2024
```

### 3. Протестировать каждый сервис
```bash
# Frontend
curl https://frontend-service-<hash>-uc.a.run.app/health

# Orchestrator
curl https://orchestrator-agent-<hash>-uc.a.run.app/health

# Остальные аналогично...
```

---

## 🐛 Troubleshooting

### Build не запускается
```bash
# Проверить статус триггера
gcloud builds triggers describe FRAI --region=global

# Проверить permissions
gcloud projects get-iam-policy financial-reports-ai-2024 \
  --flatten="bindings[].members" \
  --filter="bindings.members:financial-reports-sa@*"
```

### Образы не появляются в Registry
```bash
# Проверить логи build
gcloud builds list --limit=5
gcloud builds log <BUILD_ID>

# Проверить permissions на Artifact Registry
gcloud artifacts repositories get-iam-policy financial-reports \
  --location=us-central1
```

### Cloud Run deploy fails
```bash
# Проверить, что образ существует
gcloud artifacts docker images describe \
  us-central1-docker.pkg.dev/financial-reports-ai-2024/financial-reports/frontend-service:latest

# Проверить квоты
gcloud compute project-info describe --project=financial-reports-ai-2024
```

### Проблемы с сетью/доступом
```bash
# Проверить VPC connector (если используется)
gcloud compute networks vpc-access connectors list --region=us-central1

# Проверить Cloud Run permissions
gcloud run services get-iam-policy frontend-service --region=us-central1
```

---

## 📝 Важные заметки

1. **Последовательная сборка:** `cloudbuild.yaml` собирает агенты последовательно для экономии ресурсов
2. **Timeout:** Build может занять до 15 минут
3. **Машина:** Используется `E2_HIGHCPU_8` для быстрой сборки
4. **Теги:** Каждый образ тегируется и с `latest` и с `SHORT_SHA`
5. **Cloud Run:** Каждый сервис получает 2GB RAM и 2 CPU

---

## ✅ Критерии успеха

- [ ] Все 5 Docker образов собраны в Artifact Registry
- [ ] Все 5 сервисов задеплоены в Cloud Run
- [ ] Все сервисы отвечают на `/health` endpoint
- [ ] URLs всех сервисов доступны

---

## 🎉 После успешного deploy

1. Обновить `SESSION_9_STATUS.md` с новыми URLs
2. Протестировать взаимодействие между агентами
3. Настроить мониторинг и алерты
4. Добавить CI/CD для автоматических деплоев

---

**Последнее обновление:** 19 октября 2025

# 🚀 БЫСТРЫЙ СТАРТ - Terraform Deployment

## ⚡ 5 шагов до полной автоматизации

### 1️⃣ Создай 4 файла (из `docs/TERRAFORM_DEPLOYMENT.md`)

```bash
cd /Users/sergejbykov/financial-reports-system

# Logic Understanding Agent
nano services/logic-understanding-agent/cloudbuild.yaml
nano services/logic-understanding-agent/Dockerfile

# Visualization Agent
nano services/visualization-agent/cloudbuild.yaml
nano services/visualization-agent/Dockerfile
```

Содержимое всех файлов: **`docs/TERRAFORM_DEPLOYMENT.md`** → Шаг 0

---

### 2️⃣ GitHub OAuth (один раз, 5 мин)

Полная инструкция: **`docs/GITHUB_OAUTH_SETUP.md`**

```bash
# Открой Cloud Console
open https://console.cloud.google.com/cloud-build/triggers

# → Connect Repository → GitHub → Authorize → Install
# → Отмени создание триггера

# Получи connection ID
gcloud builds connections list --region=us-central1
```

---

### 3️⃣ Настрой Terraform

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars

# Обнови:
github_connection = "projects/YOUR_NUMBER/locations/global/connections/github-YOUR_ID"
```

---

### 4️⃣ State Bucket

```bash
gsutil mb -p financial-reports-ai-2024 -l us-central1 gs://financial-reports-terraform-state
gsutil versioning set on gs://financial-reports-terraform-state
```

---

### 5️⃣ Terraform Apply! 🎉

```bash
cd terraform
terraform init
terraform apply
# yes
```

**Готово!** Все 5 сервисов + CI/CD настроены автоматически!

---

## ✅ Проверка

```bash
terraform output
cd ..
./scripts/interactive_demo.sh
# Опция 1: Все сервисы ✅ healthy
```

---

## 🔄 Дальше - автоматически!

```bash
git push origin main
# → Cloud Build → Docker Build → Deploy
# → Готово! Никаких ручных действий!
```

---

## 📚 Полная документация

- **`SESSION_SUMMARY.md`** - что сделано в сессии
- **`docs/TERRAFORM_DEPLOYMENT.md`** - полное руководство
- **`docs/GITHUB_OAUTH_SETUP.md`** - OAuth setup
- **`terraform/README.md`** - Terraform overview

**Начни с:** `docs/TERRAFORM_DEPLOYMENT.md` 🚀

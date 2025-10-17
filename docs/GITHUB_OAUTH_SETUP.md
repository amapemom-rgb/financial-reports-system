# 🔐 GitHub OAuth Setup для Cloud Build

**Одноразовая ручная настройка для подключения GitHub к Google Cloud**

---

## 📋 Зачем это нужно?

Google Cloud Build требует авторизации через OAuth для доступа к вашему GitHub репозиторию. Terraform не может автоматически выполнить OAuth авторизацию (требуется интерактивное подтверждение в браузере), поэтому этот шаг выполняется **один раз вручную**.

После этого Terraform сможет создавать Cloud Build триггеры автоматически.

---

## ⏱️ Время выполнения: ~5 минут

---

## 🚀 Пошаговая инструкция

### Шаг 1: Откройте Cloud Console

1. Перейдите в Google Cloud Console:
   ```
   https://console.cloud.google.com/cloud-build/triggers
   ```

2. Выберите ваш проект:
   ```
   financial-reports-ai-2024
   ```

3. Убедитесь, что выбран правильный регион:
   ```
   us-central1
   ```

---

### Шаг 2: Подключите GitHub репозиторий

1. **Нажмите кнопку "CREATE TRIGGER"** (в верхней части страницы)

2. **Выберите источник:** 
   - Нажмите "CONNECT NEW REPOSITORY"

3. **Выберите платформу:**
   - Select source: **GitHub (Cloud Build GitHub App)**
   - Нажмите "CONTINUE"

4. **Authenticate with GitHub:**
   - Откроется окно GitHub OAuth
   - Войдите в свой GitHub аккаунт если нужно
   - **Authorize Google Cloud Build** (разрешите доступ)

5. **Install Google Cloud Build в GitHub:**
   - Выберите, где установить: **Only select repositories**
   - Выберите репозиторий: `amapemom-rgb/financial-reports-system`
   - Нажмите **"Install"**

6. **Выберите репозиторий:**
   - В списке выберите: `amapemom-rgb/financial-reports-system`
   - Нажмите **"CONNECT"**

7. **Согласитесь с условиями:**
   - Прочитайте и согласитесь с terms
   - Нажмите **"DONE"**

8. **Отмените создание триггера:**
   - Вернитесь на страницу триггеров (не создавайте триггер вручную)
   - Триггеры создаст Terraform автоматически

---

### Шаг 3: Получите Connection ID

После подключения GitHub, нужно получить ID созданного connection:

#### Вариант A: Через gcloud CLI (рекомендуется)

```bash
# Получить список connections
gcloud builds connections list --region=us-central1

# Вы увидите что-то вроде:
# NAME                                    CREATE_TIME          UPDATE_TIME
# projects/.../locations/global/connections/github-xxxxx  2025-01-20  2025-01-20
```

Скопируйте **полный путь** connection (вся строка `projects/.../connections/...`)

#### Вариант B: Через Cloud Console

1. Перейдите:
   ```
   https://console.cloud.google.com/cloud-build/repositories/2nd-gen
   ```

2. Найдите ваш репозиторий `financial-reports-system`

3. Нажмите на него и скопируйте **Connection name** из деталей

4. Формат будет:
   ```
   projects/PROJECT_NUMBER/locations/global/connections/github-CONNECTION_ID
   ```

---

### Шаг 4: Добавьте Connection ID в Terraform

1. Откройте файл `terraform/terraform.tfvars`:
   ```bash
   cd /Users/sergejbykov/financial-reports-system/terraform
   nano terraform.tfvars
   ```

2. Добавьте или обновите переменную `github_connection`:
   ```hcl
   # GitHub Connection (created manually via Console)
   github_connection = "projects/YOUR_PROJECT_NUMBER/locations/global/connections/github-YOUR_CONNECTION_ID"
   ```

3. **Пример:**
   ```hcl
   github_connection = "projects/123456789/locations/global/connections/github-abcd1234"
   ```

4. Сохраните файл

---

### Шаг 5: Проверьте настройку

Проверьте, что connection работает:

```bash
# Проверить connection
gcloud builds connections describe github-YOUR_CONNECTION_ID \
  --region=us-central1

# Должно вернуть детали connection со статусом ACTIVE
```

---

## ✅ Готово!

Теперь вы можете запустить Terraform:

```bash
cd /Users/sergejbykov/financial-reports-system/terraform

# Инициализация (первый раз)
terraform init

# Применить конфигурацию
terraform apply
```

Terraform автоматически создаст:
- ✅ 5 Cloud Build триггеров (по одному на каждый микросервис)
- ✅ 5 Cloud Run сервисов
- ✅ Pub/Sub топики и подписки
- ✅ Cloud Storage бакеты
- ✅ IAM роли и permissions

---

## 🔄 При каждом push в GitHub

После настройки, при каждом push в ветку `main`:

1. **GitHub → Cloud Build** (автоматически)
   - Изменения в `services/frontend-service/**` → триггер frontend
   - Изменения в `services/orchestrator-agent/**` → триггер orchestrator
   - И т.д. для всех сервисов

2. **Cloud Build → Docker Build** (автоматически)
   - Собирает Docker образ из `Dockerfile`
   - Использует `cloudbuild.yaml` для инструкций

3. **Cloud Build → Cloud Run** (автоматически)
   - Деплоит новый образ в Cloud Run
   - Обновляет сервис без downtime

4. **Готово!** 🎉

---

## 🐛 Troubleshooting

### Проблема: "Permission denied" при создании триггера

**Решение:** Убедитесь, что у вас есть роль:
```bash
gcloud projects add-iam-policy-binding financial-reports-ai-2024 \
  --member="user:YOUR_EMAIL@gmail.com" \
  --role="roles/cloudbuild.builds.editor"
```

### Проблема: Connection не найден

**Решение:** Проверьте регион:
```bash
# Попробуйте global вместо us-central1
gcloud builds connections list --region=global
```

### Проблема: GitHub App не установлен

**Решение:** 
1. Перейдите: https://github.com/settings/installations
2. Найдите "Google Cloud Build"
3. Убедитесь, что разрешен доступ к репозиторию

---

## 📚 Дополнительные ресурсы

- [Cloud Build GitHub Documentation](https://cloud.google.com/build/docs/automating-builds/github/connect-repo-github)
- [Terraform google_cloudbuildv2_connection](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/cloudbuildv2_connection)
- [Cloud Build Triggers](https://cloud.google.com/build/docs/automating-builds/create-manage-triggers)

---

**🎊 После завершения этой настройки, весь дальнейший деплой будет полностью автоматическим!**

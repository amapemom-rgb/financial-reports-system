# 🚀 Автоматический деплой - Инструкция

## ✅ Что создано

Вся инфраструктура для автоматического деплоя готова:

1. ✅ `web-ui/Dockerfile` - контейнер с nginx
2. ✅ `web-ui/nginx.conf` - конфигурация с CORS
3. ✅ `web-ui/cloudbuild.yaml` - автоматический деплой
4. ✅ `terraform/modules/web-ui/` - Terraform модули
5. ✅ Cloud Build триггер (автоматический)

## 🎯 Что ты делаешь ОДИН раз (5 команд)

### Команда 1: Подключить GitHub к Cloud Build

```bash
# Это нужно сделать ОДИН раз в GCP Console:
# 1. Открой: https://console.cloud.google.com/cloud-build/triggers
# 2. Нажми "Connect Repository"
# 3. Выбери GitHub
# 4. Авторизуйся в GitHub
# 5. Выбери репозиторий: amapemom-rgb/financial-reports-system
# 6. Нажми "Connect"
```

**Это делается через UI, потому что требует OAuth с GitHub.**

### Команда 2: Собрать первый образ Web UI

```bash
cd /Users/sergejbykov/financial-reports-system

# Собрать и загрузить образ
gcloud builds submit --config=web-ui/cloudbuild.yaml .
```

**Время:** ~3 минуты

### Команда 3: Применить Terraform

```bash
cd terraform

# Инициализировать (если ещё не сделано)
terraform init

# Применить изменения
terraform apply
```

**Terraform:**
- Создаст Web UI сервис в Cloud Run
- Настроит Cloud Build триггер
- Выдаст URL веб-интерфейса

**Время:** ~2 минуты

### Команда 4: Получить URL

```bash
# После terraform apply увидишь:
terraform output web_ui_url

# Или:
gcloud run services describe web-ui --region=us-central1 --format='value(status.url)'
```

**Скопируй этот URL!**

### Команда 5: Открой в браузере

```bash
# Автоматически открыть
open $(terraform output -raw web_ui_url)

# Или просто скопируй URL и открой вручную
```

---

## 🎉 ЧТО ПРОИСХОДИТ ДАЛЬШЕ (автоматически)

После этих 5 команд:

```
1. Ты (или я) пушу код в GitHub
   │
   ▼
2. Cloud Build автоматически:
   ├─ Видит изменения в web-ui/
   ├─ Собирает Docker образ
   ├─ Загружает в Container Registry
   └─ Деплоит в Cloud Run
   │
   ▼
3. Через 2-3 минуты:
   └─ Новая версия доступна по URL!
```

**БЕЗ ТЕРМИНАЛА! БЕЗ КОМАНД!**

Я просто пушу в GitHub → всё обновляется автоматически!

---

## 📊 Текущая архитектура

```
GitHub (код)
    │
    │ webhook
    ▼
Cloud Build (автоматически)
    │
    ├─ docker build
    ├─ docker push → Container Registry
    └─ gcloud run deploy
    │
    ▼
Cloud Run (production)
    │
    └─ https://web-ui-XXXXX.run.app ✅
```

---

## 🔧 Что делать СЕЙЧАС

### Шаг 1: Подключить GitHub (UI)

Открой: https://console.cloud.google.com/cloud-build/triggers?project=financial-reports-ai-2024

Нажми **"CONNECT REPOSITORY"** → GitHub → Авторизуйся → Выбери репозиторий

### Шаг 2-5: Выполни команды

```bash
# Команда 2: Первый build
cd /Users/sergejbykov/financial-reports-system
gcloud builds submit --config=web-ui/cloudbuild.yaml .

# Команда 3: Terraform
cd terraform
terraform init
terraform apply

# Команда 4: Получить URL
terraform output web_ui_url

# Команда 5: Открыть
open $(terraform output -raw web_ui_url)
```

---

## ✅ Проверка что работает

### После деплоя проверь:

```bash
# 1. Web UI доступен
curl -I $(terraform output -raw web_ui_url)
# Должен вернуть: HTTP/2 200

# 2. Health check работает
curl $(terraform output -raw web_ui_url)/health
# Должен вернуть: healthy

# 3. Открой в браузере
open $(terraform output -raw web_ui_url)
# Должен открыться интерфейс
```

---

## 🎯 Дальше ВСЁ АВТОМАТИЧЕСКИ

**Я пушу код:**
```bash
# Я делаю изменения в web-ui/index.html
# Коммичу в GitHub
```

**Cloud Build видит изменения:**
```
Cloud Build trigger активируется
→ Собирает новый образ
→ Деплоит автоматически
→ Через 2-3 минуты новая версия live!
```

**Ты просто обновляешь страницу в браузере!**

---

## 🐛 Troubleshooting

### Если Cloud Build не срабатывает:

```bash
# Проверь триггеры
gcloud builds triggers list

# Если пусто - нужно подключить GitHub через UI
```

### Если terraform apply падает:

```bash
# Проверь что образ существует
gcloud container images list --repository=gcr.io/financial-reports-ai-2024

# Должен быть: gcr.io/financial-reports-ai-2024/web-ui
```

### Если URL не открывается:

```bash
# Проверь что сервис запущен
gcloud run services list --region=us-central1

# Должен быть: web-ui
```

---

## 📈 Итог

**До:**
```
Ты → Терминал → Python → localhost:8000
```

**После:**
```
Я → GitHub push → Cloud Build → https://web-ui-XXX.run.app
                                          ↑
                                    Ты просто открываешь
```

**Никаких команд больше не нужно!**

---

**Готов? Выполняй 5 команд и всё заработает автоматически!** 🚀

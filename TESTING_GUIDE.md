# 🧪 Инструкция по тестированию исправленного скрипта

**Дата:** 2025-10-17  
**Статус:** ✅ Готово к тестированию

## 📋 Что было исправлено

✅ `scripts/interactive_demo.sh` - health checks теперь работают корректно  
✅ `scripts/test_health.sh` - новый скрипт для быстрой проверки  
✅ `docs/BUGFIX_INTERACTIVE_SCRIPT.md` - полная документация исправления

## 🚀 Быстрый тест (5 минут)

### 1. Обновить локальный репозиторий

```bash
cd /Users/sergejbykov/financial-reports-system
git pull origin main
```

### 2. Сделать скрипты исполняемыми

```bash
chmod +x scripts/interactive_demo.sh
chmod +x scripts/test_health.sh
```

### 3. Быстрая проверка здоровья сервисов

```bash
# Простой режим
./scripts/test_health.sh

# Ожидаемый результат:
# Frontend:            ✅ healthy
# Orchestrator:        ✅ healthy
# Report Reader:       ✅ healthy
# Logic Agent:         ✅ healthy
# Visualization:       ✅ healthy
#
# ✅ All services are healthy!
```

```bash
# Verbose режим (если что-то не работает)
./scripts/test_health.sh -v
```

### 4. Тест интерактивного меню

```bash
./scripts/interactive_demo.sh
```

**В меню выбери:**
- `1` - Проверить здоровье всех сервисов
- Должно показать ✅ healthy для всех 5 сервисов с HTTP 200

**Ожидаемый вывод:**
```
🏥 Проверка здоровья сервисов...

  frontend-service: ✅ healthy (HTTP 200)
  orchestrator-agent: ✅ healthy (HTTP 200)
  report-reader-agent: ✅ healthy (HTTP 200)
  logic-understanding-agent: ✅ healthy (HTTP 200)
  visualization-agent: ✅ healthy (HTTP 200)
```

### 5. Тест с verbose режимом

```bash
# В интерактивном меню:
# v - Включить verbose режим
# 1 - Проверить здоровье

# Должны видеть дополнительную информацию при ошибках
```

## 🔧 Полный E2E тест (10 минут)

### 1. Создать тестовый файл

```bash
./scripts/interactive_demo.sh

# В меню: 2 - Создать тестовый CSV файл
# Файл создастся в /tmp/financial_report_test.csv
```

### 2. Загрузить и проанализировать

```bash
# В меню: 3 - Загрузить файл и запустить анализ
# 
# Ожидается:
# 1. Успешная загрузка файла (получен file_id)
# 2. Создание задачи (получен task_id)
# 3. Ожидание 10 секунд
# 4. Проверка статуса задачи
```

### 3. Создать визуализацию

```bash
# В меню: 4 - Создать визуализацию
#
# Ожидается:
# - Создан график
# - Получен chart_url
# - Предложение открыть в браузере
```

### 4. Посмотреть все задачи

```bash
# В меню: 5 - Посмотреть все задачи
#
# Должен показать список задач в JSON формате
```

### 5. Проверить AI агента

```bash
# В меню: 8 - Информация об AI агенте
#
# Должна показать информацию о Logic Understanding Agent v2
```

## ✅ Чеклист проверки

Отметь каждый пункт после успешного выполнения:

- [ ] `git pull` выполнен без ошибок
- [ ] `test_health.sh` показывает все сервисы healthy
- [ ] Interactive menu запускается без ошибок
- [ ] Опция 1 (health check) показывает ✅ для всех 5 сервисов
- [ ] Опция 2 (создать CSV) создаёт файл успешно
- [ ] Опция 3 (загрузка) работает:
  - [ ] Файл загружается (file_id получен)
  - [ ] Задача создаётся (task_id получен)
  - [ ] Статус задачи проверяется
- [ ] Опция 4 (визуализация) создаёт график с URL
- [ ] Опция 5 (список задач) показывает задачи
- [ ] Опция 8 (AI агент) показывает информацию
- [ ] Опция v (verbose) включается/выключается
- [ ] Опция 0 (выход) работает корректно

## 🐛 Что делать при проблемах

### Проблема: "Failed to get auth token"

**Решение:**
```bash
gcloud auth login
gcloud config set project financial-reports-ai-2024
```

### Проблема: Сервис показывает HTTP 403

**Причина:** Токен истёк или нет прав

**Решение:**
```bash
# Обновить токен
gcloud auth application-default login

# Проверить проект
gcloud config get-value project
```

### Проблема: Connection timeout

**Причина:** Сервис недоступен или сетевые проблемы

**Решение:**
```bash
# Проверить вручную
TOKEN=$(gcloud auth print-identity-token)
curl -v -H "Authorization: Bearer $TOKEN" \
  https://frontend-service-38390150695.us-central1.run.app/health
```

### Проблема: HTTP 500 или unhealthy

**Причина:** Проблема на стороне сервиса

**Решение:**
```bash
# Посмотреть логи сервиса
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=frontend-service" \
  --limit 50 \
  --format json

# Или через консоль GCP:
# https://console.cloud.google.com/run?project=financial-reports-ai-2024
```

### Проблема: jq command not found

**Решение:**
```bash
# macOS
brew install jq

# Ubuntu/Debian
sudo apt-get install jq
```

## 📊 Ожидаемые результаты

### test_health.sh должен вернуть:
```bash
🏥 Checking health of all services...

Frontend:            ✅ healthy
Orchestrator:        ✅ healthy
Report Reader:       ✅ healthy
Logic Agent:         ✅ healthy
Visualization:       ✅ healthy

✅ All services are healthy!
```

### interactive_demo.sh опция 1 должна показать:
```bash
🏥 Проверка здоровья сервисов...

  frontend-service: ✅ healthy (HTTP 200)
  orchestrator-agent: ✅ healthy (HTTP 200)
  report-reader-agent: ✅ healthy (HTTP 200)
  logic-understanding-agent: ✅ healthy (HTTP 200)
  visualization-agent: ✅ healthy (HTTP 200)
```

### interactive_demo.sh опция 3 должна показать:
```json
{
  "file_id": "reports/financial_report_test_xxx.csv",
  "message": "File uploaded successfully"
}

{
  "task_id": "task_xxx",
  "workflow_type": "analyze_report",
  "status": "pending"
}

// После ожидания:
{
  "task_id": "task_xxx",
  "status": "completed",
  "result": { ... }
}
```

## 🎯 Следующие шаги после успешного тестирования

1. ✅ Все тесты прошли успешно
2. Создать GitHub Release v1.0.0-rc1
3. Написать release notes
4. Подготовить CI/CD pipeline
5. Настроить monitoring

## 📝 Отчёт о тестировании

После прохождения всех тестов заполни:

**Дата тестирования:** _____________  
**Тестировщик:** Сергей Быков  
**Версия:** v1.0.0-rc1

**Результаты:**
- [ ] Все тесты пройдены успешно ✅
- [ ] Найдены баги (описать ниже) ❌

**Описание багов (если есть):**
```
...
```

**Дополнительные заметки:**
```
...
```

---

## 💡 Полезные команды для отладки

```bash
# Получить свежий токен
TOKEN=$(gcloud auth print-identity-token)

# Проверить конкретный сервис вручную
curl -H "Authorization: Bearer $TOKEN" \
  https://frontend-service-38390150695.us-central1.run.app/health | jq

# Посмотреть все переменные окружения
env | grep GOOGLE

# Проверить настройки gcloud
gcloud config list

# Посмотреть логи в реальном времени
gcloud logging tail "resource.type=cloud_run_revision" \
  --format=json

# Перезапустить все сервисы (если нужно)
gcloud run services list --project=financial-reports-ai-2024
```

---

**🚀 Готово к тестированию! Удачи!**

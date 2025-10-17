# 🚀 Быстрый старт - Financial Reports System

## 📋 Перед началом

Убедись что:
- ✅ У тебя установлен `gcloud` CLI
- ✅ Ты залогинен: `gcloud auth login`
- ✅ Установлен `jq` для красивого JSON: `brew install jq` (на Mac)

## 🎯 3 способа начать

### Вариант 1: Интерактивное меню (рекомендуется) 🌟

```bash
# Сделать скрипты исполняемыми
chmod +x scripts/*.sh

# Запустить интерактивное меню
./scripts/interactive_demo.sh
```

**Что внутри:**
- 🏥 Проверка здоровья всех сервисов
- 📊 Создание тестового файла
- 📤 Загрузка и анализ
- 📈 Создание графиков
- 📋 Просмотр задач
- 🤖 Информация об AI агенте

### Вариант 2: Демонстрация обучения AI 🎓

```bash
# Показать как агент обучается
./scripts/demo_ai_training.sh
```

**Что увидишь:**
- Как агент отвечает на простые вопросы
- Как запоминает новые понятия (EBITDA)
- Как использует контекст диалога
- Как улучшается с каждым запросом

### Вариант 3: E2E тест системы 🧪

```bash
# Проверить что всё работает
./scripts/test_e2e.sh
```

**Что проверяется:**
- Все 5 сервисов здоровы
- Создание задачи работает
- Workflow выполняется
- Статусы корректны

## 📚 Полная документация

**Читай подробности:**
- [USER_GUIDE.md](USER_GUIDE.md) - полное руководство пользователя
- [PRODUCTION_READY.md](PRODUCTION_READY.md) - что готово и как использовать

## 🎯 Быстрые команды

### Проверить систему

```bash
# Получить токен
export TOKEN=$(gcloud auth print-identity-token)

# Проверить Frontend
curl -H "Authorization: Bearer $TOKEN" \
  https://frontend-service-38390150695.us-central1.run.app/health | jq

# Проверить все сервисы
for service in frontend-service orchestrator-agent report-reader-agent logic-understanding-agent visualization-agent; do
  echo "Checking $service..."
  curl -s -H "Authorization: Bearer $TOKEN" \
    "https://${service}-38390150695.us-central1.run.app/health" | jq
done
```

### Создать тестовый файл

```bash
cat > /tmp/test_report.csv << 'EOF'
Месяц,Доход,Расходы,Прибыль
Январь,100000,75000,25000
Февраль,120000,80000,40000
Март,110000,78000,32000
EOF
```

### Загрузить и проанализировать

```bash
# 1. Загрузить файл
FILE_RESPONSE=$(curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/test_report.csv" \
  https://frontend-service-38390150695.us-central1.run.app/upload)

echo $FILE_RESPONSE | jq

# 2. Получить file_id
FILE_ID=$(echo $FILE_RESPONSE | jq -r '.file_id')

# 3. Создать задачу
TASK_RESPONSE=$(curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_type": "analyze_report",
    "input_data": {
      "file_path": "'$FILE_ID'",
      "query": "Проанализируй отчёт"
    }
  }' \
  https://orchestrator-agent-38390150695.us-central1.run.app/tasks)

echo $TASK_RESPONSE | jq

# 4. Получить task_id
TASK_ID=$(echo $TASK_RESPONSE | jq -r '.task_id')

# 5. Подождать 5 секунд
sleep 5

# 6. Проверить результат
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://orchestrator-agent-38390150695.us-central1.run.app/tasks/$TASK_ID" | jq
```

### Создать график

```bash
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "chart_type": "bar",
    "data": {
      "x": ["Январь", "Февраль", "Март"],
      "y": [100000, 120000, 110000]
    },
    "title": "Доходы по месяцам"
  }' \
  https://visualization-agent-38390150695.us-central1.run.app/create | jq
```

## 🎤 Голосовой анализ

**Требования:**
- Аудио файл (WAV, MP3, FLAC)
- Уже загруженный отчёт

```bash
# Записать аудио (на Mac)
# Говори: "Какая общая прибыль?"
rec -r 16000 -c 1 /tmp/question.wav
# Ctrl+C для остановки

# Отправить на анализ
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -F "audio=@/tmp/question.wav" \
  -F "report_id=$FILE_ID" \
  https://frontend-service-38390150695.us-central1.run.app/voice/analyze | jq
```

## 🐛 Если что-то не работает

### Проблема: "Failed to get auth token"

```bash
# Залогиниться заново
gcloud auth login
gcloud auth application-default login

# Проверить
gcloud auth list
```

### Проблема: "Permission denied"

```bash
# Установить правильный проект
gcloud config set project financial-reports-ai-2024

# Проверить
gcloud config get-value project
```

### Проблема: "Service unavailable"

```bash
# Проверить статус сервисов в GCP
gcloud run services list --region=us-central1

# Посмотреть логи
gcloud logging read "resource.type=cloud_run_revision" --limit 50
```

## 📊 Мониторинг

### Открыть Cloud Console

```bash
# Все сервисы
open "https://console.cloud.google.com/run?project=financial-reports-ai-2024"

# Логи
open "https://console.cloud.google.com/logs?project=financial-reports-ai-2024"

# Мониторинг
open "https://console.cloud.google.com/monitoring?project=financial-reports-ai-2024"
```

### Посмотреть логи конкретного сервиса

```bash
# Frontend
gcloud logging read "resource.labels.service_name=frontend-service" --limit 20 --format json

# Logic Agent
gcloud logging read "resource.labels.service_name=logic-understanding-agent" --limit 20 --format json
```

## 💡 Полезные трюки

### Массовая обработка файлов

```bash
for file in /path/to/reports/*.csv; do
  echo "Processing $file..."
  
  FILE_ID=$(curl -s -X POST \
    -H "Authorization: Bearer $TOKEN" \
    -F "file=@$file" \
    https://frontend-service-38390150695.us-central1.run.app/upload | jq -r '.file_id')
  
  curl -s -X POST \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "workflow_type": "analyze_report",
      "input_data": {
        "file_path": "'$FILE_ID'",
        "query": "Сделай полный анализ"
      }
    }' \
    https://orchestrator-agent-38390150695.us-central1.run.app/tasks
  
  sleep 2
done
```

### Сохранить токен на час

```bash
# Добавить в ~/.bashrc или ~/.zshrc
export FR_TOKEN=$(gcloud auth print-identity-token)

# Использовать
curl -H "Authorization: Bearer $FR_TOKEN" ...
```

## 🎉 Готово!

Теперь ты можешь:
- ✅ Анализировать финансовые отчёты
- ✅ Использовать голосовой интерфейс
- ✅ Создавать визуализации
- ✅ Обучать AI агентов
- ✅ Мониторить систему

**Система полностью готова к использованию!** 🚀

---

**Нужна помощь?** Читай [USER_GUIDE.md](USER_GUIDE.md) или открывай issue на GitHub!

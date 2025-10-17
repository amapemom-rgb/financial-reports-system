# 🎯 Руководство пользователя - Financial Reports System

## 📋 Содержание
1. [Подготовка к работе](#подготовка)
2. [Сценарий 1: Анализ Excel файла](#сценарий-1-анализ-excel-файла)
3. [Сценарий 2: Анализ Google Sheets](#сценарий-2-анализ-google-sheets)
4. [Сценарий 3: Голосовой анализ](#сценарий-3-голосовой-анализ)
5. [Сценарий 4: Создание визуализаций](#сценарий-4-создание-визуализаций)
6. [Мониторинг и отладка](#мониторинг-и-отладка)
7. [Обучение AI агентов](#обучение-ai-агентов)

---

## 🔧 Подготовка

### 1. Получить токен аутентификации

```bash
# Получить токен (действует 1 час)
export TOKEN=$(gcloud auth print-identity-token)

# Проверить что токен получен
echo $TOKEN
```

### 2. Сохранить URL сервисов

```bash
# Базовые URL
export FRONTEND_URL="https://frontend-service-38390150695.us-central1.run.app"
export ORCHESTRATOR_URL="https://orchestrator-agent-38390150695.us-central1.run.app"
export REPORT_READER_URL="https://report-reader-agent-38390150695.us-central1.run.app"
export LOGIC_AGENT_URL="https://logic-understanding-agent-38390150695.us-central1.run.app"
export VISUALIZATION_URL="https://visualization-agent-38390150695.us-central1.run.app"
```

### 3. Проверить что все работает

```bash
# Быстрая проверка всех сервисов
curl -s -H "Authorization: Bearer $TOKEN" "$FRONTEND_URL/health" | jq
curl -s -H "Authorization: Bearer $TOKEN" "$ORCHESTRATOR_URL/health" | jq
curl -s -H "Authorization: Bearer $TOKEN" "$REPORT_READER_URL/health" | jq
curl -s -H "Authorization: Bearer $TOKEN" "$LOGIC_AGENT_URL/health" | jq
curl -s -H "Authorization: Bearer $TOKEN" "$VISUALIZATION_URL/health" | jq
```

**Ожидаемый результат:** Все 5 сервисов вернут `{"status":"healthy",...}`

---

## 📊 Сценарий 1: Анализ Excel файла

### Шаг 1: Подготовить тестовый Excel файл

Создадим простой финансовый отчёт в Excel:

```bash
# Создать тестовый CSV (для простоты)
cat > /tmp/financial_report.csv << 'EOF'
Месяц,Доход,Расходы,Прибыль
Январь,100000,75000,25000
Февраль,120000,80000,40000
Март,110000,78000,32000
Апрель,130000,85000,45000
Май,125000,82000,43000
Июнь,140000,90000,50000
EOF

echo "✅ Файл создан: /tmp/financial_report.csv"
```

### Шаг 2: Загрузить файл через Frontend API

```bash
# Загрузить файл
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/financial_report.csv" \
  "$FRONTEND_URL/upload"
```

**Что происходит:**
1. Frontend принимает файл
2. Загружает в Cloud Storage
3. Возвращает file_id

**Ожидаемый ответ:**
```json
{
  "file_id": "reports/20251017_123456_financial_report.csv",
  "bucket": "financial-reports-ai-2024-reports",
  "size": 234,
  "message": "File uploaded successfully"
}
```

### Шаг 3: Создать задачу на полный анализ

```bash
# Сохранить file_id из предыдущего ответа
export FILE_ID="reports/20251017_123456_financial_report.csv"

# Создать задачу
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_type": "analyze_report",
    "input_data": {
      "file_path": "'$FILE_ID'",
      "query": "Проанализируй финансовый отчёт. Какая динамика доходов и расходов? Есть ли тренды?"
    }
  }' \
  "$ORCHESTRATOR_URL/tasks" | jq
```

**Что происходит:**
1. ⏱️ **Orchestrator** создаёт задачу и запускает workflow
2. 📖 **Report Reader** читает файл из Storage и парсит данные
3. 🧠 **Logic Agent** (Reasoning Engine) анализирует данные с помощью Gemini:
   - Вычисляет тренды
   - Определяет паттерны
   - Делает прогнозы
   - Формулирует выводы
4. 📊 **Visualization Agent** создаёт графики (если нужно)
5. ✅ **Orchestrator** возвращает результат

**Ожидаемый ответ:**
```json
{
  "task_id": "abc123-def456-ghi789",
  "status": "pending",
  "workflow_type": "analyze_report",
  "current_step": "reading",
  "created_at": "2025-10-17T10:30:00Z"
}
```

### Шаг 4: Проверить статус задачи

```bash
# Сохранить task_id
export TASK_ID="abc123-def456-ghi789"

# Проверить статус (можно запускать много раз)
curl -H "Authorization: Bearer $TOKEN" \
  "$ORCHESTRATOR_URL/tasks/$TASK_ID" | jq
```

**Статусы задачи:**
- `pending` - Задача создана, ожидает начала
- `reading` - Читаем файл
- `analyzing` - AI анализирует данные
- `visualizing` - Создаём графики
- `completed` - Готово! ✅
- `failed` - Ошибка ❌

**Когда статус = `completed`, увидишь результат:**
```json
{
  "task_id": "abc123-def456-ghi789",
  "status": "completed",
  "workflow_type": "analyze_report",
  "output_data": {
    "report_data": {
      "rows": 6,
      "columns": ["Месяц", "Доход", "Расходы", "Прибыль"],
      "summary": {...}
    },
    "analysis": {
      "insights": "Доходы растут на 8% в месяц. Расходы растут медленнее - 6%...",
      "trends": [...],
      "recommendations": [...]
    },
    "visualization": {
      "chart_url": "https://storage.googleapis.com/...",
      "chart_type": "line"
    }
  }
}
```

---

## 📈 Сценарий 2: Анализ Google Sheets

### Шаг 1: Создать Google Sheets

1. Открой https://sheets.google.com
2. Создай новую таблицу
3. Заполни данными (как в примере выше)
4. Скопируй Spreadsheet ID из URL:
   ```
   https://docs.google.com/spreadsheets/d/1ABC123DEF456/edit
                                          ^^^^^^^^^^^^^^^^
                                          это Spreadsheet ID
   ```

### Шаг 2: Запустить анализ

```bash
export SPREADSHEET_ID="1ABC123DEF456"

curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_type": "analyze_report",
    "input_data": {
      "spreadsheet_id": "'$SPREADSHEET_ID'",
      "sheet_name": "Sheet1",
      "query": "Какова средняя прибыль за полугодие?"
    }
  }' \
  "$ORCHESTRATOR_URL/tasks" | jq
```

**Что происходит:**
1. Report Reader подключается к Google Sheets API
2. Читает данные из указанного листа
3. Передаёт в Logic Agent для анализа
4. AI отвечает на вопрос используя данные

---

## 🎤 Сценарий 3: Голосовой анализ

### Шаг 1: Записать аудио вопрос

```bash
# На Mac можно записать аудио через sox или QuickTime
# Или используй любой аудио рекордер
# Формат: WAV, MP3, FLAC (до 10MB)

# Пример с sox (если установлен):
rec -r 16000 -c 1 /tmp/question.wav

# Говори в микрофон: "Какая общая прибыль за второй квартал?"
# Нажми Ctrl+C для остановки
```

### Шаг 2: Отправить аудио на анализ

```bash
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -F "audio=@/tmp/question.wav" \
  -F "report_id=reports/20251017_123456_financial_report.csv" \
  "$FRONTEND_URL/voice/analyze"
```

**Что происходит:**
1. 🎤 **Frontend** получает аудио файл
2. 🔊 **Speech-to-Text** транскрибирует аудио в текст
3. 📊 **Report Reader** загружает указанный отчёт
4. 🧠 **Logic Agent** анализирует отчёт с учётом вопроса
5. 💬 **Text-to-Speech** синтезирует голосовой ответ
6. ✅ Возвращает и текст, и аудио ответ

**Ожидаемый ответ:**
```json
{
  "transcript": "Какая общая прибыль за второй квартал?",
  "answer_text": "Общая прибыль за второй квартал (апрель-июнь) составила 138,000 рублей",
  "answer_audio_url": "https://storage.googleapis.com/.../answer_123.mp3",
  "processing_time": 3.5
}
```

### Шаг 3: Прослушать ответ

```bash
# Скачать аудио ответ
curl -o /tmp/answer.mp3 "https://storage.googleapis.com/.../answer_123.mp3"

# Прослушать (на Mac)
afplay /tmp/answer.mp3
```

---

## 📊 Сценарий 4: Создание визуализаций

### Создать график напрямую

```bash
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "chart_type": "line",
    "data": {
      "x": ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь"],
      "y": [25000, 40000, 32000, 45000, 43000, 50000]
    },
    "title": "Динамика прибыли",
    "x_label": "Месяц",
    "y_label": "Прибыль (руб)"
  }' \
  "$VISUALIZATION_URL/create" | jq
```

**Типы графиков:**
- `line` - Линейный график (тренды)
- `bar` - Столбчатая диаграмма (сравнение)
- `pie` - Круговая диаграмма (доли)
- `scatter` - Точечная диаграмма (корреляции)
- `area` - График с областью (объёмы)

**Ожидаемый ответ:**
```json
{
  "chart_id": "chart_xyz789",
  "chart_url": "https://storage.googleapis.com/financial-reports-ai-2024-visualizations/chart_xyz789.html",
  "chart_type": "line",
  "created_at": "2025-10-17T10:45:00Z"
}
```

### Просмотреть график

```bash
# Открыть в браузере
open "https://storage.googleapis.com/.../chart_xyz789.html"

# Или скачать
curl -o /tmp/chart.html "https://storage.googleapis.com/.../chart_xyz789.html"
open /tmp/chart.html
```

---

## 🔍 Мониторинг и отладка

### Посмотреть все задачи

```bash
# Все задачи
curl -H "Authorization: Bearer $TOKEN" \
  "$ORCHESTRATOR_URL/tasks" | jq

# Только завершённые
curl -H "Authorization: Bearer $TOKEN" \
  "$ORCHESTRATOR_URL/tasks?status=completed" | jq

# Только неудачные
curl -H "Authorization: Bearer $TOKEN" \
  "$ORCHESTRATOR_URL/tasks?status=failed" | jq
```

### Посмотреть логи в GCP

```bash
# Логи Frontend Service
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=frontend-service" --limit 50 --format json

# Логи Logic Agent
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=logic-understanding-agent" --limit 50 --format json

# Логи всех сервисов за последние 10 минут
gcloud logging read "resource.type=cloud_run_revision" --limit 100 --format json
```

### Проверить метрики

```bash
# Открыть Cloud Console
open "https://console.cloud.google.com/run?project=financial-reports-ai-2024"

# Посмотреть:
# - Количество запросов
# - Latency
# - Ошибки
# - CPU/Memory usage
```

---

## 🎓 Обучение AI агентов

### Как работает Reasoning Engine (Logic Agent v2)

Logic Understanding Agent использует **Vertex AI Reasoning Engine** - это не просто API к Gemini, а **обучаемый AI агент** с памятью и планированием.

### Что происходит при каждом запросе:

1. **Contextualization** - Агент анализирует историю взаимодействий
2. **Planning** - Создаёт план решения задачи (может включать несколько шагов)
3. **Tool Selection** - Выбирает нужные инструменты:
   - Google Search (для актуальной информации)
   - Code Execution (для вычислений)
   - Custom Functions (наши функции)
4. **Execution** - Выполняет план шаг за шагом
5. **Learning** - Сохраняет результаты в память для будущих запросов

### Как агент обучается:

#### 1. Автоматическое обучение (происходит постоянно)

Каждый запрос сохраняется в памяти агента:

```bash
# Первый запрос
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Какова средняя прибыль за полугодие?",
    "report_data": {...}
  }' \
  "$LOGIC_AGENT_URL/analyze" | jq
```

**Агент запоминает:**
- Какие данные были в отчёте
- Какой вопрос задали
- Какой ответ дал
- Какие инструменты использовал

#### 2. Улучшение через feedback

```bash
# Отправить feedback на ответ
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "abc123",
    "rating": 5,
    "comment": "Отличный анализ, но хотелось бы видеть прогноз на следующий месяц"
  }' \
  "$LOGIC_AGENT_URL/feedback"
```

**Агент учится:**
- Что ответ был хорош (rating=5)
- Что нужно добавлять прогнозы
- Применяет это к следующим запросам

#### 3. Fine-tuning (для production)

Для серьёзного обучения можно сделать fine-tuning:

```bash
# 1. Собрать примеры (минимум 100)
# Формат: {"input": "вопрос", "output": "ответ", "context": {...}}

# 2. Создать датасет
gcloud ai datasets create \
  --display-name="financial-reports-training" \
  --project=financial-reports-ai-2024

# 3. Загрузить данные
gcloud ai datasets import \
  --dataset=DATASET_ID \
  --data-item-import-file=gs://your-bucket/training-data.jsonl

# 4. Запустить fine-tuning
gcloud ai models upload \
  --region=us-central1 \
  --display-name=financial-reports-gemini-ft \
  --base-model-id=gemini-2.0-flash-exp
```

### Пример обучения через использование:

```bash
# Запрос 1 (агент не знает специфики)
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Какая EBITDA?",
    "report_data": {"доход": 1000, "расходы": 700}
  }' \
  "$LOGIC_AGENT_URL/analyze"

# Ответ: "Я не нашёл EBITDA в данных, но прибыль составляет 300"

# Запрос 2 (с уточнением)
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "EBITDA = доход - расходы (приблизительно)",
    "report_data": {"доход": 1000, "расходы": 700}
  }' \
  "$LOGIC_AGENT_URL/analyze"

# Ответ: "EBITDA ≈ 300"

# Запрос 3 (агент запомнил!)
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Какая EBITDA?",
    "report_data": {"доход": 1200, "расходы": 800}
  }' \
  "$LOGIC_AGENT_URL/analyze"

# Ответ: "EBITDA составляет примерно 400"
```

### Проверить что агент обучается:

```bash
# Посмотреть информацию об агенте
curl -H "Authorization: Bearer $TOKEN" \
  "$LOGIC_AGENT_URL/agent/info" | jq

# Увидишь:
{
  "agent_type": "reasoning_engine",
  "model": "gemini-2.0-flash-exp",
  "capabilities": {
    "google_search": true,
    "code_execution": true,
    "multi_step_reasoning": true,
    "memory": true
  },
  "training_examples": 42,  # Количество примеров в памяти
  "last_training": "2025-10-17T10:30:00Z"
}
```

---

## 💡 Полезные команды

### Быстрая проверка системы

```bash
# Создать функцию для быстрого тестирования
check_system() {
  TOKEN=$(gcloud auth print-identity-token)
  echo "Checking all services..."
  
  for service in frontend orchestrator report-reader logic-understanding visualization; do
    URL="https://${service}-agent-38390150695.us-central1.run.app"
    if [[ $service == "frontend" ]]; then
      URL="https://${service}-service-38390150695.us-central1.run.app"
    fi
    
    STATUS=$(curl -s -H "Authorization: Bearer $TOKEN" "$URL/health" | jq -r .status)
    if [[ $STATUS == "healthy" ]]; then
      echo "✅ $service"
    else
      echo "❌ $service"
    fi
  done
}

# Запустить
check_system
```

### Массовый анализ файлов

```bash
# Обработать несколько файлов
for file in /path/to/reports/*.csv; do
  echo "Processing $file..."
  
  # Загрузить
  FILE_ID=$(curl -s -X POST \
    -H "Authorization: Bearer $TOKEN" \
    -F "file=@$file" \
    "$FRONTEND_URL/upload" | jq -r .file_id)
  
  # Создать задачу
  curl -X POST \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "workflow_type": "analyze_report",
      "input_data": {
        "file_path": "'$FILE_ID'",
        "query": "Сделай полный анализ"
      }
    }' \
    "$ORCHESTRATOR_URL/tasks"
  
  sleep 2
done
```

---

## 🎉 Готово!

Теперь ты можешь:
- ✅ Загружать и анализировать отчёты
- ✅ Использовать голосовой интерфейс
- ✅ Создавать визуализации
- ✅ Обучать AI агентов
- ✅ Мониторить систему

**Система полностью готова к работе!** 🚀

Если что-то не работает - проверь логи или напиши мне! 😊

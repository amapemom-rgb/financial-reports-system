# 🎯 Google AI Tools Integration Guide

## 📌 Обзор

Все агенты системы теперь полностью интегрированы с экосистемой Google Cloud и Google AI.

## 🤖 Logic Understanding Agent

### Интегрированные инструменты:

1. **Gemini 2.0 Flash** - основная AI модель
2. **Google Search** - поиск актуальной информации
3. **Code Execution** - выполнение Python кода (встроено в Gemini)
4. **Function Calling** - вызов кастомных функций

### Доступные функции:

```python
# 1. Расчёт финансовых метрик
calculate_financial_metrics(
    metric_type="roi",  # roi, profit_margin, growth_rate, debt_ratio
    values={
        "revenue": 1000000,
        "costs": 700000,
        "investment": 500000
    }
)

# 2. Анализ трендов
analyze_trend(
    data_points=[100, 120, 115, 140, 160],
    period="monthly"
)

# 3. Получение данных отчёта
get_report_data(
    report_id="report-123",
    section="revenue"  # revenue, expenses, balance_sheet
)
```

### Пример использования:

```bash
curl -X POST http://localhost:8080/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Проанализируй динамику выручки и найди в интернете средние показатели по отрасли",
    "report_id": "report-123"
  }'
```

**Агент автономно:**
1. Спланирует действия
2. Вызовет `get_report_data()` для получения данных
3. Использует Google Search для поиска отраслевых показателей
4. Рассчитает метрики через `calculate_financial_metrics()`
5. Проанализирует тренды через `analyze_trend()`
6. Даст рекомендации

---

## 📊 Report Reader Agent

### Возможности:

1. **Excel файлы** - чтение .xlsx, .xls через openpyxl
2. **Google Sheets** - прямая интеграция через Google Sheets API
3. **Data Cleaning** - автоматическая очистка данных
4. **Validation** - проверка корректности данных

### API Endpoints:

```bash
# 1. Загрузить Excel файл
curl -X POST http://localhost:8081/upload/excel \
  -F "file=@report.xlsx"

# 2. Прочитать Google Sheets
curl -X POST http://localhost:8081/read/sheets \
  -H "Content-Type: application/json" \
  -d '{
    "spreadsheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    "range": "A1:Z1000",
    "sheet_name": "Q3 Report"
  }'

# 3. Получить информацию о таблице
curl http://localhost:8081/sheets/{spreadsheet_id}/info
```

### Google Sheets Setup:

1. Создай Service Account в GCP Console
2. Скачай JSON credentials
3. Поделись таблицей с email service account
4. Укажи путь к credentials:
   ```bash
   export GOOGLE_CREDENTIALS_PATH=/path/to/credentials.json
   ```

---

## 🎤 Frontend Service

### Google Speech API Integration:

1. **Speech-to-Text** - распознавание речи
2. **Text-to-Speech** - синтез речи
3. **Voice Analysis** - голосовой анализ отчётов

### API Endpoints:

```bash
# 1. Голосовой анализ
curl -X POST http://localhost:8080/voice/analyze \
  -F "audio=@question.wav" \
  -F "language=ru-RU" \
  -F "report_id=report-123"

# 2. Речь в текст
curl -X POST http://localhost:8080/speech-to-text \
  -F "audio=@voice.wav" \
  -F "language=ru-RU"

# 3. Текст в речь
curl -X POST http://localhost:8080/text-to-speech \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Выручка выросла на 25% по сравнению с прошлым кварталом",
    "language_code": "ru-RU",
    "voice_name": "ru-RU-Wavenet-A"
  }' \
  --output speech.mp3

# 4. Список доступных голосов
curl http://localhost:8080/voices?language_code=ru-RU
```

### Поддерживаемые языки:

- **Русский**: `ru-RU` (Wavenet-A, Wavenet-B, Wavenet-C, Wavenet-D)
- **Английский**: `en-US` (множество голосов)
- **И другие**: 40+ языков

---

## 🔧 Настройка Окружения

### 1. Google Cloud Project

```bash
# Создать проект
gcloud projects create financial-reports-ai-2024

# Включить API
gcloud services enable \
  aiplatform.googleapis.com \
  speech.googleapis.com \
  texttospeech.googleapis.com \
  sheets.googleapis.com \
  storage.googleapis.com
```

### 2. Переменные окружения

```bash
export PROJECT_ID="financial-reports-ai-2024"
export REGION="us-central1"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
```

### 3. Локальное тестирование

```bash
# Запустить все сервисы
docker-compose up -d

# Проверить агенты
curl http://localhost:8080/health  # Frontend
curl http://localhost:8081/health  # Report Reader
curl http://localhost:8082/health  # Logic Understanding
```

---

## 📈 Преимущества Google AI Tools

### 1. **Google Search в агенте**
- Актуальная информация о рынке
- Автоматический поиск сравнительных данных
- Проверка фактов

### 2. **Code Execution**
- Сложные расчёты на лету
- Статистический анализ
- Обработка больших данных

### 3. **Function Calling**
- Интеграция с вашими системами
- Кастомные бизнес-логики
- Расширяемость

### 4. **Google Sheets API**
- Прямой доступ к таблицам
- Совместная работа
- Версионность данных

### 5. **Speech APIs**
- Hands-free интерфейс
- Доступность
- Естественное взаимодействие

---

## 🚀 Примеры использования

### Сценарий 1: Голосовой анализ

```bash
# Пользователь записывает голосовой вопрос
# "Как изменилась выручка за последний квартал?"

curl -X POST http://localhost:8080/voice/analyze \
  -F "audio=@question.wav" \
  -F "report_id=q3-2024"

# Ответ: текст + аудио файл с результатом
```

### Сценарий 2: Анализ с Google Search

```bash
# Агент автоматически найдёт отраслевые данные
curl -X POST http://localhost:8082/analyze \
  -d '{
    "query": "Сравни нашу прибыльность со средней по отрасли"
  }'

# Агент:
# 1. Получит данные из отчёта
# 2. Найдёт через Google Search средние показатели
# 3. Сравнит и даст рекомендации
```

### Сценарий 3: Google Sheets интеграция

```bash
# Читаем отчёт напрямую из Google Sheets
curl -X POST http://localhost:8081/read/sheets \
  -d '{
    "spreadsheet_id": "YOUR_SHEET_ID",
    "range": "Финансы!A1:Z100"
  }'

# Передаём на анализ агенту
curl -X POST http://localhost:8082/analyze \
  -d '{
    "query": "Проанализируй эти данные",
    "context": {"data": "..."}
  }'
```

---

## 💡 Best Practices

1. **Всегда используй Google Search** для проверки актуальности данных
2. **Function Calling** для сложных расчётов
3. **Google Sheets** как источник истины для данных
4. **Speech API** для улучшения UX
5. **Code Execution** для статистического анализа

---

## 🔗 Полезные ссылки

- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Google Sheets API](https://developers.google.com/sheets/api)
- [Speech-to-Text API](https://cloud.google.com/speech-to-text)
- [Text-to-Speech API](https://cloud.google.com/text-to-speech)
- [Gemini Function Calling](https://cloud.google.com/vertex-ai/docs/generative-ai/multimodal/function-calling)

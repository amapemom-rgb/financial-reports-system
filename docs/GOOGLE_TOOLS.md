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

## 📊 Report Reader Agent

### Возможности:

1. **Excel файлы** - чтение .xlsx, .xls через openpyxl
2. **Google Sheets** - прямая интеграция через Google Sheets API
3. **Data Cleaning** - автоматическая очистка данных
4. **Validation** - проверка корректности данных

## 🎤 Frontend Service

### Google Speech API Integration:

1. **Speech-to-Text** - распознавание речи
2. **Text-to-Speech** - синтез речи
3. **Voice Analysis** - голосовой анализ отчётов

## 🔧 Настройка Окружения

```bash
# Включить API
gcloud services enable \
  aiplatform.googleapis.com \
  speech.googleapis.com \
  texttospeech.googleapis.com \
  sheets.googleapis.com \
  storage.googleapis.com
```

## 🚀 Примеры использования

### Голосовой анализ

```bash
curl -X POST http://localhost:8080/voice/analyze \
  -F "audio=@question.wav" \
  -F "report_id=q3-2024"
```

### Google Sheets интеграция

```bash
curl -X POST http://localhost:8081/read/sheets \
  -d '{
    "spreadsheet_id": "YOUR_SHEET_ID",
    "range": "Финансы!A1:Z100"
  }'
```

## 🔗 Полезные ссылки

- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Google Sheets API](https://developers.google.com/sheets/api)
- [Speech-to-Text API](https://cloud.google.com/speech-to-text)
- [Text-to-Speech API](https://cloud.google.com/text-to-speech)

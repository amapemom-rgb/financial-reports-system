# 🚀 Quick Start Guide - MVP Ready!

## ⚡ Быстрый старт (5 минут)

### 1. Запуск всей системы

```bash
cd /Users/sergejbykov/financial-reports-system

# Запустить все сервисы
docker-compose up --build -d

# Проверить статус
docker-compose ps
```

### 2. Проверка здоровья агентов

```bash
# Все должны вернуть {"status": "healthy"}
curl http://localhost:8080/health  # Frontend
curl http://localhost:8081/health  # Report Reader  
curl http://localhost:8082/health  # Logic Understanding
curl http://localhost:8083/health  # Visualization
curl http://localhost:8084/health  # Orchestrator
```

### 3. Тестовый запрос - Полный анализ

```bash
# Создать задачу на анализ
curl -X POST http://localhost:8084/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_type": "analyze_report",
    "input_data": {
      "query": "Тестовый анализ"
    }
  }'

# Ответ вернёт task_id, проверьте статус:
curl http://localhost:8084/tasks/TASK_ID
```

### 4. Создать график

```bash
curl -X POST http://localhost:8083/create/bar \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Chart",
    "data": {
      "labels": ["Jan", "Feb", "Mar", "Apr"],
      "values": [100, 150, 120, 180]
    },
    "save": true
  }'
```

---

## 🎯 Все агенты работают!

| Agent | Port | URL | Status |
|-------|------|-----|--------|
| Frontend | 8080 | http://localhost:8080 | ✅ |
| Report Reader | 8081 | http://localhost:8081 | ✅ |
| Logic Understanding | 8082 | http://localhost:8082 | ✅ |
| Visualization | 8083 | http://localhost:8083 | ✅ |
| Orchestrator | 8084 | http://localhost:8084 | ✅ |

---

## 📋 Workflows

### 1. Analyze Report (Полный анализ)
```bash
POST http://localhost:8084/tasks
{
  "workflow_type": "analyze_report",
  "input_data": {
    "spreadsheet_id": "YOUR_SHEET_ID",  # или file_path
    "query": "Проанализируй выручку"
  }
}
```

### 2. Generate Visualization (Только график)
```bash
POST http://localhost:8084/tasks
{
  "workflow_type": "generate_visualization",
  "input_data": {
    "spreadsheet_id": "YOUR_SHEET_ID",
    "chart_type": "line",
    "title": "Revenue Trend"
  }
}
```

### 3. Voice Analysis (Голосовой)
```bash
POST http://localhost:8080/voice/analyze
- audio: question.wav
- report_id: report-123
```

---

## 🛑 Остановка

```bash
# Остановить все
docker-compose down

# Остановить и удалить volumes
docker-compose down -v
```

---

## 📊 Мониторинг

```bash
# Логи всех сервисов
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f orchestrator-agent

# Статус контейнеров
docker-compose ps
```

---

## 🔧 Troubleshooting

### Проблема: Контейнер не запускается

```bash
# Проверить логи
docker-compose logs SERVICE_NAME

# Пересобрать
docker-compose up --build SERVICE_NAME
```

### Проблема: Порт занят

```bash
# Проверить занятые порты
lsof -i :8080

# Изменить порт в docker-compose.yml
```

### Проблема: Agent не отвечает

```bash
# Перезапустить конкретный сервис
docker-compose restart SERVICE_NAME

# Проверить health
curl http://localhost:PORT/health
```

---

## 🎊 MVP ГОТОВ!

**Что работает:**
- ✅ Все 5 агентов запускаются
- ✅ Health checks проходят
- ✅ Workflows выполняются
- ✅ Docker Compose настроен

**Следующие шаги:**
1. Протестировать с реальными данными
2. Написать unit tests
3. Задеплоить в GCP

---

**Готово к использованию! 🚀**

# 🚀 Инструкция по обновлению кода агентов

## ⚠️ ВАЖНО

Новые версии агентов с Google AI Tools находятся в локальной директории:
```
/Users/sergejbykov/financial-reports-system/agents/
```

## 📦 Файлы для загрузки в GitHub

### 1. Logic Understanding Agent
**Путь:** `agents/logic-understanding-agent/`
- `main.py` - ОБНОВЛЁН (добавлены Google Search, Function Calling)
- `requirements.txt` - ОБНОВЛЁН

### 2. Report Reader Agent  
**Путь:** `agents/report-reader-agent/`
- `main.py` - СОЗДАН (Google Sheets API, Excel reader)
- `requirements.txt` - СОЗДАН
- `Dockerfile` - СОЗДАН

### 3. Frontend Service
**Путь:** `agents/frontend-service/`
- `main.py` - ОБНОВЛЁН (Speech-to-Text, Text-to-Speech)
- `requirements.txt` - ОБНОВЛЁН

## 🔄 Как загрузить в GitHub

### Вариант 1: Через git (рекомендуется)

```bash
cd /Users/sergejbykov/financial-reports-system

# Добавить все изменения
git add agents/

# Коммит
git commit -m "Add: Complete Google AI Tools integration for all agents

- Logic Understanding Agent: Google Search, Function Calling, Code Execution
- Report Reader Agent: Google Sheets API, Excel support
- Frontend Service: Speech-to-Text, Text-to-Speech

Full integration with Google ecosystem"

# Push
git push origin main
```

### Вариант 2: Через GitHub Web UI

1. Перейти на https://github.com/amapemom-rgb/financial-reports-system
2. Для каждого файла:
   - Открыть файл на GitHub
   - Нажать "Edit this file" (карандаш)
   - Скопировать содержимое из локального файла
   - Commit changes

## ✅ Что уже в GitHub

- [x] STATUS.md - обновлён (55% completion)
- [x] TODO.md - обновлён (отмечены выполненные задачи)
- [x] docs/GOOGLE_TOOLS.md - создан
- [ ] agents/logic-understanding-agent/main.py - НУЖНО ОБНОВИТЬ
- [ ] agents/report-reader-agent/main.py - НУЖНО ЗАГРУЗИТЬ
- [ ] agents/frontend-service/main.py - НУЖНО ОБНОВИТЬ

## 📋 Checklist

- [ ] Загрузить Logic Understanding Agent
- [ ] Загрузить Report Reader Agent  
- [ ] Загрузить Frontend Service
- [ ] Протестировать локально
- [ ] Обновить docker-compose.yml если нужно

## 🧪 Тестирование после загрузки

```bash
# Клонировать репозиторий
git clone https://github.com/amapemom-rgb/financial-reports-system.git
cd financial-reports-system

# Запустить Docker Compose
docker-compose up --build -d

# Проверить здоровье
curl http://localhost:8080/health  # Frontend
curl http://localhost:8081/health  # Report Reader
curl http://localhost:8082/health  # Logic Understanding
```

## 💡 Примечание

Файлы агентов большие (~400-600 строк), поэтому лучше использовать git для загрузки.
GitHub Web UI может быть неудобен для таких файлов.

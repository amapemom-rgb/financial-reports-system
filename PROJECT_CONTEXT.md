# 🤖 Project Context for Claude AI

## 📋 Краткое Описание Проекта

**Название:** Financial Reports Analysis System  
**Тип:** Мультиагентная система с AI  
**Технологии:** Python, FastAPI, GCP (Cloud Run, Pub/Sub, Vertex AI/Gemini), Terraform, Docker  
**Цель:** Автоматический анализ финансовых отчетов (Excel/Google Sheets) с использованием Gemini AI

## 🏗️ Архитектура (5 микросервисов)

1. **Frontend Service** - REST API, Speech-to-Text/Text-to-Speech интерфейс
2. **Orchestrator Agent** - State Machine, координация задач
3. **Report Reader Agent** - Парсинг Excel/Sheets, очистка данных
4. **Logic Understanding Agent** - AI анализ с Gemini Pro
5. **Visualization Agent** - Генерация графиков (Plotly)

**Взаимодействие:** Pub/Sub для асинхронной коммуникации между агентами

## 📂 Структура Репозитория
```
financial-reports-system/
├── PROJECT_CONTEXT.md          ← ТЫ ЗДЕСЬ (читай это первым)
├── CLAUDE_PROMPT.md            ← Промпт для новых чатов
├── STATUS.md                   ← Текущий статус проекта
├── TODO.md                     ← Что нужно сделать
├── README.md                   ← Общее описание
├── QUICKSTART.md               ← Быстрый старт
├── CHEATSHEET.md               ← Шпаргалка команд
│
├── agents/                     ← Микросервисы
│   ├── frontend-service/
│   ├── orchestrator-agent/
│   ├── report-reader-agent/
│   ├── logic-understanding-agent/
│   └── visualization-agent/
│
├── terraform/                  ← IaC для GCP
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── modules/
│
├── scripts/                    ← Утилиты
│   ├── setup_local.sh
│   ├── deploy_gcp.sh
│   └── test_local.sh
│
└── docs/                       ← Документация
    ├── ARCHITECTURE.md
    └── API.md
```

## 🎯 Текущий Статус

**Версия:** 0.3.0-alpha  
**Готовность:** 35%

✅ **Готово:**
- Базовая структура проекта
- Docker Compose для локальной разработки
- Terraform модули (Pub/Sub, Storage)
- Скелет агентов (Frontend, Logic Understanding)
- Документация (README, QUICKSTART, CHEATSHEET)

⏳ **В Процессе:**
- Полная реализация всех агентов
- Все Terraform модули (CloudSQL, IAM, Monitoring, LB)
- CI/CD pipeline
- Unit/Integration тесты

❌ **Не Начато:**
- Web UI
- Production deployment
- Advanced AI features (fine-tuning)

## 📖 Как Claude Должен Работать с Проектом

### При Первом Обращении в Новом Чате:

1. **Прочитай этот файл** (PROJECT_CONTEXT.md)
2. **Прочитай STATUS.md** - узнай текущий статус
3. **Прочитай TODO.md** - посмотри что нужно сделать
4. **НЕ читай сразу весь код** - читай только то, что нужно для задачи

### Стратегия Чтения Файлов:

- **Для задач "Добавить новый агент"** → читай `agents/` и `docker-compose.yml`
- **Для задач "Настроить Terraform"** → читай `terraform/`
- **Для задач "Написать документацию"** → читай `docs/` и `README.md`
- **Для задач "Настроить CI/CD"** → читай `.github/workflows/`
- **Для общих вопросов** → читай только `STATUS.md` и `TODO.md`

### Правила Работы:

1. ✅ **Инкрементальные изменения** - малыми шагами
2. ✅ **Обновляй STATUS.md** после каждого значительного изменения
3. ✅ **Создавай чистый, читаемый код** с комментариями
4. ✅ **Следуй существующим паттернам** в проекте
5. ✅ **Тестируй локально** перед коммитом (если возможно)

## 🔑 Ключевые Технические Решения

### Backend
- **Python 3.11+** - основной язык
- **FastAPI** - для REST API
- **SQLAlchemy** - ORM для PostgreSQL
- **Pandas** - обработка табличных данных

### GCP
- **Cloud Run** - serverless containers (автоскейлинг)
- **Pub/Sub** - асинхронная коммуникация
- **Cloud SQL** - PostgreSQL для метаданных
- **Cloud Storage** - хранение файлов и визуализаций
- **Vertex AI / Gemini Pro** - AI анализ

### IaC
- **Terraform** - управление инфраструктурой
- **Docker & Docker Compose** - локальная разработка

## 💡 Важные Концепции

### Workflow Обработки Отчета:

1. User → Frontend (загрузка файла)
2. Frontend → Pub/Sub (task-queue-topic)
3. Orchestrator → маршрутизация к Report Reader
4. Report Reader → чтение и очистка данных
5. Logic Understanding → AI анализ (Gemini)
6. Visualization → создание графиков
7. Orchestrator → ответ пользователю

### State Machine в Orchestrator:
```python
WORKFLOWS = {
    "analyze_report": [
        "report_reader",
        "logic_understanding", 
        "visualization",
        "completed"
    ]
}
```

## 🔗 Полезные Ссылки

- **Репозиторий:** https://github.com/amapemom-rgb/financial-reports-system
- **Gemini API:** https://makersuite.google.com/app/apikey
- **GCP Console:** https://console.cloud.google.com
- **Terraform Docs:** https://registry.terraform.io/providers/hashicorp/google

## 📝 Примечания для Claude

- Проект создан для реального использования, не учебный
- Пользователь: Сергей (sergejbykov, amapemom-rgb на GitHub)
- Gemini API key требуется для работы системы
- Локальная разработка через Docker Compose
- Production деплой в GCP через Terraform


## 🔄 Работа с Git (Для Claude)

### Когда Создаёшь/Изменяешь Файлы:

После каждого значительного изменения, Claude должен предложить:

\`\`\`bash
git add .
git commit -m "Add/Fix/Update: описание"
git push
\`\`\`

### Формат Коммитов:
- **Add:** новые файлы/функции
- **Fix:** исправления
- **Update:** обновления
- **Docs:** документация

### Обновление STATUS.md:
После значительных изменений обновляй процент готовности и добавляй запись в "Последние изменения".


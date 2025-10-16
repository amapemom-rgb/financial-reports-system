#!/bin/bash
set -e

echo "🚀 Создание ПОЛНОЙ структуры проекта Financial Reports System"
echo "=============================================================="

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[✓]${NC} $1"; }
section() { echo -e "\n${BLUE}[>>]${NC} $1\n"; }

# ============================================
# PROJECT CONTEXT - Главный файл для Claude
# ============================================

section "Создание PROJECT_CONTEXT.md (главный файл для Claude)"

cat > PROJECT_CONTEXT.md << 'CONTEXTEOF'
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

CONTEXTEOF

log "PROJECT_CONTEXT.md создан"

# ============================================
# CLAUDE PROMPT - Промпт для новых чатов
# ============================================

section "Создание CLAUDE_PROMPT.md"

cat > CLAUDE_PROMPT.md << 'PROMPTEOF'
# 🤖 Промпт для Нового Чата с Claude

Скопируйте и вставьте этот текст в новый чат:

---
```
Привет! Продолжаем работу над проектом Financial Reports Analysis System.

📦 Репозиторий: https://github.com/amapemom-rgb/financial-reports-system

🎯 Что нужно сделать:
1. Прочитай PROJECT_CONTEXT.md - это главный файл с контекстом проекта
2. Прочитай STATUS.md - текущий статус
3. Прочитай TODO.md - список задач

⚠️ ВАЖНО: НЕ читай весь репозиторий сразу! Читай только файлы, необходимые для конкретной задачи.

Моя задача сегодня: [ОПИШИ ЧТО НУЖНО СДЕЛАТЬ]

Например:
- "Добавить полный код Orchestrator Agent"
- "Создать Terraform модуль для CloudSQL"
- "Написать unit тесты для Frontend Service"
- "Настроить CI/CD pipeline"
- "Обновить документацию"
- "Исправить баг в Report Reader"

Начнём?
```

---

## 💡 Советы по Использованию

### Для Разных Типов Задач:

**Если нужно добавить код:**
```
Прочитай PROJECT_CONTEXT.md и STATUS.md.
Затем прочитай файл agents/SERVICE_NAME/main.py
Добавь функцию [описание]
```

**Если нужна инфраструктура:**
```
Прочитай PROJECT_CONTEXT.md.
Затем terraform/modules/
Создай модуль для [сервис]
```

**Если нужна документация:**
```
Прочитай PROJECT_CONTEXT.md и README.md.
Создай документ [название]
```

### Оптимизация Контекста:

Claude умный - он сам выберет что читать. Но вы можете помочь:

❌ **Плохо:** "Прочитай весь репозиторий и скажи что не так"  
✅ **Хорошо:** "Прочитай STATUS.md и скажи что делать дальше"

❌ **Плохо:** "Прочитай все агенты"  
✅ **Хорошо:** "Прочитай agents/frontend-service/main.py"

PROMPTEOF

log "CLAUDE_PROMPT.md создан"

# ============================================
# STATUS - Текущий статус проекта
# ============================================

section "Создание STATUS.md"

cat > STATUS.md << 'STATUSEOF'
# 📊 Статус Проекта

**Последнее обновление:** 2025-10-16  
**Версия:** 0.3.0-alpha  
**Общая готовность:** 35%

## 🎯 Milestone Tracking

### Phase 1: MVP (Цель: 50%)
- [x] Создать структуру проекта
- [x] Docker Compose для локальной разработки
- [x] Базовые Terraform модули
- [ ] Полный код всех 5 агентов (60% готово)
- [ ] Работающий E2E flow (0% готово)
- [ ] Базовые тесты (0% готово)

### Phase 2: Production Ready (Цель: 80%)
- [ ] Все Terraform модули
- [ ] CI/CD pipeline
- [ ] Monitoring и logging
- [ ] Security audit
- [ ] Полная документация

### Phase 3: Advanced Features (Цель: 100%)
- [ ] Web UI
- [ ] Fine-tuned Gemini model
- [ ] Advanced visualizations
- [ ] Multi-language support

## 📂 Статус Компонентов

### Инфраструктура (40%)

| Компонент | Статус | Готовность |
|-----------|--------|------------|
| Docker Compose | ✅ Готов | 100% |
| Terraform: Pub/Sub | ✅ Готов | 100% |
| Terraform: Storage | ✅ Готов | 100% |
| Terraform: CloudSQL | ⏳ Скелет | 30% |
| Terraform: Cloud Run | ❌ Нет | 0% |
| Terraform: IAM | ❌ Нет | 0% |
| Terraform: Load Balancer | ❌ Нет | 0% |
| Terraform: Monitoring | ❌ Нет | 0% |

### Микросервисы (30%)

| Сервис | Статус | Готовность |
|--------|--------|------------|
| Frontend Service | ⏳ Скелет | 40% |
| Orchestrator Agent | ❌ Скелет | 20% |
| Report Reader Agent | ❌ Нет | 0% |
| Logic Understanding Agent | ⏳ Есть код | 50% |
| Visualization Agent | ❌ Нет | 0% |

### Скрипты (20%)

| Скрипт | Статус | Описание |
|--------|--------|----------|
| setup_local.sh | ✅ Готов | Настройка локального окружения |
| test_local.sh | ✅ Готов | Тестирование локально |
| deploy_gcp.sh | ❌ Нет | Деплой в GCP |
| init_database.py | ❌ Нет | Инициализация БД |

### Документация (50%)

| Документ | Статус | Готовность |
|----------|--------|------------|
| README.md | ✅ Готов | 100% |
| PROJECT_CONTEXT.md | ✅ Готов | 100% |
| CLAUDE_PROMPT.md | ✅ Готов | 100% |
| QUICKSTART.md | ✅ Готов | 100% |
| CHEATSHEET.md | ✅ Готов | 100% |
| ARCHITECTURE.md | ❌ Нет | 0% |
| API.md | ❌ Нет | 0% |
| DEPLOYMENT_GUIDE.md | ❌ Нет | 0% |

### Тесты (0%)

| Тип | Статус |
|-----|--------|
| Unit Tests | ❌ Нет |
| Integration Tests | ❌ Нет |
| E2E Tests | ❌ Нет |

### CI/CD (0%)

| Компонент | Статус |
|-----------|--------|
| GitHub Actions | ❌ Нет |
| Docker Build | ❌ Нет |
| Terraform Plan/Apply | ❌ Нет |

## 🔄 Последние Изменения

### 2025-10-16
- ✅ Создан репозиторий на GitHub
- ✅ Добавлена базовая структура
- ✅ Docker Compose настроен
- ✅ Созданы Terraform модули (Pub/Sub, Storage)
- ✅ Созданы скрипты setup/test
- ✅ Создана документация (README, QUICKSTART, CHEATSHEET)
- ✅ Создан PROJECT_CONTEXT.md и CLAUDE_PROMPT.md

## 🎯 Следующие Приоритеты

### Неделя 1 (16-23 окт)
1. Завершить код всех 5 агентов
2. Создать все Terraform модули
3. Настроить локальный E2E flow
4. Добавить базовые unit тесты

### Неделя 2 (24-31 окт)
1. Деплой в GCP (dev окружение)
2. CI/CD pipeline (GitHub Actions)
3. Monitoring и logging
4. Документация API

### Неделя 3-4 (нояб)
1. Security audit
2. Performance testing
3. Production deployment
4. User acceptance testing

## 📈 Метрики

- **Коммитов:** ~10
- **Файлов:** ~20
- **Строк кода:** ~2,000
- **Времени потрачено:** ~8 часов
- **Дней разработки:** 1

## 🐛 Известные Проблемы

1. Нет полного кода агентов - только скелеты
2. Terraform модули неполные
3. Нет тестов
4. Нет CI/CD
5. Документация API отсутствует

## 💡 Заметки

- Проект активно разрабатывается
- Используется Claude AI для генерации кода
- Пользователь: Сергей (amapemom-rgb)
- Локальная разработка работает
- GCP деплой ещё не тестировался

STATUSEOF

log "STATUS.md создан"

# ============================================
# TODO - Список задач
# ============================================

section "Создание TODO.md"

cat > TODO.md << 'TODOEOF'
# ✅ TODO List

## 🔥 Критично (Сделать Первым)

### Агенты
- [ ] **Frontend Service** - Дописать полный код
  - [ ] Все API endpoints
  - [ ] Speech-to-Text/Text-to-Speech интеграция
  - [ ] Обработка ошибок
  - [ ] Логирование

- [ ] **Orchestrator Agent** - Полная реализация
  - [ ] State Machine
  - [ ] SQLAlchemy модели
  - [ ] Pub/Sub integration
  - [ ] Маршрутизация задач

- [ ] **Report Reader Agent** - Создать с нуля
  - [ ] Excel reader
  - [ ] Google Sheets reader
  - [ ] Data cleaning
  - [ ] Validation

- [ ] **Logic Understanding Agent** - Доработать
  - [ ] Gemini API интеграция
  - [ ] Промпт templates
  - [ ] Обработка результатов

- [ ] **Visualization Agent** - Создать с нуля
  - [ ] Plotly integration
  - [ ] Генерация графиков
  - [ ] Сохранение в Storage

### Terraform
- [ ] **CloudSQL Module** - Завершить
- [ ] **Cloud Run Module** - Создать
- [ ] **IAM Module** - Создать
- [ ] **Load Balancer Module** - Создать
- [ ] **Monitoring Module** - Создать
- [ ] **Secrets Module** - Создать
- [ ] **Main.tf** - Связать все модули

### Скрипты
- [ ] **deploy_gcp.sh** - Полный скрипт деплоя
- [ ] **init_database.py** - Инициализация БД
- [ ] **test_e2e.sh** - E2E тестирование

## ⚡ Важно (Сделать Потом)

### Документация
- [ ] **ARCHITECTURE.md** - Детальная архитектура
- [ ] **API.md** - OpenAPI/Swagger документация
- [ ] **DEPLOYMENT_GUIDE.md** - Полный гайд по деплою
- [ ] **TROUBLESHOOTING.md** - Решение проблем

### Тесты
- [ ] Unit тесты для каждого агента
- [ ] Integration тесты
- [ ] E2E тесты
- [ ] Load testing

### CI/CD
- [ ] GitHub Actions workflow
- [ ] Автоматическая сборка Docker образов
- [ ] Автоматический деплой в staging
- [ ] Manual approval для production

## 🎨 Желательно (Nice to Have)

### Features
- [ ] Web UI (React/Vue)
- [ ] Mobile app
- [ ] Advanced AI (fine-tuning)
- [ ] Multi-language support
- [ ] Email notifications
- [ ] Slack integration

### Оптимизация
- [ ] Redis caching
- [ ] Batch processing
- [ ] Streaming для больших файлов
- [ ] CDN для статики

### DevOps
- [ ] Staging окружение
- [ ] Production окружение
- [ ] Backup/restore automation
- [ ] Disaster recovery plan

## 📋 Для Каждой Задачи

Когда берёшь задачу:
1. Обнови STATUS.md
2. Создай ветку `git checkout -b feature/task-name`
3. Сделай изменения
4. Протестируй локально
5. Коммит `git commit -m "Add: task description"`
6. Push `git push origin feature/task-name`
7. Обнови TODO.md (отметь галочкой)

TODOEOF

log "TODO.md создан"

# ============================================
# Requirements для всех агентов
# ============================================

section "Создание requirements.txt для агентов"

# Orchestrator
mkdir -p agents/orchestrator-agent
cat > agents/orchestrator-agent/requirements.txt << 'REQEOF'
fastapi==0.109.0
uvicorn[standard]==0.27.0
google-cloud-pubsub==2.19.0
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
pydantic==2.5.3
REQEOF

# Report Reader
mkdir -p agents/report-reader-agent
cat > agents/report-reader-agent/requirements.txt << 'REQEOF'
fastapi==0.109.0
google-cloud-pubsub==2.19.0
google-cloud-storage==2.14.0
pandas==2.1.4
openpyxl==3.1.2
gspread==5.12.3
REQEOF

# Visualization
mkdir -p agents/visualization-agent
cat > agents/visualization-agent/requirements.txt << 'REQEOF'
fastapi==0.109.0
google-cloud-pubsub==2.19.0
google-cloud-storage==2.14.0
pandas==2.1.4
plotly==5.18.0
matplotlib==3.8.2
seaborn==0.13.0
REQEOF

log "Requirements для агентов созданы"

# ============================================
# .gitignore дополнения
# ============================================

section "Обновление .gitignore"

cat >> .gitignore << 'GITEOF'

# Python virtual environments
venv/
env/
ENV/
.venv/

# IDE
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Data files
*.xlsx
*.csv
data/

# Logs
*.log
logs/

GITEOF

log ".gitignore обновлён"

# ============================================
# Финализация
# ============================================

echo ""
echo "=============================================================="
echo "✅ ВСЕ ФАЙЛЫ СОЗДАНЫ!"
echo "=============================================================="
echo ""
echo "📦 Создано:"
echo "   ✓ PROJECT_CONTEXT.md - главный файл для Claude"
echo "   ✓ CLAUDE_PROMPT.md - промпт для новых чатов"  
echo "   ✓ STATUS.md - текущий статус проекта"
echo "   ✓ TODO.md - список задач"
echo "   ✓ Requirements для всех агентов"
echo "   ✓ Обновлён .gitignore"
echo ""
echo "🎯 Следующие шаги:"
echo ""
echo "   1. git add ."
echo "   2. git commit -m 'Add: complete project structure with Claude context'"
echo "   3. git push"
echo ""
echo "🤖 Для работы в новом чате с Claude:"
echo "   1. Скопируй промпт из CLAUDE_PROMPT.md"
echo "   2. Вставь в новый чат"
echo "   3. Claude автоматически прочитает PROJECT_CONTEXT.md"
echo ""


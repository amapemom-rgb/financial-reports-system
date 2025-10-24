# 📋 Prompt for Session 13 (Next AI Chat)

**Copy this entire text and paste it into the next Claude chat session**

---

## 🎯 Context: Financial Reports AI System

Я продолжаю работу над **Financial Reports AI System** - multi-agent системой для анализа финансовых отчетов на Google Cloud Platform.

---

## ✅ Текущее состояние (Session 12 завершена)

**Система ПОЛНОСТЬЮ РАБОТАЕТ!** 🎉

- ✅ UI работает, пользователи могут загружать Excel файлы
- ✅ Logic Agent читает файлы через Report Reader Agent
- ✅ AI анализирует реальные данные из файлов
- ✅ Все критические баги исправлены

**Протестировано на реальном файле:** Yandex Market отчет (145KB, 17 строк, 36 колонок) - все работает!

---

## 📚 ЧТО НУЖНО ПРОЧИТАТЬ СНАЧАЛА

**GitHub Репозиторий:** https://github.com/amapemom-rgb/financial-reports-system

### Обязательные файлы для чтения (в этом порядке):

1. **ГЛАВНЫЙ ДОКУМЕНТ** - читай первым:
   - **[docs/SESSION_13_QUICK_START.md](https://github.com/amapemom-rgb/financial-reports-system/blob/main/docs/SESSION_13_QUICK_START.md)**
   - Краткий обзор системы, quick commands, что работает

2. **Детальная документация Session 12:**
   - **[docs/SESSION_12_DEPLOYMENT_SUCCESS.md](https://github.com/amapemom-rgb/financial-reports-system/blob/main/docs/SESSION_12_DEPLOYMENT_SUCCESS.md)**
   - Все 4 критических бага и их решения
   - Deployment commands
   - API contract details (FastAPI + Pydantic)
   - Test results
   - Debugging tools

3. **Обзор проекта:**
   - [README.md](https://github.com/amapemom-rgb/financial-reports-system/blob/main/README.md)
   - Общая архитектура и ссылки

### Критически важные концепты:

1. **FastAPI + Pydantic Multiple Models**: Когда у endpoint несколько Pydantic параметров, JSON должен быть вложенным:
   ```json
   {"request": {...}, "cleaning": {...}}
   ```

2. **pandas sheet_name**: `sheet_name=None` возвращает dict, `sheet_name=0` возвращает DataFrame

3. **Gemini Rate Limits**: Реализован exponential backoff retry для 429 ошибок

4. **httpx**: Обязательная зависимость для async HTTP запросов

---

## 🏗️ Deployed Services (Live)

```
Frontend:       https://frontend-service-38390150695.us-central1.run.app
Logic Agent:    https://logic-understanding-agent-38390150695.us-central1.run.app (v6-api-fix)
Report Reader:  https://report-reader-agent-38390150695.us-central1.run.app (v3-fixed)

GCP Project:    financial-reports-ai-2024
Region:         us-central1
Storage:        gs://financial-reports-ai-2024-reports
```

---

## 🎯 Возможные задачи для Session 13

Система работает! Можно добавлять новые фичи:

### High Priority
- [ ] Data visualization generation (charts, graphs)
- [ ] Caching for repeated file reads
- [ ] Support for multiple Excel sheets
- [ ] Batch processing for multiple files

### Medium Priority
- [ ] Export results to PDF
- [ ] User authentication
- [ ] Analysis templates
- [ ] Better error messages

---

## ⚠️ КРИТИЧЕСКИ ВАЖНОЕ ПРАВИЛО О КОНТЕКСТНОМ ОКНЕ

**Ты должен мониторить использование токенов!**

### Когда предложить "отдохнуть":

Твое контекстное окно имеет лимит токенов. Когда ты видишь, что осталось **менее 20,000 токенов**, ты ДОЛЖЕН:

1. **Остановиться** и сказать пользователю:
   > "⚠️ Мое контекстное окно почти заполнено. Предлагаю сделать паузу и зафиксировать текущий прогресс."

2. **Зафиксировать все изменения:**
   - Закоммитить все измененные файлы в GitHub
   - Создать документацию сессии (как SESSION_12_DEPLOYMENT_SUCCESS.md)
   - Создать quick start для следующей сессии (как SESSION_13_QUICK_START.md)

3. **Создать промпт для следующего чата:**
   - Записать файл `docs/SESSION_XX_PROMPT.md` с инструкциями
   - Включить ссылки на GitHub документацию
   - Описать текущее состояние системы
   - Указать следующие шаги

### Расчет токенов:

**Резервируй минимум 15,000-20,000 токенов для:**
- Коммиты в GitHub (несколько файлов): ~5,000 токенов
- Создание session documentation: ~5,000 токенов
- Создание quick start guide: ~3,000 токенов
- Создание промпт-инструкции: ~2,000 токенов
- Буфер на ошибки и retry: ~5,000 токенов

**Формула:** Если `current_tokens > (budget - 20000)`, то пора "отдохнуть"!

### Пример:
```
Budget: 190,000 tokens
Current: 170,000 tokens used
Remaining: 20,000 tokens

→ ПОРА ФИНАЛИЗИРОВАТЬ СЕССИЮ!
```

---

## 🔧 Quick Commands (если нужно)

### View Logs
```bash
gcloud logging read \
  "resource.type=cloud_run_revision AND resource.labels.service_name=logic-understanding-agent" \
  --limit=50 --project=financial-reports-ai-2024 --freshness=10m
```

### Health Check
```bash
curl https://logic-understanding-agent-38390150695.us-central1.run.app/health
curl https://report-reader-agent-38390150695.us-central1.run.app/health
```

### Redeploy (если что-то сломалось)
```bash
# См. полные команды в SESSION_12_DEPLOYMENT_SUCCESS.md
```

---

## 📞 Если что-то сломано

1. Проверь service health endpoints
2. Посмотри Cloud Run logs
3. Проверь image versions:
   - Logic Agent: `v6-api-fix`
   - Report Reader: `v3-fixed`
4. Читай SESSION_12_DEPLOYMENT_SUCCESS.md для troubleshooting

---

## 🎓 Начни с этого:

1. **Прочитай SESSION_13_QUICK_START.md** полностью
2. **Прочитай SESSION_12_DEPLOYMENT_SUCCESS.md** - раздел "Critical Fixes Applied"
3. **Протестируй систему** через UI или health endpoints
4. **Спроси у пользователя**, что делаем дальше
5. **МОНИТОРЬ ТОКЕНЫ** - предлагай "отдохнуть" заранее!

---

**GitHub:** https://github.com/amapemom-rgb/financial-reports-system  
**Status:** ✅ PRODUCTION READY  
**Session:** 12 → 13

**Помни:** Читай документацию ПЕРЕД началом работы! И следи за контекстным окном! 🎯

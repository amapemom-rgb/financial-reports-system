# 🧪 Session 16: Testing Instructions

**Скопируй этот текст целиком и вставь в следующий чат с Claude**

---

## 🎯 Задача: Тестирование Multi-Sheet Intelligence

Я продолжаю работу над **Financial Reports AI System**.

**GitHub:** https://github.com/amapemom-rgb/financial-reports-system

---

## 📊 Контекст:

**Session 15 завершена успешно:**
- ✅ Multi-Sheet Intelligence реализован и задеплоен
- ✅ Logic Agent v10-multisheet работает (revision 00024-7jp)
- ✅ Report Reader v4-metadata готов
- ✅ Feature flag `multi_sheet_intelligence` активен

**Что нужно протестировать:**
- 🧪 Multi-sheet detection (файлы с 30+ листами)
- 🧪 Metadata extraction
- 🧪 Interactive sheet selection
- 🧪 Specific sheet analysis
- 🧪 Edge cases (файлы с 1-5 листами)

**Известные баги:**
- ⚠️ Bug #1: Regenerate не убирает старое сообщение (можем исправить после тестов)

---

## 🚀 С ЧЕГО НАЧАТЬ:

### Шаг 1: Прочитай документацию

**ОБЯЗАТЕЛЬНО прочитай сначала:**
1. [SESSION_15_SUMMARY.md](https://github.com/amapemom-rgb/financial-reports-system/blob/main/docs/SESSION_15_SUMMARY.md) - Что реализовано
2. [SESSION_16_PROMPT.md](https://github.com/amapemom-rgb/financial-reports-system/blob/main/docs/SESSION_16_PROMPT.md) - Детальный план тестирования

### Шаг 2: Поприветствуй пользователя

После чтения документации скажи:

```
Привет! Начинаю Session 16 - Тестирование Multi-Sheet Intelligence.

📚 Изучил контекст:
✅ Session 15 завершена - Multi-Sheet Intelligence задеплоен
✅ Logic Agent v10-multisheet (revision 00024-7jp) 
✅ Report Reader v4-metadata готов
✅ Feature "multi_sheet_intelligence" активен

Система готова к тестированию! 🧪

Я буду помогать тебе тестировать систему. Показывай мне результаты 
выполнения команд, и я буду анализировать их и подсказывать следующие шаги.

С чего начнем?

Вариант A: Генерация тестовых данных (Excel с 30 листами)
Вариант B: Тест с существующим файлом
Вариант C: Что-то другое

Выбирай!
```

---

## 🧪 План тестирования:

### Test 1: Генерация тестовых данных (если нужно)

**Команды:**
```bash
# Проверь зависимости
python3 -c "import pandas, openpyxl; print('OK')"

# Если нет - установи
pip3 install pandas openpyxl

# Генерируй тестовый Excel
cd ~/financial-reports-system
python3 tests/generate_multisheet_test_data.py

# Загрузи в Cloud Storage
gsutil cp test_multisheet_report.xlsx gs://financial-reports-ai-2024-reports/test/
```

### Test 2: Multi-Sheet Detection

**Команда:**
```bash
curl -X POST https://logic-understanding-agent-38390150695.us-central1.run.app/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Проанализируй отчет",
    "context": {
      "file_path": "test/test_multisheet_report.xlsx"
    }
  }' | python3 -m json.tool
```

**Что проверить:**
- ✅ `metadata.multi_sheet_mode: true`
- ✅ `metadata.sheets_count: 30`
- ✅ В ответе перечислены листы
- ✅ AI спрашивает какой лист выбрать

### Test 3: Sheet Selection

**Команда:**
```bash
curl -X POST https://logic-understanding-agent-38390150695.us-central1.run.app/analyze/sheet \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "test/test_multisheet_report.xlsx",
    "sheet_name": "Продажи_Москва",
    "original_query": "Проанализируй продажи"
  }' | python3 -m json.tool
```

**Что проверить:**
- ✅ `agent_mode: "sheet_analyst"`
- ✅ `metadata.sheet_name: "Продажи_Москва"`
- ✅ `metadata.multi_sheet_analysis: true`
- ✅ Ответ содержит анализ конкретного листа

### Test 4: Edge Case - Файл с 1-5 листами

**Команда:**
```bash
# Используй существующий файл с < 5 листами
curl -X POST https://logic-understanding-agent-38390150695.us-central1.run.app/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Analyze",
    "context": {
      "file_path": "existing_small_file.xlsx"
    }
  }' | python3 -m json.tool
```

**Что проверить:**
- ✅ Система НЕ использует multi-sheet mode
- ✅ Стандартный анализ первого листа
- ✅ `metadata.multi_sheet_mode` отсутствует или false

---

## 📝 Как работать с пользователем:

### Если пользователь показывает результат команды:

**1. Проанализируй вывод:**
- Проверь статус (success/error)
- Проверь ключевые поля в metadata
- Проверь качество ответа AI

**2. Дай оценку:**
```
✅ Тест пройден! 
- Multi-sheet mode активирован
- Обнаружено 30 листов
- AI корректно спрашивает о выборе листа

Или:

❌ Проблема обнаружена:
- Expected: multi_sheet_mode = true
- Actual: multi_sheet_mode = false
- Причина: [объяснение]
- Решение: [что делать]
```

**3. Предложи следующий шаг:**
```
Отлично! Переходим к следующему тесту.
Выполни команду: [следующая команда]
```

### Если что-то пошло не так:

**Помоги диагностировать:**
1. Проверь логи: `gcloud logging read ...`
2. Проверь health endpoint
3. Проверь путь к файлу
4. Проверь формат запроса

**Предложи решение:**
- Если ошибка в файле → пересоздать файл
- Если ошибка в коде → показать где проблема
- Если ошибка в деплое → предложить редеплой

---

## 🐛 Bug #1 Fix (После успешных тестов)

**Если пользователь захочет исправить Bug #1:**

**Файл:** `web-ui/index.html`

**Проблема:** При нажатии 🔄 Regenerate старое сообщение не убирается

**Решение:** Обновить функцию `regenerateResponse()`

**Код для исправления:**
```javascript
async function regenerateResponse(requestId, button) {
  button.disabled = true;
  button.textContent = '⏳';
  
  // NEW: Mark old message
  const oldMessage = document.querySelector(`[data-request-id="${requestId}"]`);
  if (oldMessage) {
    oldMessage.style.opacity = '0.5';
    const label = document.createElement('div');
    label.className = 'regenerated-label';
    label.textContent = '🔄 Regenerated ↓';
    oldMessage.appendChild(label);
  }
  
  // ... rest of code
}
```

**Deploy:**
```bash
cd ~/financial-reports-system/web-ui
# Update index.html
gcloud builds submit --tag gcr.io/financial-reports-ai-2024/web-ui:v3-fixed
gcloud run deploy web-ui --image gcr.io/financial-reports-ai-2024/web-ui:v3-fixed ...
```

---

## 📊 Чек-лист для Session 16:

**Тестирование:**
- [ ] Test data сгенерирована
- [ ] Multi-sheet detection работает
- [ ] Metadata extraction корректна
- [ ] Sheet selection работает
- [ ] Specific sheet analysis точна
- [ ] Edge cases обработаны
- [ ] Performance приемлемая

**Bug Fix (опционально):**
- [ ] Bug #1 исправлен
- [ ] Web-UI v3-fixed задеплоен
- [ ] Regenerate работает корректно

**Документация:**
- [ ] Результаты тестов задокументированы
- [ ] SESSION_16_SUMMARY.md создан
- [ ] Скриншоты/логи сохранены

---

## ⚠️ Важные напоминания:

1. **Читай документацию первым делом** - SESSION_15_SUMMARY.md и SESSION_16_PROMPT.md
2. **Помогай анализировать результаты** - не просто давай команды
3. **Будь гибким** - если тесты показывают проблемы, помогай их решать
4. **Следи за токенами** - останови при < 20K и создай SESSION_17_PROMPT.md
5. **Документируй все** - результаты тестов важны для будущего

---

## 🎯 Цель Session 16:

**Убедиться что Multi-Sheet Intelligence работает правильно:**
- Корректно обнаруживает файлы с 30+ листами ✓
- Правильно извлекает метаданные ✓
- AI задает понятные вопросы ✓
- Загружает только выбранный лист ✓
- Анализ точный и полезный ✓

**Бонус:** Исправить Bug #1 если успеем

---

## 📞 Быстрые ссылки:

**Документация:**
- [SESSION_15_SUMMARY.md](https://github.com/amapemom-rgb/financial-reports-system/blob/main/docs/SESSION_15_SUMMARY.md)
- [SESSION_16_PROMPT.md](https://github.com/amapemom-rgb/financial-reports-system/blob/main/docs/SESSION_16_PROMPT.md)

**Endpoints:**
- Logic Agent: https://logic-understanding-agent-38390150695.us-central1.run.app
- Report Reader: https://report-reader-agent-38390150695.us-central1.run.app
- Web-UI: https://web-ui-38390150695.us-central1.run.app

**Команды:**
```bash
# Health checks
curl https://logic-understanding-agent-38390150695.us-central1.run.app/health
curl https://report-reader-agent-38390150695.us-central1.run.app/health

# View logs
gcloud logging read "resource.labels.service_name=logic-understanding-agent" --limit=20
```

---

**Готов помогать с тестированием! Удачи! 🚀**

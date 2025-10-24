# 📋 Session 13: Action Plan Summary

**Создано:** October 24, 2025  
**Полный план:** [SESSION_13_IMPROVEMENT_PLAN.md](SESSION_13_IMPROVEMENT_PLAN.md)

---

## 🎯 Три улучшения от супервайзера

### 1️⃣ **Динамическая Конфигурация Промпта** ⚡ (Quick Win)
**Что:** Вынести системный промпт в Secret Manager  
**Зачем:** Менять поведение AI без передеплоя  
**Время:** 1-2 часа  
**Риск:** Низкий  

**Шаги:**
- Создать секрет `GEMINI_SYSTEM_PROMPT` в GCP
- Добавить `google-cloud-secret-manager` в dependencies
- Изменить код для чтения промпта из Secret Manager
- Настроить Cloud Run для доступа к секрету
- Протестировать изменение промпта "на лету"

---

### 2️⃣ **UI/UX Фидбэк** 👍👎 (User Experience)
**Что:** Кнопки "Переделать", "Лайк", "Дизлайк"  
**Зачем:** Собирать обратную связь + улучшить UX  
**Время:** 2-3 часа  
**Риск:** Средний  

**Шаги:**
- **Frontend:** Добавить кнопки под каждым ответом
- **Frontend API:** Endpoints `/api/regenerate` и `/api/feedback`
- **Logic Agent:** Endpoint `/feedback` для сохранения в Firestore
- Включить Firestore в GCP
- Протестировать все три кнопки

---

### 3️⃣ **Мета-Структура для 30 Листов** 📊 (Advanced)
**Что:** Интеллектуальная работа с Excel-файлами (30+ листов)  
**Зачем:** Не загружать все сразу, диалог с пользователем  
**Время:** 3-4 часа  
**Риск:** Высокий  

**Шаги:**
- **Report Reader:** Новый endpoint `/analyze/metadata` (только мета-данные)
- **Report Reader:** Новый endpoint `/read/sheet` (конкретный лист)
- **Logic Agent:** Новый файл `prompts.py` с "супер-промптом"
- **Logic Agent:** Двухэтапный flow: metadata → sheet selection → full analysis
- Протестировать с Excel файлом (30+ листов)

---

## 🚀 Рекомендуемый порядок выполнения

### **Phase 1: Quick Win** 🎯
✅ **Improvement #1** - Динамическая конфигурация  
- Низкий риск
- Высокая ценность
- Не трогает UI
- Быстро реализовать

### **Phase 2: User Value** 💎
✅ **Improvement #2** - Фидбэк кнопки  
- Прямая польза для пользователей
- Видимые изменения
- Данные для улучшения

### **Phase 3: Advanced** 🚁
✅ **Improvement #3** - Мета-структура  
- Сложная фича
- Требует тестирования
- Архитектурные изменения

---

## 📊 Изменения в коде

### Новые файлы
```
agents/logic-understanding-agent/prompts.py    # Шаблоны промптов
```

### Измененные файлы
```
agents/logic-understanding-agent/main.py       # Secret Manager + feedback + metadata
agents/logic-understanding-agent/requirements.txt  # Новые зависимости
agents/report-reader-agent/main.py             # Metadata endpoints
frontend/main.py                               # API для кнопок
frontend/templates/index.html                  # UI кнопки
```

### Новые GCP ресурсы
```
Secret Manager: GEMINI_SYSTEM_PROMPT           # Промпты
Firestore: collection "feedback"               # Фидбэк пользователей
```

---

## 🧪 Критерии успеха

### Improvement #1 ✅
- [ ] Промпт меняется без передеплоя
- [ ] Нет простоя сервиса
- [ ] Fallback на дефолтный промпт при ошибке

### Improvement #2 ✅
- [ ] Кнопка "Переделать" работает
- [ ] Кнопка "👍" сохраняет feedback
- [ ] Кнопка "👎" сохраняет feedback
- [ ] Данные в Firestore

### Improvement #3 ✅
- [ ] Обработка 30+ листов без ошибок
- [ ] Показ списка листов пользователю
- [ ] Загрузка только выбранного листа
- [ ] Точные метаданные

---

## ❓ Вопросы для согласования

1. **Какое улучшение делаем первым?**
   - Option A: По порядку (1 → 2 → 3)
   - Option B: Сразу все три параллельно
   - Option C: Только одно (какое?)

2. **Хотим ли мы добавить что-то еще?**
   - Например: экспорт в PDF, дополнительные кнопки, и т.д.

3. **Нужен ли тестовый Excel файл с 30 листами?**
   - Я могу создать для тестирования Improvement #3

4. **Версионирование:**
   - Logic Agent: v6 → v7 (или v7-improvements)?
   - Report Reader: v3 → v4 (или v4-metadata)?

---

## 📈 Текущее состояние

**Token usage:** ~39,500 / 190,000  
**Remaining:** ~150,500 tokens  
**Status:** ✅ Достаточно места для работы

---

## 🎬 Готов к старту!

Жду твоего решения:
- Какую фичу делаем первой?
- Все сразу или по одной?
- Есть ли дополнительные требования?

**Команда готова к работе! 🚀**

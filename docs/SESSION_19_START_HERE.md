# 🚀 START HERE: Session 19 Quick Start Guide

**Скопируй этот текст в новый чат с Claude**

---

Привет! Я продолжаю работу над **Financial Reports AI System**.

**GitHub:** https://github.com/amapemom-rgb/financial-reports-system

**Session 18 завершена:** ✅ Edge Cases, Performance Baseline, Stability Review  
**Session 19 задача:** 🛠️ System Hardening - Retry Logic Implementation

---

## 📚 ШАГ 1: Прочитай эти документы (ОБЯЗАТЕЛЬНО)

**Читай В ТАКОМ ПОРЯДКЕ:**

1. **[docs/SESSION_18_SUMMARY.md](https://github.com/amapemom-rgb/financial-reports-system/blob/main/docs/SESSION_18_SUMMARY.md)**
   - Результаты Edge Cases (Empty, Corrupted, 120 sheets)
   - Система ready for production с оговорками
   - Current failure rate: ~11%

2. **[docs/STABILITY_REVIEW.md](https://github.com/amapemom-rgb/financial-reports-system/blob/main/docs/STABILITY_REVIEW.md)**
   - Детальный анализ стабильности
   - Найденные gaps: Report Reader (7%), Firestore (5%)
   - Готовые code examples для fix

3. **[docs/SESSION_19_PROMPT.md](https://github.com/amapemom-rgb/financial-reports-system/blob/main/docs/SESSION_19_PROMPT.md)**
   - Полный план Session 19
   - 3 приоритета hardening
   - Success criteria

---

## 🎯 ШАГ 2: Твоя Задача в Session 19

### Цель: Снизить failure rate с 11% → 1% через Retry Logic

**Приоритеты (в порядке важности):**

1. **Report Reader Retry Logic** (2 часа) ⭐⭐⭐
   - Problem: 7% failure risk (cold start + network)
   - Solution: `tenacity` library с 3 retries
   - File: `agents/logic-understanding-agent/main.py`

2. **Firestore Retry Logic** (1 час) ⭐⭐
   - Problem: 5% failure risk (transient DB issues)
   - Solution: `google.api_core.retry`
   - File: `agents/logic-understanding-agent/main.py`

3. **Gemini Explicit Timeout** (1 час) ⭐⭐⭐
   - Problem: No timeout → potential Cloud Run timeout
   - Solution: `asyncio.wait_for()` с 30s limit
   - File: `agents/logic-understanding-agent/main.py`

---

## 🛠️ ШАГ 3: Начинаем с Приоритета 1

**Инструкция от Supervisor:**

Первым делом внедрим логику повторных попыток для вызовов внутреннего сервиса Report Reader. Мы будем использовать библиотеку `tenacity` (если она ещё не установлена, её нужно добавить в `requirements.txt`).

**Файл:** `agents/logic-understanding-agent/main.py`  
**Цель:** Применить `@retry` к функции, которая выполняет HTTP-запрос к Report Reader.

### 1. Добавление Импортов

Убедись, что в начале `agents/logic-understanding-agent/main.py` добавлены необходимые импорты для логики повторных попыток и обработки ошибок `httpx`:

```python
import httpx  # Предполагаем, что используется httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
```

### 2. Внедрение Логики Retry

Предположим, что вызов метаданных Report Reader находится в отдельной асинхронной функции. Обнови её, добавив декоратор `@retry`.

**Твоя задача:** Замени существующую функцию, отвечающую за вызов Report Reader (например, `get_file_metadata`), на следующую реализацию:

```python
# Конфигурация для Report Reader (3 попытки, экспоненциальная задержка)
REPORT_READER_RETRY_POLICY = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    # Повторить только при сетевых/HTTP-ошибках, но не при ошибках клиента (4xx)
    retry=retry_if_exception_type(httpx.HTTPError)
)

async def call_report_reader(endpoint: str, file_path: str, provider: str) -> dict:
    # URL Report Reader
    REPORT_READER_URL = os.environ.get("REPORT_READER_URL")
    url = f"{REPORT_READER_URL}/{endpoint}"
    
    payload = {
        "file_path": file_path,
        "provider": provider
    }
    
    # --- Декоратор Retry применяется здесь ---
    @REPORT_READER_RETRY_POLICY
    async def fetch_with_retry():
        async with httpx.AsyncClient(timeout=65.0) as client:  # Таймаут увеличен до 65с для Report Reader
            response = await client.post(url, json=payload)
            # Если ответ 4xx (ошибка клиента), не повторять, а сразу выбросить исключение
            response.raise_for_status() 
            return response.json()

    try:
        return await fetch_with_retry()
    except httpx.HTTPStatusError as e:
        # Обработка ошибок, которые не подлежат повторению (например, 404, 422, 500 после всех попыток)
        logging.error(f"Report Reader non-recoverable error: {e}")
        # Возвращаем понятное сообщение пользователю, как в Edge Case #4
        raise HTTPException(
            status_code=500,
            detail=f"Report Reader failed with status {e.response.status_code}. File might be corrupted or unreadable."
        )

# Теперь, когда вызываешь Report Reader, используй эту функцию:
# metadata = await call_report_reader("analyze/metadata", file_path, provider)
```

**Твоя задача:** Внедри эту структуру в `agents/logic-understanding-agent/main.py`. После этого мы перейдем к Приоритету 2 (Firestore).

---

## ✅ Success Criteria для Приоритета 1

- [ ] `tenacity` добавлен в `requirements.txt`
- [ ] Импорты добавлены в `main.py`
- [ ] Функция `call_report_reader()` с retry создана
- [ ] Все 3 вызова Report Reader используют новую функцию:
  - `get_file_metadata()` → `/analyze/metadata`
  - `read_specific_sheet()` → `/read/sheet`
  - `read_file_from_storage()` → `/read/storage`
- [ ] Код закоммичен в GitHub
- [ ] Docker image собран: `logic-understanding-agent:v11-hardened`
- [ ] Deployed на Cloud Run
- [ ] Manual testing через UI

---

## 📝 После Приоритета 1

Скажи мне:
```
✅ Приоритет 1 завершён!

Что сделано:
- [x] tenacity добавлен
- [x] Retry logic внедрён
- [x] Код задеплоен
- [x] Manual testing пройден

Готов к Приоритету 2: Firestore Retry Logic
```

И мы продолжим с Firestore и Gemini Timeout.

---

## 🔗 Полезные Ссылки

**Документация:**
- [SESSION_18_SUMMARY.md](https://github.com/amapemom-rgb/financial-reports-system/blob/main/docs/SESSION_18_SUMMARY.md)
- [STABILITY_REVIEW.md](https://github.com/amapemom-rgb/financial-reports-system/blob/main/docs/STABILITY_REVIEW.md)
- [SESSION_19_PROMPT.md](https://github.com/amapemom-rgb/financial-reports-system/blob/main/docs/SESSION_19_PROMPT.md)

**Код:**
- [main.py](https://github.com/amapemom-rgb/financial-reports-system/blob/main/agents/logic-understanding-agent/main.py)
- [requirements.txt](https://github.com/amapemom-rgb/financial-reports-system/blob/main/agents/logic-understanding-agent/requirements.txt)

**Services:**
- Logic Agent: https://logic-understanding-agent-38390150695.us-central1.run.app
- Report Reader: https://report-reader-agent-38390150695.us-central1.run.app
- Web UI: https://web-ui-38390150695.us-central1.run.app

---

**Ready to start Session 19!** 🚀  
**Remember:** Read docs → Implement Priority 1 → Test → Deploy → Continue to Priority 2

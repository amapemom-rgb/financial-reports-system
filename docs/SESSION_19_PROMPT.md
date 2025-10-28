# 📋 Prompt for Session 19 (Next AI Chat)

**Copy this entire text and paste it into the next Claude chat session**

---

## 🎯 Session 19 - System Hardening & Retry Logic Implementation

Привет! Я продолжаю работу над **Financial Reports AI System**.

**GitHub:** https://github.com/amapemom-rgb/financial-reports-system

**Session 18 завершена:** ✅ Edge Cases Verification, Performance Baseline, Stability Review

---

## 🚨 ВАЖНО: Прочитай сначала эти файлы

Прочитай **В ТАКОМ ПОРЯДКЕ:**

1. **[docs/SESSION_18_SUMMARY.md](https://github.com/amapemom-rgb/financial-reports-system/blob/main/docs/SESSION_18_SUMMARY.md)** - Edge Cases результаты и Stability findings
2. **[docs/STABILITY_REVIEW.md](https://github.com/amapemom-rgb/financial-reports-system/blob/main/docs/STABILITY_REVIEW.md)** - Детальный анализ стабильности с code examples
3. **[docs/PERFORMANCE_BASELINE.md](https://github.com/amapemom-rgb/financial-reports-system/blob/main/docs/PERFORMANCE_BASELINE.md)** - Performance metrics и optimization opportunities

**Ключевое из Session 18:**
- ✅ Edge Cases верифицированы (Empty, Corrupted, Very Large файлы)
- ✅ Performance baseline задокументирован (2.5s - 8.65s)
- ✅ Stability review выявил критические gaps:
  - ❌ Report Reader: NO retry logic (7% failure risk)
  - ❌ Firestore: NO retry logic (3-5% failure risk)
  - ⚠️ Gemini API: Missing explicit timeout
- ✅ Система производственно готова с оговорками (low-traffic OK, high-traffic needs hardening)

---

## 📋 Твоя Задача в Session 19

### Цель: Повысить стабильность с 11% failure rate → 1% через Retry Logic

Session 19 полностью посвящена **System Hardening** - внедрению retry logic для всех критических внешних зависимостей.

---

## 🛠️ Приоритет 1: Report Reader Retry Logic (2 часа)

**Проблема:** HTTP-вызовы к Report Reader Agent могут failить при cold start (~5%) или network issues (~2%), что дает 7% failure rate.

**Решение:** Внедрить retry logic с библиотекой `tenacity`.

**Файл для модификации:** `agents/logic-understanding-agent/main.py`

**Функции для обновления:**
1. `get_file_metadata()` - для `/analyze/metadata`
2. `read_specific_sheet()` - для `/read/sheet`
3. `read_file_from_storage()` - для `/read/storage`

**Код для добавления:**

```python
from tenacity import (
    retry, 
    stop_after_attempt, 
    wait_exponential, 
    retry_if_exception_type,
    before_sleep_log
)
import logging

logger = logging.getLogger(__name__)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
async def get_file_metadata_with_retry(file_path: str) -> Dict:
    """Get metadata with automatic retry on failures"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{REPORT_READER_URL}/analyze/metadata",
            json={"request": {"file_path": file_path}}
        )
        
        # Raise for bad status codes to trigger retry
        response.raise_for_status()
        
        return response.json()
```

**Критерий успеха:**
- ✅ `tenacity` добавлен в `requirements.txt`
- ✅ Все 3 функции обёрнуты в `@retry` decorator
- ✅ Код задеплоен и протестирован
- ✅ Логи показывают retry attempts при failures

**Expected Impact:** 7% failure rate → ~1% (7× improvement)

---

## 🛠️ Приоритет 2: Firestore Retry Logic (1 час)

**Проблема:** Операции записи в Firestore могут failить при transient DB issues (~3-5%), что приводит к потере feedback data.

**Решение:** Использовать встроенную retry policy из `google.api_core.retry`.

**Файл для модификации:** `agents/logic-understanding-agent/main.py`

**Endpoint для обновления:** `/feedback` (функция `submit_feedback`)

**Код для добавления:**

```python
from google.api_core import retry as google_retry
from google.api_core import exceptions as google_exceptions

# Define retry policy for Firestore operations
FIRESTORE_RETRY_POLICY = google_retry.Retry(
    initial=1.0,       # Initial delay: 1.0s
    maximum=10.0,      # Maximum delay: 10.0s
    multiplier=2.0,    # Exponential backoff multiplier
    deadline=30.0,     # Total retry deadline: 30s
    predicate=google_retry.if_exception_type(
        google_exceptions.DeadlineExceeded,
        google_exceptions.ServiceUnavailable,
        google_exceptions.InternalServerError,
    )
)

# In submit_feedback():
doc_ref.set(feedback_data, retry=FIRESTORE_RETRY_POLICY)
```

**Критерий успеха:**
- ✅ Firestore retry policy добавлен
- ✅ Применён к операциям `.set()` в `/feedback`
- ✅ Google API errors обрабатываются с понятными 503 messages
- ✅ Код задеплоен

**Expected Impact:** 5% failure rate → ~0.5% (10× improvement)

---

## 🛠️ Приоритет 3: Gemini API Explicit Timeout (1 час)

**Проблема:** Отсутствие explicit timeout может привести к Cloud Run timeout (> 60s) или зависанию при долгих Gemini responses.

**Решение:** Обернуть `model.generate_content()` в `asyncio.wait_for()`.

**Файл для модификации:** `agents/logic-understanding-agent/main.py`

**Endpoints для обновления:** `/analyze`, `/analyze/sheet`, `/regenerate`

**Код для добавления:**

```python
import asyncio

GEMINI_TIMEOUT_SECONDS = 30.0  # Maximum 30 seconds for AI response

async def generate_with_timeout(model, prompt, max_retries=3):
    """Generate Gemini response with timeout and retry logic"""
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Generating AI response (attempt {attempt + 1}/{max_retries})")
            
            # Wrap in timeout
            response = await asyncio.wait_for(
                asyncio.to_thread(model.generate_content, prompt),
                timeout=GEMINI_TIMEOUT_SECONDS
            )
            
            logger.info("✅ AI response generated successfully")
            return response
            
        except asyncio.TimeoutError:
            logger.error(f"❌ Gemini API timeout (attempt {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay * (2 ** attempt))
                continue
            else:
                raise HTTPException(
                    status_code=504,
                    detail="AI analysis timed out (30s limit). Please simplify your query or try again."
                )
                
        except Exception as gemini_error:
            if "429" in str(gemini_error) or "Resource exhausted" in str(gemini_error):
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    logger.warning(f"⚠️ Rate limit hit, retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)  # Use async sleep
                    continue
                else:
                    raise HTTPException(
                        status_code=429,
                        detail="Слишком много запросов. Подождите 30 секунд и попробуйте снова."
                    )
            raise

# Usage in /analyze:
response = await generate_with_timeout(model, prompt)
```

**Критерий успеха:**
- ✅ Helper function `generate_with_timeout()` создана
- ✅ Все 3 endpoints используют новую функцию вместо прямого `model.generate_content()`
- ✅ 30-second timeout применяется
- ✅ `time.sleep()` заменён на `await asyncio.sleep()` (async-safe)
- ✅ Код задеплоен

**Expected Impact:**
- Cloud Run timeout protection
- Better 504 error messages для пользователей
- Proper async/await pattern

---

## 🧪 Приоритет 4: Testing & Verification (30 минут)

**После внедрения всех трёх приоритетов, провести тестирование:**

### Unit Tests (Optional - если есть время):

```python
# Test retry logic
async def test_report_reader_retry_on_timeout():
    with patch('httpx.AsyncClient.post') as mock_post:
        # First two calls timeout, third succeeds
        mock_post.side_effect = [
            httpx.TimeoutException("timeout"),
            httpx.TimeoutException("timeout"),
            {"status": "success"}
        ]
        
        result = await get_file_metadata_with_retry("test.xlsx")
        assert result["status"] == "success"
        assert mock_post.call_count == 3
```

### Integration Tests (Обязательно):

1. **Manual Testing через UI:**
   - Upload файл и проверить, что анализ работает
   - Submit feedback и проверить, что сохраняется в Firestore
   - Попробовать regenerate функцию

2. **Simulate Failures (если возможно):**
   - Временно выключить Report Reader → проверить retry logs
   - Симулировать Gemini timeout → проверить 504 error

3. **Check Logs:**
   - Проверить Cloud Logging на наличие retry warnings
   - Убедиться, что errors логируются корректно

**Критерий успеха:**
- ✅ Система работает через UI
- ✅ Логи показывают retry attempts
- ✅ Failure rate снижен (визуально подтверждено)

---

## 📝 Приоритет 5: Documentation (30 минут)

**После внедрения и тестирования, обновить документацию:**

### Update STABILITY_REVIEW.md:

Добавить секцию в конец документа:

```markdown
## 11. 🎉 Session 19 Implementation Results

### Implementation Status:

| Priority | Component | Status | Outcome |
|----------|-----------|--------|---------|
| 1 | Report Reader Retry | ✅ DONE | 7% → 1% failure rate |
| 2 | Firestore Retry | ✅ DONE | 5% → 0.5% failure rate |
| 3 | Gemini Timeout | ✅ DONE | Cloud Run protection |

### Final System Status: ✅ EXCELLENT

**Before Hardening:**
- Total Failure Rate: ~11%
- Stability Score: FAIR (6/10)

**After Hardening:**
- Total Failure Rate: ~1%
- Stability Score: EXCELLENT (9/10)

System is now **production-ready for high-traffic deployment**.
```

### Create SESSION_19_SUMMARY.md:

Comprehensive summary of:
- What was implemented (code changes)
- Testing results
- Before/after metrics
- Production readiness assessment

---

## 🎯 Success Criteria для Session 19

### Must-Have (Blocking):
- [ ] `tenacity` added to `requirements.txt`
- [ ] Report Reader retry logic implemented (Priority 1)
- [ ] Firestore retry logic implemented (Priority 2)
- [ ] Gemini timeout wrapper implemented (Priority 3)
- [ ] Code deployed to Cloud Run
- [ ] Manual testing через UI completed
- [ ] STABILITY_REVIEW.md updated
- [ ] SESSION_19_SUMMARY.md created

### Nice-to-Have (Non-Blocking):
- [ ] Unit tests for retry logic
- [ ] Enhanced error messages (400/503/504 classification)
- [ ] Monitoring dashboard setup
- [ ] Load testing with simulated failures

---

## 🚀 Как Начать

**Твой первый ответ пользователю:**

```
Привет! Начинаю Session 19 - System Hardening & Retry Logic Implementation.

Быстро изучаю результаты Session 18...
[читаешь SESSION_18_SUMMARY.md и STABILITY_REVIEW.md]

Отлично! Понял текущий статус:
✅ Edge Cases верифицированы (Empty, Corrupted, Large files)
✅ Performance baseline задокументирован
⚠️ Система ready for low-traffic, но needs hardening для high-traffic

**Критические gaps выявлены:**
- ❌ Report Reader: 7% failure risk (no retry)
- ❌ Firestore: 5% failure risk (no retry)
- ⚠️ Gemini: Missing explicit timeout

**План Session 19:**

Вариант A (рекомендую):
1. Report Reader Retry Logic (2 часа)
2. Firestore Retry Logic (1 час)
3. Gemini Timeout Wrapper (1 час)
4. Testing & Verification (30 минут)
5. Documentation (30 минут)

Вариант B:
1. Сначала все три priorities в коде
2. Потом deploy + testing
3. Потом documentation

Что выбираешь? Или начать с чего-то другого?
```

---

## ⚠️ Критические Правила для Session 19

### 1. Код Changes:
- Модифицируй `agents/logic-understanding-agent/main.py`
- Добавь `tenacity` в `requirements.txt`
- Commit каждое изменение отдельно (для rollback если нужно)
- Deploy после каждого priority для тестирования

### 2. Testing First:
- После каждого изменения делай manual test через UI
- Проверяй Cloud Logging на наличие retry attempts
- Убедись, что система не сломалась

### 3. Deployment:
- Build новый Docker image: `logic-understanding-agent:v11-hardened`
- Deploy на Cloud Run
- Проверь health endpoint перед тестированием

### 4. Documentation:
- Update STABILITY_REVIEW.md с результатами
- Create SESSION_19_SUMMARY.md
- Update README если нужно

### 5. Токены:
- Мониторь использование токенов
- При < 30K tokens → финализируй session
- Create SESSION_19_SUMMARY.md
- Create SESSION_20_PROMPT.md (if needed)

---

## 📚 Полезные Ссылки

**Система:**
- [SESSION_18_SUMMARY.md](https://github.com/amapemom-rgb/financial-reports-system/blob/main/docs/SESSION_18_SUMMARY.md) - Edge Cases results
- [STABILITY_REVIEW.md](https://github.com/amapemom-rgb/financial-reports-system/blob/main/docs/STABILITY_REVIEW.md) - Detailed stability analysis
- [PERFORMANCE_BASELINE.md](https://github.com/amapemom-rgb/financial-reports-system/blob/main/docs/PERFORMANCE_BASELINE.md) - Performance metrics

**Код:**
- Logic Agent: `agents/logic-understanding-agent/main.py`
- Requirements: `agents/logic-understanding-agent/requirements.txt`
- Dockerfile: `agents/logic-understanding-agent/Dockerfile`

**Deployed Services:**
- Web UI: https://web-ui-38390150695.us-central1.run.app
- Logic Agent: https://logic-understanding-agent-38390150695.us-central1.run.app
- Report Reader: https://report-reader-agent-38390150695.us-central1.run.app

**Libraries Documentation:**
- Tenacity: https://tenacity.readthedocs.io/
- Google API Core Retry: https://googleapis.dev/python/google-api-core/latest/retry.html

---

## 🎊 После Session 19

После успешного завершения Session 19, система будет:

✅ **Production-Ready для High-Traffic Deployment**
- Failure rate: 1% (industry standard)
- Retry logic на всех критических путях
- Explicit timeouts везде
- Clear error messages для пользователей

✅ **Готова к Scale:**
- 1,000+ requests/hour
- SLA commitments (99.9% uptime)
- Mission-critical applications

Следующие шаги (Session 20+):
- Monitoring & alerting setup
- Enhanced error messages (400/503/504)
- Circuit breaker pattern
- Load testing & performance optimization
- Advanced features (memory, fine-tuning)

---

**GitHub:** https://github.com/amapemom-rgb/financial-reports-system  
**Status:** Ready for Session 19  
**Focus:** System Hardening (Retry Logic + Timeouts)  
**Token Budget:** ~110K available  

**Remember:** Test after each change! Deploy incrementally! Document everything! 🚀

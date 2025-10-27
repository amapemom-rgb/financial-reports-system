# 📋 Prompt for Session 15 (Next AI Chat)

**Copy this entire text and paste it into the next Claude chat session**

---

## 🎯 ТВОЯ ЗАДАЧА: Bug Fixes + Improvement #3 (Multi-Sheet Intelligence)

Я продолжаю работу над **Financial Reports AI System**.

**GitHub:** https://github.com/amapemom-rgb/financial-reports-system

**Session 14 завершена:** ✅ Improvement #2 (User Feedback UI/UX) РАБОТАЕТ!

---

## 🚀 ЧТО ДЕЛАТЬ ПЕРВЫМ ДЕЛОМ:

### Шаг 1: Прочитай контекст (3 минуты)

Прочитай эти файлы В ТАКОМ ПОРЯДКЕ:

1. **[docs/SESSION_14_SUMMARY.md](https://github.com/amapemom-rgb/financial-reports-system/blob/main/docs/SESSION_14_SUMMARY.md)** - Что сделано в Session 14
2. **[docs/SESSION_13_IMPROVEMENT_PLAN.md](https://github.com/amapemom-rgb/financial-reports-system/blob/main/docs/SESSION_13_IMPROVEMENT_PLAN.md)** - Раздел "Improvement #3" для Multi-Sheet

### Шаг 2: Определи приоритет работ

После чтения спроси пользователя:

```
Привет! Начинаю Session 15.

Изучил контекст - Session 14 завершена успешно! 🎉
Кнопки feedback (👍👎🔄) работают отлично!

Но есть 2 известные проблемы:

**Bug #1 (MINOR):** При нажатии 🔄 Regenerate старое сообщение не убирается из чата
**Bug #2 (OPTIONAL):** Загрузка файлов не работает (нужна интеграция с orchestrator)

**Что делаем в Session 15?**

**Вариант A (рекомендую):** Сразу начать Improvement #3 (Multi-Sheet Intelligence для Excel с 30+ листами)
**Вариант B:** Сначала исправить Bug #1, потом Improvement #3
**Вариант C:** Исправить оба бага, потом Improvement #3

Что выбираешь?
```

---

## 📋 План работы по вариантам:

### Вариант A: Improvement #3 сразу (рекомендуется)

**Почему:** Баги минорные, не блокируют работу, Improvement #3 - важная функциональность

**Phase 1: Report Reader Enhancement (1 час)**
1. Добавить endpoint `/analyze/metadata` для метаданных Excel
2. Добавить endpoint `/read/sheet` для чтения конкретного листа
3. Build & Deploy: `report-reader-agent:v4-metadata`

**Phase 2: Logic Agent Super Prompt (1 час)**
1. Создать `agents/logic-understanding-agent/prompts.py`
2. Добавить функцию `build_super_prompt(metadata, user_query)`
3. Обновить `/analyze` для работы с метаданными
4. Build & Deploy: `logic-understanding-agent:v10-multisheet`

**Phase 3: Testing (30 минут)**
1. Создать тестовый Excel с 30+ листами
2. Test metadata extraction
3. Test interactive sheet selection
4. Document results

### Вариант B: Bug #1 → Improvement #3

**Phase 1: Fix Regenerate UI (30 минут)**
1. Обновить `web-ui/index.html`
2. Изменить `addChatMessage()` чтобы заменять старое сообщение
3. Deploy: `web-ui:v3-fixed`

**Phase 2-4:** Как в Варианте A

### Вариант C: Bug #1 + Bug #2 → Improvement #3

**Phase 1: Fix Regenerate UI (30 минут)**
**Phase 2: Fix File Upload (1-2 часа)**
1. Опция A: Интегрировать с frontend-service
2. Опция B: Добавить upload в web-ui backend
**Phase 3-5:** Improvement #3 (может не хватить времени)

---

## 🔍 Детали реализации Improvement #3:

### Report Reader: Metadata Endpoint

**File:** `agents/report-reader-agent/main.py`

```python
from pydantic import BaseModel
from typing import Dict, List

class SheetMetadata(BaseModel):
    rows: int
    columns: List[str]
    sample_data: List[Dict]  # First 1-2 rows
    data_types: Dict[str, str]

class FileMetadata(BaseModel):
    sheets_count: int
    sheet_names: List[str]
    file_size_bytes: int
    preliminary_summary: Dict[str, SheetMetadata]

@app.post("/analyze/metadata")
async def get_file_metadata(request: ReadStorageRequest) -> FileMetadata:
    """Generate metadata for all sheets without loading full data"""
    
    # Download from Cloud Storage
    bucket = storage_client.bucket(REPORTS_BUCKET)
    blob = bucket.blob(request.request.file_path)
    file_bytes = blob.download_as_bytes()
    
    # Read sheet names only
    all_sheets = pd.read_excel(
        BytesIO(file_bytes),
        sheet_name=None,
        nrows=2  # Only first 2 rows
    )
    
    metadata = FileMetadata(
        sheets_count=len(all_sheets),
        sheet_names=list(all_sheets.keys()),
        file_size_bytes=len(file_bytes),
        preliminary_summary={}
    )
    
    # Get top 5 largest sheets
    sorted_sheets = sorted(
        all_sheets.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )[:5]
    
    for sheet_name, df in sorted_sheets:
        metadata.preliminary_summary[sheet_name] = SheetMetadata(
            rows=len(df),
            columns=list(df.columns),
            sample_data=df.head(1).to_dict(orient='records'),
            data_types={col: str(dtype) for col, dtype in df.dtypes.items()}
        )
    
    return metadata

@app.post("/read/sheet")
async def read_specific_sheet(
    request: ReadStorageRequest,
    sheet_name: str
) -> dict:
    """Read specific sheet by name"""
    # Same as read_from_cloud_storage but with sheet_name parameter
```

### Logic Agent: Super Prompt

**File:** `agents/logic-understanding-agent/prompts.py` (NEW)

```python
def build_super_prompt(metadata: FileMetadata, user_query: str) -> str:
    """Build intelligent prompt for multi-sheet analysis"""
    
    return f"""
[ИНСТРУКЦИЯ ДЛЯ АНАЛИТИКА GEMINI]

Ты — AI-ассистент "Финансовый Эксперт". Твой тон — дружелюбный и профессиональный.

[РОЛЬ]
Твоя задача — интерактивный анализ. Не пытайся ответить сразу. Сначала собери контекст.

[КОНТЕКСТ ДАННЫХ]
Пользователь загрузил Excel-файл. Вот его **МЕТА-СТРУКТУРА**:

Количество листов: {metadata.sheets_count}
Названия листов: {", ".join(metadata.sheet_names)}
Размер файла: {metadata.file_size_bytes / 1024:.1f} KB

Предварительное резюме топ-5 листов:
{format_preliminary_summary(metadata.preliminary_summary)}

[ВОПРОС ПОЛЬЗОВАТЕЛЯ]
"{user_query}"

[СТРУКТУРА ОТВЕТА (Обязательно)]
1. **РЕЗЮМЕ ОТЧЕТА:** Укажи количество листов ({metadata.sheets_count}) и перечисли их названия.

2. **ГЛАВНЫЙ ВОПРОС:** Задай ОДИН четкий вопрос пользователю, чтобы он выбрал, какой лист анализировать.

[ПРИМЕР ОТВЕТА]
"В отчете {metadata.sheets_count} листов: {', '.join(metadata.sheet_names[:3])}...
Какой из них (например, 'Продажи' или 'Расходы') вы хотите проанализировать первым?"

[СЛЕДУЮЩИЙ ШАГ]
После выбора пользователем конкретного листа, система загрузит полные данные этого листа.
"""
```

### Logic Agent: Updated Analyze

**File:** `agents/logic-understanding-agent/main.py`

```python
from .prompts import build_super_prompt

@app.post("/analyze")
async def analyze_report(request: AnalyzeRequest):
    """Enhanced analysis with metadata-first approach"""
    
    file_path = request.context.get("file_path")
    
    if file_path:
        # Step 1: Get metadata first
        metadata_url = f"{REPORT_READER_URL}/analyze/metadata"
        metadata_response = await http_client.post(
            metadata_url,
            json={"request": {"file_path": file_path}}
        )
        metadata = FileMetadata(**metadata_response.json())
        
        # Check if many sheets
        if metadata.sheets_count > 5:
            # Step 2: Build super prompt for sheet selection
            system_prompt = build_super_prompt(metadata, request.query)
            
            # Step 3: Ask Gemini for interactive question
            response = model.generate_content(system_prompt)
            
            return AnalyzeResponse(
                status="completed",
                insights=response.text,
                request_id=request_id,
                metadata={
                    "sheets_count": metadata.sheets_count,
                    "sheet_names": metadata.sheet_names,
                    "next_action": "select_sheet"
                }
            )
        else:
            # Few sheets - load all data normally
            # ... existing logic ...
```

---

## ✅ Success Criteria:

### For Improvement #3:
- [ ] Report reader returns metadata for 30+ sheet files
- [ ] Logic agent asks which sheet to analyze
- [ ] User can select specific sheet
- [ ] Only selected sheet is loaded (performance optimization)
- [ ] System handles files with different sheet structures

### For Bug Fixes (if doing):
- [ ] Bug #1: Regenerate removes/marks old message
- [ ] Bug #2: File upload works through UI

---

## 🧪 Testing Multi-Sheet Feature:

**Create Test Excel:**
```python
import pandas as pd

# Create Excel with 30 sheets
with pd.ExcelWriter('test_30_sheets.xlsx') as writer:
    for i in range(1, 31):
        df = pd.DataFrame({
            'Product': [f'Product_{j}' for j in range(100)],
            'Sales': [1000 + j for j in range(100)],
            'Date': pd.date_range('2024-01-01', periods=100)
        })
        df.to_excel(writer, sheet_name=f'Sheet_{i}', index=False)
```

**Test Flow:**
1. Upload file
2. System: "Found 30 sheets: Sheet_1, Sheet_2, ... Which to analyze?"
3. User: "Sheet_5"
4. System: Loads only Sheet_5 and analyzes

---

## ⚠️ ВАЖНО: Мониторинг токенов

Когда останется **< 20,000 токенов**:
1. Остановись
2. Закоммить все в GitHub
3. Создать SESSION_15_SUMMARY.md
4. Создать SESSION_16_PROMPT.md

---

## 📚 Полная документация:

**Базовая архитектура:**
- [SESSION_12_DEPLOYMENT_SUCCESS.md](https://github.com/amapemom-rgb/financial-reports-system/blob/main/docs/SESSION_12_DEPLOYMENT_SUCCESS.md) - System baseline
- [SESSION_13_SUMMARY.md](https://github.com/amapemom-rgb/financial-reports-system/blob/main/docs/SESSION_13_SUMMARY.md) - Dynamic Prompts
- [SESSION_14_SUMMARY.md](https://github.com/amapemom-rgb/financial-reports-system/blob/main/docs/SESSION_14_SUMMARY.md) - User Feedback

**Детальный план Improvement #3:**
- [SESSION_13_IMPROVEMENT_PLAN.md - Раздел Improvement #3](https://github.com/amapemom-rgb/financial-reports-system/blob/main/docs/SESSION_13_IMPROVEMENT_PLAN.md)

**Известные проблемы:**
- Bug #1: Regenerate не убирает старое сообщение
- Bug #2: Загрузка файлов не работает

---

## 🚀 НАЧНИ РАБОТУ:

**Твой первый ответ пользователю должен быть:**

```
Привет! Начинаю Session 15 - Bug Fixes + Improvement #3 (Multi-Sheet Intelligence).

Сначала быстро изучу контекст...
[читаешь SESSION_14_SUMMARY.md и SESSION_13_IMPROVEMENT_PLAN.md]

Отлично! Session 14 завершена успешно! 🎉
- ✅ Firestore настроен
- ✅ Feedback endpoints работают
- ✅ Web-UI с кнопками 👍👎🔄 задеплоен
- ✅ CORS включен

Есть 2 известные проблемы:
1. Bug #1: Regenerate не убирает старое сообщение (MINOR)
2. Bug #2: Загрузка файлов не работает (OPTIONAL)

**Что делаем в Session 15?**

Вариант A (рекомендую): Сразу начать Improvement #3 (Multi-Sheet для Excel 30+)
Вариант B: Исправить Bug #1 → Improvement #3
Вариант C: Исправить оба бага → Improvement #3

Что выбираешь?
```

---

**GitHub:** https://github.com/amapemom-rgb/financial-reports-system  
**Status:** Ready for Session 15  
**Task:** Bug Fixes (optional) + Improvement #3 (Multi-Sheet Intelligence)

**Помни:** 
- Читай документацию ПЕРЕД началом
- Спроси пользователя о приоритетах
- Следи за токенами (останови при < 20K)
- Improvement #3 - сложная задача, может потребовать 2 сессии

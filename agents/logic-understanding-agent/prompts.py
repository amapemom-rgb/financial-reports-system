"""Prompt templates for Logic Understanding Agent"""
from typing import Dict, List, Any


def format_preliminary_summary(summary: List[Dict[str, Any]]) -> str:
    """Format metadata summary for prompt"""
    lines = []
    for sheet in summary:
        sheet_name = sheet.get("name", "Unknown")
        rows = sheet.get("rows", 0)
        columns = sheet.get("columns", [])
        
        lines.append(f"- '{sheet_name}': {rows} строк, {len(columns)} колонок")
        
        # Show first 5 columns
        col_preview = ", ".join(columns[:5])
        if len(columns) > 5:
            col_preview += f"... (ещё {len(columns) - 5})"
        lines.append(f"  Колонки: {col_preview}")
    
    return "\n".join(lines)


def build_super_prompt(metadata: Dict[str, Any], user_query: str) -> str:
    """Build intelligent prompt for multi-sheet analysis
    
    This prompt instructs Gemini to:
    1. Show metadata summary
    2. Ask user which sheet to analyze
    3. Wait for user's sheet selection
    """
    
    sheets_count = metadata.get("sheets_count", 0)
    sheet_names = metadata.get("sheet_names", [])
    file_size_kb = metadata.get("file_size_bytes", 0) / 1024
    top_sheets = metadata.get("top_sheets_summary", [])
    
    # Format sheet names for display
    if len(sheet_names) <= 10:
        sheet_list = ", ".join([f"'{name}'" for name in sheet_names])
    else:
        # Show first 8 and last 2
        first_sheets = ", ".join([f"'{name}'" for name in sheet_names[:8]])
        last_sheets = ", ".join([f"'{name}'" for name in sheet_names[-2:]])
        sheet_list = f"{first_sheets}... {last_sheets}"
    
    summary = format_preliminary_summary(top_sheets)
    
    return f"""[ИНСТРУКЦИЯ ДЛЯ АНАЛИТИКА GEMINI]

Ты — AI-ассистент "Финансовый Эксперт". Твой тон — дружелюбный и профессиональный.

[РОЛЬ]
Твоя задача — интерактивный анализ. НЕ пытайся анализировать данные прямо сейчас. Сначала помоги пользователю выбрать правильный лист для анализа.

[КОНТЕКСТ ДАННЫХ]
Пользователь загрузил Excel-файл. Вот его **СТРУКТУРА**:

📊 **Общая информация:**
- Количество листов: {sheets_count}
- Размер файла: {file_size_kb:.1f} KB

📋 **Все листы в файле:**
{sheet_list}

📈 **Топ-{len(top_sheets)} самых больших листов:**
{summary}

[ВОПРОС ПОЛЬЗОВАТЕЛЯ]
"{user_query}"

[ТВОЯ ЗАДАЧА]
Сформируй ответ из ДВУХ частей:

**1. РЕЗЮМЕ ФАЙЛА** (2-3 предложения):
- Укажи количество листов ({sheets_count})
- Кратко опиши что содержится в топ-листах
- Можешь предположить назначение файла по названиям листов

**2. ВОПРОС К ПОЛЬЗОВАТЕЛЮ** (1-2 предложения):
Задай ОДИН четкий вопрос: какой лист пользователь хочет проанализировать?

Примеры хороших вопросов:
- "Какой из этих листов вас интересует больше всего?"
- "Какой лист вы хотите проанализировать первым: 'Продажи', 'Транзакции' или другой?"
- "Скажите название листа, который нужно изучить детально"

[ВАЖНЫЕ ПРАВИЛА]
✅ Будь кратким (максимум 5-6 предложений всего)
✅ НЕ используй markdown форматирование (нет **, ##, списков)
✅ Пиши обычным текстом, разделяй абзацы пустой строкой
✅ НЕ анализируй данные - просто помоги выбрать лист
✅ НЕ повторяй все названия листов - пользователь их видит в структуре выше

[СЛЕДУЮЩИЙ ШАГ]
После того как пользователь назовёт лист, система загрузит ПОЛНЫЕ данные этого листа для детального анализа.
"""


def build_sheet_analysis_prompt(sheet_data: Dict[str, Any], user_query: str, sheet_name: str) -> str:
    """Build prompt for analyzing specific sheet after user selection
    
    This prompt is used after user has selected a specific sheet to analyze.
    """
    
    rows = sheet_data.get("rows", 0)
    columns = sheet_data.get("columns", [])
    sample_data = sheet_data.get("data", [])[:3]  # First 3 rows
    
    # Format sample data
    data_preview = "\n".join([str(row) for row in sample_data])
    
    return f"""Ты опытный финансовый аналитик маркетплейсов.

**Контекст:**
Пользователь загрузил Excel-файл с {rows} строками данных из листа '{sheet_name}'.

**Структура данных:**
Колонки: {', '.join(columns[:10])}
{f'... (ещё {len(columns) - 10} колонок)' if len(columns) > 10 else ''}

**Образец данных (первые 3 строки):**
```
{data_preview}
```

**Вопрос пользователя:**
"{user_query}"

**Твоя задача:**
Проанализируй данные и ответь на вопрос пользователя. Фокусируйся на:
- Ключевых метриках и цифрах
- Трендах и закономерностях
- Конкретных выводах и рекомендациях

**Правила:**
✅ Будь конкретным - ссылайся на реальные данные и цифры
✅ Будь кратким - максимум 4-5 абзацев
✅ Используй обычный текст без markdown
✅ Если нужна дополнительная информация - спроси

Отвечай профессионально и по делу.
"""

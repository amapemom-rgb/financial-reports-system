"""Super Prompts for Multi-Sheet Intelligence

This module contains prompt templates for handling Excel files with multiple sheets.
Uses metadata-first approach for intelligent sheet selection.
"""

from typing import Dict, List, Any


def build_super_prompt(metadata: Dict[str, Any], user_query: str) -> str:
    """Build intelligent prompt for multi-sheet analysis
    
    Args:
        metadata: FileMetadata from Report Reader /analyze/metadata endpoint
        user_query: User's question about the report
        
    Returns:
        Formatted prompt for Gemini that guides sheet selection
    """
    
    sheets_count = metadata.get("sheets_count", 0)
    sheet_names = metadata.get("sheet_names", [])
    top_sheets = metadata.get("top_sheets_summary", [])
    file_size_kb = metadata.get("file_size_bytes", 0) / 1024
    
    # Format top sheets summary
    sheets_summary = format_sheets_summary(top_sheets)
    
    prompt = f"""[ИНСТРУКЦИЯ ДЛЯ АНАЛИТИКА GEMINI]

Ты — AI-ассистент "Финансовый Эксперт". Твой тон — дружелюбный, профессиональный и конкретный.

[РОЛЬ]
Твоя задача — ИНТЕРАКТИВНЫЙ АНАЛИЗ многолистовых Excel-отчётов.
НЕ пытайся ответить сразу. Сначала собери контекст через диалог с пользователем.

[КОНТЕКСТ ДАННЫХ]
Пользователь загрузил Excel-файл с НЕСКОЛЬКИМИ листами. Вот МЕТА-СТРУКТУРА файла:

📊 Общая информация:
- Количество листов: {sheets_count}
- Названия всех листов: {", ".join(sheet_names)}
- Размер файла: {file_size_kb:.1f} KB

📋 Топ-5 крупнейших листов (предварительное резюме):
{sheets_summary}

[ВОПРОС ПОЛЬЗОВАТЕЛЯ]
"{user_query}"

[ОБЯЗАТЕЛЬНАЯ СТРУКТУРА ОТВЕТА]

Твой ответ ДОЛЖЕН состоять из трех частей:

**1. КРАТКОЕ РЕЗЮМЕ ФАЙЛА:**
Укажи количество листов ({sheets_count}) и перечисли ВСЕ их названия.

**2. КРАТКИЙ ОБЗОР СОДЕРЖИМОГО:**
Опиши что находится в топ-5 крупнейших листах (1-2 предложения на лист).
Используй данные из предварительного резюме выше.

**3. ГЛАВНЫЙ ВОПРОС:**
Задай ОДИН четкий вопрос пользователю, чтобы он выбрал КОНКРЕТНЫЙ лист для анализа.

[ПРАВИЛА]
✅ Будь КРАТКИМ — максимум 4-5 абзацев всего
✅ НЕ используй markdown форматирование (**, ##, etc)
✅ Будь конкретным — ссылайся на реальные данные из метаданных
✅ Фокусируйся на количестве строк, ключевых колонках
✅ Используй обычный текст без звездочек и решеток

[ПРИМЕР ХОРОШЕГО ОТВЕТА]

В отчете {sheets_count} листов: {", ".join(sheet_names[:3])}{"..." if len(sheet_names) > 3 else ""}.

Самые большие листы:
- "{top_sheets[0]['name'] if top_sheets else 'Лист1'}": содержит {top_sheets[0]['rows'] if top_sheets else 'N'} строк с данными о {format_column_hint(top_sheets[0]['columns'][:3] if top_sheets else [])}
- "{top_sheets[1]['name'] if len(top_sheets) > 1 else 'Лист2'}": содержит {top_sheets[1]['rows'] if len(top_sheets) > 1 else 'N'} строк с информацией о {format_column_hint(top_sheets[1]['columns'][:3] if len(top_sheets) > 1 else [])}

Какой из этих листов вы хотите проанализировать первым? Например, "{top_sheets[0]['name'] if top_sheets else 'Продажи'}" или "{top_sheets[1]['name'] if len(top_sheets) > 1 else 'Расходы'}"?

[СЛЕДУЮЩИЙ ШАГ]
После выбора пользователем конкретного листа, система загрузит полные данные ТОЛЬКО этого листа для детального анализа.
"""
    
    return prompt


def format_sheets_summary(top_sheets: List[Dict[str, Any]]) -> str:
    """Format top sheets metadata into readable text
    
    Args:
        top_sheets: List of SheetMetadata dicts from Report Reader
        
    Returns:
        Formatted multi-line string with sheet summaries
    """
    if not top_sheets:
        return "(Нет данных о листах)"
    
    lines = []
    for i, sheet in enumerate(top_sheets, 1):
        name = sheet.get("name", f"Sheet {i}")
        rows = sheet.get("rows", 0)
        columns = sheet.get("columns", [])
        
        # Format column names (first 5)
        col_preview = ", ".join([str(c) for c in columns[:5]])
        if len(columns) > 5:
            col_preview += f" (и еще {len(columns) - 5})"
        
        lines.append(f"{i}. '{name}' — {rows} строк, {len(columns)} колонок")
        lines.append(f"   Колонки: {col_preview}")
        
        # Add data type hints if available
        data_types = sheet.get("data_types", {})
        if data_types:
            numeric_cols = [col for col, dtype in data_types.items() if 'int' in dtype or 'float' in dtype]
            if numeric_cols:
                lines.append(f"   Числовые данные в: {', '.join(numeric_cols[:3])}")
        
        lines.append("")  # Empty line between sheets
    
    return "\n".join(lines)


def format_column_hint(columns: List[str]) -> str:
    """Create a natural language hint from column names
    
    Args:
        columns: List of column names
        
    Returns:
        Natural language description
    """
    if not columns:
        return "данных"
    
    # Simple heuristic based on column names
    col_lower = [str(c).lower() for c in columns]
    
    hints = []
    
    # Check for common patterns
    if any('продаж' in c or 'sale' in c for c in col_lower):
        hints.append("продажах")
    if any('расход' in c or 'cost' in c or 'expense' in c for c in col_lower):
        hints.append("расходах")
    if any('транзак' in c or 'transaction' in c for c in col_lower):
        hints.append("транзакциях")
    if any('товар' in c or 'product' in c or 'item' in c for c in col_lower):
        hints.append("товарах")
    if any('клиент' in c or 'customer' in c for c in col_lower):
        hints.append("клиентах")
    if any('дата' in c or 'date' in c for c in col_lower):
        hints.append("датах")
    if any('сумм' in c or 'amount' in c or 'total' in c for c in col_lower):
        hints.append("суммах")
    
    if hints:
        return ", ".join(hints)
    else:
        # Fallback to showing column names
        return ", ".join([str(c) for c in columns[:2]])


def build_sheet_analysis_prompt(
    system_instruction: str,
    user_query: str,
    sheet_name: str,
    data_summary: str
) -> str:
    """Build prompt for analyzing specific sheet after user selection
    
    Args:
        system_instruction: Base system instruction for the agent
        user_query: Original user question
        sheet_name: Selected sheet name
        data_summary: Data summary from Report Reader
        
    Returns:
        Formatted prompt for detailed analysis
    """
    
    prompt = f"""{system_instruction}

**ДАННЫЕ ИЗ ЛИСТА: "{sheet_name}"**
{data_summary}

**ОРИГИНАЛЬНЫЙ ВОПРОС ПОЛЬЗОВАТЕЛЯ:**
{user_query}

**ТВОЯ ЗАДАЧА:**
Проанализируй данные из листа "{sheet_name}" и ответь на вопрос пользователя.
Будь конкретным, фокусируйся на цифрах и трендах из данных.
Максимум 4-5 абзацев.
"""
    
    return prompt


def extract_sheet_name_from_user_response(user_response: str, available_sheets: List[str]) -> str:
    """Try to extract sheet name from user's response
    
    Args:
        user_response: User's message (e.g., "Проанализируй лист Продажи")
        available_sheets: List of available sheet names
        
    Returns:
        Detected sheet name or empty string if not found
    """
    user_lower = user_response.lower()
    
    # Direct match
    for sheet in available_sheets:
        if sheet.lower() in user_lower:
            return sheet
    
    # Partial match
    for sheet in available_sheets:
        sheet_words = sheet.lower().split()
        if any(word in user_lower for word in sheet_words if len(word) > 3):
            return sheet
    
    return ""

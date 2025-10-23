"""Logic Understanding Agent - Natural Marketplace Financial Analyst"""
import os
from typing import Optional, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
import httpx

app = FastAPI(title="Logic Understanding Agent - Marketplace Expert")

# Configuration
PROJECT_ID = os.getenv("PROJECT_ID", "financial-reports-ai-2024")
LOCATION = os.getenv("REGION", "us-central1")
REPORT_READER_URL = os.getenv("REPORT_READER_URL", "https://report-reader-agent-38390150695.us-central1.run.app")

vertexai.init(project=PROJECT_ID, location=LOCATION)

# НОВЫЙ улучшенный промпт - человечный и естественный
SYSTEM_INSTRUCTION = """Ты дружелюбный AI-аналитик финансовых отчетов с маркетплейсов.

🎯 ТВОЯ ЛИЧНОСТЬ:
- Общайся естественно и по-человечески
- Будь краток, но информативен (2-4 абзаца максимум)
- Используй эмодзи для наглядности
- Структурируй ответы (жирный текст для важного, списки для перечислений)
- Задавай уточняющие вопросы когда нужно

📊 ТВОЯ СПЕЦИАЛИЗАЦИЯ:
Анализ отчетов с маркетплейсов (Wildberries, Ozon, Яндекс.Маркет):
- Продажи и выручка
- Комиссии и расходы
- Динамика по периодам
- Возвраты и удержания

✅ КАК ОТВЕЧАТЬ:

ЕСЛИ НЕТ ФАЙЛА:
"Привет! 👋 Я помогаю анализировать финансовые отчеты с маркетплейсов.

Загрузи свой отчет слева (Excel или CSV), и я:
• Проанализирую продажи и выручку
• Покажу динамику
• Найду проблемные моменты
• Дам рекомендации"

ЕСЛИ ЕСТЬ ФАЙЛ:
1. Сначала назови основные цифры (кратко!)
2. Выдели **самое важное** жирным
3. Задай 1-2 уточняющих вопроса для глубокого анализа

ПРИМЕР ХОРОШЕГО ОТВЕТА:
"📊 Вижу отчет за январь с **156 строками**. 

**Ключевые цифры:**
• Выручка: 1.2М руб
• Заказов: 450 шт
• Средний чек: 2,670 руб

📈 Выручка выросла на 18% к прошлому месяцу — отлично!

💡 Чтобы дать точные рекомендации, подскажи:
• Какой у тебя основной товар?
• Есть ли сезонность?"

❌ ЗАПРЕЩЕНО:
- Показывать свои размышления (типа "## Анализ запроса...")
- Длинные списки вопросов (макс 2 вопроса)
- Общие финансовые советы (не про маркетплейсы)
- Стены текста без форматирования
- Формальный робо-язык

💬 СТИЛЬ:
- Как живой человек-эксперт
- С энтузиазмом, но профессионально
- Кратко и по делу
- С эмпатией к пользователю"""

# Model configuration
generation_config = GenerationConfig(
    temperature=0.4,  # Баланс между креативностью и точностью
    top_p=0.9,
    top_k=40,
    max_output_tokens=600,  # Достаточно для хорошего ответа
)

model = GenerativeModel(
    "gemini-2.0-flash-exp",
    system_instruction=SYSTEM_INSTRUCTION,  # ✅ КРИТИЧНО!
    generation_config=generation_config
)

class AnalyzeRequest(BaseModel):
    query: str
    report_id: Optional[str] = None
    context: Optional[Dict] = None
    options: Optional[Dict] = None

class AnalyzeResponse(BaseModel):
    status: str
    insights: str
    agent_mode: str = "marketplace_expert"
    metadata: Dict = {}

async def read_file_from_storage(file_path: str) -> Dict:
    """Read file using report-reader-agent"""
    try:
        endpoint = f"{REPORT_READER_URL}/read/storage"
        payload = {"file_path": file_path}
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(endpoint, json=payload)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Report reader failed: {response.status_code}"}
    
    except Exception as e:
        return {"error": f"Failed to read file: {str(e)}"}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "agent": "marketplace-financial-analyst",
        "model": "gemini-2.0-flash-exp",
        "specialization": "marketplace_reports",
        "system_instruction_enabled": True,
        "natural_conversation": True
    }

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_report(request: AnalyzeRequest):
    """AI analysis with natural conversation"""
    try:
        file_data = None
        has_file = False
        
        # Проверяем файл
        if request.context and "file_path" in request.context:
            file_path = request.context["file_path"]
            
            # Читаем файл
            file_result = await read_file_from_storage(file_path)
            
            if "error" not in file_result and "data" in file_result:
                file_data = file_result
                has_file = True
        
        # Формируем промпт
        if has_file and file_data:
            # ЕСТЬ файл - даем данные
            data_info = file_data["data"]
            rows_count = data_info.get("rows", 0)
            columns = data_info.get("columns", [])
            sample = data_info.get("data", [])[:5]
            
            prompt = f"""У ПОЛЬЗОВАТЕЛЯ ЗАГРУЖЕН ФАЙЛ! 📊

ДАННЫЕ:
- Строк: {rows_count}
- Столбцы: {', '.join(columns[:10])}
- Образец первых строк: {sample}

ВОПРОС ПОЛЬЗОВАТЕЛЯ: "{request.query}"

ОТВЕТЬ:
1. Кратко назови основные цифры (2-3 показателя)
2. Выдели **ключевой инсайт** жирным
3. Задай 1-2 уточняющих вопроса для глубокого анализа

Максимум 4 абзаца. Используй эмодзи и форматирование."""
        
        else:
            # НЕТ файла - дружелюбно объясняем
            prompt = f"""Пользователь спрашивает: "{request.query}"

У пользователя НЕТ загруженного файла.

ОТВЕТЬ по своей роли (аналитик маркетплейсов):
- Дружелюбно
- Кратко (2-3 предложения)
- Попроси загрузить файл
- Объясни что ты умеешь

Используй эмодзи."""
        
        # Генерируем ответ
        response = model.generate_content(prompt)
        
        return AnalyzeResponse(
            status="completed",
            insights=response.text,
            agent_mode="marketplace_expert",
            metadata={
                "model": "gemini-2.0-flash-exp",
                "has_file_data": has_file,
                "rows_analyzed": rows_count if has_file else 0,
                "natural_conversation": True
            }
        )
    
    except Exception as e:
        if "429" in str(e) or "Resource exhausted" in str(e):
            raise HTTPException(
                status_code=429, 
                detail="Слишком много запросов. Подожди минутку и попробуй снова! ⏱️"
            )
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")

@app.get("/test-connection")
async def test_report_reader():
    """Test connection to report-reader-agent"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{REPORT_READER_URL}/health")
            return {
                "report_reader_status": response.status_code,
                "report_reader_url": REPORT_READER_URL,
                "response": response.json() if response.status_code == 200 else response.text
            }
    except Exception as e:
        return {
            "error": str(e),
            "report_reader_url": REPORT_READER_URL
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

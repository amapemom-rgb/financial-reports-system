"""Logic Understanding Agent - Specialized for Marketplace Financial Analysis"""
import os
from typing import Optional, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
import httpx

app = FastAPI(title="Logic Understanding Agent - Marketplace Expert")

# Инициализация
PROJECT_ID = os.getenv("PROJECT_ID", "financial-reports-ai-2024")
LOCATION = os.getenv("REGION", "us-central1")
REPORT_READER_URL = os.getenv("REPORT_READER_URL", "https://report-reader-agent-38390150695.us-central1.run.app")

vertexai.init(project=PROJECT_ID, location=LOCATION)

# Gemini model with optimized config
generation_config = GenerationConfig(
    temperature=0.3,  # Более детерминированные ответы
    top_p=0.8,
    top_k=40,
    max_output_tokens=1024,  # Ограничиваем длину ответа
)

model = GenerativeModel(
    "gemini-2.0-flash-exp",
    generation_config=generation_config
)

SYSTEM_INSTRUCTION = """Ты опытный финансовый аналитик, специализирующийся на анализе отчетов маркетплейсов.

**Твоя роль:**
- Анализировать финансовые отчеты с маркетплейсов (продажи, транзакции, метрики)
- Выявлять тренды, аномалии, ключевые показатели
- Давать конкретные выводы и рекомендации

**Правила общения:**
- Будь КРАТКИМ и по существу (максимум 3-4 абзаца)
- Если нет данных из файла - попроси пользователя загрузить отчет
- Фокусируйся на ключевых метриках: выручка, количество транзакций, средний чек, динамика
- Не уходи в общие советы - работай с конкретными данными
- Отвечай на русском языке профессионально

**Если пользователь спрашивает общие вопросы:**
Скажи: "Я специализируюсь на анализе финансовых отчетов маркетплейсов. Загрузите файл слева, и я проанализирую ваши данные: выручку, транзакции, тренды продаж."
"""

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
        "specialization": "marketplace_reports"
    }

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_report(request: AnalyzeRequest):
    """AI analysis specialized for marketplace financial reports"""
    try:
        file_data = None
        data_summary = ""
        
        # Проверяем есть ли file_path в контексте
        if request.context and "file_path" in request.context:
            file_path = request.context["file_path"]
            
            # Читаем файл через report-reader-agent
            file_result = await read_file_from_storage(file_path)
            
            if "error" not in file_result:
                file_data = file_result
                
                # Создаем структурированное описание данных
                if "data" in file_result:
                    data_info = file_result["data"]
                    rows_count = data_info.get("rows", 0)
                    columns = data_info.get("columns", [])
                    sample_data = data_info.get("data", [])[:3]  # Первые 3 строки
                    
                    data_summary = f"""
**Загруженный отчет:**
Строк: {rows_count}
Столбцы: {', '.join(columns[:15])}

Образец данных (первые 3 записи):
```
{chr(10).join([str(row) for row in sample_data])}
```
"""
        
        # Формируем промпт
        if data_summary:
            prompt = f"""{SYSTEM_INSTRUCTION}

**ДАННЫЕ ИЗ ОТЧЕТА:**
{data_summary}

**ВОПРОС ПОЛЬЗОВАТЕЛЯ:**
{request.query}

**ТВОЯ ЗАДАЧА:**
Проанализируй данные и ответь на вопрос. Будь конкретным, фокусируйся на цифрах и трендах. Максимум 4 абзаца.
"""
        else:
            # Нет данных - короткий ответ
            prompt = f"""{SYSTEM_INSTRUCTION}

Пользователь спрашивает: "{request.query}"

У тебя НЕТ загруженных данных. Ответь кратко (1-2 предложения) и попроси загрузить отчет для анализа.
"""
        
        # Генерируем ответ
        response = model.generate_content(prompt)
        
        return AnalyzeResponse(
            status="completed",
            insights=response.text,
            agent_mode="marketplace_expert",
            metadata={
                "model": "gemini-2.0-flash-exp",
                "has_file_data": file_data is not None,
                "rows_analyzed": file_data.get("data", {}).get("rows", 0) if file_data else 0
            }
        )
    
    except Exception as e:
        # Обработка rate limit
        if "429" in str(e) or "Resource exhausted" in str(e):
            raise HTTPException(
                status_code=429, 
                detail="Слишком много запросов. Подождите 30 секунд и попробуйте снова."
            )
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

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

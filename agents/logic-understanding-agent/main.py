"""Logic Understanding Agent - with Report Reader Integration"""
import os
from typing import Optional, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import vertexai
from vertexai.generative_models import GenerativeModel
import httpx

app = FastAPI(title="Logic Understanding Agent - with File Reading")

# Инициализация
PROJECT_ID = os.getenv("PROJECT_ID", "financial-reports-ai-2024")
LOCATION = os.getenv("REGION", "us-central1")
REPORT_READER_URL = os.getenv("REPORT_READER_URL", "https://report-reader-agent-38390150695.us-central1.run.app")

vertexai.init(project=PROJECT_ID, location=LOCATION)

# Simple Gemini model
model = GenerativeModel("gemini-2.0-flash-exp")

class AnalyzeRequest(BaseModel):
    query: str
    report_id: Optional[str] = None
    context: Optional[Dict] = None
    options: Optional[Dict] = None

class AnalyzeResponse(BaseModel):
    status: str
    insights: str
    agent_mode: str = "with_file_reading"
    metadata: Dict = {}

async def read_file_from_storage(file_path: str) -> Dict:
    """Read file using report-reader-agent"""
    try:
        # Определяем тип файла
        if file_path.endswith(('.xlsx', '.xls')):
            endpoint = f"{REPORT_READER_URL}/read/storage"
            payload = {"file_path": file_path}
        elif file_path.endswith('.csv'):
            endpoint = f"{REPORT_READER_URL}/read/storage"
            payload = {"file_path": file_path}
        else:
            return {"error": "Unsupported file type"}
        
        # Вызываем report-reader-agent
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
        "agent": "logic-understanding-with-files",
        "model": "gemini-2.0-flash-exp",
        "features": ["file_reading", "data_analysis"]
    }

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_report(request: AnalyzeRequest):
    """AI analysis with file reading capability"""
    try:
        file_data = None
        file_summary = ""
        
        # Проверяем есть ли file_path в контексте
        if request.context and "file_path" in request.context:
            file_path = request.context["file_path"]
            
            # Читаем файл через report-reader-agent
            file_result = await read_file_from_storage(file_path)
            
            if "error" not in file_result:
                file_data = file_result
                
                # Создаем краткое описание данных для промпта
                if "data" in file_result:
                    data_info = file_result["data"]
                    rows_count = data_info.get("rows", 0)
                    columns = data_info.get("columns", [])
                    
                    file_summary = f"""
**Данные из файла:**
- Количество строк: {rows_count}
- Столбцы: {', '.join(columns[:10])}
- Первые несколько записей:
{str(data_info.get('data', [])[:5])}
"""
                else:
                    file_summary = f"Данные файла: {str(file_result)[:500]}"
        
        # Формируем промпт
        prompt = f"""Ты опытный финансовый аналитик. Проанализируй следующую ситуацию:

**Вопрос пользователя:**
{request.query}

{file_summary if file_summary else ""}

**Твоя задача:**
1. Если есть данные из файла - проанализируй их подробно
2. Выдели ключевые метрики и тренды
3. Дай конкретные выводы и рекомендации
4. Будь кратким и по существу

Отвечай на русском языке профессионально, но понятно.
"""
        
        # Генерируем ответ через Gemini
        response = model.generate_content(prompt)
        
        return AnalyzeResponse(
            status="completed",
            insights=response.text,
            agent_mode="with_file_reading",
            metadata={
                "model": "gemini-2.0-flash-exp",
                "file_read": file_data is not None,
                "has_data": bool(file_summary)
            }
        )
    
    except Exception as e:
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

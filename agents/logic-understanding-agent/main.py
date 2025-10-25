"""Logic Understanding Agent - Specialized for Marketplace Financial Analysis"""
import os
import logging
import time
import uuid
from datetime import datetime
from typing import Optional, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
import httpx
from google.cloud import secretmanager, firestore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Logic Understanding Agent - Marketplace Expert")

# Инициализация
PROJECT_ID = os.getenv("PROJECT_ID", "financial-reports-ai-2024")
LOCATION = os.getenv("REGION", "us-central1")
REPORT_READER_URL = os.getenv("REPORT_READER_URL", "https://report-reader-agent-38390150695.us-central1.run.app")

vertexai.init(project=PROJECT_ID, location=LOCATION)

# Firestore client for feedback storage
db = firestore.Client(project=PROJECT_ID)

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

# Default system instruction (fallback)
DEFAULT_SYSTEM_INSTRUCTION = """Ты опытный финансовый аналитик, специализирующийся на анализе отчетов маркетплейсов.

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

def get_system_prompt() -> str:
    """
    Load system prompt from Secret Manager.
    Falls back to DEFAULT_SYSTEM_INSTRUCTION if secret is unavailable.
    """
    try:
        client = secretmanager.SecretManagerServiceClient()
        secret_name = f"projects/{PROJECT_ID}/secrets/GEMINI_SYSTEM_PROMPT/versions/latest"
        
        logger.info(f"Attempting to load system prompt from Secret Manager: {secret_name}")
        
        response = client.access_secret_version(request={"name": secret_name})
        prompt = response.payload.data.decode("UTF-8")
        
        logger.info("✅ System prompt loaded successfully from Secret Manager")
        return prompt
        
    except Exception as e:
        logger.warning(f"⚠️ Failed to load prompt from Secret Manager, using default: {e}")
        return DEFAULT_SYSTEM_INSTRUCTION

# Cache the system prompt on startup (refresh every request for dynamic updates)
# For production, you might want to cache this for a few minutes
_cached_prompt = None
_last_prompt_refresh = 0
PROMPT_CACHE_SECONDS = 60  # Refresh every 60 seconds

def get_cached_system_prompt() -> str:
    """Get system prompt with caching to avoid excessive Secret Manager calls"""
    global _cached_prompt, _last_prompt_refresh
    
    current_time = time.time()
    if _cached_prompt is None or (current_time - _last_prompt_refresh) > PROMPT_CACHE_SECONDS:
        _cached_prompt = get_system_prompt()
        _last_prompt_refresh = current_time
        logger.info("🔄 System prompt cache refreshed")
    
    return _cached_prompt

# In-memory cache for request data (for regenerate functionality)
_request_cache: Dict[str, Dict] = {}

class AnalyzeRequest(BaseModel):
    query: str
    report_id: Optional[str] = None
    context: Optional[Dict] = None
    options: Optional[Dict] = None

class AnalyzeResponse(BaseModel):
    status: str
    insights: str
    request_id: str  # NEW: for feedback tracking
    agent_mode: str = "marketplace_expert"
    metadata: Dict = {}

class FeedbackRequest(BaseModel):
    request_id: str
    feedback_type: str  # "positive" or "negative"
    comment: Optional[str] = None

class RegenerateRequest(BaseModel):
    request_id: str

async def read_file_from_storage(file_path: str) -> Dict:
    """Read file using report-reader-agent"""
    try:
        endpoint = f"{REPORT_READER_URL}/read/storage"
        payload = {"request": {"file_path": file_path}}  # Nested structure for FastAPI
        
        logger.info(f"Reading file from storage: {file_path}")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(endpoint, json=payload)
            
            if response.status_code == 200:
                logger.info(f"✅ File read successfully: {file_path}")
                return response.json()
            else:
                logger.error(f"❌ Report reader failed: {response.status_code}")
                return {"error": f"Report reader failed: {response.status_code}"}
    
    except Exception as e:
        logger.error(f"❌ Failed to read file: {str(e)}")
        return {"error": f"Failed to read file: {str(e)}"}

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent": "marketplace-financial-analyst",
        "model": "gemini-2.0-flash-exp",
        "specialization": "marketplace_reports",
        "features": ["dynamic_prompts", "secret_manager", "user_feedback", "regenerate"]
    }

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_report(request: AnalyzeRequest):
    """AI analysis specialized for marketplace financial reports"""
    try:
        # Generate unique request_id
        request_id = str(uuid.uuid4())
        
        file_data = None
        data_summary = ""
        
        # Load dynamic system prompt
        system_instruction = get_cached_system_prompt()
        
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
            prompt = f"""{system_instruction}

**ДАННЫЕ ИЗ ОТЧЕТА:**
{data_summary}

**ВОПРОС ПОЛЬЗОВАТЕЛЯ:**
{request.query}

**ТВОЯ ЗАДАЧА:**
Проанализируй данные и ответь на вопрос. Будь конкретным, фокусируйся на цифрах и трендах. Максимум 4 абзаца.
"""
        else:
            # Нет данных - короткий ответ
            prompt = f"""{system_instruction}

Пользователь спрашивает: "{request.query}"

У тебя НЕТ загруженных данных. Ответь кратко (1-2 предложения) и попроси загрузить отчет для анализа.
"""
        
        # Генерируем ответ с retry logic для 429 errors
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Generating AI response (attempt {attempt + 1}/{max_retries})")
                response = model.generate_content(prompt)
                logger.info("✅ AI response generated successfully")
                break
            except Exception as gemini_error:
                if "429" in str(gemini_error) or "Resource exhausted" in str(gemini_error):
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)
                        logger.warning(f"⚠️ Rate limit hit, retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise HTTPException(
                            status_code=429,
                            detail="Слишком много запросов. Подождите 30 секунд и попробуйте снова."
                        )
                raise
        
        # Cache request for regenerate functionality
        _request_cache[request_id] = {
            "query": request.query,
            "context": request.context,
            "options": request.options,
            "prompt": prompt,
            "response": response.text,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return AnalyzeResponse(
            status="completed",
            insights=response.text,
            request_id=request_id,
            agent_mode="marketplace_expert",
            metadata={
                "model": "gemini-2.0-flash-exp",
                "has_file_data": file_data is not None,
                "rows_analyzed": file_data.get("data", {}).get("rows", 0) if file_data else 0,
                "prompt_source": "secret_manager"
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """Store user feedback in Firestore"""
    try:
        # Get cached request data
        cached_request = _request_cache.get(request.request_id)
        
        if not cached_request:
            raise HTTPException(
                status_code=404,
                detail="Request ID not found. Feedback can only be submitted for recent requests."
            )
        
        # Prepare feedback document
        feedback_data = {
            "request_id": request.request_id,
            "feedback_type": request.feedback_type,
            "comment": request.comment,
            "timestamp": datetime.utcnow(),
            "user_query": cached_request.get("query"),
            "ai_response": cached_request.get("response"),
            "prompt_used": cached_request.get("prompt")[:500],  # Truncate for storage
        }
        
        # Store in Firestore
        doc_ref = db.collection("feedback").document(request.request_id)
        doc_ref.set(feedback_data)
        
        logger.info(f"✅ Feedback stored: {request.request_id} - {request.feedback_type}")
        
        return {
            "status": "success",
            "message": f"Feedback ({request.feedback_type}) stored successfully",
            "request_id": request.request_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to store feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to store feedback: {str(e)}")

@app.post("/regenerate", response_model=AnalyzeResponse)
async def regenerate_response(request: RegenerateRequest):
    """Regenerate AI response for a previous request"""
    try:
        # Get cached request data
        cached_request = _request_cache.get(request.request_id)
        
        if not cached_request:
            raise HTTPException(
                status_code=404,
                detail="Request ID not found. Can only regenerate recent requests."
            )
        
        # Generate new request_id for regenerated response
        new_request_id = str(uuid.uuid4())
        
        logger.info(f"Regenerating response for request: {request.request_id}")
        
        # Use the same prompt but generate new response
        prompt = cached_request.get("prompt")
        
        # Generate new response
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Generating regenerated response (attempt {attempt + 1}/{max_retries})")
                response = model.generate_content(prompt)
                logger.info("✅ Regenerated response generated successfully")
                break
            except Exception as gemini_error:
                if "429" in str(gemini_error) or "Resource exhausted" in str(gemini_error):
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)
                        logger.warning(f"⚠️ Rate limit hit, retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise HTTPException(
                            status_code=429,
                            detail="Слишком много запросов. Подождите 30 секунд и попробуйте снова."
                        )
                raise
        
        # Cache new regenerated request
        _request_cache[new_request_id] = {
            "query": cached_request.get("query"),
            "context": cached_request.get("context"),
            "options": cached_request.get("options"),
            "prompt": prompt,
            "response": response.text,
            "timestamp": datetime.utcnow().isoformat(),
            "regenerated_from": request.request_id
        }
        
        return AnalyzeResponse(
            status="completed",
            insights=response.text,
            request_id=new_request_id,
            agent_mode="marketplace_expert",
            metadata={
                "model": "gemini-2.0-flash-exp",
                "regenerated": True,
                "original_request_id": request.request_id,
                "prompt_source": "secret_manager"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Regenerate failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Regenerate failed: {str(e)}")

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

@app.get("/prompt/info")
async def get_prompt_info():
    """Get information about current system prompt (for debugging)"""
    try:
        current_prompt = get_cached_system_prompt()
        return {
            "status": "success",
            "prompt_length": len(current_prompt),
            "prompt_source": "secret_manager" if current_prompt != DEFAULT_SYSTEM_INSTRUCTION else "default",
            "cache_age_seconds": time.time() - _last_prompt_refresh,
            "prompt_preview": current_prompt[:200] + "..." if len(current_prompt) > 200 else current_prompt
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

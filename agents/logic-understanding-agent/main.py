"""Logic Understanding Agent - Specialized for Marketplace Financial Analysis

Enhanced with Multi-Sheet Intelligence for handling Excel files with 30+ sheets.
Session 19: Added Retry Logic for Report Reader (Priority 1) and Firestore (Priority 2)
"""
import os
import logging
import time
import uuid
from datetime import datetime
from typing import Optional, Dict
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
import httpx
from google.cloud import secretmanager, firestore

# Session 19: Retry logic for Report Reader and Firestore
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
from google.api_core import retry as google_retry
from google.api_core import exceptions as google_exceptions

# Import multi-sheet intelligence functions
from prompts import (
    build_super_prompt,
    build_sheet_analysis_prompt,
    extract_sheet_name_from_user_response
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Logic Understanding Agent - Marketplace Expert")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# In-memory cache for request data (for regenerate functionality and multi-sheet context)
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

class AnalyzeSheetRequest(BaseModel):
    """Request to analyze a specific sheet after metadata review"""
    file_path: str
    sheet_name: str
    original_query: str
    conversation_context: Optional[str] = None

# Session 19 Priority 1: Retry configuration for Report Reader calls
# Retries on network errors, timeouts, and HTTP errors (except 4xx client errors)
REPORT_READER_RETRY_POLICY = retry(
    stop=stop_after_attempt(3),  # Try 3 times total
    wait=wait_exponential(multiplier=1, min=2, max=10),  # 2s → 4s → 8s
    retry=retry_if_exception_type((
        httpx.HTTPError,
        httpx.TimeoutException,
        httpx.ConnectError,
        httpx.ReadTimeout
    )),
    before_sleep=before_sleep_log(logger, logging.WARNING)
)

# Session 19 Priority 2: Retry policy for Firestore operations
# Retries on transient Google Cloud API errors
FIRESTORE_RETRY_POLICY = google_retry.Retry(
    initial=1.0,      # Initial delay: 1.0s
    maximum=10.0,     # Maximum delay: 10.0s
    multiplier=2.0,   # Exponential backoff multiplier (1s → 2s → 4s → 8s → 10s)
    deadline=30.0,    # Total retry deadline: 30s
    predicate=google_retry.if_exception_type(
        google_exceptions.DeadlineExceeded,
        google_exceptions.ServiceUnavailable,
        google_exceptions.InternalServerError,
        google_exceptions.TooManyRequests,
    )
)

async def get_file_metadata(file_path: str) -> Dict:
    """Get metadata for Excel file (all sheets) using Report Reader
    
    Session 19: Enhanced with retry logic (3 attempts with exponential backoff)
    Expected: 7% failure rate → ~1% failure rate
    """
    
    @REPORT_READER_RETRY_POLICY
    async def _fetch_with_retry():
        """Inner function with retry decorator"""
        endpoint = f"{REPORT_READER_URL}/analyze/metadata"
        payload = {"request": {"file_path": file_path}}
        
        logger.info(f"Fetching metadata for file: {file_path}")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(endpoint, json=payload)
            
            # Don't retry on 4xx client errors (bad request, not found, etc.)
            if 400 <= response.status_code < 500:
                logger.error(f"❌ Client error (no retry): {response.status_code}")
                return {"error": f"Client error: {response.status_code}"}
            
            # Raise for 5xx errors to trigger retry
            response.raise_for_status()
            
            logger.info(f"✅ Metadata fetched successfully")
            return response.json()
    
    try:
        return await _fetch_with_retry()
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ Metadata fetch failed after retries: {e}")
        return {"error": f"Metadata fetch failed: {e.response.status_code}"}
    except Exception as e:
        logger.error(f"❌ Failed to fetch metadata after retries: {str(e)}")
        return {"error": f"Failed to fetch metadata: {str(e)}"}

async def read_specific_sheet(file_path: str, sheet_name: str) -> Dict:
    """Read specific sheet using Report Reader
    
    Session 19: Enhanced with retry logic (3 attempts with exponential backoff)
    """
    
    @REPORT_READER_RETRY_POLICY
    async def _read_with_retry():
        """Inner function with retry decorator"""
        endpoint = f"{REPORT_READER_URL}/read/sheet"
        payload = {
            "file_path": file_path,
            "sheet_name": sheet_name
        }
        
        logger.info(f"Reading sheet '{sheet_name}' from file: {file_path}")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(endpoint, json=payload)
            
            # Don't retry on 4xx client errors
            if 400 <= response.status_code < 500:
                logger.error(f"❌ Client error (no retry): {response.status_code}")
                return {"error": f"Client error: {response.status_code}"}
            
            # Raise for 5xx errors to trigger retry
            response.raise_for_status()
            
            logger.info(f"✅ Sheet '{sheet_name}' read successfully")
            return response.json()
    
    try:
        return await _read_with_retry()
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ Sheet read failed after retries: {e}")
        return {"error": f"Sheet read failed: {e.response.status_code}"}
    except Exception as e:
        logger.error(f"❌ Failed to read sheet after retries: {str(e)}")
        return {"error": f"Failed to read sheet: {str(e)}"}

async def read_file_from_storage(file_path: str) -> Dict:
    """Read file using report-reader-agent (reads first sheet only)
    
    Session 19: Enhanced with retry logic (3 attempts with exponential backoff)
    """
    
    @REPORT_READER_RETRY_POLICY
    async def _read_with_retry():
        """Inner function with retry decorator"""
        endpoint = f"{REPORT_READER_URL}/read/storage"
        payload = {"request": {"file_path": file_path}}  # Nested structure for FastAPI
        
        logger.info(f"Reading file from storage: {file_path}")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(endpoint, json=payload)
            
            # Don't retry on 4xx client errors
            if 400 <= response.status_code < 500:
                logger.error(f"❌ Client error (no retry): {response.status_code}")
                return {"error": f"Client error: {response.status_code}"}
            
            # Raise for 5xx errors to trigger retry
            response.raise_for_status()
            
            logger.info(f"✅ File read successfully: {file_path}")
            return response.json()
    
    try:
        return await _read_with_retry()
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ Report reader failed after retries: {e}")
        return {"error": f"Report reader failed: {e.response.status_code}"}
    except Exception as e:
        logger.error(f"❌ Failed to read file after retries: {str(e)}")
        return {"error": f"Failed to read file: {str(e)}"}

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent": "marketplace-financial-analyst",
        "model": "gemini-2.0-flash-exp",
        "specialization": "marketplace_reports",
        "features": [
            "dynamic_prompts", 
            "secret_manager", 
            "user_feedback", 
            "regenerate", 
            "cors_enabled",
            "multi_sheet_intelligence",
            "report_reader_retry_logic",  # Priority 1
            "firestore_retry_logic"       # Priority 2
        ]
    }

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_report(request: AnalyzeRequest):
    """AI analysis specialized for marketplace financial reports
    
    Enhanced with Multi-Sheet Intelligence:
    - For files with 5+ sheets: uses metadata-first approach
    - Asks user to select specific sheet for analysis
    - Loads only selected sheet data (performance optimization)
    """
    try:
        # Generate unique request_id
        request_id = str(uuid.uuid4())
        
        file_data = None
        data_summary = ""
        use_multi_sheet = False
        
        # Load dynamic system prompt
        system_instruction = get_cached_system_prompt()
        
        # Проверяем есть ли file_path в контексте
        if request.context and "file_path" in request.context:
            file_path = request.context["file_path"]
            
            # Step 1: Check if file is Excel and get metadata
            if file_path.endswith(('.xlsx', '.xls')):
                logger.info("📊 Excel file detected - checking for multiple sheets")
                
                metadata_result = await get_file_metadata(file_path)
                
                if "error" not in metadata_result:
                    sheets_count = metadata_result.get("sheets_count", 1)
                    
                    # Multi-sheet logic: if > 5 sheets, use metadata-first approach
                    if sheets_count > 5:
                        logger.info(f"🎯 Multi-sheet mode activated: {sheets_count} sheets detected")
                        use_multi_sheet = True
                        
                        # Build super prompt for sheet selection
                        prompt = build_super_prompt(metadata_result, request.query)
                        
                        # Generate response
                        response = model.generate_content(prompt)
                        
                        # Cache metadata and request for follow-up
                        _request_cache[request_id] = {
                            "query": request.query,
                            "context": request.context,
                            "options": request.options,
                            "prompt": prompt,
                            "response": response.text,
                            "timestamp": datetime.utcnow().isoformat(),
                            "metadata": metadata_result,  # Store metadata for next interaction
                            "multi_sheet_mode": True
                        }
                        
                        return AnalyzeResponse(
                            status="completed",
                            insights=response.text,
                            request_id=request_id,
                            agent_mode="multi_sheet_selector",
                            metadata={
                                "model": "gemini-2.0-flash-exp",
                                "sheets_count": sheets_count,
                                "sheet_names": metadata_result.get("sheet_names", []),
                                "multi_sheet_mode": True,
                                "next_action": "select_sheet",
                                "prompt_source": "secret_manager"
                            }
                        )
            
            # Standard flow: single sheet or < 5 sheets
            if not use_multi_sheet:
                # Читаем файл через report-reader-agent (first sheet)
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

@app.post("/analyze/sheet", response_model=AnalyzeResponse)
async def analyze_specific_sheet(request: AnalyzeSheetRequest):
    """Analyze specific sheet after user selection (Part 2 of multi-sheet flow)
    
    This endpoint is called after user selects a sheet from the metadata preview.
    It loads full data for the selected sheet and performs detailed analysis.
    """
    try:
        # Generate unique request_id
        request_id = str(uuid.uuid4())
        
        logger.info(f"📊 Analyzing specific sheet: {request.sheet_name}")
        
        # Read specific sheet data
        sheet_result = await read_specific_sheet(request.file_path, request.sheet_name)
        
        if "error" in sheet_result:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to read sheet: {sheet_result['error']}"
            )
        
        # Extract data summary
        data_info = sheet_result.get("data", {})
        rows_count = data_info.get("rows", 0)
        columns = data_info.get("columns", [])
        sample_data = data_info.get("data", [])[:3]
        
        data_summary = f"""
**Лист: "{request.sheet_name}"**
Строк: {rows_count}
Столбцы: {', '.join(columns[:15])}

Образец данных (первые 3 записи):
```
{chr(10).join([str(row) for row in sample_data])}
```
"""
        
        # Load system instruction
        system_instruction = get_cached_system_prompt()
        
        # Build analysis prompt
        prompt = build_sheet_analysis_prompt(
            system_instruction=system_instruction,
            user_query=request.original_query,
            sheet_name=request.sheet_name,
            data_summary=data_summary
        )
        
        # Generate analysis
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Generating sheet analysis (attempt {attempt + 1}/{max_retries})")
                response = model.generate_content(prompt)
                logger.info("✅ Sheet analysis generated successfully")
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
        
        # Cache request
        _request_cache[request_id] = {
            "query": request.original_query,
            "sheet_name": request.sheet_name,
            "file_path": request.file_path,
            "prompt": prompt,
            "response": response.text,
            "timestamp": datetime.utcnow().isoformat(),
            "multi_sheet_analysis": True
        }
        
        return AnalyzeResponse(
            status="completed",
            insights=response.text,
            request_id=request_id,
            agent_mode="sheet_analyst",
            metadata={
                "model": "gemini-2.0-flash-exp",
                "sheet_name": request.sheet_name,
                "rows_analyzed": rows_count,
                "multi_sheet_analysis": True,
                "prompt_source": "secret_manager"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Sheet analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Sheet analysis failed: {str(e)}")

@app.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """Store user feedback in Firestore
    
    Session 19 Priority 2: Enhanced with retry logic for transient Firestore errors
    Expected: 5% failure rate → ~0.5% failure rate
    """
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
        
        # Store in Firestore with retry policy
        try:
            doc_ref = db.collection("feedback").document(request.request_id)
            doc_ref.set(feedback_data, retry=FIRESTORE_RETRY_POLICY)
            
            logger.info(f"✅ Feedback stored: {request.request_id} - {request.feedback_type}")
            
            return {
                "status": "success",
                "message": f"Feedback ({request.feedback_type}) stored successfully",
                "request_id": request.request_id
            }
            
        except google_exceptions.GoogleAPIError as db_error:
            # Specific Google Cloud API errors
            error_type = type(db_error).__name__
            logger.error(f"❌ Firestore error after retries: {error_type} - {str(db_error)}")
            
            # Return 503 Service Unavailable for transient database issues
            raise HTTPException(
                status_code=503,
                detail="Database temporarily unavailable. Please try again in a moment."
            )
        
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

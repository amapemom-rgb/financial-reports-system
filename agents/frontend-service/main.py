"""Frontend Service with Google Speech API Integration"""
import os
import io
import base64
from typing import Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from datetime import datetime
import httpx

# Google Cloud Speech and Text-to-Speech
from google.cloud import speech_v1 as speech
from google.cloud import texttospeech

app = FastAPI(title="Financial Reports - Frontend API")

# Configuration
LOGIC_AGENT_URL = os.getenv("LOGIC_AGENT_URL", "http://logic-understanding-agent:8080")
REPORT_READER_URL = os.getenv("REPORT_READER_URL", "http://report-reader-agent:8081")
PROJECT_ID = os.getenv("PROJECT_ID", "financial-reports-ai-2024")

# Initialize Google Cloud clients
try:
    speech_client = speech.SpeechClient()
    tts_client = texttospeech.TextToSpeechClient()
    speech_available = True
except Exception as e:
    print(f"Warning: Google Speech APIs not available: {e}")
    speech_client = None
    tts_client = None
    speech_available = False

# Data Models
class AnalysisRequest(BaseModel):
    query: str
    report_id: Optional[str] = None
    file_path: Optional[str] = None
    use_voice_response: bool = False

class TextToSpeechRequest(BaseModel):
    text: str
    language_code: str = "ru-RU"
    voice_name: str = "ru-RU-Wavenet-A"

class SpeechToTextResponse(BaseModel):
    transcript: str
    confidence: float
    language: str

class ChatRequest(BaseModel):
    message: str
    file_id: Optional[str] = None
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    timestamp: str
    file_context: Optional[dict] = None

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "frontend-service",
        "timestamp": datetime.utcnow().isoformat(),
        "features": {
            "speech_to_text": speech_available,
            "text_to_speech": speech_available,
            "ai_analysis": True,
            "chat": True
        }
    }

@app.post("/chat")
async def chat_with_ai(request: ChatRequest):
    """Chat with AI agent about financial reports"""
    try:
        context = {}
        if request.file_id:
            context["file_path"] = request.file_id
        if request.conversation_id:
            context["conversation_id"] = request.conversation_id
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{LOGIC_AGENT_URL}/analyze",
                json={
                    "query": request.message,
                    "context": context
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"AI agent failed: {response.text}"
                )
            
            result = response.json()
            conv_id = request.conversation_id or f"conv_{datetime.utcnow().timestamp()}"
            
            return ChatResponse(
                response=result.get("insights", "Извините, не могу обработать запрос"),
                conversation_id=conv_id,
                timestamp=datetime.utcnow().isoformat(),
                file_context={"file_id": request.file_id} if request.file_id else None
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload CSV or Excel file"""
    try:
        filename = file.filename.lower()
        if filename.endswith(('.xlsx', '.xls')):
            endpoint = f"{REPORT_READER_URL}/upload/excel"
        elif filename.endswith('.csv'):
            endpoint = f"{REPORT_READER_URL}/upload/csv"
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            files = {"file": (file.filename, await file.read(), file.content_type)}
            response = await client.post(endpoint, files=files)
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)
            
            result = response.json()
            return {
                "status": "success",
                "file_id": result.get("file_id", f"reports/{file.filename}"),
                "filename": file.filename,
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
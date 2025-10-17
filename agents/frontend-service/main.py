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

# ==========================================
# Configuration
# ==========================================

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

# ==========================================
# Data Models
# ==========================================

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

# ==========================================
# Speech Functions
# ==========================================

def speech_to_text(audio_content: bytes, language_code: str = "ru-RU") -> dict:
    """Convert speech to text using Google Speech-to-Text"""
    if not speech_client:
        raise HTTPException(status_code=503, detail="Speech-to-Text not available")
    
    try:
        audio = speech.RecognitionAudio(content=audio_content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code=language_code,
            enable_automatic_punctuation=True,
            model="default",
            use_enhanced=True
        )
        
        response = speech_client.recognize(config=config, audio=audio)
        
        if not response.results:
            return {"transcript": "", "confidence": 0.0}
        
        result = response.results[0]
        alternative = result.alternatives[0]
        
        return {
            "transcript": alternative.transcript,
            "confidence": alternative.confidence,
            "language": language_code
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech-to-Text failed: {str(e)}")

def text_to_speech(text: str, language_code: str = "ru-RU", 
                  voice_name: str = "ru-RU-Wavenet-A") -> bytes:
    """Convert text to speech using Google Text-to-Speech"""
    if not tts_client:
        raise HTTPException(status_code=503, detail="Text-to-Speech not available")
    
    try:
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=voice_name
        )
        
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        
        response = tts_client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        return response.audio_content
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text-to-Speech failed: {str(e)}")

# ==========================================
# API Endpoints
# ==========================================

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "frontend-service",
        "timestamp": datetime.utcnow().isoformat(),
        "features": {
            "speech_to_text": speech_available,
            "text_to_speech": speech_available,
            "ai_analysis": True
        }
    }

@app.get("/")
async def root():
    return {
        "service": "Financial Reports Analysis System",
        "version": "1.0.0",
        "status": "running",
        "capabilities": [
            "Voice interface (Speech-to-Text/Text-to-Speech)",
            "AI-powered financial analysis",
            "Excel and Google Sheets support",
            "Interactive visualizations"
        ]
    }

@app.post("/analyze")
async def analyze_report(request: AnalysisRequest):
    """Analyze financial report with AI agent"""
    try:
        # Call Logic Understanding Agent
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{LOGIC_AGENT_URL}/analyze",
                json={
                    "query": request.query,
                    "report_id": request.report_id,
                    "context": {"file_path": request.file_path} if request.file_path else None
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Analysis failed: {response.text}"
                )
            
            result = response.json()
            
            # If voice response requested, convert to speech
            if request.use_voice_response and speech_available:
                audio_content = text_to_speech(result.get("insights", ""))
                audio_base64 = base64.b64encode(audio_content).decode('utf-8')
                result["audio_response"] = audio_base64
            
            return {
                "status": "success",
                "timestamp": datetime.utcnow().isoformat(),
                "query": request.query,
                "analysis": result
            }
    
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Agent unavailable: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/voice/analyze")
async def voice_analyze(
    audio: UploadFile = File(...),
    language: str = "ru-RU",
    report_id: Optional[str] = None
):
    """Analyze report using voice input"""
    if not speech_available:
        raise HTTPException(status_code=503, detail="Voice features not available")
    
    try:
        # Read audio file
        audio_content = await audio.read()
        
        # Convert speech to text
        stt_result = speech_to_text(audio_content, language)
        transcript = stt_result["transcript"]
        
        if not transcript:
            raise HTTPException(status_code=400, detail="Could not understand speech")
        
        # Analyze with AI
        analysis_request = AnalysisRequest(
            query=transcript,
            report_id=report_id,
            use_voice_response=True
        )
        
        result = await analyze_report(analysis_request)
        result["voice_input"] = {
            "transcript": transcript,
            "confidence": stt_result["confidence"]
        }
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice analysis failed: {str(e)}")

@app.post("/speech-to-text", response_model=SpeechToTextResponse)
async def convert_speech_to_text(
    audio: UploadFile = File(...),
    language: str = "ru-RU"
):
    """Convert speech to text"""
    if not speech_available:
        raise HTTPException(status_code=503, detail="Speech-to-Text not available")
    
    try:
        audio_content = await audio.read()
        result = speech_to_text(audio_content, language)
        
        return SpeechToTextResponse(
            transcript=result["transcript"],
            confidence=result["confidence"],
            language=result["language"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/text-to-speech")
async def convert_text_to_speech(request: TextToSpeechRequest):
    """Convert text to speech"""
    if not speech_available:
        raise HTTPException(status_code=503, detail="Text-to-Speech not available")
    
    try:
        audio_content = text_to_speech(
            request.text,
            request.language_code,
            request.voice_name
        )
        
        return StreamingResponse(
            io.BytesIO(audio_content),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=speech.mp3"
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/voices")
async def list_voices(language_code: str = "ru-RU"):
    """List available voices for Text-to-Speech"""
    if not speech_available:
        raise HTTPException(status_code=503, detail="Text-to-Speech not available")
    
    try:
        response = tts_client.list_voices(language_code=language_code)
        
        voices = []
        for voice in response.voices:
            voices.append({
                "name": voice.name,
                "language_codes": list(voice.language_codes),
                "gender": texttospeech.SsmlVoiceGender(voice.ssml_gender).name
            })
        
        return {
            "language_code": language_code,
            "voices": voices
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload/excel")
async def upload_excel_report(file: UploadFile = File(...)):
    """Upload and parse Excel report"""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            files = {"file": (file.filename, await file.read(), file.content_type)}
            response = await client.post(
                f"{REPORT_READER_URL}/upload/excel",
                files=files
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Upload failed: {response.text}"
                )
            
            return response.json()
    
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Report Reader unavailable: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/read/sheets")
async def read_google_sheets(spreadsheet_id: str, range: str = "A1:Z1000"):
    """Read Google Sheets"""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{REPORT_READER_URL}/read/sheets",
                json={
                    "spreadsheet_id": spreadsheet_id,
                    "range": range
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Read failed: {response.text}"
                )
            
            return response.json()
    
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Report Reader unavailable: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Read failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

"""Frontend Service with Storage, Pub/Sub and HTML UI"""
import os
import io
import json
import uuid
import base64
from typing import Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse, HTMLResponse
from pydantic import BaseModel
from datetime import datetime
import httpx

# Google Cloud Services
from google.cloud import speech_v1 as speech
from google.cloud import texttospeech
from google.cloud import storage
from google.cloud import pubsub_v1

app = FastAPI(title="Financial Reports - Frontend API")

# Configuration
PROJECT_ID = os.getenv("PROJECT_ID", "financial-reports-ai-2024")
REGION = os.getenv("REGION", "us-central1")
REPORTS_BUCKET = os.getenv("REPORTS_BUCKET", "financial-reports-ai-2024-reports")
TASKS_TOPIC = os.getenv("TASKS_TOPIC", "financial-reports-tasks")
RESULTS_TOPIC = os.getenv("RESULTS_TOPIC", "financial-reports-results")

LOGIC_AGENT_URL = os.getenv("LOGIC_AGENT_URL", "https://logic-understanding-agent-38390150695.us-central1.run.app")
REPORT_READER_URL = os.getenv("REPORT_READER_URL", "http://report-reader-agent:8081")
ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "https://orchestrator-agent-eu66elwpia-uc.a.run.app")

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

# Initialize Storage
try:
    storage_client = storage.Client()
    bucket = storage_client.bucket(REPORTS_BUCKET)
    storage_available = True
except Exception as e:
    print(f"Warning: Cloud Storage not available: {e}")
    storage_client = None
    bucket = None
    storage_available = False

# Initialize Pub/Sub Publisher
try:
    publisher = pubsub_v1.PublisherClient()
    tasks_topic_path = publisher.topic_path(PROJECT_ID, TASKS_TOPIC)
    pubsub_available = True
except Exception as e:
    print(f"Warning: Pub/Sub not available: {e}")
    publisher = None
    pubsub_available = False

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
    request_id: Optional[str] = None  # NEW: for feedback tracking
    file_context: Optional[dict] = None

class FeedbackRequest(BaseModel):
    request_id: str
    feedback_type: str  # "positive" or "negative"
    comment: Optional[str] = None

class RegenerateRequest(BaseModel):
    request_id: str

# HTML UI with Feedback Buttons
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Financial Reports AI System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { opacity: 0.9; font-size: 1.1em; }
        .content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            padding: 30px;
        }
        .panel {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 25px;
        }
        .panel h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.5em;
        }
        .upload-zone {
            border: 3px dashed #667eea;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            background: white;
            cursor: pointer;
            transition: all 0.3s;
        }
        .upload-zone:hover {
            background: #f0f4ff;
            border-color: #764ba2;
        }
        .upload-zone.dragover {
            background: #e6efff;
            border-color: #667eea;
            transform: scale(1.02);
        }
        #fileInput { display: none; }
        .upload-icon {
            font-size: 3em;
            color: #667eea;
            margin-bottom: 10px;
        }
        .chat-container {
            display: flex;
            flex-direction: column;
            height: 500px;
        }
        .messages {
            flex: 1;
            overflow-y: auto;
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
        }
        .message {
            margin-bottom: 15px;
            animation: slideIn 0.3s;
        }
        .message-content {
            padding: 12px 18px;
            border-radius: 18px;
            max-width: 80%;
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .message.user .message-content {
            background: #667eea;
            color: white;
            margin-left: auto;
            text-align: right;
        }
        .message.ai .message-content {
            background: #e6efff;
            color: #333;
        }
        /* Feedback buttons */
        .feedback-buttons {
            display: flex;
            gap: 8px;
            margin-top: 8px;
            margin-left: 0;
        }
        .feedback-btn {
            padding: 6px 12px;
            border: 1px solid #ddd;
            background: white;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }
        .feedback-btn:hover {
            background: #f5f5f5;
            transform: translateY(-1px);
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .feedback-btn:active {
            transform: translateY(0);
        }
        .feedback-btn.liked {
            background: #d4edda;
            border-color: #c3e6cb;
            color: #155724;
        }
        .feedback-btn.disliked {
            background: #f8d7da;
            border-color: #f5c6cb;
            color: #721c24;
        }
        .feedback-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .input-group {
            display: flex;
            gap: 10px;
        }
        input[type="text"] {
            flex: 1;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 1em;
            transition: border 0.3s;
        }
        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            padding: 15px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1em;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
        }
        button:active {
            transform: translateY(0);
        }
        .status {
            padding: 15px;
            border-radius: 10px;
            margin-top: 15px;
            display: none;
        }
        .status.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .status.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .status.info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 1s ease-in-out infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        @media (max-width: 768px) {
            .content {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Financial Reports AI</h1>
            <p>Загрузите отчет и общайтесь с AI-ассистентом</p>
        </div>
        
        <div class="content">
            <div class="panel">
                <h2>📁 Загрузка отчета</h2>
                <div class="upload-zone" id="uploadZone">
                    <div class="upload-icon">📊</div>
                    <p><strong>Перетащите файл сюда</strong></p>
                    <p>или нажмите для выбора</p>
                    <p style="font-size: 0.9em; color: #666; margin-top: 10px;">
                        Поддерживаются: Excel (.xlsx, .xls), CSV
                    </p>
                </div>
                <input type="file" id="fileInput" accept=".xlsx,.xls,.csv">
                <div class="status" id="uploadStatus"></div>
            </div>
            
            <div class="panel">
                <h2>💬 Чат с AI</h2>
                <div class="chat-container">
                    <div class="messages" id="messages">
                        <div class="message ai">
                            <div class="message-content">
                                Привет! Я AI-ассистент для анализа финансовых отчетов. 
                                Загрузите файл слева, и я помогу вам его проанализировать.
                            </div>
                        </div>
                    </div>
                    <div class="input-group">
                        <input type="text" id="messageInput" placeholder="Задайте вопрос..." />
                        <button onclick="sendMessage()">Отправить</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentFileId = null;
        let conversationId = null;

        // Upload Zone
        const uploadZone = document.getElementById('uploadZone');
        const fileInput = document.getElementById('fileInput');
        const uploadStatus = document.getElementById('uploadStatus');

        uploadZone.addEventListener('click', () => fileInput.click());

        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('dragover');
        });

        uploadZone.addEventListener('dragleave', () => {
            uploadZone.classList.remove('dragover');
        });

        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('dragover');
            const file = e.dataTransfer.files[0];
            if (file) uploadFile(file);
        });

        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) uploadFile(file);
        });

        async function uploadFile(file) {
            const formData = new FormData();
            formData.append('file', file);

            showStatus('info', '⏳ Загрузка файла...');

            try {
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (response.ok) {
                    currentFileId = data.file_id;
                    showStatus('success', `✅ Файл загружен: ${data.filename}`);
                    addMessage('ai', `Файл "${data.filename}" успешно загружен! Задайте мне вопрос об этом отчете.`);
                } else {
                    showStatus('error', `❌ Ошибка: ${data.detail}`);
                }
            } catch (error) {
                showStatus('error', `❌ Ошибка загрузки: ${error.message}`);
            }
        }

        // Chat
        const messagesDiv = document.getElementById('messages');
        const messageInput = document.getElementById('messageInput');

        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });

        async function sendMessage() {
            const message = messageInput.value.trim();
            if (!message) return;

            addMessage('user', message);
            messageInput.value = '';

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: message,
                        file_id: currentFileId,
                        conversation_id: conversationId
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    conversationId = data.conversation_id;
                    addMessage('ai', data.response, data.request_id);
                } else {
                    addMessage('ai', `Ошибка: ${data.detail}`);
                }
            } catch (error) {
                addMessage('ai', `Ошибка связи: ${error.message}`);
            }
        }

        function addMessage(type, text, requestId = null) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}`;
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            contentDiv.textContent = text;
            
            messageDiv.appendChild(contentDiv);
            
            // Add feedback buttons only for AI messages with requestId
            if (type === 'ai' && requestId) {
                const feedbackDiv = document.createElement('div');
                feedbackDiv.className = 'feedback-buttons';
                feedbackDiv.innerHTML = `
                    <button class="feedback-btn" onclick="sendFeedback('${requestId}', 'positive', this)" title="Мне понравился этот ответ">
                        👍 Нравится
                    </button>
                    <button class="feedback-btn" onclick="sendFeedback('${requestId}', 'negative', this)" title="Мне не понравился этот ответ">
                        👎 Не нравится
                    </button>
                    <button class="feedback-btn" onclick="regenerateResponse('${requestId}', this)" title="Переделать ответ">
                        🔄 Переделать
                    </button>
                `;
                messageDiv.appendChild(feedbackDiv);
            }
            
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        async function sendFeedback(requestId, feedbackType, buttonElement) {
            // Disable all buttons in this feedback group
            const feedbackDiv = buttonElement.parentElement;
            const buttons = feedbackDiv.querySelectorAll('.feedback-btn');
            buttons.forEach(btn => btn.disabled = true);

            try {
                const response = await fetch('/api/feedback', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        request_id: requestId,
                        feedback_type: feedbackType
                    })
                });

                if (response.ok) {
                    // Highlight the clicked button
                    buttonElement.classList.add(feedbackType === 'positive' ? 'liked' : 'disliked');
                    
                    // Show brief success message
                    const originalText = buttonElement.textContent;
                    buttonElement.textContent = feedbackType === 'positive' ? '✓ Отправлено' : '✓ Отправлено';
                    setTimeout(() => {
                        buttonElement.textContent = originalText;
                    }, 2000);
                } else {
                    alert('Ошибка отправки фидбэка');
                    buttons.forEach(btn => btn.disabled = false);
                }
            } catch (error) {
                alert(`Ошибка: ${error.message}`);
                buttons.forEach(btn => btn.disabled = false);
            }
        }

        async function regenerateResponse(requestId, buttonElement) {
            // Disable button during regeneration
            buttonElement.disabled = true;
            const originalText = buttonElement.textContent;
            buttonElement.textContent = '⏳ Переделываю...';

            try {
                const response = await fetch('/api/regenerate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        request_id: requestId
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    // Add new regenerated message
                    addMessage('ai', data.response, data.request_id);
                    buttonElement.textContent = '✓ Готово';
                    setTimeout(() => {
                        buttonElement.textContent = originalText;
                        buttonElement.disabled = false;
                    }, 2000);
                } else {
                    alert(`Ошибка: ${data.detail}`);
                    buttonElement.textContent = originalText;
                    buttonElement.disabled = false;
                }
            } catch (error) {
                alert(`Ошибка: ${error.message}`);
                buttonElement.textContent = originalText;
                buttonElement.disabled = false;
            }
        }

        function showStatus(type, message) {
            uploadStatus.className = `status ${type}`;
            uploadStatus.textContent = message;
            uploadStatus.style.display = 'block';
            setTimeout(() => {
                uploadStatus.style.display = 'none';
            }, 5000);
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve HTML UI"""
    return HTML_TEMPLATE

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "frontend-service",
        "timestamp": datetime.utcnow().isoformat(),
        "features": {
            "speech_to_text": speech_available,
            "text_to_speech": speech_available,
            "storage": storage_available,
            "pubsub": pubsub_available,
            "ai_analysis": True,
            "chat": True,
            "user_feedback": True,  # NEW
            "regenerate": True  # NEW
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
                request_id=result.get("request_id"),  # NEW: pass request_id from Logic Agent
                file_context={"file_id": request.file_id} if request.file_id else None
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.post("/api/feedback")
async def submit_feedback(request: FeedbackRequest):
    """Proxy feedback to Logic Agent"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{LOGIC_AGENT_URL}/feedback",
                json=request.dict()
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Feedback submission failed: {response.text}"
                )
            
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feedback failed: {str(e)}")

@app.post("/api/regenerate")
async def regenerate_response(request: RegenerateRequest):
    """Proxy regenerate request to Logic Agent"""
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{LOGIC_AGENT_URL}/regenerate",
                json=request.dict()
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Regenerate failed: {response.text}"
                )
            
            result = response.json()
            
            # Return in same format as chat
            return {
                "response": result.get("insights", "Извините, не могу обработать запрос"),
                "request_id": result.get("request_id"),
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Regenerate failed: {str(e)}")

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload file to Cloud Storage and trigger orchestration via Pub/Sub"""
    try:
        if not storage_available:
            raise HTTPException(status_code=503, detail="Cloud Storage not available")
        
        if not pubsub_available:
            raise HTTPException(status_code=503, detail="Pub/Sub not available")
        
        # Generate unique file ID
        file_id = f"{uuid.uuid4().hex}_{file.filename}"
        file_path = f"reports/{file_id}"
        
        # Upload to Cloud Storage
        blob = bucket.blob(file_path)
        content = await file.read()
        blob.upload_from_string(content, content_type=file.content_type)
        
        # Publish task to Pub/Sub for orchestrator
        task_data = {
            "task_id": f"task_{uuid.uuid4().hex[:12]}",
            "workflow_type": "analyze_report",
            "file_id": file_id,
            "file_path": file_path,
            "filename": file.filename,
            "bucket": REPORTS_BUCKET,
            "uploaded_at": datetime.utcnow().isoformat()
        }
        
        message_json = json.dumps(task_data)
        message_bytes = message_json.encode('utf-8')
        
        # Publish message
        future = publisher.publish(tasks_topic_path, message_bytes)
        message_id = future.result()
        
        return {
            "status": "success",
            "file_id": file_path,
            "filename": file.filename,
            "message_id": message_id,
            "task_id": task_data["task_id"],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

"""Logic Understanding Agent - Simplified Version without Search"""
import os
from typing import Optional, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import vertexai
from vertexai.generative_models import GenerativeModel

app = FastAPI(title="Logic Understanding Agent - Simplified")

# Инициализация
PROJECT_ID = os.getenv("PROJECT_ID", "financial-reports-ai-2024")
LOCATION = os.getenv("REGION", "us-central1")

vertexai.init(project=PROJECT_ID, location=LOCATION)

# Simple Gemini model without complex tools
model = GenerativeModel("gemini-2.0-flash-exp")

class AnalyzeRequest(BaseModel):
    query: str
    report_id: Optional[str] = None
    context: Optional[Dict] = None
    options: Optional[Dict] = None

class AnalyzeResponse(BaseModel):
    status: str
    insights: str
    agent_mode: str = "simple"
    metadata: Dict = {}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "agent": "logic-understanding-simple",
        "model": "gemini-2.0-flash-exp"
    }

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_report(request: AnalyzeRequest):
    """Simple AI analysis using Gemini"""
    try:
        # Build prompt with context
        prompt = f"""Ты финансовый аналитик. Проанализируй следующий запрос:

{request.query}
"""
        
        if request.context:
            prompt += f"\n\nКонтекст: {request.context}"
        
        # Generate response
        response = model.generate_content(prompt)
        
        return AnalyzeResponse(
            status="completed",
            insights=response.text,
            agent_mode="simple",
            metadata={"model": "gemini-2.0-flash-exp"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

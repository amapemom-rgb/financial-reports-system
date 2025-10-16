"""Frontend Service с интеграцией AI агента"""
import os
import httpx
from fastapi import FastAPI
from datetime import datetime
from pydantic import BaseModel

app = FastAPI(title="Financial Reports - Frontend API")

LOGIC_AGENT_URL = os.getenv(
    "LOGIC_AGENT_URL",
    "https://logic-understanding-agent-eu66elwpia-uc.a.run.app"
)

class AnalysisRequest(BaseModel):
    query: str
    file_path: str = "gs://bucket/sample-report.xlsx"

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "frontend-service",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/")
async def root():
    return {
        "service": "Financial Reports Analysis",
        "version": "1.0.0",
        "status": "running",
        "ai_agent": "connected"
    }

@app.post("/analyze")
async def analyze_report(request: AnalysisRequest):
    """Отправляет запрос AI агенту для анализа отчета"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{LOGIC_AGENT_URL}/analyze",
                params={"file_path": request.file_path, "query": request.query}
            )
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "query": request.query,
                    "ai_response": response.json()
                }
            else:
                return {"status": "error", "error": f"Agent returned {response.status_code}"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

#!/bin/bash
echo "🤖 Создание Google AI Агентов..."
echo ""

# Создаём простую версию агента для начала
cat > agents/logic-understanding-agent/main.py << 'AGENTCODE'
"""Google Vertex AI Agent - Financial Analyst"""
import os
from fastapi import FastAPI
from vertexai.generative_models import GenerativeModel
import vertexai

app = FastAPI(title="Logic Understanding Agent")

# Инициализация
PROJECT_ID = os.getenv("PROJECT_ID", "financial-reports-ai-2024")
LOCATION = os.getenv("REGION", "us-central1")
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Создаём агента
model = GenerativeModel(
    "gemini-2.0-flash-exp",
    system_instruction="""
    Ты автономный финансовый аналитик агент.
    Анализируй отчеты, планируй действия, принимай решения.
    """
)

@app.get("/health")
async def health():
    return {"status": "healthy", "agent": "logic-understanding"}

@app.post("/analyze")
async def analyze_report(file_path: str, query: str):
    """Агент анализирует отчет"""
    
    prompt = f"""
    Задача: {query}
    Файл: {file_path}
    
    Проанализируй автономно:
    1. Спланируй свои действия
    2. Определи что нужно сделать
    3. Дай рекомендации
    """
    
    response = model.generate_content(prompt)
    
    return {
        "status": "analyzed",
        "insights": response.text
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
AGENTCODE

# Requirements
cat > agents/logic-understanding-agent/requirements.txt << 'REQS'
fastapi==0.109.0
uvicorn[standard]==0.27.0
google-cloud-aiplatform==1.60.0
REQS

# Dockerfile
cat > agents/logic-understanding-agent/Dockerfile << 'DOCKER'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
DOCKER

echo "✅ Logic Understanding Agent создан"
echo ""
echo "🚀 Готово к деплою!"

#!/usr/bin/env python3
"""
Web UI для Financial Reports Analysis System
Запускается в Cloud Run и предоставляет браузерный интерфейс
"""

import os
import json
import subprocess
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# URLs сервисов
SERVICES = {
    "frontend": "https://frontend-service-38390150695.us-central1.run.app",
    "orchestrator": "https://orchestrator-agent-38390150695.us-central1.run.app",
    "reader": "https://report-reader-agent-38390150695.us-central1.run.app",
    "logic": "https://logic-understanding-agent-38390150695.us-central1.run.app",
    "visualization": "https://visualization-agent-38390150695.us-central1.run.app",
}


@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html', services=SERVICES)


@app.route('/api/health')
def api_health():
    """Health check самого web-ui"""
    return jsonify({
        "status": "healthy",
        "service": "web-ui",
        "version": "1.0.0-rc1"
    })


@app.route('/api/services/health', methods=['GET'])
def check_services_health():
    """Проверка здоровья всех микросервисов"""
    import requests
    
    # Получаем токен (в Cloud Run это будет metadata сервер)
    try:
        # В Cloud Run используем metadata сервер
        metadata_server = "http://metadata.google.internal/computeMetadata/v1"
        token_url = f"{metadata_server}/instance/service-accounts/default/token"
        headers = {"Metadata-Flavor": "Google"}
        
        response = requests.get(token_url, headers=headers, timeout=5)
        if response.status_code == 200:
            token = response.json().get('access_token')
        else:
            # Fallback для локального тестирования
            token = subprocess.check_output(
                ["gcloud", "auth", "print-identity-token"],
                text=True
            ).strip()
    except Exception as e:
        return jsonify({
            "error": "Failed to get authentication token",
            "details": str(e)
        }), 500
    
    results = {}
    
    for name, url in SERVICES.items():
        try:
            resp = requests.get(
                f"{url}/health",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            
            if resp.status_code == 200:
                data = resp.json()
                results[name] = {
                    "status": "healthy" if data.get("status") == "healthy" else "unhealthy",
                    "http_code": resp.status_code,
                    "response": data
                }
            else:
                results[name] = {
                    "status": "unhealthy",
                    "http_code": resp.status_code,
                    "error": resp.text
                }
        except requests.exceptions.Timeout:
            results[name] = {
                "status": "timeout",
                "error": "Request timed out"
            }
        except Exception as e:
            results[name] = {
                "status": "error",
                "error": str(e)
            }
    
    return jsonify(results)


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Загрузка файла"""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400
    
    # Здесь будет логика загрузки через Frontend service
    # TODO: Implement file upload to frontend service
    
    return jsonify({
        "message": "File upload endpoint - to be implemented",
        "filename": file.filename
    })


@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Создание задачи анализа"""
    data = request.json
    
    # TODO: Implement task creation via Orchestrator
    
    return jsonify({
        "message": "Task creation endpoint - to be implemented",
        "data": data
    })


@app.route('/docs/<path:doc_path>')
def serve_docs(doc_path):
    """Отдача документации"""
    try:
        with open(f'/app/{doc_path}', 'r', encoding='utf-8') as f:
            content = f.read()
        return content, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    except FileNotFoundError:
        return "Document not found", 404


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)

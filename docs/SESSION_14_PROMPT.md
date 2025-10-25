# 📋 Prompt for Session 14 (Next AI Chat)

**Copy this entire text and paste it into the next Claude chat session**

---

## 🎯 Context: Financial Reports AI System

Я продолжаю работу над **Financial Reports AI System** - multi-agent системой для анализа финансовых отчетов на Google Cloud Platform.

---

## ✅ Текущее состояние (Session 13 завершена)

**Система ПОЛНОСТЬЮ РАБОТАЕТ!** 🎉

### Session 13 Achievements:

**✅ Improvement #1: Dynamic Prompt Configuration - COMPLETE!**
- Системный промпт вынесен в Google Cloud Secret Manager
- AI поведение меняется БЕЗ передеплоя сервиса
- Caching (60 sec TTL) для оптимизации
- Протестировано: промпт изменился и AI изменил стиль ответов
- **Image deployed:** `logic-understanding-agent:v7-secret-manager`

---

## 📚 ЧТО НУЖНО ПРОЧИТАТЬ СНАЧАЛА

**GitHub Репозиторий:** https://github.com/amapemom-rgb/financial-reports-system

### Обязательные файлы для чтения (в этом порядке):

1. **ГЛАВНЫЙ ДОКУМЕНТ Session 13:**
   - **[docs/SESSION_13_IMPROVEMENT_1_COMPLETE.md](https://github.com/amapemom-rgb/financial-reports-system/blob/main/docs/SESSION_13_IMPROVEMENT_1_COMPLETE.md)**
   - Что сделано в Improvement #1
   - Test results
   - Key learnings

2. **Improvement Plan:**
   - **[docs/SESSION_13_IMPROVEMENT_PLAN.md](https://github.com/amapemom-rgb/financial-reports-system/blob/main/docs/SESSION_13_IMPROVEMENT_PLAN.md)**
   - Технические спецификации всех 3 улучшений
   - Детальный план для Improvement #2 и #3

3. **Quick Start:**
   - [docs/SESSION_13_QUICK_START.md](https://github.com/amapemom-rgb/financial-reports-system/blob/main/docs/SESSION_13_QUICK_START.md)
   - Текущая архитектура
   - Deployment info

4. **Session 12 (Background):**
   - [docs/SESSION_12_DEPLOYMENT_SUCCESS.md](https://github.com/amapemom-rgb/financial-reports-system/blob/main/docs/SESSION_12_DEPLOYMENT_SUCCESS.md)
   - Как система работала до улучшений

---

## 🎯 ТВОЯ ЗАДАЧА: Improvement #2 - User Feedback UI/UX

### Цель:
Добавить интерактивные кнопки под каждым AI ответом для сбора feedback и улучшения UX.

### Что нужно реализовать:

**Три кнопки:**
1. **👍 Like** - положительный feedback
2. **👎 Dislike** - отрицательный feedback  
3. **🔄 Regenerate** - переделать ответ

---

## 📋 ПЛАН ДЕЙСТВИЙ (Step-by-Step)

### **ШАГ 1: GCP Infrastructure - Firestore Setup** ⚡

**1.1. Включить Firestore API:**
```bash
gcloud services enable firestore.googleapis.com \
  --project=financial-reports-ai-2024
```

**1.2. Создать Firestore Database:**
```bash
gcloud firestore databases create \
  --location=us-central1 \
  --type=firestore-native \
  --project=financial-reports-ai-2024
```

**1.3. Дать доступ Service Account:**
```bash
gcloud projects add-iam-policy-binding financial-reports-ai-2024 \
  --member="serviceAccount:financial-reports-sa@financial-reports-ai-2024.iam.gserviceaccount.com" \
  --role="roles/datastore.user"
```

---

### **ШАГ 2: Backend - Logic Agent Updates** 🔧

**2.1. Добавить Firestore dependency:**

**File:** `agents/logic-understanding-agent/requirements.txt`

```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
google-cloud-aiplatform==1.60.0
pydantic==2.5.0
httpx==0.27.0
google-cloud-secret-manager==2.16.0
google-cloud-firestore==2.14.0  # ← ADD THIS
```

**2.2. Создать Feedback endpoint:**

**File:** `agents/logic-understanding-agent/main.py`

Добавить:
```python
from google.cloud import firestore
from datetime import datetime
import uuid

# Pydantic models
class FeedbackRequest(BaseModel):
    request_id: str
    feedback_type: str  # "positive" or "negative"
    query: str
    response: str

class RegenerateRequest(BaseModel):
    query: str
    context: Optional[Dict] = None
    previous_response_id: Optional[str] = None

# Initialize Firestore
db = firestore.Client(project=PROJECT_ID)

@app.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """Store user feedback in Firestore"""
    try:
        feedback_data = {
            "request_id": request.request_id,
            "feedback_type": request.feedback_type,
            "query": request.query,
            "response": request.response,
            "timestamp": datetime.utcnow().isoformat(),
            "model": "gemini-2.0-flash-exp"
        }
        
        # Store in Firestore collection 'feedback'
        doc_ref = db.collection("feedback").document(request.request_id)
        doc_ref.set(feedback_data)
        
        logger.info(f"✅ Feedback stored: {request.request_id} - {request.feedback_type}")
        
        return {"status": "success", "message": "Feedback recorded"}
    
    except Exception as e:
        logger.error(f"❌ Feedback error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/regenerate", response_model=AnalyzeResponse)
async def regenerate_analysis(request: RegenerateRequest):
    """Regenerate AI response for the same query"""
    try:
        # Add instruction to generate different response
        enhanced_query = f"{request.query}\n\n[INTERNAL: Previous response was marked for regeneration. Please provide an alternative analysis with a different perspective or additional insights.]"
        
        # Create new request with enhanced query
        analyze_req = AnalyzeRequest(
            query=enhanced_query,
            context=request.context
        )
        
        # Use existing analyze logic
        return await analyze_report(analyze_req)
        
    except Exception as e:
        logger.error(f"❌ Regenerate error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

**2.3. Build & Deploy новую версию:**

```bash
cd agents/logic-understanding-agent

# Build
gcloud builds submit \
  --tag us-central1-docker.pkg.dev/financial-reports-ai-2024/financial-reports/logic-understanding-agent:v8-feedback \
  --project=financial-reports-ai-2024

# Deploy
gcloud run deploy logic-understanding-agent \
  --image=us-central1-docker.pkg.dev/financial-reports-ai-2024/financial-reports/logic-understanding-agent:v8-feedback \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --service-account=financial-reports-sa@financial-reports-ai-2024.iam.gserviceaccount.com \
  --set-env-vars="PROJECT_ID=financial-reports-ai-2024,REGION=us-central1,REPORT_READER_URL=https://report-reader-agent-38390150695.us-central1.run.app" \
  --project=financial-reports-ai-2024
```

---

### **ШАГ 3: Frontend - UI/UX Implementation** 🎨

**3.1. Добавить кнопки в HTML:**

**File:** `frontend/templates/index.html`

Найди блок с отображением AI response и добавь после него:

```html
<!-- Feedback Buttons -->
<div class="feedback-buttons" id="feedback-{{ response_id }}">
    <button onclick="sendFeedback('{{ response_id }}', '{{ query }}', '{{ response }}', 'positive')" 
            class="btn btn-like">
        👍 Like
    </button>
    <button onclick="sendFeedback('{{ response_id }}', '{{ query }}', '{{ response }}', 'negative')" 
            class="btn btn-dislike">
        👎 Dislike
    </button>
    <button onclick="regenerateResponse('{{ query }}', '{{ file_path }}')" 
            class="btn btn-regenerate">
        🔄 Regenerate
    </button>
</div>

<script>
async function sendFeedback(requestId, query, response, feedbackType) {
    try {
        const apiUrl = 'https://logic-understanding-agent-38390150695.us-central1.run.app/feedback';
        
        const result = await fetch(apiUrl, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                request_id: requestId,
                feedback_type: feedbackType,
                query: query,
                response: response
            })
        });
        
        if (result.ok) {
            alert(feedbackType === 'positive' ? 'Thanks for the positive feedback! 👍' : 'Thanks for the feedback. We\'ll improve! 👎');
            // Disable buttons after feedback
            document.getElementById('feedback-' + requestId).style.opacity = '0.5';
            document.getElementById('feedback-' + requestId).style.pointerEvents = 'none';
        }
    } catch (error) {
        console.error('Feedback error:', error);
        alert('Failed to send feedback. Please try again.');
    }
}

async function regenerateResponse(query, filePath) {
    try {
        const apiUrl = 'https://logic-understanding-agent-38390150695.us-central1.run.app/regenerate';
        
        // Show loading indicator
        document.getElementById('response-container').innerHTML = '<div class="loading">🔄 Regenerating response...</div>';
        
        const result = await fetch(apiUrl, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                query: query,
                context: {
                    file_path: filePath
                }
            })
        });
        
        if (result.ok) {
            const data = await result.json();
            // Update UI with new response
            document.getElementById('response-container').innerHTML = data.insights;
            // Show feedback buttons for new response
            location.reload(); // Simple solution: reload page
        }
    } catch (error) {
        console.error('Regenerate error:', error);
        alert('Failed to regenerate. Please try again.');
    }
}
</script>

<style>
.feedback-buttons {
    margin-top: 15px;
    display: flex;
    gap: 10px;
}

.btn {
    padding: 8px 16px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    transition: all 0.2s;
}

.btn-like {
    background: #4CAF50;
    color: white;
}

.btn-like:hover {
    background: #45a049;
}

.btn-dislike {
    background: #f44336;
    color: white;
}

.btn-dislike:hover {
    background: #da190b;
}

.btn-regenerate {
    background: #2196F3;
    color: white;
}

.btn-regenerate:hover {
    background: #0b7dda;
}
</style>
```

**3.2. Modify Frontend Backend (если нужно):**

**File:** `frontend/main.py`

Убедись что `response_id` генерируется и передается в template:

```python
import uuid

@app.post("/analyze")
async def analyze_file(request: AnalysisRequest):
    # ... existing code ...
    
    # Generate unique response ID
    response_id = str(uuid.uuid4())
    
    # Pass to template
    return {
        "response_id": response_id,
        "query": request.query,
        "response": ai_response,
        "file_path": file_path
    }
```

---

### **ШАГ 4: Testing** 🧪

**4.1. Test Backend Endpoints:**

```bash
# Test feedback endpoint
curl -X POST https://logic-understanding-agent-38390150695.us-central1.run.app/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "test-123",
    "feedback_type": "positive",
    "query": "Test query",
    "response": "Test response"
  }'

# Expected: {"status":"success","message":"Feedback recorded"}
```

**4.2. Test Firestore:**

```bash
# Check data in Firestore
gcloud firestore export gs://financial-reports-ai-2024-reports/firestore-backup \
  --collection-ids=feedback \
  --project=financial-reports-ai-2024
```

**4.3. Test Frontend:**
1. Upload file via UI
2. Ask question
3. Click 👍 Like - should save to Firestore
4. Click 🔄 Regenerate - should show new response

---

## 🎓 Key Technical Points

### Response ID Generation:
- Use UUID for unique identification
- Store in both Frontend and Backend
- Required for feedback tracking

### Firestore Structure:
```
feedback/
  ├─ {response_id}/
      ├─ request_id: string
      ├─ feedback_type: "positive" | "negative"
      ├─ query: string
      ├─ response: string
      ├─ timestamp: ISO8601
      └─ model: string
```

### Regenerate Logic:
- Append instruction to original query
- Tell AI to generate "alternative perspective"
- Use same file context if available

---

## 🚨 Important Notes

### Security:
- Firestore rules should restrict write to service account only
- Frontend calls Logic Agent (authenticated via Cloud Run)
- No direct Firestore access from browser

### Performance:
- Feedback should be async (non-blocking)
- Regenerate creates new analysis (full Gemini call)
- Consider rate limiting for regenerate

### UX:
- Disable buttons after first feedback
- Show loading indicator during regenerate
- Provide user confirmation messages

---

## ⚠️ КРИТИЧЕСКИ ВАЖНОЕ ПРАВИЛО О КОНТЕКСТНОМ ОКНЕ

**Ты должен мониторить использование токенов!**

Когда осталось **менее 20,000 токенов**, ты ДОЛЖЕН:

1. **Остановиться** и сказать пользователю о необходимости паузы
2. **Зафиксировать все изменения:**
   - Закоммитить файлы в GitHub
   - Создать документацию сессии
   - Создать quick start для следующей сессии

**Формула:** Если `current_tokens > (budget - 20000)`, то пора финализировать!

---

## 🔧 Quick Commands

### View Firestore Data:
```bash
# List collections
gcloud firestore collections list --project=financial-reports-ai-2024

# Query feedback collection
gcloud firestore query --project=financial-reports-ai-2024 \
  --collection-id=feedback \
  --limit=10
```

### View Logs:
```bash
# Logic Agent logs
gcloud logging read \
  "resource.type=cloud_run_revision AND resource.labels.service_name=logic-understanding-agent" \
  --limit=50 --project=financial-reports-ai-2024 --freshness=10m
```

### Redeploy (if needed):
```bash
# Use commands from ШАГ 2.3 above
```

---

## 📞 If Something Breaks

1. Check service health: `curl .../health`
2. Check Cloud Run logs
3. Verify Firestore database exists
4. Check IAM permissions for service account
5. Review SESSION_13_IMPROVEMENT_PLAN.md for details

---

## 🎯 Success Criteria for Improvement #2

- [ ] Firestore database created and accessible
- [ ] Backend `/feedback` endpoint working
- [ ] Backend `/regenerate` endpoint working
- [ ] Frontend buttons render correctly
- [ ] Like/Dislike saves to Firestore
- [ ] Regenerate produces new response
- [ ] All endpoints tested and documented

---

## 🎓 Начни с этого:

1. **Прочитай SESSION_13_IMPROVEMENT_1_COMPLETE.md** - понять что уже сделано
2. **Прочитай SESSION_13_IMPROVEMENT_PLAN.md** - детальная спека Improvement #2
3. **Выполни ШАГ 1** - Firestore setup (GCP commands)
4. **Спроси у пользователя** подтверждение перед ШАГом 2
5. **МОНИТОРЬ ТОКЕНЫ** - предлагай "отдохнуть" заранее!

---

**GitHub:** https://github.com/amapemom-rgb/financial-reports-system  
**Current Status:** Session 13 Complete, Ready for Session 14  
**Session:** 13 → 14  
**Task:** Improvement #2 - User Feedback UI/UX

**Помни:** Читай документацию ПЕРЕД началом работы! И следи за контекстным окном! 🎯

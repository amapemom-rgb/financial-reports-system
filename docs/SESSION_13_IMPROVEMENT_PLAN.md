# 📋 Session 13: Improvement Plan (Supervisor Request)

**Date:** October 24, 2025  
**Status:** 📝 **PLANNING PHASE**  
**Source:** Supervisor Request  
**Current System:** ✅ Fully Operational (Session 12)

---

## 🎯 Overview

Three major improvements requested:

1. **Dynamic Prompt Configuration** - Move system prompt to Secret Manager
2. **User Feedback UI/UX** - Add "Regenerate" and "Like/Dislike" buttons
3. **Multi-Sheet Intelligence** - Handle Excel files with 30+ sheets using metadata

---

## 📊 Improvement #1: Dynamic Prompt Configuration

### Goal
Extract system prompt from `logic-understanding-agent` code into Google Cloud Secret Manager for easy updates without redeployment.

### Benefits
- ✅ Update AI behavior without code changes
- ✅ Quick A/B testing of prompts
- ✅ Version control for prompts
- ✅ No service downtime

### Technical Implementation

#### Step 1.1: Create Secret in Secret Manager

```bash
# Create secret with initial prompt
gcloud secrets create GEMINI_SYSTEM_PROMPT \
  --replication-policy="automatic" \
  --project=financial-reports-ai-2024

# Add prompt content (version 1)
echo "You are a professional financial analyst..." | \
gcloud secrets versions add GEMINI_SYSTEM_PROMPT \
  --data-file=- \
  --project=financial-reports-ai-2024
```

#### Step 1.2: Grant Access to Service Account

```bash
# Allow logic-understanding-agent to read the secret
gcloud secrets add-iam-policy-binding GEMINI_SYSTEM_PROMPT \
  --member="serviceAccount:financial-reports-sa@financial-reports-ai-2024.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --project=financial-reports-ai-2024
```

#### Step 1.3: Modify Logic Agent Code

**File:** `agents/logic-understanding-agent/main.py`

```python
from google.cloud import secretmanager

def get_system_prompt() -> str:
    """Load system prompt from Secret Manager"""
    client = secretmanager.SecretManagerServiceClient()
    project_id = os.getenv("PROJECT_ID")
    secret_name = f"projects/{project_id}/secrets/GEMINI_SYSTEM_PROMPT/versions/latest"
    
    try:
        response = client.access_secret_version(request={"name": secret_name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        logger.warning(f"Failed to load secret, using default: {e}")
        return DEFAULT_SYSTEM_PROMPT  # Fallback

# Use in analyze endpoint
system_prompt = get_system_prompt()
```

#### Step 1.4: Update Dependencies

**File:** `agents/logic-understanding-agent/requirements.txt`

```txt
google-cloud-secret-manager==2.16.0  # NEW
```

#### Step 1.5: Cloud Run Configuration

**Option A:** Mount as environment variable (recommended)
```bash
gcloud run services update logic-understanding-agent \
  --update-secrets=GEMINI_SYSTEM_PROMPT=GEMINI_SYSTEM_PROMPT:latest \
  --region=us-central1 \
  --project=financial-reports-ai-2024
```

**Option B:** Read directly in code (already implemented in Step 1.3)

### Testing
1. Deploy updated agent
2. Change secret value in Secret Manager
3. Verify agent uses new prompt without redeployment

---

## 📊 Improvement #2: User Feedback UI/UX

### Goal
Add interactive buttons for user feedback and response regeneration.

### Features
- ✅ "Regenerate" button - re-run analysis with same input
- ✅ "👍 Like" button - positive feedback
- ✅ "👎 Dislike" button - negative feedback
- ✅ Store feedback for quality improvement

### Technical Implementation

#### Step 2.1: Frontend UI Changes

**File:** `frontend/templates/index.html`

```html
<!-- Add after response display -->
<div class="response-actions">
  <button onclick="regenerateResponse('{{ request_id }}')" class="btn-regenerate">
    🔄 Regenerate
  </button>
  <button onclick="sendFeedback('{{ request_id }}', 'positive')" class="btn-like">
    👍 Like
  </button>
  <button onclick="sendFeedback('{{ request_id }}', 'negative')" class="btn-dislike">
    👎 Dislike
  </button>
</div>

<script>
async function regenerateResponse(requestId) {
  const response = await fetch('/api/regenerate', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({request_id: requestId})
  });
  // Update UI with new response
}

async function sendFeedback(requestId, type) {
  await fetch('/api/feedback', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      request_id: requestId,
      feedback_type: type
    })
  });
  // Show success message
}
</script>
```

#### Step 2.2: Frontend Backend API

**File:** `frontend/main.py`

```python
from pydantic import BaseModel

class RegenerateRequest(BaseModel):
    request_id: str

class FeedbackRequest(BaseModel):
    request_id: str
    feedback_type: str  # "positive" or "negative"

@app.post("/api/regenerate")
async def regenerate_analysis(request: RegenerateRequest):
    """Re-run analysis with original parameters"""
    # Retrieve original request from cache/database
    original_request = get_cached_request(request.request_id)
    
    # Forward to Logic Agent
    response = await forward_to_logic_agent(original_request)
    return response

@app.post("/api/feedback")
async def submit_feedback(request: FeedbackRequest):
    """Store user feedback"""
    # Forward to Logic Agent for Gemini feedback API
    await forward_feedback_to_logic(request)
    return {"status": "success"}
```

#### Step 2.3: Logic Agent Enhancement

**File:** `agents/logic-understanding-agent/main.py`

```python
from pydantic import BaseModel
from typing import Literal

class FeedbackRequest(BaseModel):
    request_id: str
    feedback_type: Literal["positive", "negative"]
    original_prompt: str
    ai_response: str

@app.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """Send feedback to Gemini API"""
    try:
        # Use Gemini's feedback API (if available)
        # Or store in Firestore for analysis
        feedback_data = {
            "request_id": request.request_id,
            "type": request.feedback_type,
            "timestamp": datetime.utcnow().isoformat(),
            "prompt": request.original_prompt,
            "response": request.ai_response
        }
        
        # Store in Firestore
        db = firestore.Client(project=PROJECT_ID)
        db.collection("feedback").add(feedback_data)
        
        logger.info(f"Feedback stored: {request.request_id} - {request.feedback_type}")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Feedback error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

#### Step 2.4: Add Firestore Dependency

**File:** `agents/logic-understanding-agent/requirements.txt`

```txt
google-cloud-firestore==2.14.0  # NEW
```

#### Step 2.5: Enable Firestore

```bash
# Enable Firestore API
gcloud services enable firestore.googleapis.com \
  --project=financial-reports-ai-2024

# Create Firestore database (if not exists)
gcloud firestore databases create \
  --region=us-central1 \
  --project=financial-reports-ai-2024
```

### Testing
1. Click "Regenerate" - should show new analysis
2. Click "👍" - should store positive feedback
3. Click "👎" - should store negative feedback
4. Check Firestore for stored feedback

---

## 📊 Improvement #3: Multi-Sheet Intelligence (30+ Sheets)

### Goal
Handle Excel files with many sheets by creating metadata structure and interactive dialogue.

### Challenge
- Excel files with 30+ sheets too large for context
- Need intelligent sheet selection
- Progressive disclosure of data

### Solution: Metadata-First Approach

#### Step 3.1: Report Reader Enhancement

**File:** `agents/report-reader-agent/main.py`

```python
from pydantic import BaseModel
from typing import Dict, List, Optional

class SheetMetadata(BaseModel):
    rows: int
    columns: List[str]
    sample_data: List[Dict]  # First 1-2 rows
    data_types: Dict[str, str]  # Column -> dtype

class FileMetadata(BaseModel):
    sheets_count: int
    sheet_names: List[str]
    file_size_bytes: int
    preliminary_summary: Dict[str, SheetMetadata]

@app.post("/analyze/metadata")
async def get_file_metadata(request: ReadStorageRequest) -> FileMetadata:
    """Generate metadata for all sheets without loading full data"""
    
    try:
        # Download from Cloud Storage
        bucket = storage_client.bucket(REPORTS_BUCKET)
        blob = bucket.blob(request.file_path)
        file_bytes = blob.download_as_bytes()
        
        # Read all sheets (names only first)
        all_sheets = pd.read_excel(
            BytesIO(file_bytes),
            sheet_name=None,  # Load all sheets
            nrows=2  # Only first 2 rows for metadata
        )
        
        metadata = FileMetadata(
            sheets_count=len(all_sheets),
            sheet_names=list(all_sheets.keys()),
            file_size_bytes=len(file_bytes),
            preliminary_summary={}
        )
        
        # Generate summary for top 5 largest sheets
        sorted_sheets = sorted(
            all_sheets.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:5]
        
        for sheet_name, df in sorted_sheets:
            metadata.preliminary_summary[sheet_name] = SheetMetadata(
                rows=len(df),
                columns=list(df.columns),
                sample_data=df.head(1).to_dict(orient='records'),
                data_types={col: str(dtype) for col, dtype in df.dtypes.items()}
            )
        
        return metadata
        
    except Exception as e:
        logger.error(f"Metadata generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/read/sheet")
async def read_specific_sheet(
    request: ReadStorageRequest,
    sheet_name: str
) -> dict:
    """Read specific sheet by name"""
    # Same as current read_from_cloud_storage but with sheet_name parameter
    pass
```

#### Step 3.2: Logic Agent - Super Prompt

**File:** `agents/logic-understanding-agent/prompts.py` (NEW)

```python
def build_super_prompt(metadata: FileMetadata, user_query: str) -> str:
    """Build intelligent prompt for multi-sheet analysis"""
    
    return f"""
[ИНСТРУКЦИЯ ДЛЯ АНАЛИТИКА GEMINI]

Ты — AI-ассистент "Финансовый Эксперт". Твой тон — дружелюбный и строго профессиональный.

[РОЛЬ]
Твоя задача — интерактивный анализ. Не пытайся ответить сразу. Сначала собери контекст, используя предоставленную тобой мета-структуру отчета.

[КОНТЕКСТ ДАННЫХ]
Пользователь загрузил Excel-файл. Полные данные доступны по требованию, но вот его **МЕТА-СТРУКТУРА**:

Количество листов: {metadata.sheets_count}
Названия листов: {", ".join(metadata.sheet_names)}
Размер файла: {metadata.file_size_bytes / 1024:.1f} KB

Предварительное резюме топ-5 листов:
{format_preliminary_summary(metadata.preliminary_summary)}

[ВОПРОС ПОЛЬЗОВАТЕЛЯ]
"{user_query}"

[СТРУКТУРА ОТВЕТА (Обязательно)]
Ответ должен состоять из двух разделов:

1. **РЕЗЮМЕ ОТЧЕТА:** Обязательно укажи общее количество листов ({metadata.sheets_count}) и перечисли их названия.

2. **ГЛАВНЫЙ ВОПРОС:** Задай ОДИН четкий вопрос пользователю, чтобы он выбрал, какой лист (или какие данные) ему нужно анализировать в первую очередь.

[ОГРАНИЧЕНИЯ]
* НЕ используй звездочки или решетки для форматирования.
* Будь краток.
* Пример вопроса: "В отчете {metadata.sheets_count} листов: {', '.join(metadata.sheet_names[:3])}... Какой из них (например, 'Продажи' или 'Расходы') вы хотите проанализировать первым?"

[СЛЕДУЮЩИЙ ШАГ]
После выбора пользователем конкретного листа, система загрузит полные данные этого листа для детального анализа.
"""

def format_preliminary_summary(summary: Dict[str, SheetMetadata]) -> str:
    """Format metadata summary for prompt"""
    lines = []
    for sheet_name, meta in summary.items():
        lines.append(f"- '{sheet_name}': {meta.rows} строк, {len(meta.columns)} колонок")
        lines.append(f"  Колонки: {', '.join(meta.columns[:5])}...")
    return "\n".join(lines)
```

#### Step 3.3: Logic Agent Flow

**File:** `agents/logic-understanding-agent/main.py`

```python
from .prompts import build_super_prompt

@app.post("/analyze")
async def analyze_report(request: AnalysisRequest):
    """Enhanced analysis with metadata-first approach"""
    
    file_path = request.context.get("file_path")
    
    try:
        # Step 1: Get metadata first (NEW)
        metadata_url = f"{REPORT_READER_URL}/analyze/metadata"
        metadata_response = await http_client.post(
            metadata_url,
            json={"request": {"file_path": file_path}}
        )
        metadata = FileMetadata(**metadata_response.json())
        
        # Step 2: Build super prompt
        system_prompt = build_super_prompt(metadata, request.query)
        
        # Step 3: Ask Gemini for interactive question
        model = GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(system_prompt)
        
        return {
            "status": "success",
            "response": response.text,
            "metadata": metadata.dict(),
            "next_action": "select_sheet"  # Signal to frontend
        }
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/sheet")
async def analyze_specific_sheet(
    file_path: str,
    sheet_name: str,
    user_query: str
):
    """Analyze specific sheet after user selection"""
    
    # Load full sheet data
    reader_url = f"{REPORT_READER_URL}/read/sheet"
    sheet_response = await http_client.post(
        reader_url,
        json={
            "request": {"file_path": file_path},
            "sheet_name": sheet_name
        }
    )
    
    # Full analysis with complete data
    # ... existing logic ...
```

### Testing
1. Upload Excel with 30 sheets
2. System shows summary and asks which sheet to analyze
3. User selects sheet name
4. System loads and analyzes only that sheet

---

## 🗂️ File Changes Summary

### New Files
```
docs/SESSION_13_IMPROVEMENT_PLAN.md           (this file)
agents/logic-understanding-agent/prompts.py   (prompt templates)
```

### Modified Files
```
agents/logic-understanding-agent/main.py      (Secret Manager, feedback, metadata)
agents/logic-understanding-agent/requirements.txt  (new dependencies)
agents/report-reader-agent/main.py            (metadata endpoint, sheet selection)
frontend/main.py                              (regenerate, feedback APIs)
frontend/templates/index.html                 (UI buttons)
```

### New GCP Resources
```
Secret Manager: GEMINI_SYSTEM_PROMPT
Firestore: feedback collection
```

---

## 📝 Implementation Order (Recommended)

### Phase 1: Quick Wins (1-2 hours)
1. ✅ Improvement #1 - Dynamic Prompt Configuration
   - Low risk, high value
   - No UI changes needed
   - Easy to test

### Phase 2: User Experience (2-3 hours)
2. ✅ Improvement #2 - Feedback UI/UX
   - Moderate complexity
   - Requires frontend + backend changes
   - Direct user value

### Phase 3: Advanced Feature (3-4 hours)
3. ✅ Improvement #3 - Multi-Sheet Intelligence
   - High complexity
   - Requires testing with real multi-sheet files
   - Significant architectural change

---

## 🧪 Testing Strategy

### Improvement #1 Testing
```bash
# 1. Create secret with test prompt
echo "Test prompt v1" | gcloud secrets versions add GEMINI_SYSTEM_PROMPT --data-file=-

# 2. Deploy agent
# 3. Analyze file - check logs for "Test prompt v1"
# 4. Update secret to "Test prompt v2"
echo "Test prompt v2" | gcloud secrets versions add GEMINI_SYSTEM_PROMPT --data-file=-

# 5. Wait 60 seconds (cache refresh)
# 6. Analyze file again - check logs for "Test prompt v2"
```

### Improvement #2 Testing
```bash
# 1. Upload file via UI
# 2. Click "Regenerate" - should show new response
# 3. Click "👍" - check Firestore console
# 4. Click "👎" - check Firestore console
```

### Improvement #3 Testing
```bash
# 1. Create Excel with 30 sheets (test data)
# 2. Upload via UI
# 3. Should show: "Found 30 sheets: Sheet1, Sheet2, ... Which to analyze?"
# 4. Reply: "Sheet5"
# 5. Should load and analyze only Sheet5
```

---

## 🎯 Success Criteria

### Improvement #1
- ✅ Prompt changes without redeployment
- ✅ No service downtime
- ✅ Fallback to default prompt if secret fails

### Improvement #2
- ✅ All buttons functional
- ✅ Feedback stored in Firestore
- ✅ Regenerate produces new response

### Improvement #3
- ✅ Handles 30+ sheets without errors
- ✅ Interactive sheet selection works
- ✅ Only selected sheet loaded (performance)
- ✅ Accurate metadata display

---

## 📊 Current Token Usage

**Tokens used:** ~32,000 / 190,000  
**Remaining:** ~158,000 tokens  
**Status:** ✅ Plenty of room

---

## 🚀 Next Steps

**Awaiting approval to proceed with:**
1. Phase selection (which improvement to implement first?)
2. Implementation timeline
3. Testing approach

**Ready to start immediately once approved!** 🎯

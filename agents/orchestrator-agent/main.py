"""Orchestrator Agent - Workflow Coordination & State Machine"""
import os
import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from google.cloud import pubsub_v1
import httpx

app = FastAPI(title="Orchestrator Agent")

# ==========================================
# Configuration
# ==========================================

PROJECT_ID = os.getenv("PROJECT_ID", "financial-reports-ai-2024")
REGION = os.getenv("REGION", "us-central1")

# Service URLs
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://frontend-service:8080")
REPORT_READER_URL = os.getenv("REPORT_READER_URL", "http://report-reader-agent:8081")
LOGIC_AGENT_URL = os.getenv("LOGIC_AGENT_URL", "http://logic-understanding-agent:8082")
VISUALIZATION_URL = os.getenv("VISUALIZATION_URL", "http://visualization-agent:8083")

# Pub/Sub
PUBSUB_TOPIC = os.getenv("PUBSUB_TOPIC", "task-queue-topic")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./orchestrator.db")

# Initialize Pub/Sub
try:
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(PROJECT_ID, PUBSUB_TOPIC)
    pubsub_available = True
except Exception as e:
    print(f"Warning: Pub/Sub not available: {e}")
    publisher = None
    pubsub_available = False

# Initialize Database
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==========================================
# State Machine
# ==========================================

class TaskStatus(str, Enum):
    PENDING = "pending"
    READING = "reading"
    ANALYZING = "analyzing"
    VISUALIZING = "visualizing"
    COMPLETED = "completed"
    FAILED = "failed"

class WorkflowType(str, Enum):
    ANALYZE_REPORT = "analyze_report"
    GENERATE_VISUALIZATION = "generate_visualization"
    VOICE_ANALYSIS = "voice_analysis"

# Workflow definitions
WORKFLOWS = {
    WorkflowType.ANALYZE_REPORT: [
        TaskStatus.READING,
        TaskStatus.ANALYZING,
        TaskStatus.VISUALIZING,
        TaskStatus.COMPLETED
    ],
    WorkflowType.GENERATE_VISUALIZATION: [
        TaskStatus.READING,
        TaskStatus.VISUALIZING,
        TaskStatus.COMPLETED
    ],
    WorkflowType.VOICE_ANALYSIS: [
        TaskStatus.ANALYZING,
        TaskStatus.COMPLETED
    ]
}

# ==========================================
# Database Models
# ==========================================

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(String, primary_key=True, index=True)
    workflow_type = Column(String, nullable=False)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING)
    input_data = Column(JSON)
    output_data = Column(JSON)
    current_step = Column(String)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# ==========================================
# Pydantic Models
# ==========================================

class CreateTaskRequest(BaseModel):
    workflow_type: WorkflowType
    input_data: Dict[str, Any]

class TaskResponse(BaseModel):
    task_id: str
    status: TaskStatus
    workflow_type: str
    current_step: Optional[str] = None
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

# ==========================================
# Database Functions
# ==========================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_task(db: Session, workflow_type: WorkflowType, input_data: Dict) -> Task:
    """Create new task"""
    task_id = f"task_{uuid.uuid4().hex[:12]}"
    task = Task(
        id=task_id,
        workflow_type=workflow_type.value,
        status=TaskStatus.PENDING,
        input_data=input_data,
        output_data={}
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def update_task_status(db: Session, task_id: str, status: TaskStatus,
                       output_data: Dict = None, error: str = None):
    """Update task status"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        task.status = status
        task.updated_at = datetime.utcnow()
        if output_data:
            task.output_data = output_data
        if error:
            task.error_message = error
        db.commit()
        db.refresh(task)
    return task

# ==========================================
# Agent Communication Functions
# ==========================================

async def call_report_reader(file_path: str = None, spreadsheet_id: str = None,
                             sheet_data: bytes = None) -> Dict:
    """Call Report Reader Agent"""
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            if spreadsheet_id:
                response = await client.post(
                    f"{REPORT_READER_URL}/read/sheets",
                    json={"spreadsheet_id": spreadsheet_id}
                )
            elif sheet_data:
                files = {"file": ("report.xlsx", sheet_data)}
                response = await client.post(
                    f"{REPORT_READER_URL}/upload/excel",
                    files=files
                )
            else:
                raise ValueError("Either file_path, spreadsheet_id, or sheet_data required")
            
            response.raise_for_status()
            return response.json()
    
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Report Reader failed: {str(e)}")

async def call_logic_agent(query: str, report_id: str = None, context: Dict = None) -> Dict:
    """Call Logic Understanding Agent"""
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{LOGIC_AGENT_URL}/analyze",
                json={
                    "query": query,
                    "report_id": report_id,
                    "context": context
                }
            )
            response.raise_for_status()
            return response.json()
    
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Logic Agent failed: {str(e)}")

async def call_visualization_agent(chart_type: str, data: Dict, title: str) -> Dict:
    """Call Visualization Agent"""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{VISUALIZATION_URL}/create",
                json={
                    "chart_type": chart_type,
                    "data": data,
                    "title": title,
                    "save_to_storage": True
                }
            )
            response.raise_for_status()
            return response.json()
    
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Visualization Agent failed: {str(e)}")

# ==========================================
# Workflow Execution
# ==========================================

async def execute_analyze_report_workflow(task_id: str, input_data: Dict, db: Session):
    """Execute full report analysis workflow"""
    try:
        # Step 1: Read Report
        update_task_status(db, task_id, TaskStatus.READING)
        
        report_data = await call_report_reader(
            file_path=input_data.get("file_path"),
            spreadsheet_id=input_data.get("spreadsheet_id")
        )
        
        # Step 2: Analyze with AI
        update_task_status(db, task_id, TaskStatus.ANALYZING)
        
        analysis = await call_logic_agent(
            query=input_data.get("query", "Проанализируй этот отчёт"),
            context={"report_data": report_data}
        )
        
        # Step 3: Create Visualization
        update_task_status(db, task_id, TaskStatus.VISUALIZING)
        
        # Extract data for visualization (example)
        if "data" in report_data and "data" in report_data["data"]:
            chart_data = {
                "labels": [str(i) for i in range(len(report_data["data"]["data"]))],
                "values": [row.get("value", 0) for row in report_data["data"]["data"][:10]]
            }
            
            visualization = await call_visualization_agent(
                chart_type="bar",
                data=chart_data,
                title=input_data.get("title", "Financial Report Analysis")
            )
        else:
            visualization = {"status": "skipped", "reason": "no data for visualization"}
        
        # Step 4: Complete
        output = {
            "report_data": report_data,
            "analysis": analysis,
            "visualization": visualization
        }
        
        update_task_status(db, task_id, TaskStatus.COMPLETED, output_data=output)
    
    except Exception as e:
        update_task_status(db, task_id, TaskStatus.FAILED, error=str(e))

async def execute_visualization_workflow(task_id: str, input_data: Dict, db: Session):
    """Execute visualization-only workflow"""
    try:
        # Step 1: Read Report
        update_task_status(db, task_id, TaskStatus.READING)
        
        report_data = await call_report_reader(
            file_path=input_data.get("file_path"),
            spreadsheet_id=input_data.get("spreadsheet_id")
        )
        
        # Step 2: Create Visualization
        update_task_status(db, task_id, TaskStatus.VISUALIZING)
        
        visualization = await call_visualization_agent(
            chart_type=input_data.get("chart_type", "bar"),
            data=input_data.get("data"),
            title=input_data.get("title", "Chart")
        )
        
        # Complete
        output = {
            "report_data": report_data,
            "visualization": visualization
        }
        
        update_task_status(db, task_id, TaskStatus.COMPLETED, output_data=output)
    
    except Exception as e:
        update_task_status(db, task_id, TaskStatus.FAILED, error=str(e))

async def execute_voice_analysis_workflow(task_id: str, input_data: Dict, db: Session):
    """Execute voice analysis workflow"""
    try:
        # Step 1: Analyze with AI
        update_task_status(db, task_id, TaskStatus.ANALYZING)
        
        analysis = await call_logic_agent(
            query=input_data.get("query"),
            report_id=input_data.get("report_id")
        )
        
        # Complete
        output = {"analysis": analysis}
        update_task_status(db, task_id, TaskStatus.COMPLETED, output_data=output)
    
    except Exception as e:
        update_task_status(db, task_id, TaskStatus.FAILED, error=str(e))

# Workflow executors mapping
WORKFLOW_EXECUTORS = {
    WorkflowType.ANALYZE_REPORT: execute_analyze_report_workflow,
    WorkflowType.GENERATE_VISUALIZATION: execute_visualization_workflow,
    WorkflowType.VOICE_ANALYSIS: execute_voice_analysis_workflow
}

# ==========================================
# API Endpoints
# ==========================================

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "agent": "orchestrator",
        "features": {
            "pubsub": pubsub_available,
            "workflows": list(WorkflowType)
        }
    }

@app.post("/tasks", response_model=TaskResponse)
async def create_task_endpoint(request: CreateTaskRequest, background_tasks: BackgroundTasks):
    """Create new task and start workflow"""
    db = next(get_db())
    
    try:
        # Create task
        task = create_task(db, request.workflow_type, request.input_data)
        
        # Execute workflow in background
        executor = WORKFLOW_EXECUTORS.get(request.workflow_type)
        if executor:
            background_tasks.add_task(executor, task.id, request.input_data, db)
        else:
            raise HTTPException(status_code=400, detail="Unknown workflow type")
        
        return TaskResponse(
            task_id=task.id,
            status=task.status,
            workflow_type=task.workflow_type,
            current_step=task.current_step,
            output_data=task.output_data,
            error_message=task.error_message,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    """Get task status"""
    db = next(get_db())
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskResponse(
        task_id=task.id,
        status=task.status,
        workflow_type=task.workflow_type,
        current_step=task.current_step,
        output_data=task.output_data,
        error_message=task.error_message,
        created_at=task.created_at,
        updated_at=task.updated_at
    )

@app.get("/workflows")
async def get_workflows():
    """Get available workflows and their steps"""
    return {
        "workflows": {
            workflow_type.value: {
                "name": workflow_type.value,
                "steps": [step.value for step in steps]
            }
            for workflow_type, steps in WORKFLOWS.items()
        }
    }

@app.get("/tasks")
async def list_tasks(status: Optional[TaskStatus] = None, limit: int = 50):
    """List all tasks"""
    db = next(get_db())
    
    query = db.query(Task)
    if status:
        query = query.filter(Task.status == status)
    
    tasks = query.order_by(Task.created_at.desc()).limit(limit).all()
    
    return {
        "total": len(tasks),
        "tasks": [
            TaskResponse(
                task_id=task.id,
                status=task.status,
                workflow_type=task.workflow_type,
                current_step=task.current_step,
                output_data=task.output_data,
                error_message=task.error_message,
                created_at=task.created_at,
                updated_at=task.updated_at
            )
            for task in tasks
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8084)

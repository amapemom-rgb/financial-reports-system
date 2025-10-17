"""Visualization Agent - Chart Generation with Plotly & Cloud Storage"""
import os
import io
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import plotly.graph_objects as go
import plotly.express as px
from google.cloud import storage

app = FastAPI(title="Visualization Agent")

# ==========================================
# Configuration
# ==========================================

PROJECT_ID = os.getenv("PROJECT_ID", "financial-reports-ai-2024")
BUCKET_NAME = os.getenv("STORAGE_BUCKET", f"{PROJECT_ID}-visualizations")
REGION = os.getenv("REGION", "us-central1")

# Initialize Google Cloud Storage
try:
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    storage_available = True
except Exception as e:
    print(f"Warning: Cloud Storage not available: {e}")
    storage_client = None
    bucket = None
    storage_available = False

# ==========================================
# Data Models
# ==========================================

class ChartData(BaseModel):
    labels: List[str]
    values: List[float]
    series_name: Optional[str] = "Data"

class MultiSeriesData(BaseModel):
    labels: List[str]
    series: Dict[str, List[float]]

class CreateChartRequest(BaseModel):
    chart_type: str  # line, bar, pie, scatter, area
    data: Dict[str, Any]
    title: str
    x_label: Optional[str] = None
    y_label: Optional[str] = None
    save_to_storage: bool = True

class ChartResponse(BaseModel):
    status: str
    chart_id: str
    chart_url: Optional[str] = None
    public_url: Optional[str] = None
    html: Optional[str] = None

# ==========================================
# Chart Generation Functions
# ==========================================

def create_line_chart(data: Dict[str, Any], title: str, 
                     x_label: str = None, y_label: str = None) -> go.Figure:
    """Create line chart"""
    fig = go.Figure()
    
    if "series" in data:
        # Multiple series
        for series_name, values in data["series"].items():
            fig.add_trace(go.Scatter(
                x=data["labels"],
                y=values,
                mode='lines+markers',
                name=series_name
            ))
    else:
        # Single series
        fig.add_trace(go.Scatter(
            x=data["labels"],
            y=data["values"],
            mode='lines+markers',
            name=data.get("series_name", "Data")
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title=x_label or "Period",
        yaxis_title=y_label or "Value",
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig

def create_bar_chart(data: Dict[str, Any], title: str,
                    x_label: str = None, y_label: str = None) -> go.Figure:
    """Create bar chart"""
    fig = go.Figure()
    
    if "series" in data:
        # Multiple series (grouped bars)
        for series_name, values in data["series"].items():
            fig.add_trace(go.Bar(
                x=data["labels"],
                y=values,
                name=series_name
            ))
    else:
        # Single series
        fig.add_trace(go.Bar(
            x=data["labels"],
            y=data["values"],
            name=data.get("series_name", "Data")
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title=x_label or "Category",
        yaxis_title=y_label or "Value",
        barmode='group',
        template='plotly_white'
    )
    
    return fig

def create_pie_chart(data: Dict[str, Any], title: str) -> go.Figure:
    """Create pie chart"""
    fig = go.Figure(data=[go.Pie(
        labels=data["labels"],
        values=data["values"],
        hole=0.3  # Donut chart
    )])
    
    fig.update_layout(
        title=title,
        template='plotly_white'
    )
    
    return fig

def create_scatter_chart(data: Dict[str, Any], title: str,
                        x_label: str = None, y_label: str = None) -> go.Figure:
    """Create scatter plot"""
    fig = go.Figure()
    
    if "series" in data:
        for series_name, values in data["series"].items():
            fig.add_trace(go.Scatter(
                x=data["labels"],
                y=values,
                mode='markers',
                name=series_name,
                marker=dict(size=10)
            ))
    else:
        fig.add_trace(go.Scatter(
            x=data["labels"],
            y=data["values"],
            mode='markers',
            name=data.get("series_name", "Data"),
            marker=dict(size=10)
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title=x_label or "X Axis",
        yaxis_title=y_label or "Y Axis",
        template='plotly_white'
    )
    
    return fig

def create_area_chart(data: Dict[str, Any], title: str,
                     x_label: str = None, y_label: str = None) -> go.Figure:
    """Create area chart"""
    fig = go.Figure()
    
    if "series" in data:
        for series_name, values in data["series"].items():
            fig.add_trace(go.Scatter(
                x=data["labels"],
                y=values,
                mode='lines',
                name=series_name,
                fill='tonexty'
            ))
    else:
        fig.add_trace(go.Scatter(
            x=data["labels"],
            y=data["values"],
            mode='lines',
            name=data.get("series_name", "Data"),
            fill='tozeroy'
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title=x_label or "Period",
        yaxis_title=y_label or "Value",
        template='plotly_white'
    )
    
    return fig

# Chart type mapping
CHART_GENERATORS = {
    "line": create_line_chart,
    "bar": create_bar_chart,
    "pie": create_pie_chart,
    "scatter": create_scatter_chart,
    "area": create_area_chart
}

# ==========================================
# Cloud Storage Functions
# ==========================================

def upload_to_storage(html_content: str, chart_id: str) -> tuple:
    """Upload chart HTML to Cloud Storage"""
    if not storage_available:
        return None, None
    
    try:
        blob = bucket.blob(f"charts/{chart_id}.html")
        blob.upload_from_string(html_content, content_type='text/html')
        
        # Make it publicly accessible
        blob.make_public()
        
        # Generate URLs
        storage_url = f"gs://{BUCKET_NAME}/charts/{chart_id}.html"
        public_url = blob.public_url
        
        return storage_url, public_url
    
    except Exception as e:
        print(f"Error uploading to storage: {e}")
        return None, None

# ==========================================
# API Endpoints
# ==========================================

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "agent": "visualization",
        "capabilities": {
            "chart_types": ["line", "bar", "pie", "scatter", "area"],
            "cloud_storage": storage_available
        }
    }

@app.post("/create", response_model=ChartResponse)
async def create_chart(request: CreateChartRequest):
    """Create a chart and optionally save to Cloud Storage"""
    try:
        # Validate chart type
        if request.chart_type not in CHART_GENERATORS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid chart type. Must be one of: {list(CHART_GENERATORS.keys())}"
            )
        
        # Generate chart
        chart_generator = CHART_GENERATORS[request.chart_type]
        fig = chart_generator(
            request.data,
            request.title,
            request.x_label,
            request.y_label
        )
        
        # Convert to HTML
        html_content = fig.to_html(include_plotlyjs='cdn')
        
        # Generate chart ID
        chart_id = f"{request.chart_type}_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d')}"
        
        # Upload to storage if requested
        storage_url = None
        public_url = None
        
        if request.save_to_storage and storage_available:
            storage_url, public_url = upload_to_storage(html_content, chart_id)
        
        return ChartResponse(
            status="created",
            chart_id=chart_id,
            chart_url=storage_url,
            public_url=public_url,
            html=html_content if not request.save_to_storage else None
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chart creation failed: {str(e)}")

@app.post("/create/line")
async def create_line_chart_endpoint(data: ChartData, title: str, save: bool = True):
    """Quick endpoint for line charts"""
    request = CreateChartRequest(
        chart_type="line",
        data=data.dict(),
        title=title,
        save_to_storage=save
    )
    return await create_chart(request)

@app.post("/create/bar")
async def create_bar_chart_endpoint(data: ChartData, title: str, save: bool = True):
    """Quick endpoint for bar charts"""
    request = CreateChartRequest(
        chart_type="bar",
        data=data.dict(),
        title=title,
        save_to_storage=save
    )
    return await create_chart(request)

@app.post("/create/pie")
async def create_pie_chart_endpoint(data: ChartData, title: str, save: bool = True):
    """Quick endpoint for pie charts"""
    request = CreateChartRequest(
        chart_type="pie",
        data=data.dict(),
        title=title,
        save_to_storage=save
    )
    return await create_chart(request)

@app.get("/charts/{chart_id}")
async def get_chart(chart_id: str):
    """Get chart from Cloud Storage"""
    if not storage_available:
        raise HTTPException(status_code=503, detail="Cloud Storage not available")
    
    try:
        blob = bucket.blob(f"charts/{chart_id}.html")
        
        if not blob.exists():
            raise HTTPException(status_code=404, detail="Chart not found")
        
        return {
            "chart_id": chart_id,
            "storage_url": f"gs://{BUCKET_NAME}/charts/{chart_id}.html",
            "public_url": blob.public_url,
            "created": blob.time_created,
            "size": blob.size
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/charts")
async def list_charts(limit: int = 50):
    """List all charts in storage"""
    if not storage_available:
        raise HTTPException(status_code=503, detail="Cloud Storage not available")
    
    try:
        blobs = bucket.list_blobs(prefix="charts/", max_results=limit)
        
        charts = []
        for blob in blobs:
            if blob.name.endswith('.html'):
                chart_id = blob.name.replace("charts/", "").replace(".html", "")
                charts.append({
                    "chart_id": chart_id,
                    "public_url": blob.public_url,
                    "created": blob.time_created,
                    "size": blob.size
                })
        
        return {
            "total": len(charts),
            "charts": charts
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/charts/{chart_id}")
async def delete_chart(chart_id: str):
    """Delete chart from storage"""
    if not storage_available:
        raise HTTPException(status_code=503, detail="Cloud Storage not available")
    
    try:
        blob = bucket.blob(f"charts/{chart_id}.html")
        blob.delete()
        
        return {"status": "deleted", "chart_id": chart_id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8083)

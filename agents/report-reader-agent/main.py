"""Report Reader Agent - Excel & Google Sheets Parser with Cloud Storage"""
import os
import io
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.cloud import storage

app = FastAPI(title="Report Reader Agent")

# ==========================================
# Configuration
# ==========================================

PROJECT_ID = os.getenv("PROJECT_ID", "financial-reports-ai-2024")
REPORTS_BUCKET = os.getenv("REPORTS_BUCKET", "financial-reports-ai-2024-reports")
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "/secrets/google-credentials.json")

# Initialize Cloud Storage client
try:
    storage_client = storage.Client()
    storage_available = True
except Exception as e:
    print(f"Warning: Cloud Storage not available: {e}")
    storage_client = None
    storage_available = False

# Google Sheets API Setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def get_sheets_service():
    """Initialize Google Sheets API service"""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            GOOGLE_CREDENTIALS_PATH, scopes=SCOPES
        )
        service = build('sheets', 'v4', credentials=credentials)
        return service
    except Exception as e:
        print(f"Warning: Could not initialize Google Sheets API: {e}")
        return None

# ==========================================
# Data Models
# ==========================================

class ReadExcelRequest(BaseModel):
    file_path: str
    sheet_name: Optional[str] = None
    header_row: int = 0

class ReadStorageRequest(BaseModel):
    file_path: str
    bucket: Optional[str] = None
    sheet_name: Optional[str] = None
    header_row: int = 0

class ReadSheetsRequest(BaseModel):
    spreadsheet_id: str
    range: str = "A1:Z1000"
    sheet_name: Optional[str] = None

class DataCleaningOptions(BaseModel):
    remove_empty_rows: bool = True
    remove_empty_columns: bool = True
    fill_missing_values: bool = False
    convert_types: bool = True

class ReadResponse(BaseModel):
    status: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    warnings: List[str] = []

# ==========================================
# Helper Functions
# ==========================================

def clean_dataframe(df: pd.DataFrame, options: DataCleaningOptions) -> pd.DataFrame:
    """Clean and prepare dataframe"""
    warnings = []
    
    # Remove empty rows
    if options.remove_empty_rows:
        before = len(df)
        df = df.dropna(how='all')
        after = len(df)
        if before != after:
            warnings.append(f"Removed {before - after} empty rows")
    
    # Remove empty columns
    if options.remove_empty_columns:
        before = len(df.columns)
        df = df.dropna(axis=1, how='all')
        after = len(df.columns)
        if before != after:
            warnings.append(f"Removed {before - after} empty columns")
    
    # Fill missing values
    if options.fill_missing_values:
        df = df.fillna(0)
        warnings.append("Filled missing values with 0")
    
    # Convert types
    if options.convert_types:
        # Try to convert numeric columns
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col])
            except (ValueError, TypeError):
                pass  # Keep as string if conversion fails
    
    return df, warnings

def extract_metadata(df: pd.DataFrame) -> Dict[str, Any]:
    """Extract metadata from dataframe"""
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": df.columns.tolist(),
        "column_types": {col: str(df[col].dtype) for col in df.columns},
        "has_missing_values": df.isnull().any().any(),
        "numeric_columns": df.select_dtypes(include=['number']).columns.tolist(),
        "text_columns": df.select_dtypes(include=['object']).columns.tolist()
    }

def dataframe_to_json(df: pd.DataFrame) -> Dict[str, Any]:
    """Convert dataframe to structured JSON"""
    return {
        "columns": df.columns.tolist(),
        "rows": len(df),
        "data": df.head(100).to_dict(orient='records'),  # Ограничиваем до 100 строк
        "summary": {
            "total_rows": len(df),
            "numeric_columns": df.select_dtypes(include=['number']).columns.tolist()
        }
    }

# ==========================================
# Core Functions
# ==========================================

def read_from_storage(file_path: str, bucket_name: Optional[str] = None) -> bytes:
    """Read file from Cloud Storage"""
    if not storage_available:
        raise HTTPException(status_code=503, detail="Cloud Storage not available")
    
    try:
        bucket_name = bucket_name or REPORTS_BUCKET
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_path)
        
        if not blob.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
        
        return blob.download_as_bytes()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read from storage: {str(e)}")

def read_excel_file(file_path: str, sheet_name: Optional[str] = None, 
                   header_row: int = 0) -> pd.DataFrame:
    """Read Excel file"""
    try:
        if sheet_name:
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)
        else:
            df = pd.read_excel(file_path, header=header_row)
        return df
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read Excel file: {str(e)}")

def read_google_sheets(spreadsheet_id: str, range_name: str = "A1:Z1000", 
                       sheet_name: Optional[str] = None) -> pd.DataFrame:
    """Read Google Sheets"""
    try:
        service = get_sheets_service()
        if not service:
            raise HTTPException(status_code=503, detail="Google Sheets API not configured")
        
        # Adjust range if sheet name provided
        if sheet_name:
            range_name = f"{sheet_name}!{range_name}"
        
        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            raise HTTPException(status_code=404, detail="No data found in spreadsheet")
        
        # Convert to DataFrame
        df = pd.DataFrame(values[1:], columns=values[0])
        return df
    
    except HttpError as e:
        raise HTTPException(status_code=400, detail=f"Google Sheets API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read Google Sheets: {str(e)}")

# ==========================================
# API Endpoints
# ==========================================

@app.get("/health")
async def health():
    sheets_available = get_sheets_service() is not None
    return {
        "status": "healthy",
        "agent": "report-reader",
        "capabilities": {
            "excel": True,
            "google_sheets": sheets_available,
            "cloud_storage": storage_available
        }
    }

@app.post("/read/storage", response_model=ReadResponse)
async def read_from_cloud_storage(request: ReadStorageRequest,
                                   cleaning: DataCleaningOptions = DataCleaningOptions()):
    """Read and parse file from Cloud Storage"""
    try:
        # Read file from storage
        file_bytes = read_from_storage(request.file_path, request.bucket)
        
        # Determine file type and read
        if request.file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(file_bytes), 
                             sheet_name=request.sheet_name, 
                             header=request.header_row)
        elif request.file_path.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(file_bytes))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Clean data
        df, warnings = clean_dataframe(df, cleaning)
        
        # Extract metadata
        metadata = extract_metadata(df)
        metadata["file_path"] = request.file_path
        
        # Convert to JSON
        data = dataframe_to_json(df)
        
        return ReadResponse(
            status="success",
            data=data,
            metadata=metadata,
            warnings=warnings
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/read/excel", response_model=ReadResponse)
async def read_excel(request: ReadExcelRequest, 
                    cleaning: DataCleaningOptions = DataCleaningOptions()):
    """Read and parse Excel file"""
    try:
        # Read file
        df = read_excel_file(request.file_path, request.sheet_name, request.header_row)
        
        # Clean data
        df, warnings = clean_dataframe(df, cleaning)
        
        # Extract metadata
        metadata = extract_metadata(df)
        
        # Convert to JSON
        data = dataframe_to_json(df)
        
        return ReadResponse(
            status="success",
            data=data,
            metadata=metadata,
            warnings=warnings
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/read/sheets", response_model=ReadResponse)
async def read_sheets(request: ReadSheetsRequest,
                     cleaning: DataCleaningOptions = DataCleaningOptions()):
    """Read and parse Google Sheets"""
    try:
        # Read Google Sheets
        df = read_google_sheets(request.spreadsheet_id, request.range, request.sheet_name)
        
        # Clean data
        df, warnings = clean_dataframe(df, cleaning)
        
        # Extract metadata
        metadata = extract_metadata(df)
        
        # Convert to JSON
        data = dataframe_to_json(df)
        
        return ReadResponse(
            status="success",
            data=data,
            metadata=metadata,
            warnings=warnings
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload/excel")
async def upload_excel(file: UploadFile = File(...),
                      cleaning: DataCleaningOptions = DataCleaningOptions()):
    """Upload and parse Excel file"""
    try:
        # Read uploaded file
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        # Clean data
        df, warnings = clean_dataframe(df, cleaning)
        
        # Extract metadata
        metadata = extract_metadata(df)
        metadata["filename"] = file.filename
        
        # Convert to JSON
        data = dataframe_to_json(df)
        
        return ReadResponse(
            status="success",
            data=data,
            metadata=metadata,
            warnings=warnings
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/sheets/{spreadsheet_id}/info")
async def get_sheets_info(spreadsheet_id: str):
    """Get information about Google Sheets spreadsheet"""
    try:
        service = get_sheets_service()
        if not service:
            raise HTTPException(status_code=503, detail="Google Sheets API not configured")
        
        # Get spreadsheet metadata
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        
        sheets = []
        for sheet in spreadsheet.get('sheets', []):
            properties = sheet.get('properties', {})
            sheets.append({
                'title': properties.get('title'),
                'sheet_id': properties.get('sheetId'),
                'index': properties.get('index'),
                'rows': properties.get('gridProperties', {}).get('rowCount'),
                'columns': properties.get('gridProperties', {}).get('columnCount')
            })
        
        return {
            "spreadsheet_id": spreadsheet_id,
            "title": spreadsheet.get('properties', {}).get('title'),
            "locale": spreadsheet.get('properties', {}).get('locale'),
            "sheets": sheets
        }
    
    except HttpError as e:
        raise HTTPException(status_code=400, detail=f"Google Sheets API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)

"""
Nextcloud Log Analyzer - FastAPI Backend
Simplified Docker Web Deployment

No Celery, No Redis, No PostgreSQL - Just FastAPI + Synchronous Processing
Version: 1.0.4 - DataStore attributes fixed
"""

import os
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import aiofiles

# Import parsers
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from shared.web_parser import analyze_log_files
except ImportError:
    # Fallback if parser not available
    def analyze_log_files(file_paths):
        return {
            "status": "failed",
            "error_message": "Parser not available",
            "file_count": len(file_paths),
            "total_entries": 0,
            "categories": {},
            "entries": []
        }

# Configuration
MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB in bytes

# Create FastAPI app
app = FastAPI(
    title="Nextcloud Log Analyzer",
    description="Simple web-based log analysis for Nextcloud",
    version="1.0.0"
)

# CORS middleware (allow localhost access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
UPLOAD_DIR = Path("uploads")
RESULTS_DIR = Path("results")
UPLOAD_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

# Mount static files (frontend)
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# === Data Models ===

class AnalysisResult(BaseModel):
    """Analysis result model"""
    id: str
    timestamp: str
    status: str  # "completed" or "failed"
    file_count: int
    total_entries: int
    categories: Dict[str, int]
    entries: List[Dict]
    error_message: Optional[str] = None


class UploadResponse(BaseModel):
    """Upload response model"""
    analysis_id: str
    message: str
    file_count: int


# === Helper Functions ===

def analyze_logs_sync(file_paths: List[Path]) -> Dict:
    """
    Synchronous log analysis using web_parser
    """
    return analyze_log_files(file_paths)


def save_result(analysis_id: str, result: Dict):
    """Save analysis result to JSON file"""
    result_file = RESULTS_DIR / f"{analysis_id}.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)


def load_result(analysis_id: str) -> Optional[Dict]:
    """Load analysis result from JSON file"""
    result_file = RESULTS_DIR / f"{analysis_id}.json"
    if not result_file.exists():
        return None
    
    with open(result_file, 'r', encoding='utf-8') as f:
        return json.load(f)


# === API Endpoints ===

@app.get("/")
async def root():
    """Serve main HTML page"""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/results.html")
async def results_page():
    """Serve results HTML page"""
    return FileResponse(STATIC_DIR / "results.html")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/api/upload", response_model=UploadResponse)
async def upload_and_analyze(
    files: List[UploadFile] = File(..., description="Log files to analyze")
):
    """
    Upload log files and run analysis synchronously
    
    This endpoint:
    1. Saves uploaded files
    2. Runs analysis immediately (no background job)
    3. Returns analysis ID
    
    Max file size: 2GB per file
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")
    
    # Generate analysis ID
    analysis_id = str(uuid.uuid4())
    analysis_dir = UPLOAD_DIR / analysis_id
    analysis_dir.mkdir(exist_ok=True)
    
    # Save uploaded files
    saved_files = []
    for file in files:
        # Check file extension
        if not file.filename.endswith(('.log', '.txt', '.gz')):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type: {file.filename}. Only .log, .txt, .gz allowed"
            )
        
        # Save file
        file_path = analysis_dir / file.filename
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            
            # Check file size (2GB limit)
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File too large: {file.filename} (max 2GB)"
                )
            
            await f.write(content)
        
        saved_files.append(file_path)
    
    # Run analysis synchronously
    result = analyze_logs_sync(saved_files)
    
    # Add metadata
    result["id"] = analysis_id
    result["timestamp"] = datetime.now().isoformat()
    
    # Save result
    save_result(analysis_id, result)
    
    # Cleanup uploaded files (optional, keep for now)
    # for file_path in saved_files:
    #     file_path.unlink()
    
    return UploadResponse(
        analysis_id=analysis_id,
        message="Analysis completed",
        file_count=len(files)
    )


@app.get("/api/results/{analysis_id}", response_model=AnalysisResult)
async def get_results(analysis_id: str):
    """
    Get analysis results by ID
    
    Returns the complete analysis result including:
    - Statistics (categories, counts)
    - Log entries
    - Timestamp
    """
    result = load_result(analysis_id)
    
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Analysis {analysis_id} not found"
        )
    
    return result


@app.get("/api/results")
async def list_results():
    """List all available analysis results"""
    results = []
    
    for result_file in RESULTS_DIR.glob("*.json"):
        try:
            result = load_result(result_file.stem)
            if result:
                # Return minimal info
                results.append({
                    "id": result.get("id"),
                    "timestamp": result.get("timestamp"),
                    "file_count": result.get("file_count"),
                    "total_entries": result.get("total_entries"),
                    "status": result.get("status")
                })
        except:
            pass
    
    # Sort by timestamp (newest first)
    results.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    return {"results": results, "count": len(results)}


@app.delete("/api/results/{analysis_id}")
async def delete_result(analysis_id: str):
    """Delete an analysis result"""
    result_file = RESULTS_DIR / f"{analysis_id}.json"
    upload_dir = UPLOAD_DIR / analysis_id
    
    if not result_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Analysis {analysis_id} not found"
        )
    
    # Delete result file
    result_file.unlink()
    
    # Delete uploaded files
    if upload_dir.exists():
        import shutil
        shutil.rmtree(upload_dir)
    
    return {"message": f"Analysis {analysis_id} deleted"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

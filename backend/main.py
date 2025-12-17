"""
Nextcloud Log Analyzer - FastAPI Backend
Simplified Docker Web Deployment

No Celery, No Redis, No PostgreSQL - Just FastAPI + Synchronous Processing
Version: 1.0.6 - Security hardening and resource cleanup
"""

import os
import json
import uuid
import re
import zipfile
import tempfile
import shutil
import logging
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, Security, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import aiofiles

# Configure logging with rotation
from logging.handlers import RotatingFileHandler

# Create logs directory in project root (not backend/)
# Use absolute path to ensure logs always go to the same place
PROJECT_ROOT = Path(__file__).parent.parent  # Go up from backend/ to project root
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Configure rotating file handler (10MB per file, keep 5 backups)
file_handler = RotatingFileHandler(
    str(LOG_DIR / "app.log"),  # Absolute path: /project/logs/app.log
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=5,
    encoding='utf-8'
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)
logger = logging.getLogger(__name__)

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

# Environment Configuration
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE_MB", "2048")) * 1024 * 1024  # Default 2GB
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000").split(",")
ENABLE_AUTH = os.getenv("ENABLE_AUTH", "false").lower() == "true"
API_KEY = os.getenv("API_KEY", "")  # Set in production if ENABLE_AUTH=true
CLEANUP_ENABLED = os.getenv("CLEANUP_ENABLED", "true").lower() == "true"
CLEANUP_DAYS = int(os.getenv("CLEANUP_DAYS", "7"))  # Delete results older than 7 days

# Rate Limiting Configuration
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
RATE_LIMIT_UPLOAD = os.getenv("RATE_LIMIT_UPLOAD", "5/minute")  # 5 uploads per minute per IP
RATE_LIMIT_API = os.getenv("RATE_LIMIT_API", "30/minute")  # 30 API calls per minute per IP

# Create FastAPI app
app = FastAPI(
    title="Nextcloud Log Analyzer",
    description="Simple web-based log analysis for Nextcloud",
    version="1.0.6"
)

# Rate Limiting
limiter = Limiter(key_func=get_remote_address, enabled=RATE_LIMIT_ENABLED)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware (secure configuration)
logger.info(f"CORS allowed origins: {ALLOWED_ORIGINS}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # ✅ Restricted origins from environment
    allow_credentials=False,  # ✅ Disabled for security
    allow_methods=["GET", "POST", "DELETE"],  # ✅ Only needed methods
    allow_headers=["*"],
)

# Directories (use absolute paths from project root)
PROJECT_ROOT = Path(__file__).parent.parent  # Already defined for logs
UPLOAD_DIR = PROJECT_ROOT / "uploads"
RESULTS_DIR = PROJECT_ROOT / "results"
UPLOAD_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

# Mount static files (frontend)
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# === Authentication ===

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(request: Request, api_key: str = Security(api_key_header)):
    """
    Verify API key if authentication is enabled
    
    Authentication rules:
    - Web frontend (Referer header present) → ALWAYS allowed (no auth required)
    - API clients (no Referer) → Require API key if ENABLE_AUTH=true
    
    This allows the web UI to work while protecting API access.
    """
    # Check if request is from web frontend (has Referer header)
    referer = request.headers.get("referer", "")
    is_web_request = bool(referer)  # Web browsers always send Referer header
    
    if is_web_request:
        return True  # Web frontend always allowed
    
    # API client request - check authentication
    if not ENABLE_AUTH:
        return True  # Auth disabled for API clients too
    
    if not api_key or api_key != API_KEY:
        logger.warning(f"Unauthorized API access attempt with key: {api_key[:10] if api_key else 'None'}...")
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key. Set X-API-Key header for API access."
        )
    return True


# === Cleanup Functions ===

def cleanup_old_results():
    """
    Delete old analysis results and uploaded files
    Called on startup and can be scheduled
    """
    if not CLEANUP_ENABLED:
        logger.info("Cleanup disabled (CLEANUP_ENABLED=false)")
        return
    
    cutoff_time = datetime.now() - timedelta(days=CLEANUP_DAYS)
    deleted_results = 0
    deleted_uploads = 0
    
    # Cleanup results
    for result_file in RESULTS_DIR.glob("*.json"):
        try:
            file_mtime = datetime.fromtimestamp(result_file.stat().st_mtime)
            if file_mtime < cutoff_time:
                result_file.unlink()
                deleted_results += 1
                logger.info(f"Deleted old result: {result_file.name}")
        except Exception as e:
            logger.error(f"Error deleting result {result_file}: {e}")
    
    # Cleanup uploads
    for upload_dir in UPLOAD_DIR.iterdir():
        if upload_dir.is_dir():
            try:
                dir_mtime = datetime.fromtimestamp(upload_dir.stat().st_mtime)
                if dir_mtime < cutoff_time:
                    shutil.rmtree(upload_dir)
                    deleted_uploads += 1
                    logger.info(f"Deleted old upload dir: {upload_dir.name}")
            except Exception as e:
                logger.error(f"Error deleting upload dir {upload_dir}: {e}")
    
    logger.info(f"Cleanup complete: {deleted_results} results, {deleted_uploads} upload dirs deleted (older than {CLEANUP_DAYS} days)")
    return {"deleted_results": deleted_results, "deleted_uploads": deleted_uploads}


@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("=" * 60)
    logger.info("Nextcloud Log Analyzer - Starting")
    logger.info(f"Version: 1.0.6")
    logger.info(f"Max file size: {MAX_FILE_SIZE / (1024*1024):.0f} MB")
    logger.info(f"Authentication: {'ENABLED' if ENABLE_AUTH else 'DISABLED'}")
    logger.info(f"Auto-cleanup: {'ENABLED' if CLEANUP_ENABLED else 'DISABLED'} (retention: {CLEANUP_DAYS} days)")
    logger.info("=" * 60)
    
    # Run initial cleanup
    cleanup_old_results()
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

def extract_zip_logs(zip_path: Path, extract_dir: Path) -> List[Path]:
    """
    Extract log files from ZIP archive
    
    Args:
        zip_path: Path to ZIP file
        extract_dir: Directory to extract files to
        
    Returns:
        List of extracted log file paths
    """
    log_files = []
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Get all entries
            for file_info in zip_ref.namelist():
                # Only extract files from logs/ directory
                if file_info.startswith('logs/') and not file_info.endswith('/'):
                    # Check if it's a log file
                    filename = Path(file_info).name
                    # Allow .log*, .txt, .gz files
                    if filename.endswith(('.txt', '.gz')) or '.log' in filename:
                        # Extract to analysis directory
                        extract_path = extract_dir / filename
                        with zip_ref.open(file_info) as source:
                            with open(extract_path, 'wb') as target:
                                shutil.copyfileobj(source, target)
                        log_files.append(extract_path)
                        print(f"[ZIP] Extracted: {filename} ({extract_path.stat().st_size} bytes)")
    
    except zipfile.BadZipFile:
        print(f"[ERROR] Invalid ZIP file: {zip_path}")
        raise HTTPException(status_code=400, detail=f"Invalid ZIP file: {zip_path.name}")
    
    if not log_files:
        print(f"[WARNING] No log files found in ZIP: {zip_path}")
        raise HTTPException(
            status_code=400, 
            detail="No log files found in ZIP archive. Expected files in 'logs/' directory with extensions: .log*, .txt, .gz"
        )
    
    print(f"[ZIP] Extracted {len(log_files)} log files from {zip_path.name}")
    return log_files


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


def validate_analysis_id(analysis_id: str) -> bool:
    """
    Validate analysis_id to prevent path traversal attacks.
    Only allows valid UUID format.
    
    Args:
        analysis_id: The ID to validate
        
    Returns:
        True if valid UUID format, False otherwise
    """
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    return bool(uuid_pattern.match(analysis_id))


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
@limiter.limit(RATE_LIMIT_API)
async def health_check(request: Request):
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/api/config")
async def get_config():
    """
    Get public configuration for frontend
    No authentication required - public info only
    """
    return {
        "auth_required": False,  # Web UI never requires auth (only API clients do)
        "max_file_size_mb": MAX_FILE_SIZE / (1024 * 1024),
        "version": "1.0.6"
    }


@app.post("/api/upload", response_model=UploadResponse)
@limiter.limit(RATE_LIMIT_UPLOAD)  # Strict limit for uploads
async def upload_and_analyze(
    request: Request,
    files: List[UploadFile] = File(..., description="Log files or ZIP archives to analyze"),
    authenticated: bool = Depends(verify_api_key)
):
    """
    Upload log files and run analysis synchronously
    
    This endpoint:
    1. Saves uploaded files
    2. If ZIP file: extracts log files from logs/ directory
    3. Runs analysis immediately (no background job)
    4. Returns analysis ID
    
    Supported formats:
    - Direct log files: .log* (including .log.1, .log.gz, etc.), .txt, .gz
    - ZIP archives: .zip (will extract files from logs/ directory)
    
    Max file size: 2GB per file
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")
    
    # Generate analysis ID
    analysis_id = str(uuid.uuid4())
    analysis_dir = UPLOAD_DIR / analysis_id
    analysis_dir.mkdir(exist_ok=True)
    
    # Save uploaded files and extract ZIPs
    files_to_analyze = []
    
    for file in files:
        file_lower = file.filename.lower()
        
        # Check file extension - allow .log*, .txt, .gz, .zip
        allowed = (
            file_lower.endswith(('.txt', '.gz', '.zip')) or 
            '.log' in file_lower
        )
        if not allowed:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type: {file.filename}. Only .log*, .txt, .gz, .zip allowed"
            )
        
        # Save file with streaming (memory efficient for large files)
        file_path = analysis_dir / file.filename
        file_size = 0
        chunk_size = 1024 * 1024  # 1MB chunks
        
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await file.read(chunk_size):
                file_size += len(chunk)
                
                # Check file size during streaming (2GB limit)
                if file_size > MAX_FILE_SIZE:
                    # Clean up partial file
                    await f.close()
                    file_path.unlink()
                    raise HTTPException(
                        status_code=400,
                        detail=f"File too large: {file.filename} (max 2GB)"
                    )
                
                await f.write(chunk)
        
        # Handle ZIP files
        if file_lower.endswith('.zip'):
            print(f"[UPLOAD] ZIP file detected: {file.filename}")
            extracted_files = extract_zip_logs(file_path, analysis_dir)
            files_to_analyze.extend(extracted_files)
            
            # Remove ZIP file after extraction
            file_path.unlink()
            print(f"[CLEANUP] Removed ZIP file: {file.filename}")
        else:
            # Regular log file
            files_to_analyze.append(file_path)
    
    if not files_to_analyze:
        raise HTTPException(
            status_code=400,
            detail="No valid log files found. For ZIP files, ensure logs are in 'logs/' directory."
        )
    
    print(f"[ANALYZE] Processing {len(files_to_analyze)} log files...")
    
    # Run analysis synchronously
    result = analyze_logs_sync(files_to_analyze)
    
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
        file_count=len(files_to_analyze)
    )


@app.get("/api/results/{analysis_id}", response_model=AnalysisResult)
@limiter.limit(RATE_LIMIT_API)
async def get_results(request: Request, analysis_id: str, authenticated: bool = Depends(verify_api_key)):
    """
    Get analysis results by ID
    
    Returns the complete analysis result including:
    - Statistics (categories, counts)
    - Log entries
    - Timestamp
    """
    # Validate analysis_id to prevent path traversal
    if not validate_analysis_id(analysis_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid analysis ID format"
        )
    
    result = load_result(analysis_id)
    
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Analysis {analysis_id} not found"
        )
    
    return result


@app.get("/api/results")
@limiter.limit(RATE_LIMIT_API)
async def list_results(request: Request, authenticated: bool = Depends(verify_api_key)):
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
@limiter.limit(RATE_LIMIT_API)
async def delete_result(request: Request, analysis_id: str, authenticated: bool = Depends(verify_api_key)):
    """Delete an analysis result"""
    # Validate analysis_id to prevent path traversal
    if not validate_analysis_id(analysis_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid analysis ID format"
        )
    
    result_file = RESULTS_DIR / f"{analysis_id}.json"
    upload_dir = UPLOAD_DIR / analysis_id
    
    if not result_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Analysis {analysis_id} not found"
        )
    
    # Delete result file
    result_file.unlink()
    logger.info(f"Deleted result: {analysis_id}")
    
    # Delete uploaded files
    if upload_dir.exists():
        shutil.rmtree(upload_dir)
        logger.info(f"Deleted upload directory: {analysis_id}")
    
    return {"message": f"Analysis {analysis_id} deleted"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# backend/main.py

"""
AI Agent Builder Backend
------------------------
FastAPI service that powers:
- Visual workflow execution
- File uploads (PDF / images)
- LLM-based agents (Gemini)
"""

from dotenv import load_dotenv
load_dotenv()

# ================================
# Standard Library Imports
# ================================
import shutil
import time
from pathlib import Path
from typing import List

# ================================
# Third-Party Imports
# ================================
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# ================================
# Local Application Imports
# ================================
from models import ExecuteRequest, ExecuteResponse, Workflow
from registry import registry
from engine import WorkflowEngine
from services.gemini import gemini_generate

# ================================
# Agent Injection (Gemini)
# ================================
import agents.llm
import agents.summarizer
import agents.guardrail

agents.llm.gemini_generate = gemini_generate
agents.summarizer.gemini_generate = gemini_generate
agents.guardrail.gemini_generate = gemini_generate


# ================================
# FastAPI App Initialization
# ================================
app = FastAPI(title="AI Agent Builder")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ================================
# File Upload Configuration
# ================================
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}


# ================================
# Core Engine
# ================================
engine = WorkflowEngine(registry)

# NOTE: In-memory storage (replace with DB in production)
workflows_db = {}


# ================================
# Health & Metadata Endpoints
# ================================
@app.get("/")
async def root():
    """Basic service status"""
    return {"status": "running", "version": "1.0"}


@app.get("/api/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "gemini": True}


@app.get("/api/nodes")
async def get_nodes():
    """Return all available agent/tool metadata"""
    return registry.get_metadata()


# ================================
# File Upload Endpoint
# ================================
@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload PDF or image files.
    Returns saved file path for workflow usage.
    """
    try:
        file_ext = Path(file.filename).suffix.lower()

        if file_ext not in ALLOWED_EXTENSIONS:
            return {
                "success": False,
                "error": f"Unsupported file type: {file_ext}"
            }

        timestamp = int(time.time() * 1000)
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = UPLOAD_DIR / safe_filename

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {
            "success": True,
            "file_path": str(file_path),
            "file_name": file.filename,
            "file_size": file_path.stat().st_size,
        }

    except Exception as exc:
        return {"success": False, "error": str(exc)}


# ================================
# Workflow Execution
# ================================
@app.post("/api/execute", response_model=ExecuteResponse)
async def execute_workflow(req: ExecuteRequest):
    """
    Execute a workflow DAG using WorkflowEngine
    """
    try:
        results, logs = await engine.execute(req.workflow)
        return ExecuteResponse(
            success=True,
            status="success",
            result=results,
            logs=logs,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


# ================================
# Workflow Persistence (In-Memory)
# ================================
@app.post("/api/workflows/save")
async def save_workflow(workflow: Workflow):
    workflows_db[workflow.id] = workflow.dict()
    return {"success": True, "message": "Workflow saved"}


@app.get("/api/workflows", response_model=List[Workflow])
async def list_workflows():
    return list(workflows_db.values())


@app.get("/api/workflows/{workflow_id}", response_model=Workflow)
async def get_workflow(workflow_id: str):
    if workflow_id not in workflows_db:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflows_db[workflow_id]


@app.delete("/api/workflows/{workflow_id}")
async def delete_workflow(workflow_id: str):
    if workflow_id not in workflows_db:
        raise HTTPException(status_code=404, detail="Workflow not found")

    del workflows_db[workflow_id]
    return {"success": True, "message": "Workflow deleted"}

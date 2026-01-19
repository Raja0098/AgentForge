# backend/models.py

"""
Pydantic models for:
- Workflow definition
- Nodes and connections
- Execution request / response
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


# ================================
# Core Workflow Models
# ================================

class WorkflowNode(BaseModel):
    """
    Represents a single node in the workflow graph.
    """
    id: str
    type: str             
    subtype: str            
    name: str

    config: Dict[str, Any] = Field(default_factory=dict)
    position: Optional[Dict[str, float]] = None


class Connection(BaseModel):
    """
    Directed edge between two nodes.
    """
    source: str
    target: str


class Workflow(BaseModel):
    """
    Complete workflow definition.
    """
    id: str
    name: str = "Untitled Workflow"

    nodes: List[WorkflowNode]
    connections: List[Connection]

    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None


# ================================
# Execution Models
# ================================

class ExecuteRequest(BaseModel):
    """
    Request payload to execute a workflow.
    """
    workflow: Workflow


class ExecuteResponse(BaseModel):
    """
    Standardized execution response.
    """
    success: bool
    status: str = "success"

    result: Optional[Dict[str, Any]] = None
    logs: Optional[List[Dict[str, Any]]] = None

    error: Optional[str] = None
    message: Optional[str] = None

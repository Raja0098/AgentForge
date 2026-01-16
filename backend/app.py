# =====================================================
# AI AGENT BUILDER — WITH INPUT/OUTPUT NODES
# =====================================================

import os
import time
from collections import deque
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Type

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator, Field
import uvicorn

from dotenv import load_dotenv
import google.generativeai as genai

# =====================================================
# ENV + GEMINI SETUP
# =====================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("❌ GEMINI_API_KEY not found in environment")

genai.configure(api_key=GEMINI_API_KEY)
GEMINI_MODEL_NAME = "gemini-2.5-flash"

def get_gemini_model():
    return genai.GenerativeModel(GEMINI_MODEL_NAME)

# =====================================================
# FASTAPI APP
# =====================================================

app = FastAPI(
    title="AI Agent Builder API",
    description="No-Code AI Platform Backend",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# DATA MODELS
# =====================================================

class NodePosition(BaseModel):
    x: float = 0.0
    y: float = 0.0

class WorkflowNode(BaseModel):
    id: str
    type: str
    subtype: str
    name: str
    position: Optional[NodePosition] = None
    config: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('position', pre=True)
    def handle_empty_position(cls, v):
        if v == {} or v == '':
            return None
        return v
    
    @validator('config', pre=True)
    def handle_empty_config(cls, v):
        if v is None or v == '':
            return {}
        return v

class Connection(BaseModel):
    source: str
    target: str

class Workflow(BaseModel):
    id: str
    nodes: List[WorkflowNode]
    connections: List[Connection]

class ExecuteRequest(BaseModel):
    workflow: Workflow
    input_data: Dict[str, Any] = Field(default_factory=dict)

class ExecuteResponse(BaseModel):
    success: bool
    result: Optional[Dict[str, Any]] = None
    logs: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None

# =====================================================
# BASE CLASSES
# =====================================================

class BaseNode(ABC):
    def __init__(self, name: str, description: str, icon: str, node_type: str):
        self.name = name
        self.description = description
        self.icon = icon
        self.type = node_type

    @abstractmethod
    async def execute(self, node_input: Dict[str, Any], parent_outputs: Dict[str, Any]):
        pass

    def get_parent_data(self, parent_outputs: Dict[str, Any]) -> str:
        data = []
        for output in parent_outputs.values():
            if output.get("success"):
                data.append(str(output.get("data", "")))
        return "\n\n".join(data)

class BaseAgent(BaseNode):
    def __init__(self, name: str, description: str, icon: str = "🤖"):
        super().__init__(name, description, icon, "agent")

class BaseTool(BaseNode):
    def __init__(self, name: str, description: str, icon: str = "🔧"):
        super().__init__(name, description, icon, "tool")

# =====================================================
# INPUT/OUTPUT NODES
# =====================================================

class InputNode(BaseNode):
    """Start node that provides initial input"""
    def __init__(self):
        super().__init__("Input", "Workflow input", "📥", "input")

    async def execute(self, node_input, parent_outputs):
        user_input = node_input.get("input", "")
        input_type = node_input.get("input_type", "text")
        
        return {
            "success": True,
            "data": user_input,
            "input_type": input_type,
            "node_type": "input"
        }

class OutputNode(BaseNode):
    """End node that captures final output"""
    def __init__(self):
        super().__init__("Output", "Workflow output", "📤", "output")

    async def execute(self, node_input, parent_outputs):
        # Collect all parent outputs
        final_output = self.get_parent_data(parent_outputs)
        
        return {
            "success": True,
            "data": final_output,
            "node_type": "output",
            "is_final": True
        }

# =====================================================
# AGENTS
# =====================================================

class LLMAgent(BaseAgent):
    def __init__(self):
        super().__init__("LLM Agent", "Gemini-powered reasoning agent", "🤖")
        self.model = get_gemini_model()

    async def execute(self, node_input, parent_outputs):
        try:
            prompt = node_input.get("input") or self.get_parent_data(parent_outputs)

            if not prompt or len(prompt.strip()) == 0:
                return {"success": False, "error": "No input provided"}

            response = self.model.generate_content(prompt)

            return {
                "success": True,
                "data": response.text,
                "node_type": "llm"
            }
        except Exception as e:
            return {"success": False, "error": f"LLM Error: {str(e)}"}

class SummarizerAgent(BaseAgent):
    def __init__(self):
        super().__init__("Summarizer", "Summarizes text using AI", "📝")
        self.model = get_gemini_model()

    async def execute(self, node_input, parent_outputs):
        try:
            text = node_input.get("input") or self.get_parent_data(parent_outputs)

            if not text or len(text.strip()) == 0:
                return {"success": False, "error": "No text to summarize"}

            prompt = f"Summarize the following text clearly and concisely:\n\n{text}"
            response = self.model.generate_content(prompt)

            return {
                "success": True,
                "data": response.text,
                "node_type": "summarizer"
            }
        except Exception as e:
            return {"success": False, "error": f"Summarizer Error: {str(e)}"}

# =====================================================
# TOOLS
# =====================================================

class WebSearchTool(BaseTool):
    def __init__(self):
        super().__init__("Web Search", "Search the web", "🔍")

    async def execute(self, node_input, parent_outputs):
        try:
            query = node_input.get("query") or node_input.get("input")
            
            if not query:
                query = self.get_parent_data(parent_outputs) if parent_outputs else None
            
            if not query:
                return {"success": False, "error": "No search query provided"}

            return {
                "success": True,
                "data": {
                    "query": query,
                    "results": [
                        {
                            "title": f"Result for: {query}",
                            "snippet": "This is a placeholder. Integrate with SerpAPI for real results.",
                            "url": "https://example.com"
                        }
                    ]
                },
                "node_type": "web_search"
            }
        except Exception as e:
            return {"success": False, "error": f"Search Error: {str(e)}"}

class DataExtractorTool(BaseTool):
    def __init__(self):
        super().__init__("Data Extractor", "Extract structured data", "📊")
        self.model = get_gemini_model()

    async def execute(self, node_input, parent_outputs):
        try:
            text = node_input.get("input") or self.get_parent_data(parent_outputs)
            
            if not text:
                return {"success": False, "error": "No text provided"}

            prompt = f"Extract key points from this text as a bullet list:\n\n{text}"
            response = self.model.generate_content(prompt)

            return {
                "success": True,
                "data": response.text,
                "node_type": "data_extractor"
            }
        except Exception as e:
            return {"success": False, "error": f"Extractor Error: {str(e)}"}

# =====================================================
# REGISTRY
# =====================================================

class NodeRegistry:
    def __init__(self):
        self._nodes: Dict[str, Type] = {
            "input": InputNode,
            "output": OutputNode,
            "llm": LLMAgent,
            "summarizer": SummarizerAgent,
            "web_search": WebSearchTool,
            "data_extractor": DataExtractorTool,
        }
        print(f"📦 Registry loaded with {len(self._nodes)} nodes")

    def get_node_instance(self, subtype: str):
        cls = self._nodes.get(subtype)
        if not cls:
            raise ValueError(f"Unknown node type: {subtype}")
        return cls()

    def get_metadata(self):
        agents, tools, special = [], [], []
        for subtype, cls in self._nodes.items():
            inst = cls()
            meta = {
                "type": subtype,
                "name": inst.name,
                "description": inst.description,
                "icon": inst.icon
            }
            
            if subtype in ["input", "output"]:
                special.append(meta)
            elif inst.type == "agent":
                agents.append(meta)
            else:
                tools.append(meta)
                
        return {"agents": agents, "tools": tools, "special": special}

registry = NodeRegistry()

# =====================================================
# WORKFLOW ENGINE
# =====================================================

class WorkflowEngine:
    def __init__(self, registry: NodeRegistry):
        self.registry = registry

    async def execute(self, workflow: Workflow, global_input: Dict[str, Any]):
        results, logs = {}, []
        start_time = time.time()

        if not workflow.nodes:
            raise HTTPException(status_code=400, detail="Workflow has no nodes")

        node_map = {n.id: n for n in workflow.nodes}
        adj = {n.id: [] for n in workflow.nodes}
        indeg = {n.id: 0 for n in workflow.nodes}

        for c in workflow.connections:
            if c.source not in node_map or c.target not in node_map:
                raise HTTPException(status_code=400, detail=f"Invalid connection")
            adj[c.source].append(c.target)
            indeg[c.target] += 1

        queue = deque([n for n in indeg if indeg[n] == 0])
        order = []

        while queue:
            n = queue.popleft()
            order.append(n)
            for nb in adj[n]:
                indeg[nb] -= 1
                if indeg[nb] == 0:
                    queue.append(nb)

        if len(order) != len(node_map):
            raise HTTPException(status_code=400, detail="Cycle detected in workflow")

        logs.append({"event": "start", "order": order})

        for node_id in order:
            node = node_map[node_id]
            node_start = time.time()
            
            try:
                instance = self.registry.get_node_instance(node.subtype)

                parents = {
                    c.source: results[c.source]
                    for c in workflow.connections
                    if c.target == node_id and c.source in results
                }

                output = await instance.execute(node.config, parents)
                results[node_id] = output

                logs.append({
                    "node": node.name,
                    "success": output.get("success"),
                    "duration_ms": round((time.time() - node_start) * 1000, 2)
                })

            except Exception as e:
                results[node_id] = {"success": False, "error": str(e)}

        logs.append({"event": "complete", "total_ms": round((time.time() - start_time) * 1000, 2)})

        return results, logs

engine = WorkflowEngine(registry)

# =====================================================
# API ROUTES
# =====================================================

@app.get("/")
async def root():
    return {"status": "running", "version": "1.0.0"}

@app.get("/api/health")
async def health():
    return {"status": "healthy", "gemini": bool(GEMINI_API_KEY)}

@app.get("/api/nodes")
async def nodes():
    return registry.get_metadata()

@app.post("/api/execute", response_model=ExecuteResponse)
async def execute(req: ExecuteRequest):
    try:
        results, logs = await engine.execute(req.workflow, req.input_data)
        return ExecuteResponse(success=True, result=results, logs=logs)
    except HTTPException as e:
        raise e
    except Exception as e:
        return ExecuteResponse(success=False, error=str(e))

# =====================================================
# RUN
# =====================================================

if __name__ == "__main__":
    print("🚀 AI Agent Builder running at http://127.0.0.1:8000")
    print(f"📦 Available nodes: {list(registry._nodes.keys())}")
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)

# backend/registry.py

"""
Node Registry
-------------
Central place that:
- Registers all available nodes (agents, tools, IO)
- Provides node instances for execution
- Exposes metadata for frontend rendering
"""

# ================================
# LLM Service
# ================================
from services.gemini import gemini_generate

# ================================
# Agents
# ================================
from agents.llm import LLMAgent
from agents.llm_with_tools import LLMWithToolsAgent
from agents.summarizer import SummarizerAgent
from agents.guardrail import GuardrailAgent

# ================================
# Core Nodes
# ================================
from nodes.input_output import InputNode, OutputNode

# ================================
# Tools
# ================================
from tools.document_extractor import DocumentExtractorTool
from tools.web_search import WebSearchTool


class NodeRegistry:
    """
    Registry responsible for:
    - Initializing all nodes
    - Returning node instances by subtype
    - Providing metadata for the frontend
    """

    def __init__(self):
        # LLM function (Gemini)
        self.llm = gemini_generate

        # ----------------------------
        # Tool instances (singleton)
        # ----------------------------
        self.document_extractor = DocumentExtractorTool()
        self.web_search = WebSearchTool()

        # Tools available to tool-aware LLMs
        self.available_tools = {
            "web_search": {
                "description": "Search the web for information",
                "instance": self.web_search,
            },
            "document_extractor": {
                "description": "Extract text from PDF or image files",
                "instance": self.document_extractor,
            },
        }

        # ----------------------------
        # Node factory map
        # ----------------------------
        self._nodes = {
            # Boundary nodes
            "input": InputNode,
            "output": OutputNode,

            # Agents
            "guardrail": lambda: GuardrailAgent(self.llm),
            "summarizer": lambda: SummarizerAgent(self.llm),
            "llm": lambda: LLMAgent(self.llm),
            "llm_tools": lambda: LLMWithToolsAgent(self.llm, self.available_tools),

            # Tools
            "document_extractor": lambda: self.document_extractor,
            "web_search": lambda: self.web_search,
        }

    # ================================
    # Node Access
    # ================================
    def get_node_instance(self, subtype: str):
        """
        Return a node instance based on subtype.
        """
        creator = self._nodes.get(subtype)
        if not creator:
            raise ValueError(f"Unknown node type: {subtype}")
        return creator()

    # ================================
    # Frontend Metadata
    # ================================
    def get_metadata(self):
        """
        Metadata used by frontend to render node palette.
        """
        agents: list = []
        tools: list = []
        special: list = []

        metadata_map = {
            # Special / boundary nodes
            "input": {
                "type": "input",
                "name": "Input Source",
                "description": "Multi-type input (text / file / URL)",
                "icon": "📥",
            },
            "output": {
                "type": "output",
                "name": "Output",
                "description": "Final workflow output",
                "icon": "📤",
            },

            # Agents
            "guardrail": {
                "type": "guardrail",
                "name": "Guardrail",
                "description": "Safety and validation checks",
                "icon": "🛡️",
            },
            "summarizer": {
                "type": "summarizer",
                "name": "Summarizer",
                "description": "Text summarization agent",
                "icon": "📝",
            },
            "llm": {
                "type": "llm",
                "name": "LLM Agent",
                "description": "Basic language model",
                "icon": "🤖",
            },
            "llm_tools": {
                "type": "llm_tools",
                "name": "LLM with Tools",
                "description": "LLM capable of tool usage (ReAct)",
                "icon": "🔧🤖",
            },

            # Tools
            "document_extractor": {
                "type": "document_extractor",
                "name": "Document Extractor",
                "description": "Extract text from PDFs and images",
                "icon": "📄",
            },
            "web_search": {
                "type": "web_search",
                "name": "Web Search",
                "description": "Search the web for information",
                "icon": "🔍",
            },
        }

        for subtype, meta in metadata_map.items():
            if subtype in ("input", "output"):
                special.append(meta)
            elif subtype in ("guardrail", "summarizer", "llm", "llm_tools"):
                agents.append(meta)
            else:
                tools.append(meta)

        return {
            "agents": agents,
            "tools": tools,
            "special": special,
        }


# ================================
# Global Registry Instance
# ================================
registry = NodeRegistry()

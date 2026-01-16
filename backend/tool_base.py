# tool_base.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseTool(ABC):
    def __init__(self, name, description, icon="🔧"):
        self.name = name
        self.description = description
        self.icon = icon
        self.type = "tool"

    @abstractmethod
    async def execute(self, node_input: Dict[str, Any], parent_outputs: Dict[str, Any]):
        pass

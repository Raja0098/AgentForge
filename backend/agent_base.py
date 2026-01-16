# backend/agent_base.py

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseNode(ABC):
    """
    Abstract base class for ALL workflow nodes:
    - Input / Output
    - Agents
    - Tools
    """

    def __init__(
        self,
        name: str,
        description: str,
        node_type: str,
        icon: str = "",
    ):
        self.name = name
        self.description = description
        self.type = node_type
        self.icon = icon

    @abstractmethod
    async def execute(
        self,
        node_input: Dict[str, Any],
        parent_outputs: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Execute the node.

        Args:
            node_input: Configuration/input for this node
            parent_outputs: Outputs from parent nodes

        Returns:
            A dictionary containing execution result
        """
        raise NotImplementedError

    def get_parent_data(
        self,
        parent_outputs: Dict[str, Dict[str, Any]],
    ) -> str:
        """
        Combine successful parent outputs into a single string.

        This is useful for agents/tools that consume
        text from previous steps.
        """
        parts = []

        for output in parent_outputs.values():
            if output.get("success"):
                parts.append(str(output.get("data", "")))

        return "\n\n".join(parts)


class BaseAgent(BaseNode):
    """
    Base class for all LLM-based agents.
    """

    def __init__(
        self,
        name: str,
        description: str,
        llm=None,
        icon: str = "🤖",
    ):
        super().__init__(
            name=name,
            description=description,
            node_type="agent",
            icon=icon,
        )
        self.llm = llm


class BaseTool(BaseNode):
    """
    Base class for all non-LLM tools.
    """

    def __init__(
        self,
        name: str,
        description: str,
        icon: str = "🔧",
    ):
        super().__init__(
            name=name,
            description=description,
            node_type="tool",
            icon=icon,
        )

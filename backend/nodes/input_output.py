# backend/nodes/input_output.py

import os
from agent_base import BaseNode


class InputNode(BaseNode):
    """
    Entry point for workflows.
    Supports:
    - Text input
    - URL input
    - File path input (PDF / image)
    """

    def __init__(self):
        super().__init__(
            name="Input Source",
            description="Multi-type input: text, URL, or file",
            node_type="tool",
            icon="📥",
        )

    async def execute(self, node_input, parent_outputs):
        # ================================
        # Resolve Input
        # ================================
        input_type = node_input.get("input_type", "text")
        input_value = node_input.get("value", "")

        if not input_value:
            return {
                "success": False,
                "error": "No input provided",
            }

        # ================================
        # File Input Handling
        # ================================
        # For files, only validate and pass the path.
        # Actual processing happens in DocumentExtractorTool.
        if input_type == "file":
            if not os.path.exists(input_value):
                return {
                    "success": False,
                    "error": f"File not found: {input_value}",
                }

            return {
                "success": True,
                "data": input_value,
                "node_type": "input",
                "input_type": "file",
            }

        # ================================
        # Text / URL Input
        # ================================
        return {
            "success": True,
            "data": input_value,
            "node_type": "input",
            "input_type": input_type,
        }


class OutputNode(BaseNode):
    """
    Terminal node.
    Returns the output of the last executed parent node.
    """

    def __init__(self):
        super().__init__(
            name="Final Output",
            description="Terminal node to display results",
            node_type="tool",
            icon="📤",
        )

    async def execute(self, node_input, parent_outputs):
        if not parent_outputs:
            return {
                "success": False,
                "error": "No input received",
            }

        # Get the most recent parent output
        last_output = list(parent_outputs.values())[-1]
        data = last_output.get("data", "")

        return {
            "success": True,
            "data": data,
            "node_type": "output",
        }

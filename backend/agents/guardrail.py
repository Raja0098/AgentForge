# backend/agents/guardrail.py

from agent_base import BaseAgent


class GuardrailAgent(BaseAgent):
    """
    Guardrail agent that validates text against safety and policy constraints.
    If content is unsafe, it blocks further workflow execution.
    """

    def __init__(self, llm):
        super().__init__(
            name="Guardrail",
            description="Safety and policy checker",
            llm=llm,
            icon="🛡️",
        )

    async def execute(self, node_input, parent_outputs):
        """
        Validate input text for safety.

        Priority:
        1. Explicit node input
        2. Aggregated parent node outputs
        """
        text = node_input.get("input") or self.get_parent_data(parent_outputs)

        if not text:
            return {
                "success": False,
                "error": "No input provided for safety validation",
            }

        # ================================
        # Guardrail Prompt
        # ================================
        prompt = f"""
You are a strict content safety validator.

Analyze the input below and determine whether it violates
any safety, ethical, or policy constraints such as:
- harmful or illegal activity
- hate, harassment, or violence
- self-harm or explicit content
- unsafe or misleading instructions

Respond ONLY in valid JSON.

If the content is unsafe:
{{ "allowed": false, "reason": "<short explanation>" }}

If the content is safe:
{{ "allowed": true }}

Input:
\"\"\"
{text}
\"\"\"
"""

        response = self.llm(prompt)

        # ================================
        # Blocking logic
        # ================================
        if '"allowed": false' in response:
            return {
                "success": False,
                "blocked": True,
                "data": response,
                "node_type": "guardrail",
            }

        return {
            "success": True,
            "data": text,
            "node_type": "guardrail",
        }

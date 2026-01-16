# backend/agents/summarizer.py

from agent_base import BaseAgent


class SummarizerAgent(BaseAgent):
    """
    Agent responsible for summarizing text input.
    Supports different summary lengths via `mode`.
    """

    def __init__(self, llm):
        super().__init__(
            name="Summarizer",
            description="Summarizes text",
            llm=llm,
            icon="📝",
        )

    async def execute(self, node_input, parent_outputs):
        # ================================
        # Input Resolution
        # ================================
        text = node_input.get("input") or self.get_parent_data(parent_outputs)

        if not text:
            return {
                "success": False,
                "error": "No text to summarize",
            }

        # ================================
        # Summary Configuration
        # ================================
        mode = node_input.get("mode", "medium")

        word_limits = {
            "small": 50,
            "medium": 100,
            "large": 400,
        }

        limit = word_limits.get(mode, 100)

        # ================================
        # Prompt Construction
        # ================================
        prompt = f"""
Summarize the following text in approximately {limit} words.

Text:
{text}
"""

        # ================================
        # LLM Execution
        # ================================
        summary = self.llm(prompt)

        return {
            "success": True,
            "data": summary,
            "mode": mode,
            "node_type": "summarizer",
        }

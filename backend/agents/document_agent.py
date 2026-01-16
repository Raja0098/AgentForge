from agent_base import BaseAgent

class DocumentAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="AI Summarizer",
            description="Uses LLMs to summarize provided context."
        )

    async def execute(self, node_input, parent_outputs):
        # Your logic here...
        return {"success": True, "data": "Summary result..."}
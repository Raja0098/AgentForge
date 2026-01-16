# backend/agents/llm.py

from agent_base import BaseAgent


class LLMAgent(BaseAgent):
    """
    Core LLM agent.
    Executes a Gemini-powered language model with configurable prompt behavior.
    """

    def __init__(self, llm):
        super().__init__(
            name="LLM Agent",
            description="Gemini-powered language model with configurable prompts",
            llm=llm,
            icon="🤖",
        )

    async def execute(self, node_input, parent_outputs):
        # ================================
        # Configuration
        # ================================
        user_prompt = node_input.get("prompt", "")
        description = node_input.get("description", "")
        execution_mode = node_input.get("execution_mode", "user_prompt")

        # ================================
        # Parent Data
        # ================================
        parent_data = self.get_parent_data(parent_outputs)

        # ================================
        # Prompt Construction
        # ================================
        if execution_mode == "system_prompt":
            # Treat prompt as system-level instruction
            final_prompt = f"""System Instruction:
{user_prompt}

User Input:
{parent_data}"""

        elif execution_mode == "combined":
            # Combine prompt and input data
            final_prompt = f"""{user_prompt}

Input Data:
{parent_data}"""

        else:
            # Default: user prompt mode
            if user_prompt:
                final_prompt = f"""{user_prompt}

{parent_data}"""
            else:
                final_prompt = parent_data

        if not final_prompt.strip():
            return {
                "success": False,
                "error": "No input or prompt provided",
            }

        # ================================
        # LLM Execution
        # ================================
        try:
            output = self.llm(final_prompt)

            return {
                "success": True,
                "data": output,
                "node_type": "llm",
                "prompt_used": user_prompt,
                "description": description,
                "execution_mode": execution_mode,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"LLM execution failed: {str(e)}",
                "node_type": "llm",
            }

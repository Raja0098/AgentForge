# backend/agents/llm_with_tools.py

from agent_base import BaseAgent


class LLMWithToolsAgent(BaseAgent):
    """
    LLM agent capable of deciding whether to call external tools
    using a simple ReAct-style interaction loop.
    """

    def __init__(self, llm, available_tools=None):
        super().__init__(
            name="LLM with Tools",
            description="LLM that can decide to use tools (ReAct framework)",
            llm=llm,
            icon="🤖",
        )
        self.available_tools = available_tools or {}

    async def execute(self, node_input, parent_outputs):
        """
        Execute the LLM with optional tool usage.
        """
        user_prompt = node_input.get("prompt", "")
        enable_tools = node_input.get("enable_tools", False)

        parent_data = self.get_parent_data(parent_outputs)

        if not user_prompt and not parent_data:
            return {
                "success": False,
                "error": "No input provided",
            }

        # ================================
        # Initial Prompt
        # ================================
        if user_prompt:
            base_prompt = f"""{user_prompt}

Input:
{parent_data}"""
        else:
            base_prompt = parent_data

        # ================================
        # No tools → simple LLM call
        # ================================
        if not enable_tools or not self.available_tools:
            try:
                output = self.llm(base_prompt)
                return {
                    "success": True,
                    "data": output,
                    "node_type": "llm",
                    "tool_used": None,
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                }

        # ================================
        # ReAct Prompt
        # ================================
        tools_description = "\n".join(
            f"- {name}: {tool['description']}"
            for name, tool in self.available_tools.items()
        )

        react_prompt = f"""{base_prompt}

Available Tools (you may use ONE tool if needed):
{tools_description}

Instructions:
- If a tool is required, respond ONLY in the format:
  TOOL_CALL: <tool_name> | <input_for_tool>
- Otherwise, respond with the final answer directly.

Response:
"""

        try:
            # Step 1: LLM decision
            decision = self.llm(react_prompt).strip()

            # ================================
            # Tool Invocation
            # ================================
            if decision.startswith("TOOL_CALL:"):
                tool_call = decision.replace("TOOL_CALL:", "").strip()
                parts = tool_call.split("|", 1)

                if len(parts) != 2:
                    return {
                        "success": True,
                        "data": decision,
                        "node_type": "llm",
                        "tool_used": None,
                    }

                tool_name = parts[0].strip()
                tool_input = parts[1].strip()

                if tool_name in self.available_tools:
                    tool_result = await self._execute_tool(tool_name, tool_input)

                    final_prompt = f"""Original Query:
{base_prompt}

Tool Used: {tool_name}
Tool Output:
{tool_result}

Using the tool output, provide a complete and accurate answer:
"""

                    final_answer = self.llm(final_prompt)

                    return {
                        "success": True,
                        "data": final_answer,
                        "node_type": "llm_with_tools",
                        "tool_used": tool_name,
                        "tool_result": (
                            tool_result[:200] + "..."
                            if len(tool_result) > 200
                            else tool_result
                        ),
                    }

            # ================================
            # No tool required
            # ================================
            return {
                "success": True,
                "data": decision,
                "node_type": "llm",
                "tool_used": None,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"LLM execution failed: {str(e)}",
            }

    async def _execute_tool(self, tool_name, tool_input):
        """
        Execute a single tool safely and return its textual output.
        """
        tool_info = self.available_tools.get(tool_name)

        if not tool_info:
            return f"Error: Tool '{tool_name}' not found"

        try:
            tool_instance = tool_info["instance"]
            result = await tool_instance.execute(
                {"value": tool_input, "query": tool_input},
                {},
            )

            if result.get("success"):
                return result.get("data", "No data returned")

            return f"Tool error: {result.get('error', 'Unknown error')}"

        except Exception as e:
            return f"Tool execution error: {str(e)}"

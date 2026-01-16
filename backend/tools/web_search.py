# backend/tools/web_search.py

import json

from agent_base import BaseTool
from duckduckgo_search import DDGS


class WebSearchTool(BaseTool):
    """
    Tool for performing web searches using DuckDuckGo
    and returning structured + readable results.
    """

    def __init__(self):
        super().__init__(
            name="Web Search",
            description="Search the web using DuckDuckGo",
            icon="🔍",
        )

    async def execute(self, node_input, parent_outputs):
        """
        Execute a web search and return formatted results.
        """

        # ================================
        # Resolve Search Query
        # ================================
        query = (
            node_input.get("query")
            or node_input.get("value")
            or self.get_parent_data(parent_outputs)
        )

        max_results = node_input.get("max_results", 5)

        if not query:
            return {
                "success": False,
                "error": "No search query provided",
            }

        try:
            # ================================
            # Perform Search
            # ================================
            ddgs = DDGS()
            results = list(ddgs.text(query, max_results=max_results))

            # ================================
            # Structure Results
            # ================================
            formatted_results = {
                "query": query,
                "results_count": len(results),
                "results": [],
            }

            for index, result in enumerate(results, start=1):
                formatted_results["results"].append({
                    "rank": index,
                    "title": result.get("title", ""),
                    "url": result.get("href", ""),
                    "snippet": result.get("body", ""),
                })

            # ================================
            # Build Human-Readable Summary
            # ================================
            summary_lines = [f"Search Results for: {query}", ""]

            for r in formatted_results["results"]:
                summary_lines.extend([
                    f"{r['rank']}. {r['title']}",
                    r["snippet"],
                    f"URL: {r['url']}",
                    "",
                ])

            summary = "\n".join(summary_lines)

            return {
                "success": True,
                "data": summary,
                "json_data": json.dumps(formatted_results, indent=2),
                "node_type": "web_search",
                "results_count": len(results),
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Web search failed: {str(e)}",
                "node_type": "web_search",
            }

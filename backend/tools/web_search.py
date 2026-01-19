import json
from agent_base import BaseTool
from duckduckgo_search import DDGS

class WebSearchTool(BaseTool):
    """Tool for performing India-localized web searches with quality filtering."""
    
    def __init__(self):
        super().__init__(
            name="Web Search",
            description="Searches the web for Indian context with quality filtering.",
            icon="🔍",
        )
        self.region = "in-en"
        self.blocked_sites = [
            "dictionary.cambridge.org",
            "merriam-webster.com", 
            "dictionary.com"
        ]
    
    def _clean_query(self, query: str) -> str:
        """Remove noise words and block low-quality sites."""
        noise_words = {"meaning", "definition", "translate"}
        
        # Keep meaningful words
        words = [w for w in query.lower().split() if w not in noise_words]
        clean = " ".join(words) if words else query
        
        # Block dictionary sites only
        blocks = " ".join(f"-site:{site}" for site in self.blocked_sites)
        return f"{clean} {blocks}".strip()
    
    async def execute(self, node_input, parent_outputs):
        # Get query
        query = (
            node_input.get("query") 
            or node_input.get("value") 
            or self.get_parent_data(parent_outputs)
        )
        
        if not query:
            return {"success": False, "error": "No query provided"}
        
        max_results = node_input.get("max_results", 8)
        processed_query = self._clean_query(query)
        
        try:
            # Search with India region
            with DDGS() as ddgs:
                results = list(ddgs.text(
                    processed_query,
                    region=self.region,
                    safesearch="moderate",
                    backend="html",
                    max_results=max_results
                ))
            
            # Light filtering - just remove empty snippets
            valid = [r for r in results if r.get("body", "").strip()][:6]
            
            if not valid:
                return {
                    "success": False,
                    "error": "No results found. Try a different query.",
                    "node_type": "web_search"
                }
            
            # Format for AI
            summary = f"### Search: {query}\n\n"
            for i, r in enumerate(valid, 1):
                summary += (
                    f"**{i}. {r.get('title', 'No title')}**\n"
                    f"{r.get('body', '')}\n"
                    f"Source: {r.get('href', '')}\n\n"
                )
            
            return {
                "success": True,
                "data": summary,
                "json_data": json.dumps({
                    "query": query,
                    "processed": processed_query,
                    "region": self.region,
                    "results": [
                        {
                            "rank": i,
                            "title": r.get("title", ""),
                            "url": r.get("href", ""),
                            "snippet": r.get("body", "")
                        } for i, r in enumerate(valid, 1)
                    ]
                }, indent=2),
                "node_type": "web_search",
                "count": len(valid)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Search failed: {str(e)}",
                "node_type": "web_search"
            }
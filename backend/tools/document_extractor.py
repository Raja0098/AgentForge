from agent_base import BaseTool
from docling.document_converter import DocumentConverter

class DocumentExtractorTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="Document Extractor",
            description="Extracts markdown text from documents using Docling",
            icon="📄"
        )
        self.converter = DocumentConverter()

    async def execute(self, node_input, parent_outputs):
        """Extract markdown directly from the source"""
        
        # Determine source (path or URL)
        source = node_input.get("value") or self.get_parent_data(parent_outputs)
        
        if not source:
            return {"success": False, "error": "No source path or URL provided"}
        
        try:
            # Simple conversion logic as requested
            doc = self.converter.convert(source).document
            markdown_output = doc.export_to_markdown()
            
            return {
                "success": True,
                "data": markdown_output,
                "node_type": "document_extractor"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "node_type": "document_extractor"
            }

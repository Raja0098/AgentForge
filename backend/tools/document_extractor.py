# backend/tools/document_extractor.py

from agent_base import BaseTool
from docling.document_converter import DocumentConverter
import json


class DocumentExtractorTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="Document Extractor",
            description="Extracts structured data from PDFs and images using Docling",
            icon="📄"
        )
        self.converter = DocumentConverter()

    async def execute(self, node_input, parent_outputs):
        """Extract text and structure from documents"""
        
        # Get file path from parent or config
        file_path = node_input.get("value") or self.get_parent_data(parent_outputs)
        
        if not file_path:
            return {"success": False, "error": "No file path provided"}
        
        try:
            # Convert document
            result = self.converter.convert(file_path)
            
            # Extract structured content
            extracted_data = {
                "text": result.document.export_to_markdown(),
                "metadata": {
                    "pages": len(result.document.pages) if hasattr(result.document, 'pages') else 1,
                    "source": file_path
                },
                "tables": [],
                "images": []
            }
            
            # Extract tables if available
            if hasattr(result.document, 'tables'):
                for table in result.document.tables:
                    extracted_data["tables"].append({
                        "data": table.export_to_dataframe().to_dict() if hasattr(table, 'export_to_dataframe') else str(table)
                    })
            
            # Return as JSON string for next node
            json_output = json.dumps(extracted_data, indent=2)
            
            return {
                "success": True,
                "data": json_output,
                "node_type": "document_extractor",
                "extracted_pages": extracted_data["metadata"]["pages"],
                "has_tables": len(extracted_data["tables"]) > 0
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Document extraction failed: {str(e)}",
                "node_type": "document_extractor"
            }

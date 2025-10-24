# ABOUTME: Document tracking and management tools
# ABOUTME: Track created Excel, Word, PowerPoint, PDF files

from claude_agent_sdk import tool
from typing import Any, Dict
from pathlib import Path


class DocumentTools:
    def __init__(self, memory_manager, session_id=None, docs_dir: str = "storage/documents"):
        self.memory = memory_manager
        self.session_id = session_id
        self.docs_dir = Path(docs_dir)
        self.docs_dir.mkdir(parents=True, exist_ok=True)

    def get_tools(self):
        """Return list of document tracking tools"""
        return [
            self._register_document_tool(),
            self._list_documents_tool(),
            self._read_pdf_tool()
        ]

    def _register_document_tool(self):
        @tool(
            "register_document",
            "Register a created document (Excel, Word, PowerPoint, PDF) in the database for tracking.",
            {
                "filename": str,
                "file_type": str,  # xlsx, docx, pptx, pdf
                "description": str  # What the document contains
            }
        )
        async def register_document(args: Dict[str, Any]) -> Dict[str, Any]:
            filename = args["filename"]
            file_type = args["file_type"]
            description = args.get("description", "")

            # Determine file path
            file_path = str(self.docs_dir / filename)

            # Check if file exists
            if not Path(file_path).exists():
                return {
                    "content": [{
                        "type": "text",
                        "text": f"[WARN] File not found: {file_path}\nRegistering anyway for tracking."
                    }]
                }

            # Save to database
            doc_id = await self.memory.save_document(
                filename=filename,
                file_type=file_type,
                file_path=file_path,
                description=description,
                session_id=self.session_id
            )

            return {
                "content": [{
                    "type": "text",
                    "text": f"[OK] Document registered\n"
                           f"ID: {doc_id}\n"
                           f"File: {filename}\n"
                           f"Type: {file_type}\n"
                           f"Path: {file_path}"
                }]
            }

        return register_document

    def _list_documents_tool(self):
        @tool(
            "list_documents",
            "List created documents with optional type filter (xlsx, docx, pptx, pdf).",
            {
                "file_type": str  # Optional: xlsx, docx, pptx, pdf
            }
        )
        async def list_documents(args: Dict[str, Any]) -> Dict[str, Any]:
            file_type = args.get("file_type")

            # Query database
            docs = await self.memory.list_documents(file_type=file_type)

            if not docs:
                filter_msg = f" of type '{file_type}'" if file_type else ""
                return {
                    "content": [{
                        "type": "text",
                        "text": f"[INFO] No documents found{filter_msg}"
                    }]
                }

            # Format output
            output = f"[OK] Found {len(docs)} document(s):\n\n"
            for doc in docs:
                output += f"**{doc['filename']}** ({doc['file_type']})\n"
                output += f"  Created: {doc['created_at']}\n"
                output += f"  Path: {doc['file_path']}\n"
                if doc['description']:
                    output += f"  Description: {doc['description']}\n"
                output += "\n"

            return {
                "content": [{
                    "type": "text",
                    "text": output
                }]
            }

        return list_documents

    def _read_pdf_tool(self):
        @tool(
            "read_pdf",
            "Extract text content from a PDF file. Use bash with markitdown or pypdf for extraction.",
            {
                "file_path": str  # Path to PDF file
            }
        )
        async def read_pdf(args: Dict[str, Any]) -> Dict[str, Any]:
            file_path = args["file_path"]

            # Check if file exists
            if not Path(file_path).exists():
                return {
                    "content": [{
                        "type": "text",
                        "text": f"[ERROR] File not found: {file_path}"
                    }]
                }

            return {
                "content": [{
                    "type": "text",
                    "text": f"[INFO] To read PDF, use bash command:\n"
                           f"  pip install markitdown --break-system-packages\n"
                           f"  python -m markitdown {file_path}\n\n"
                           f"Or use pypdf:\n"
                           f"  pip install pypdf\n"
                           f"  python -c \"from pypdf import PdfReader; r=PdfReader('{file_path}'); print(''.join(p.extract_text() for p in r.pages))\"\n\n"
                           f"You'll be prompted to approve the bash command."
                    }]
                }

        return read_pdf

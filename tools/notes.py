# ABOUTME: Note management tools
# ABOUTME: Create, search, and retrieve notes with markdown storage

from claude_agent_sdk import tool
from typing import Any, Dict, List
from pathlib import Path
from datetime import datetime
import json


class NoteTools:
    def __init__(self, memory_manager, notes_dir: str = "storage/notes"):
        self.memory = memory_manager
        self.notes_dir = Path(notes_dir)
        self.notes_dir.mkdir(parents=True, exist_ok=True)

    def get_tools(self):
        """Return list of note-related tools"""
        return [
            self._create_note_tool(),
            self._search_notes_tool(),
            self._list_recent_notes_tool()
        ]

    def _create_note_tool(self):
        @tool(
            "create_note",
            "Create a new note with title, content, and optional tags. Saves as markdown file and database entry.",
            {
                "title": str,
                "content": str,
                "tags": list  # Optional list of tag strings
            }
        )
        async def create_note(args: Dict[str, Any]) -> Dict[str, Any]:
            title = args["title"]
            content = args["content"]
            tags = args.get("tags", [])

            # Generate filename from title and timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in title)
            safe_title = safe_title.replace(' ', '_')[:50]
            filename = f"{timestamp}_{safe_title}.md"
            file_path = self.notes_dir / filename

            # Create markdown content
            md_content = f"# {title}\n\n"
            if tags:
                md_content += f"**Tags:** {', '.join(tags)}\n\n"
            md_content += f"**Created:** {datetime.now().isoformat()}\n\n"
            md_content += "---\n\n"
            md_content += content

            # Save to file
            file_path.write_text(md_content, encoding="utf-8")

            # Save to database
            note_id = await self.memory.save_note(
                title=title,
                content=content,
                tags=tags,
                file_path=str(file_path),
                session_id=None  # Will be set by client
            )

            return {
                "content": [{
                    "type": "text",
                    "text": f"[OK] Note created: {title}\nID: {note_id}\nFile: {file_path}\nTags: {', '.join(tags) if tags else 'none'}"
                }]
            }

        return create_note

    def _search_notes_tool(self):
        @tool(
            "search_notes",
            "Search notes by text query or tags. Returns matching notes with metadata.",
            {
                "query": str,  # Optional text search
                "tags": list   # Optional tag filter
            }
        )
        async def search_notes(args: Dict[str, Any]) -> Dict[str, Any]:
            query = args.get("query")
            tags = args.get("tags")

            if not query and not tags:
                return {
                    "content": [{
                        "type": "text",
                        "text": "[ERROR] Must provide either query or tags"
                    }]
                }

            results = await self.memory.search_notes(query=query, tags=tags)

            if not results:
                return {
                    "content": [{
                        "type": "text",
                        "text": f"[INFO] No notes found for query='{query}' tags={tags}"
                    }]
                }

            # Format results
            output = f"[OK] Found {len(results)} note(s):\n\n"
            for note in results[:10]:  # Limit to 10 results
                output += f"**{note['title']}**\n"
                output += f"  ID: {note['id']}\n"
                output += f"  Created: {note['created_at']}\n"
                output += f"  Tags: {', '.join(note['tags']) if note['tags'] else 'none'}\n"
                output += f"  Preview: {note['content'][:100]}...\n\n"

            if len(results) > 10:
                output += f"... and {len(results) - 10} more\n"

            return {
                "content": [{
                    "type": "text",
                    "text": output
                }]
            }

        return search_notes

    def _list_recent_notes_tool(self):
        @tool(
            "list_recent_notes",
            "List most recent notes (up to 20)",
            {}
        )
        async def list_recent_notes(args: Dict[str, Any]) -> Dict[str, Any]:
            results = await self.memory.search_notes()

            if not results:
                return {
                    "content": [{
                        "type": "text",
                        "text": "[INFO] No notes found"
                    }]
                }

            output = f"[OK] Recent notes ({len(results)}):\n\n"
            for note in results:
                output += f"- {note['title']}\n"
                output += f"  Created: {note['created_at']}\n"
                if note['tags']:
                    output += f"  Tags: {', '.join(note['tags'])}\n"

            return {
                "content": [{
                    "type": "text",
                    "text": output
                }]
            }

        return list_recent_notes

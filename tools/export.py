# ABOUTME: Data export and import tools
# ABOUTME: Backup and restore notes, research, sessions to/from JSON

from claude_agent_sdk import tool
from typing import Any, Dict, List
from pathlib import Path
import json
from datetime import datetime
import aiosqlite


class ExportTools:
    def __init__(self, memory_manager, export_dir: str = "storage/exports"):
        self.memory = memory_manager
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def get_tools(self):
        """Return list of export/import tools"""
        return [
            self._export_data_tool(),
            self._import_data_tool(),
            self._list_exports_tool()
        ]

    def _export_data_tool(self):
        @tool(
            "export_data",
            "Export all data (notes, research, sessions, suggestions, documents) to JSON backup file.",
            {
                "filename": str  # Optional custom filename
            }
        )
        async def export_data(args: Dict[str, Any]) -> Dict[str, Any]:
            custom_filename = args.get("filename")

            # Generate filename
            if custom_filename:
                filename = custom_filename if custom_filename.endswith('.json') else f"{custom_filename}.json"
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"backup_{timestamp}.json"

            filepath = self.export_dir / filename

            try:
                # Gather all data
                export_data = {
                    "exported_at": datetime.utcnow().isoformat(),
                    "version": "1.0",
                    "research": [],
                    "sessions": [],
                    "documents": []
                }

                async with aiosqlite.connect(self.memory.db_path) as db:
                    # Export research
                    cursor = await db.execute("SELECT * FROM research")
                    columns = [desc[0] for desc in cursor.description]
                    for row in await cursor.fetchall():
                        export_data["research"].append(dict(zip(columns, row)))

                    # Export sessions
                    cursor = await db.execute("SELECT * FROM sessions")
                    columns = [desc[0] for desc in cursor.description]
                    for row in await cursor.fetchall():
                        export_data["sessions"].append(dict(zip(columns, row)))

                    # Export documents
                    cursor = await db.execute("SELECT * FROM documents")
                    columns = [desc[0] for desc in cursor.description]
                    for row in await cursor.fetchall():
                        export_data["documents"].append(dict(zip(columns, row)))

                # Write to file
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)

                # Get file size
                file_size = filepath.stat().st_size
                size_kb = file_size / 1024

                return {
                    "content": [{
                        "type": "text",
                        "text": f"[OK] Data exported successfully\n\n"
                               f"File: {filepath}\n"
                               f"Size: {size_kb:.1f} KB\n\n"
                               f"Exported:\n"
                               f"- {len(export_data['research'])} research items\n"
                               f"- {len(export_data['sessions'])} sessions\n"
                               f"- {len(export_data['documents'])} documents"
                    }]
                }

            except Exception as e:
                return {
                    "content": [{
                        "type": "text",
                        "text": f"[ERROR] Export failed: {str(e)}"
                    }]
                }

        return export_data

    def _import_data_tool(self):
        @tool(
            "import_data",
            "Import data from a JSON backup file. Merges with existing data (no duplicates).",
            {
                "file_path": str
            }
        )
        async def import_data(args: Dict[str, Any]) -> Dict[str, Any]:
            file_path = Path(args["file_path"])

            if not file_path.exists():
                # Try relative to export_dir
                file_path = self.export_dir / file_path.name
                if not file_path.exists():
                    return {
                        "content": [{
                            "type": "text",
                            "text": f"[ERROR] File not found: {args['file_path']}\n\n"
                                   f"Available exports in {self.export_dir}:\n" +
                                   "\n".join(f"- {f.name}" for f in self.export_dir.glob("*.json"))
                        }]
                    }

            try:
                # Load JSON
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                imported = {
                    "research": 0,
                    "sessions": 0,
                    "documents": 0
                }

                async with aiosqlite.connect(self.memory.db_path) as db:
                    # Import research
                    for item in data.get("research", []):
                        try:
                            await db.execute(
                                """INSERT OR IGNORE INTO research
                                   (query, sources, analysis, created_at, session_id)
                                   VALUES (?, ?, ?, ?, ?)""",
                                (item['query'], item['sources'], item['analysis'],
                                 item['created_at'], item.get('session_id'))
                            )
                            imported["research"] += 1
                        except KeyError:
                            continue

                    # Import documents
                    for doc in data.get("documents", []):
                        try:
                            await db.execute(
                                """INSERT OR IGNORE INTO documents
                                   (filename, file_type, file_path, description, created_at, session_id)
                                   VALUES (?, ?, ?, ?, ?, ?)""",
                                (doc['filename'], doc['file_type'], doc['file_path'],
                                 doc.get('description'), doc['created_at'], doc.get('session_id'))
                            )
                            imported["documents"] += 1
                        except KeyError:
                            continue

                    await db.commit()

                return {
                    "content": [{
                        "type": "text",
                        "text": f"[OK] Data imported successfully from: {file_path.name}\n\n"
                               f"Imported:\n"
                               f"- {imported['research']} research items\n"
                               f"- {imported['documents']} documents\n\n"
                               f"[INFO] Duplicate entries were skipped"
                    }]
                }

            except json.JSONDecodeError:
                return {
                    "content": [{
                        "type": "text",
                        "text": f"[ERROR] Invalid JSON file: {file_path}"
                    }]
                }
            except Exception as e:
                return {
                    "content": [{
                        "type": "text",
                        "text": f"[ERROR] Import failed: {str(e)}"
                    }]
                }

        return import_data

    def _list_exports_tool(self):
        @tool(
            "list_exports",
            "List all available export/backup files.",
            {}
        )
        async def list_exports(args: Dict[str, Any]) -> Dict[str, Any]:
            exports = list(self.export_dir.glob("*.json"))

            if not exports:
                return {
                    "content": [{
                        "type": "text",
                        "text": f"[INFO] No export files found in: {self.export_dir}"
                    }]
                }

            # Sort by modification time (newest first)
            exports.sort(key=lambda p: p.stat().st_mtime, reverse=True)

            output = f"[OK] Found {len(exports)} export file(s):\n\n"
            for exp in exports:
                stat = exp.stat()
                size_kb = stat.st_size / 1024
                modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                output += f"- **{exp.name}**\n"
                output += f"  Size: {size_kb:.1f} KB\n"
                output += f"  Modified: {modified}\n\n"

            output += f"\n[TIP] Use import_data tool to restore from any backup"

            return {
                "content": [{
                    "type": "text",
                    "text": output
                }]
            }

        return list_exports

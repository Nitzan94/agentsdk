# ABOUTME: Custom memory management tools
# ABOUTME: Save, retrieve, and delete persistent facts across sessions

from claude_agent_sdk import tool
from typing import Any, Dict


class MemoryTools:
    def __init__(self, memory_manager, session_id: str):
        self.memory = memory_manager
        self.session_id = session_id

    def get_tools(self):
        """Return list of memory management tools"""
        return [
            self._save_memory_tool(),
            self._list_memories_tool(),
            self._delete_memory_tool()
        ]

    def _save_memory_tool(self):
        @tool(
            "save_memory",
            "Save important fact to persistent memory. Facts persist across ALL sessions. Use for business info, preferences, personal details. Categories: business, preferences, personal, technical.",
            {
                "category": str,  # Memory category (business, preferences, personal, technical)
                "key": str,       # Memory key (business_type, email_format, timezone, etc.)
                "value": str      # Memory value
            }
        )
        async def save_memory(args: Dict[str, Any]) -> Dict[str, Any]:
            category = args["category"]
            key = args["key"]
            value = args["value"]

            try:
                await self.memory.save_memory(
                    category=category,
                    key=key,
                    value=value,
                    session_id=self.session_id
                )

                return {
                    "content": [{
                        "type": "text",
                        "text": f"[OK] Saved memory: {category}/{key} = {value}"
                    }]
                }
            except Exception as e:
                return {
                    "content": [{
                        "type": "text",
                        "text": f"[ERROR] Failed to save memory: {str(e)}"
                    }],
                    "isError": True
                }

        return save_memory

    def _list_memories_tool(self):
        @tool(
            "list_memories",
            "List all saved memories or filter by category. Shows what I permanently remember about you.",
            {
                "category": str  # Optional category filter (business, preferences, personal, technical)
            }
        )
        async def list_memories(args: Dict[str, Any]) -> Dict[str, Any]:
            category = args.get("category")

            try:
                memories = await self.memory.get_memories(category=category)

                if not memories:
                    msg = f"No memories found" + (f" in category '{category}'" if category else "")
                    return {
                        "content": [{
                            "type": "text",
                            "text": f"[INFO] {msg}"
                        }]
                    }

                # Format memories by category
                by_category = {}
                for mem in memories:
                    cat = mem['category']
                    if cat not in by_category:
                        by_category[cat] = []
                    by_category[cat].append(f"  - {mem['key']}: {mem['value']}")

                output = []
                for cat, items in by_category.items():
                    output.append(f"{cat.upper()}:")
                    output.extend(items)

                return {
                    "content": [{
                        "type": "text",
                        "text": "\n".join(output)
                    }]
                }
            except Exception as e:
                return {
                    "content": [{
                        "type": "text",
                        "text": f"[ERROR] Failed to list memories: {str(e)}"
                    }],
                    "isError": True
                }

        return list_memories

    def _delete_memory_tool(self):
        @tool(
            "delete_memory",
            "Delete specific memory entry. Use when information becomes outdated or incorrect.",
            {
                "category": str,  # Memory category
                "key": str        # Memory key to delete
            }
        )
        async def delete_memory(args: Dict[str, Any]) -> Dict[str, Any]:
            category = args["category"]
            key = args["key"]

            try:
                deleted = await self.memory.delete_memory(category, key)

                if deleted:
                    return {
                        "content": [{
                            "type": "text",
                            "text": f"[OK] Deleted memory: {category}/{key}"
                        }]
                    }
                else:
                    return {
                        "content": [{
                            "type": "text",
                            "text": f"[WARN] Memory not found: {category}/{key}"
                        }]
                    }
            except Exception as e:
                return {
                    "content": [{
                        "type": "text",
                        "text": f"[ERROR] Failed to delete memory: {str(e)}"
                    }],
                    "isError": True
                }

        return delete_memory

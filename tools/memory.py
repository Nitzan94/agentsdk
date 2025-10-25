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
            self._delete_memory_tool(),
            self._list_sessions_tool(),
            self._view_session_tool(),
            self._search_history_tool()
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

    def _list_sessions_tool(self):
        @tool(
            "list_sessions",
            "List all conversation sessions with metadata. Shows when each session started, message count, cost.",
            {
                "limit": int  # Max sessions to return (default 20)
            }
        )
        async def list_sessions(args: Dict[str, Any]) -> Dict[str, Any]:
            limit = args.get("limit", 20)

            try:
                sessions = await self.memory.list_all_sessions(limit=limit)

                if not sessions:
                    return {
                        "content": [{
                            "type": "text",
                            "text": "[INFO] No sessions found"
                        }]
                    }

                output = f"[OK] Found {len(sessions)} session(s):\n\n"
                for sess in sessions:
                    is_current = sess['session_id'] == self.session_id
                    marker = " (CURRENT)" if is_current else ""

                    output += f"**Session: {sess['session_id'][:16]}...{marker}**\n"
                    output += f"  Started: {sess['started_at']}\n"
                    output += f"  Last Active: {sess['last_active_at']}\n"
                    output += f"  Messages: {sess['message_count']}\n"
                    output += f"  Cost: ${sess['total_cost_usd']:.4f}\n\n"

                return {
                    "content": [{
                        "type": "text",
                        "text": output
                    }]
                }
            except Exception as e:
                return {
                    "content": [{
                        "type": "text",
                        "text": f"[ERROR] Failed to list sessions: {str(e)}"
                    }],
                    "isError": True
                }

        return list_sessions

    def _view_session_tool(self):
        @tool(
            "view_session",
            "View conversation history from a specific session. Use list_sessions to find session IDs.",
            {
                "session_id": str,  # Session ID to view
                "limit": int        # Max messages to return (default 50)
            }
        )
        async def view_session(args: Dict[str, Any]) -> Dict[str, Any]:
            session_id = args["session_id"]
            limit = args.get("limit", 50)

            try:
                messages = await self.memory.get_session_history(session_id, limit=limit)

                if not messages:
                    return {
                        "content": [{
                            "type": "text",
                            "text": f"[INFO] No messages found in session {session_id[:16]}..."
                        }]
                    }

                output = f"[OK] Session {session_id[:16]}... ({len(messages)} messages):\n\n"

                for msg in messages:
                    role = msg['role']
                    content = msg['content'][:200]  # Truncate long messages
                    timestamp = msg['timestamp']

                    if role == 'user':
                        output += f"👤 User ({timestamp}):\n{content}\n\n"
                    elif role == 'assistant':
                        output += f"🤖 Assistant ({timestamp}):\n{content}\n\n"
                    # Skip tool messages

                return {
                    "content": [{
                        "type": "text",
                        "text": output
                    }]
                }
            except Exception as e:
                return {
                    "content": [{
                        "type": "text",
                        "text": f"[ERROR] Failed to view session: {str(e)}"
                    }],
                    "isError": True
                }

        return view_session

    def _search_history_tool(self):
        @tool(
            "search_history",
            "Search across ALL past conversations for specific keywords or topics.",
            {
                "query": str,  # Search query
                "limit": int   # Max results (default 20)
            }
        )
        async def search_history(args: Dict[str, Any]) -> Dict[str, Any]:
            query = args["query"]
            limit = args.get("limit", 20)

            try:
                results = await self.memory.search_all_messages(query, limit=limit)

                if not results:
                    return {
                        "content": [{
                            "type": "text",
                            "text": f"[INFO] No messages found matching: {query}"
                        }]
                    }

                output = f"[OK] Found {len(results)} message(s) matching '{query}':\n\n"

                for msg in results:
                    role = msg['role']
                    content = msg['content'][:150]  # Truncate
                    timestamp = msg['timestamp']
                    session_id = msg['session_id'][:16]

                    prefix = "👤" if role == 'user' else "🤖"
                    output += f"{prefix} {role.title()} ({timestamp})\n"
                    output += f"   Session: {session_id}...\n"
                    output += f"   {content}...\n\n"

                return {
                    "content": [{
                        "type": "text",
                        "text": output
                    }]
                }
            except Exception as e:
                return {
                    "content": [{
                        "type": "text",
                        "text": f"[ERROR] Search failed: {str(e)}"
                    }],
                    "isError": True
                }

        return search_history

# ABOUTME: SQLite-based memory and session management
# ABOUTME: Handles persistent storage of conversations, notes, research

import aiosqlite
import json
from datetime import datetime, UTC
from pathlib import Path
from typing import Optional, Dict, List, Any


class MemoryManager:
    def __init__(self, db_path: str = "storage/agent.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    async def initialize(self):
        """Create database schema"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    started_at TEXT NOT NULL,
                    last_active_at TEXT NOT NULL,
                    total_cost_usd REAL DEFAULT 0.0,
                    message_count INTEGER DEFAULT 0
                )
            """)

            await db.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                )
            """)


            await db.execute("""
                CREATE TABLE IF NOT EXISTS research (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    sources TEXT NOT NULL,
                    analysis TEXT,
                    created_at TEXT NOT NULL,
                    session_id TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                )
            """)


            await db.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    session_id TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                )
            """)

            await db.execute("""
                CREATE TABLE IF NOT EXISTS custom_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    session_id TEXT,
                    UNIQUE(category, key),
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                )
            """)

            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_memory_category ON custom_memory(category)
            """)

            await db.commit()

    async def create_session(self, session_id: str) -> str:
        """Create new session"""
        now = datetime.now(UTC).isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO sessions (id, started_at, last_active_at) VALUES (?, ?, ?)",
                (session_id, now, now)
            )
            await db.commit()
        return session_id

    async def get_last_session_id(self) -> Optional[str]:
        """Get most recent session ID"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT id FROM sessions ORDER BY last_active_at DESC LIMIT 1"
            )
            row = await cursor.fetchone()
            return row[0] if row else None

    async def update_session(self, session_id: str, cost_usd: float = 0.0, message_count: int = 0):
        """Update session stats"""
        now = datetime.now(UTC).isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """UPDATE sessions
                   SET last_active_at = ?,
                       total_cost_usd = total_cost_usd + ?,
                       message_count = message_count + ?
                   WHERE id = ?""",
                (now, cost_usd, message_count, session_id)
            )
            await db.commit()

    async def save_message(self, session_id: str, role: str, content: str, message_type: str = "text"):
        """Save conversation message

        Args:
            session_id: Session identifier
            role: Message role (user, assistant, tool)
            content: Message content (text or JSON for tool messages)
            message_type: Message type (text, tool_use, tool_result)
        """
        now = datetime.now(UTC).isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO messages (session_id, timestamp, role, content) VALUES (?, ?, ?, ?)",
                (session_id, now, role, content)
            )
            await db.commit()

    async def get_session_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve conversation history"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """SELECT timestamp, role, content
                   FROM messages
                   WHERE session_id = ?
                   ORDER BY timestamp DESC
                   LIMIT ?""",
                (session_id, limit)
            )
            rows = await cursor.fetchall()
            return [
                {"timestamp": r[0], "role": r[1], "content": r[2]}
                for r in reversed(rows)
            ]

    async def list_all_sessions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """List all sessions with metadata"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """SELECT id, started_at, last_active_at, message_count, total_cost_usd
                   FROM sessions
                   ORDER BY last_active_at DESC
                   LIMIT ?""",
                (limit,)
            )
            rows = await cursor.fetchall()
            return [
                {
                    "session_id": r[0],
                    "started_at": r[1],
                    "last_active_at": r[2],
                    "message_count": r[3],
                    "total_cost_usd": r[4]
                }
                for r in rows
            ]

    async def search_all_messages(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search messages across all sessions"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """SELECT m.session_id, m.timestamp, m.role, m.content, s.started_at
                   FROM messages m
                   JOIN sessions s ON m.session_id = s.id
                   WHERE m.role IN ('user', 'assistant') AND m.content LIKE ?
                   ORDER BY m.timestamp DESC
                   LIMIT ?""",
                (f'%{query}%', limit)
            )
            rows = await cursor.fetchall()
            return [
                {
                    "session_id": r[0],
                    "timestamp": r[1],
                    "role": r[2],
                    "content": r[3],
                    "session_started": r[4]
                }
                for r in rows
            ]


    async def save_research(self, query: str, sources: List[str],
                           analysis: str, session_id: Optional[str] = None) -> int:
        """Save research results"""
        now = datetime.now(UTC).isoformat()
        sources_json = json.dumps(sources)
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """INSERT INTO research (query, sources, analysis, created_at, session_id)
                   VALUES (?, ?, ?, ?, ?)""",
                (query, sources_json, analysis, now, session_id)
            )
            await db.commit()
            return cursor.lastrowid


    async def save_document(self, filename: str, file_type: str, file_path: str,
                           description: Optional[str] = None,
                           session_id: Optional[str] = None) -> int:
        """Save document metadata"""
        now = datetime.now(UTC).isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """INSERT INTO documents (filename, file_type, file_path, description, created_at, session_id)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (filename, file_type, file_path, description, now, session_id)
            )
            await db.commit()
            return cursor.lastrowid

    async def list_documents(self, file_type: Optional[str] = None,
                            session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List documents with optional filters"""
        async with aiosqlite.connect(self.db_path) as db:
            if file_type and session_id:
                cursor = await db.execute(
                    """SELECT id, filename, file_type, file_path, description, created_at
                       FROM documents
                       WHERE file_type = ? AND session_id = ?
                       ORDER BY created_at DESC""",
                    (file_type, session_id)
                )
            elif file_type:
                cursor = await db.execute(
                    """SELECT id, filename, file_type, file_path, description, created_at
                       FROM documents
                       WHERE file_type = ?
                       ORDER BY created_at DESC""",
                    (file_type,)
                )
            elif session_id:
                cursor = await db.execute(
                    """SELECT id, filename, file_type, file_path, description, created_at
                       FROM documents
                       WHERE session_id = ?
                       ORDER BY created_at DESC""",
                    (session_id,)
                )
            else:
                cursor = await db.execute(
                    """SELECT id, filename, file_type, file_path, description, created_at
                       FROM documents
                       ORDER BY created_at DESC
                       LIMIT 20"""
                )

            rows = await cursor.fetchall()
            return [
                {
                    "id": r[0],
                    "filename": r[1],
                    "file_type": r[2],
                    "file_path": r[3],
                    "description": r[4],
                    "created_at": r[5]
                }
                for r in rows
            ]

    async def get_session_stats(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session statistics"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """SELECT started_at, last_active_at, total_cost_usd, message_count
                   FROM sessions WHERE id = ?""",
                (session_id,)
            )
            row = await cursor.fetchone()
            if not row:
                return None
            return {
                "started_at": row[0],
                "last_active_at": row[1],
                "total_cost_usd": row[2],
                "message_count": row[3]
            }

    async def save_memory(self, category: str, key: str, value: str,
                         session_id: Optional[str] = None) -> None:
        """Save or update custom memory fact

        Args:
            category: Memory category (business, preferences, personal, etc.)
            key: Memory key (business_type, email_format, etc.)
            value: Memory value
            session_id: Optional session where this was learned
        """
        now = datetime.now(UTC).isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT INTO custom_memory (category, key, value, created_at, updated_at, session_id)
                   VALUES (?, ?, ?, ?, ?, ?)
                   ON CONFLICT(category, key) DO UPDATE SET
                       value = excluded.value,
                       updated_at = excluded.updated_at,
                       session_id = excluded.session_id""",
                (category, key, value, now, now, session_id)
            )
            await db.commit()

    async def get_memories(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve custom memories

        Args:
            category: Optional category filter

        Returns:
            List of memory entries
        """
        async with aiosqlite.connect(self.db_path) as db:
            if category:
                cursor = await db.execute(
                    """SELECT category, key, value, created_at, updated_at
                       FROM custom_memory
                       WHERE category = ?
                       ORDER BY updated_at DESC""",
                    (category,)
                )
            else:
                cursor = await db.execute(
                    """SELECT category, key, value, created_at, updated_at
                       FROM custom_memory
                       ORDER BY category, updated_at DESC"""
                )

            rows = await cursor.fetchall()
            return [
                {
                    "category": r[0],
                    "key": r[1],
                    "value": r[2],
                    "created_at": r[3],
                    "updated_at": r[4]
                }
                for r in rows
            ]

    async def delete_memory(self, category: str, key: str) -> bool:
        """Delete specific memory entry

        Returns:
            True if deleted, False if not found
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "DELETE FROM custom_memory WHERE category = ? AND key = ?",
                (category, key)
            )
            await db.commit()
            return cursor.rowcount > 0

    async def get_all_memories_formatted(self) -> str:
        """Get all memories formatted for system prompt"""
        memories = await self.get_memories()
        if not memories:
            return ""

        by_category = {}
        for mem in memories:
            cat = mem['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(f"- {mem['key']}: {mem['value']}")

        sections = []
        for cat, items in by_category.items():
            sections.append(f"{cat.upper()}:\n" + "\n".join(items))

        return "\n\n".join(sections)

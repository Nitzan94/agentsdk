# ABOUTME: SQLite-based memory and session management
# ABOUTME: Handles persistent storage of conversations, notes, research

import aiosqlite
import json
from datetime import datetime
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

            await db.commit()

    async def create_session(self, session_id: str) -> str:
        """Create new session"""
        now = datetime.utcnow().isoformat()
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
        now = datetime.utcnow().isoformat()
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
        now = datetime.utcnow().isoformat()
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


    async def save_research(self, query: str, sources: List[str],
                           analysis: str, session_id: Optional[str] = None) -> int:
        """Save research results"""
        now = datetime.utcnow().isoformat()
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
        now = datetime.utcnow().isoformat()
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

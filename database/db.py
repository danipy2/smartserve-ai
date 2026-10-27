"""
SmartServe AI — Database Manager
SQLite database for storing conversations, messages, and analytics data.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

import config

DB_PATH = str(config.DB_PATH)


def init_db() -> None:
    """Initialize the database with required tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active'
        );

        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
            content TEXT NOT NULL,
            confidence REAL,
            needs_escalation BOOLEAN DEFAULT FALSE,
            sources TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        );

        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            file_type TEXT NOT NULL,
            chunk_count INTEGER DEFAULT 0,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active'
        );

        CREATE INDEX IF NOT EXISTS idx_messages_conversation 
            ON messages(conversation_id);
        CREATE INDEX IF NOT EXISTS idx_conversations_session 
            ON conversations(session_id);
    """)

    conn.commit()
    conn.close()


# --- Conversation Operations ---

def create_conversation(session_id: str) -> int:
    """Create a new conversation and return its ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO conversations (session_id) VALUES (?)",
        (session_id,)
    )
    conversation_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return conversation_id


def get_conversation_by_session(session_id: str) -> Optional[Dict]:
    """Get conversation by session ID."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM conversations WHERE session_id = ?",
        (session_id,)
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_or_create_conversation(session_id: str) -> int:
    """Get existing conversation ID or create a new one."""
    existing = get_conversation_by_session(session_id)
    if existing:
        return existing["id"]
    return create_conversation(session_id)


# --- Message Operations ---

def add_message(
    conversation_id: int,
    role: str,
    content: str,
    confidence: Optional[float] = None,
    needs_escalation: bool = False,
    sources: Optional[List[Dict]] = None,
) -> int:
    """Add a message to a conversation."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    sources_json = json.dumps(sources) if sources else None

    cursor.execute(
        """INSERT INTO messages 
           (conversation_id, role, content, confidence, needs_escalation, sources)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (conversation_id, role, content, confidence, needs_escalation, sources_json)
    )

    # Update conversation timestamp
    cursor.execute(
        "UPDATE conversations SET updated_at = ? WHERE id = ?",
        (datetime.now().isoformat(), conversation_id)
    )

    message_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return message_id


def get_conversation_messages(
    conversation_id: int,
    limit: int = 50,
) -> List[Dict]:
    """Get all messages for a conversation."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        """SELECT * FROM messages 
           WHERE conversation_id = ? 
           ORDER BY created_at ASC 
           LIMIT ?""",
        (conversation_id, limit)
    )
    rows = cursor.fetchall()
    conn.close()

    messages = []
    for row in rows:
        msg = dict(row)
        if msg["sources"]:
            msg["sources"] = json.loads(msg["sources"])
        messages.append(msg)
    return messages


def get_chat_history(conversation_id: int, limit: int = 10) -> List[Dict]:
    """Get simplified chat history for the RAG chain context."""
    messages = get_conversation_messages(conversation_id, limit)
    return [
        {"role": m["role"], "content": m["content"]}
        for m in messages
    ]


# --- Document Operations ---

def add_document_record(
    filename: str,
    file_type: str,
    chunk_count: int,
) -> int:
    """Record an uploaded document."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO documents (filename, file_type, chunk_count)
           VALUES (?, ?, ?)""",
        (filename, file_type, chunk_count)
    )
    doc_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return doc_id


def get_all_documents() -> List[Dict]:
    """Get all uploaded documents."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM documents WHERE status = 'active' ORDER BY uploaded_at DESC"
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def delete_document_record(filename: str) -> bool:
    """Soft-delete a document record."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE documents SET status = 'deleted' WHERE filename = ?",
        (filename,)
    )
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


# --- Analytics Operations ---

def get_analytics() -> Dict:
    """Get analytics data for the dashboard."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Total conversations
    cursor.execute("SELECT COUNT(*) FROM conversations")
    total_conversations = cursor.fetchone()[0]

    # Total messages
    cursor.execute("SELECT COUNT(*) FROM messages")
    total_messages = cursor.fetchone()[0]

    # Average confidence
    cursor.execute(
        "SELECT AVG(confidence) FROM messages WHERE confidence IS NOT NULL"
    )
    avg_confidence = cursor.fetchone()[0] or 0

    # Escalation count
    cursor.execute(
        "SELECT COUNT(*) FROM messages WHERE needs_escalation = TRUE"
    )
    escalation_count = cursor.fetchone()[0]

    # Total documents
    cursor.execute(
        "SELECT COUNT(*) FROM documents WHERE status = 'active'"
    )
    total_documents = cursor.fetchone()[0]

    # Messages per day (last 7 days)
    cursor.execute("""
        SELECT DATE(created_at) as date, COUNT(*) as count
        FROM messages
        WHERE created_at >= DATE('now', '-7 days')
        GROUP BY DATE(created_at)
        ORDER BY date
    """)
    daily_messages = [
        {"date": row[0], "count": row[1]}
        for row in cursor.fetchall()
    ]

    # Low confidence questions (for improvement)
    cursor.execute("""
        SELECT content, confidence, created_at
        FROM messages
        WHERE role = 'user' AND confidence IS NOT NULL AND confidence < ?
        ORDER BY created_at DESC
        LIMIT 10
    """, (config.CONFIDENCE_THRESHOLD,))
    low_confidence_queries = [
        {"question": row[0], "confidence": row[1], "date": row[2]}
        for row in cursor.fetchall()
    ]

    conn.close()

    return {
        "total_conversations": total_conversations,
        "total_messages": total_messages,
        "average_confidence": round(avg_confidence, 2),
        "escalation_count": escalation_count,
        "total_documents": total_documents,
        "daily_messages": daily_messages,
        "low_confidence_queries": low_confidence_queries,
    }


# Initialize database on import
init_db()

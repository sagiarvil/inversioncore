import os
import json
import sqlite3
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime

DB_PATH = os.getenv("INVERSION_DB_PATH", os.path.abspath("inversion_memory.db"))
_db_lock = threading.Lock()

def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=15.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # Eşzamanlılık ve Kilitlenme Koruması (Concurrency & Lock Prevention)
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA busy_timeout = 10000;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    return conn

def init_memory_db():
    with _db_lock:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    topic TEXT DEFAULT 'genel',
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS core_memory (
                    session_id TEXT PRIMARY KEY,
                    user_dilemma TEXT DEFAULT '',
                    power_dynamics TEXT DEFAULT '',
                    trauma_codes TEXT DEFAULT '',
                    opponent_profile TEXT DEFAULT '',
                    unresolved_conflicts TEXT DEFAULT '',
                    updated_at TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recall_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    round INTEGER,
                    role TEXT,
                    content TEXT,
                    created_at TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                )
            """)
            conn.commit()

init_memory_db()

class InversionMemoryStore:
    @staticmethod
    def get_or_create_session(session_id: str, topic: str = "genel") -> Dict[str, Any]:
        now = datetime.utcnow().isoformat()
        with _db_lock:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
                row = cursor.fetchone()
                if not row:
                    cursor.execute(
                        "INSERT INTO sessions (session_id, topic, created_at, updated_at) VALUES (?, ?, ?, ?)",
                        (session_id, topic, now, now)
                    )
                    cursor.execute(
                        "INSERT INTO core_memory (session_id, user_dilemma, power_dynamics, trauma_codes, opponent_profile, unresolved_conflicts, updated_at) VALUES (?, '', '', '', '', '', ?)",
                        (session_id, now)
                    )
                    conn.commit()
                    return {"session_id": session_id, "topic": topic, "created_at": now, "updated_at": now}
                return dict(row)

    @staticmethod
    def get_core_memory(session_id: str) -> Dict[str, str]:
        with _db_lock:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM core_memory WHERE session_id = ?", (session_id,))
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return {}

    @staticmethod
    def update_core_memory(session_id: str, updates: Dict[str, str]):
        now = datetime.utcnow().isoformat()
        fields = []
        values = []
        for k, v in updates.items():
            if k in ["user_dilemma", "power_dynamics", "trauma_codes", "opponent_profile", "unresolved_conflicts"]:
                fields.append(f"{k} = ?")
                values.append(v)
        if not fields:
            return
        fields.append("updated_at = ?")
        values.append(now)
        values.append(session_id)
        
        with _db_lock:
            with get_db() as conn:
                cursor = conn.cursor()
                query = f"UPDATE core_memory SET {', '.join(fields)} WHERE session_id = ?"
                cursor.execute(query, tuple(values))
                conn.commit()

    @staticmethod
    def append_message(session_id: str, round_num: int, role: str, content: str):
        now = datetime.utcnow().isoformat()
        with _db_lock:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO recall_history (session_id, round, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
                    (session_id, round_num, role, content, now)
                )
                cursor.execute(
                    "UPDATE sessions SET updated_at = ? WHERE session_id = ?",
                    (now, session_id)
                )
                conn.commit()

    @staticmethod
    def get_recall_history(session_id: str) -> List[Dict[str, Any]]:
        with _db_lock:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM recall_history WHERE session_id = ? ORDER BY id ASC",
                    (session_id,)
                )
                return [dict(r) for r in cursor.fetchall()]

    @staticmethod
    def format_context_for_prompt(session_id: str) -> str:
        with _db_lock:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM core_memory WHERE session_id = ?", (session_id,))
                core_row = cursor.fetchone()
                core = dict(core_row) if core_row else {}

                cursor.execute(
                    "SELECT * FROM recall_history WHERE session_id = ? ORDER BY id ASC",
                    (session_id,)
                )
                history = [dict(r) for r in cursor.fetchall()]
        
        ctx_parts = []
        if core and (core.get("user_dilemma") or core.get("power_dynamics")):
            ctx_parts.append("=== KULLANICI BİLİNÇALTI VE KÖK HARİTASI ===")
            if core.get("user_dilemma"):
                ctx_parts.append(f"- Kök İkilem: {core['user_dilemma']}")
            if core.get("power_dynamics"):
                ctx_parts.append(f"- Güç Dinamiği: {core['power_dynamics']}")
            if core.get("trauma_codes"):
                ctx_parts.append(f"- Savunma Prangası: {core['trauma_codes']}")
        
        if history:
            ctx_parts.append("=== GEÇMİŞ TUR DİYALOĞU ===")
            for h in history[-4:]: # son 4 mesaj
                ctx_parts.append(f"{h['role'].upper()} (Tur {h['round']}): {h['content'][:250]}")
                
        return "\n".join(ctx_parts)

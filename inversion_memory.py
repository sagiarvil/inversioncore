import os
import sqlite3
import threading

DB_PATH = os.getenv("INVERSION_DB_PATH", os.path.abspath("inversion_memory.db"))
_db_lock = threading.Lock()

def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=15.0, check_same_thread=False)
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA busy_timeout = 10000;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    return conn

def init_memory_db():
    with _db_lock:
        with get_connection() as conn:
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                topic TEXT DEFAULT 'genel',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS core_memory (
                session_id TEXT PRIMARY KEY,
                user_dilemma TEXT DEFAULT '',
                power_dynamics TEXT DEFAULT '',
                trauma_codes TEXT DEFAULT '',
                opponent_profile TEXT DEFAULT '',
                unresolved_conflicts TEXT DEFAULT '',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            );
            CREATE TABLE IF NOT EXISTS recall_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                round INTEGER DEFAULT 1,
                role TEXT,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            );
            """)

init_memory_db()

def get_core_memory(session_id: str) -> dict:
    with _db_lock:
        with get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM core_memory WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            return dict(row) if row else {}

def update_core_memory(session_id: str, updates):
    if isinstance(updates, str):
        updates = {"trauma_codes": updates}
    elif not isinstance(updates, dict):
        return

    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO sessions (session_id) VALUES (?)", (session_id,))
            cursor.execute("""
            INSERT OR IGNORE INTO core_memory (session_id, user_dilemma, power_dynamics, trauma_codes)
            VALUES (?, '', '', '')
            """, (session_id,))
            
            fields = []
            values = []
            for k, v in updates.items():
                if k in ["user_dilemma", "power_dynamics", "trauma_codes", "opponent_profile", "unresolved_conflicts"]:
                    fields.append(f"{k} = ?")
                    values.append(v)
            if fields:
                fields.append("updated_at = CURRENT_TIMESTAMP")
                values.append(session_id)
                query = f"UPDATE core_memory SET {', '.join(fields)} WHERE session_id = ?"
                cursor.execute(query, tuple(values))

def append_message(session_id: str, role: str, content: str, round_num: int = 1):
    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO sessions (session_id) VALUES (?)", (session_id,))
            cursor.execute(
                "INSERT INTO recall_history (session_id, round, role, content) VALUES (?, ?, ?, ?)",
                (session_id, round_num, role, content)
            )

def get_recall_history(session_id: str, limit: int = 5) -> list:
    with _db_lock:
        with get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role, content FROM recall_history WHERE session_id = ? ORDER BY id DESC LIMIT ?",
                (session_id, limit)
            )
            rows = cursor.fetchall()
            return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]

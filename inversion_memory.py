import os
import sqlite3
import threading

DB_PATH = os.getenv("INVERSION_DB_PATH", os.path.abspath("inversion_memory.db"))
_db_lock = threading.Lock()

# Firestore Bulut Bellek İstemcisi
_firestore_db = None
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    if not firebase_admin._apps:
        project_id = os.getenv("FIREBASE_PROJECT_ID", "inversioncore")
        firebase_admin.initialize_app(options={"projectId": project_id})
    _firestore_db = firestore.client()
    print("[*] InversionCore Cloud Firestore Bellek Motoru Aktif!")
except Exception as _fe:
    _firestore_db = None
    # Sessizce SQLite WAL moduna geçer, logu kirletmez

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
    if _firestore_db is not None:
        try:
            doc_ref = _firestore_db.collection("inversion_core_memory").document(session_id)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
        except Exception as e:
            print(f"[Firestore Read Error]: {e}")

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

    # 1. Firestore Bulut Senkronizasyonu
    if _firestore_db is not None:
        try:
            doc_ref = _firestore_db.collection("inversion_core_memory").document(session_id)
            payload = dict(updates)
            payload["updated_at"] = firestore.SERVER_TIMESTAMP
            doc_ref.set(payload, merge=True)
        except Exception as e:
            print(f"[Firestore Update Error]: {e}")

    # 2. SQLite Yerel Senkronizasyonu
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
    if _firestore_db is not None:
        try:
            msg_ref = _firestore_db.collection("inversion_sessions").document(session_id).collection("messages")
            msg_ref.add({
                "round": round_num,
                "role": role,
                "content": content,
                "created_at": firestore.SERVER_TIMESTAMP
            })
        except Exception as e:
            print(f"[Firestore Append Message Error]: {e}")

    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO sessions (session_id) VALUES (?)", (session_id,))
            cursor.execute(
                "INSERT INTO recall_history (session_id, round, role, content) VALUES (?, ?, ?, ?)",
                (session_id, round_num, role, content)
            )

def get_recall_history(session_id: str, limit: int = 5) -> list:
    if _firestore_db is not None:
        try:
            msg_ref = _firestore_db.collection("inversion_sessions").document(session_id).collection("messages")
            query = msg_ref.order_by("created_at", direction=firestore.Query.DESCENDING).limit(limit)
            docs = query.stream()
            history = [{"role": d.to_dict().get("role"), "content": d.to_dict().get("content")} for d in docs]
            if history:
                return list(reversed(history))
        except Exception as e:
            print(f"[Firestore Recall History Error]: {e}")

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

"""
Cost Ledger - Her LLM cagrisinin maliyetini SQLite'a kaydeder
Token sayisi, USD maliyet, timestamp, motor, problem_tipi
"""
import sqlite3
import threading
import time
from pathlib import Path
from typing import Optional


class CostLedger:
    def __init__(self, db_path: str = "data/cost_ledger.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._init_db()
    
    def _init_db(self):
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS llm_calls (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL NOT NULL,
                        customer_id TEXT,
                        problem_type TEXT,
                        model TEXT,
                        prompt_tokens INTEGER,
                        completion_tokens INTEGER,
                        total_tokens INTEGER,
                        cost_usd REAL,
                        cache_status TEXT,
                        latency_ms REAL
                    )
                """)
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_timestamp ON llm_calls(timestamp)
                """)
                conn.commit()
    
    def record(self, customer_id: str, problem_type: str, model: str,
               prompt_tokens: int, completion_tokens: int, cost_usd: float,
               cache_status: str = "MISS", latency_ms: float = 0.0):
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO llm_calls 
                    (timestamp, customer_id, problem_type, model, 
                     prompt_tokens, completion_tokens, total_tokens, 
                     cost_usd, cache_status, latency_ms)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (time.time(), customer_id, problem_type, model,
                      prompt_tokens, completion_tokens, 
                      prompt_tokens + completion_tokens,
                      cost_usd, cache_status, latency_ms))
                conn.commit()
    
    def summary(self, since: Optional[float] = None) -> dict:
        since = since or 0
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("""
                SELECT 
                    COUNT(*) as total_calls,
                    COALESCE(SUM(total_tokens), 0) as total_tokens,
                    COALESCE(SUM(cost_usd), 0) as total_cost_usd,
                    COALESCE(SUM(CASE WHEN cache_status = 'HIT' THEN 1 ELSE 0 END), 0) as cache_hits,
                    COALESCE(SUM(CASE WHEN cache_status = 'MISS' THEN 1 ELSE 0 END), 0) as cache_misses
                FROM llm_calls WHERE timestamp >= ?
            """, (since,)).fetchone()
            return {
                "total_calls": row[0],
                "total_tokens": row[1],
                "total_cost_usd": round(row[2], 6),
                "cache_hits": row[3],
                "cache_misses": row[4],
                "hit_rate": round(row[3] / max(row[0], 1) * 100, 2)
            }


_ledger_instance: Optional[CostLedger] = None

def get_ledger() -> CostLedger:
    global _ledger_instance
    if _ledger_instance is None:
        _ledger_instance = CostLedger()
    return _ledger_instance

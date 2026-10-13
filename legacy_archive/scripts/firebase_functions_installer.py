import os

FILES = {}

# 1. FIREBASE.JSON GÜNCELLEMESI (functions ekleniyor)
FILES["firebase.json"] = '''{
  "hosting": {
    "site": "inversioncore",
    "public": "public",
    "ignore": ["firebase.json", "**/.*", "**/node_modules/**"],
    "rewrites": [
      {
        "source": "/api/**",
        "function": "analyze"
      }
    ]
  },
  "functions": [
    {
      "source": "functions",
      "codebase": "default",
      "ignore": ["venv", ".git", "firebase-debug.log", "firebase-debug.*.log", "*.local"]
    }
  ]
}
'''

# 2. FUNCTIONS KLASORU INIT
FILES["functions/.gitignore"] = '''venv/
*.pyc
__pycache__/
.env
*.local
firebase-debug.log
'''

FILES["functions/requirements.txt"] = '''firebase-functions==0.4.2
firebase-admin==6.5.0
flask==3.0.3
z3-solver
ortools
networkx
scipy
SALib
pysd
nashpy
dowhy
numpy
pandas
litellm
cachetools
'''

# 3. FIREBASE FUNCTIONS MAIN (FastAPI yerine Flask + Firebase HTTP trigger)
FILES["functions/main.py"] = '''"""
InversionCore Firebase Functions Backend
"""
import os
import sys
import json
import hashlib
import sqlite3
import threading
import time
from pathlib import Path
from typing import Optional, Any

from firebase_functions import https_fn, options
from firebase_admin import initialize_app, firestore
import flask

# Firebase init
initialize_app()

import z3 as z3mod
from ortools.sat.python import cp_model
import networkx as nx
from scipy import stats
import numpy as np


class Z3Surgeon:
    def find_contradictions(self, statements):
        solver = z3mod.Solver()
        namespace = {}
        import re
        for stmt in statements:
            for token in re.findall(r"[A-Za-z_][A-Za-z_0-9]*", stmt):
                if token not in namespace and token not in ["and","or","not","True","False"]:
                    namespace[token] = z3mod.Int(token)
            solver.add(eval(stmt, {"__builtins__": None}, {**{k: getattr(z3mod, k) for k in dir(z3mod) if not k.startswith("_")}, **namespace}))
        if solver.check() == z3mod.unsat:
            return {"motor": "Z3", "contradiction_found": True, "negative_finding": "Bu sistem mantıksal olarak tutarsız"}
        return {"motor": "Z3", "contradiction_found": False, "negative_finding": "Çelişki bulunamadı"}


class ORToolsSurgeon:
    def find_infeasible(self, variables, constraints):
        model = cp_model.CpModel()
        namespace = {}
        for name, bounds in variables.items():
            namespace[name] = model.NewIntVar(int(bounds[0]), int(bounds[1]), name)
        for constraint in constraints:
            model.Add(eval(constraint, {"__builtins__": None}, namespace))
        solver = cp_model.CpSolver()
        status = solver.Solve(model)
        if status == cp_model.INFEASIBLE:
            return {"motor": "OR-Tools", "infeasible": True, "negative_finding": "Bu sistem matematiksel olarak çalışamaz"}
        return {"motor": "OR-Tools", "infeasible": False, "negative_finding": "Sistem çalışabilir"}


class NetworkSurgeon:
    def find_hidden_connections(self, nodes, edges):
        G = nx.Graph()
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        centrality = nx.betweenness_centrality(G)
        hidden = [n for n, c in centrality.items() if c > 0.5]
        return {
            "motor": "NetworkX",
            "hidden_brokers": hidden,
            "negative_finding": "Bu ağda gizli aracılar var" if hidden else "Ağ temiz"
        }


class StatsSurgeon:
    def find_manipulation(self, data):
        observed = np.array(data, dtype=float)
        mu = max(float(np.mean(observed)), 0.0001)
        pmf = stats.poisson.pmf(range(len(observed)), mu)
        expected = (pmf / np.sum(pmf)) * np.sum(observed)
        chi2, p_value = stats.chisquare(observed, expected)
        return {
            "motor": "SciPy",
            "organic": bool(p_value > 0.05),
            "p_value": float(p_value),
            "negative_finding": "Bu veri organik değil, manipüle edilmiş" if p_value < 0.05 else "Veri organik"
        }


class ProblemOntology:
    RULES = {
        "LOGICAL": ["çelişki", "ispat", "doğru", "yanlış", "aksiyom", "mantık", "tutarlılık", "celiski"],
        "NETWORK": ["ilişki", "bağlantı", "ağ", "ortak", "aracı", "düğüm", "grafik", "ag"],
        "PROBABILISTIC": ["olasılık", "anomali", "dağılım", "manipülasyon", "istatistik", "organik"],
        "OPTIMIZATION": ["kısıt", "kaynak", "kapasite", "optimum", "maliyet", "darboğaz"],
    }

    def classify(self, text):
        text_lower = text.lower()
        scores = {pt: sum(1 for kw in kws if kw in text_lower) for pt, kws in self.RULES.items()}
        if max(scores.values()) == 0:
            return "UNKNOWN"
        return max(scores, key=scores.get)


MOTOR_VERSION = "v2.0"
ONTOLOGY_VERSION = "v1.0"

def make_cache_key(prefix: str, data: Any) -> str:
    serialized = json.dumps(data, sort_keys=True, default=str, ensure_ascii=False)
    digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:24]
    return f"ic:{prefix}:{MOTOR_VERSION}:{ONTOLOGY_VERSION}:{digest}"


_memory_cache = {}


def cache_get(key: str) -> Optional[dict]:
    entry = _memory_cache.get(key)
    if entry and entry["expires_at"] > time.time():
        return entry["value"]
    if entry:
        del _memory_cache[key]
    return None


def cache_set(key: str, value: dict, ttl: int = 86400):
    _memory_cache[key] = {"value": value, "expires_at": time.time() + ttl}


DB_PATH = "/tmp/cost_ledger.db"
_db_lock = threading.Lock()


def init_db():
    with _db_lock:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS llm_calls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    customer_id TEXT, problem_type TEXT, model TEXT,
                    prompt_tokens INTEGER, completion_tokens INTEGER,
                    total_tokens INTEGER, cost_usd REAL,
                    cache_status TEXT, latency_ms REAL
                )
            """)
            conn.commit()


def record_call(customer_id, problem_type, model, prompt_tokens, completion_tokens, cost_usd, cache_status, latency_ms):
    with _db_lock:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                INSERT INTO llm_calls
                (timestamp, customer_id, problem_type, model, prompt_tokens, completion_tokens,
                 total_tokens, cost_usd, cache_status, latency_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (time.time(), customer_id, problem_type, model,
                  prompt_tokens, completion_tokens,
                  prompt_tokens + completion_tokens,
                  cost_usd, cache_status, latency_ms))
            conn.commit()


def ledger_summary():
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute("""
            SELECT COUNT(*), COALESCE(SUM(total_tokens), 0), COALESCE(SUM(cost_usd), 0),
                   COALESCE(SUM(CASE WHEN cache_status = 'HIT' THEN 1 ELSE 0 END), 0),
                   COALESCE(SUM(CASE WHEN cache_status = 'MISS' THEN 1 ELSE 0 END), 0)
            FROM llm_calls
        """).fetchone()
        return {
            "total_calls": row[0], "total_tokens": row[1],
            "total_cost_usd": round(row[2], 6),
            "cache_hits": row[3], "cache_misses": row[4],
            "hit_rate": round(row[3] / max(row[0], 1) * 100, 2)
        }


def synthesize_with_deepseek(physical_findings, customer_id, problem_type):
    start = time.time()
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")

    if not api_key:
        latency_ms = (time.time() - start) * 1000
        record_call(customer_id, problem_type, "offline-no-key", 0, 0, 0.0, "OFFLINE", latency_ms)
        return {
            "synthesis": "\\n".join(
                ["[OFFLINE SENTEZ]"] +
                [f"- {f.get('motor', '?')}: {f.get('negative_finding', '?')}" for f in physical_findings]
            ),
            "tokens": 0, "cost_usd": 0.0,
            "latency_ms": round(latency_ms, 2),
            "source": "offline", "offline": True
        }

    try:
        import litellm
        system_prompt = (
            "Sen InversionCore fiziksel motorlarının çıktısını insan diline çeviren bir sentez motorusun. "
            "ASLA yeni bilgi ekleme, ASLA hesaplama yapma. Sadece verilen bulguları özetle. Türkçe cevap ver."
        )
        user_prompt = "Aşağıdaki fiziksel motor bulgularını sentezle:\\n\\n" + "\\n".join(
            f"- {f.get('motor', '?')}: {f.get('negative_finding', '?')}" for f in physical_findings
        )
        response = litellm.completion(
            model="deepseek/deepseek-chat",
            messages=[{"role": "system", "content": system_prompt},
                      {"role": "user", "content": user_prompt}],
            api_key=api_key,
            api_base="https://api.deepseek.com",
            temperature=0.0, max_tokens=400
        )
        latency_ms = (time.time() - start) * 1000
        usage = response.usage
        cost = response._hidden_params.get("response_cost", 0.0) or 0.0
        record_call(customer_id, problem_type, "deepseek/deepseek-chat",
                    usage.prompt_tokens, usage.completion_tokens, cost, "MISS", latency_ms)
        return {
            "synthesis": response.choices[0].message.content,
            "tokens": usage.total_tokens, "cost_usd": round(cost, 6),
            "latency_ms": round(latency_ms, 2), "source": "deepseek"
        }
    except Exception as e:
        latency_ms = (time.time() - start) * 1000
        record_call(customer_id, problem_type, "deepseek/deepseek-chat", 0, 0, 0.0, "ERROR", latency_ms)
        return {
            "error": str(e),
            "synthesis": "\\n".join(
                ["[HATA - Offline Fallback]"] +
                [f"- {f.get('motor', '?')}: {f.get('negative_finding', '?')}" for f in physical_findings]
            )
        }


ontology = ProblemOntology()
motors = {
    "LOGICAL": Z3Surgeon(),
    "OPTIMIZATION": ORToolsSurgeon(),
    "NETWORK": NetworkSurgeon(),
    "PROBABILISTIC": StatsSurgeon(),
}


def auto_invert(text: str, data: dict, customer_id: str = "default"):
    problem_type = ontology.classify(text)

    motor_key = make_cache_key(f"motor:{problem_type}", data)
    cached_motor = cache_get(motor_key)
    if cached_motor is not None:
        motor_results = cached_motor
        motor_cache = "HIT"
    else:
        motor = motors.get(problem_type)
        if not motor:
            motor_results = [{"error": f"Bilinmeyen problem tipi: {problem_type}"}]
        else:
            if problem_type == "LOGICAL":
                motor_results = [motor.find_contradictions(data.get("statements", []))]
            elif problem_type == "OPTIMIZATION":
                motor_results = [motor.find_infeasible(data.get("variables", {}), data.get("constraints", []))]
            elif problem_type == "NETWORK":
                motor_results = [motor.find_hidden_connections(data.get("nodes", []), data.get("edges", []))]
            elif problem_type == "PROBABILISTIC":
                motor_results = [motor.find_manipulation(data.get("data", []))]
            else:
                motor_results = [{"error": "Motor bulunamadı"}]
        if motor_results and not motor_results[0].get("error"):
            cache_set(motor_key, motor_results)
        motor_cache = "MISS"

    synth_key = make_cache_key(f"synth:{problem_type}", {"data": data, "results": motor_results})
    cached_synth = cache_get(synth_key)
    if cached_synth is not None:
        synthesis = cached_synth
        synth_cache = "HIT"
    else:
        if any(r.get("error") for r in motor_results):
            synthesis = {"synthesis": "Motor hatası, sentez atlandı", "source": "error"}
        else:
            synthesis = synthesize_with_deepseek(motor_results, customer_id, problem_type)
            if "error" not in synthesis:
                cache_set(synth_key, synthesis)
        synth_cache = "MISS"

    return {
        "problem_type": problem_type,
        "motor_results": motor_results,
        "synthesis": synthesis,
        "cache_stats": {"motor": motor_cache, "synthesis": synth_cache, "backend": "memory"},
        "cost_summary": ledger_summary()
    }


@https_fn.on_request(
    region=options.SupportedRegion.EUROPE_WEST1,
    cors=options.CorsOptions(cors_origins=["https://inversioncore.com", "https://inversioncore.web.app"],
                              cors_methods=["POST", "GET"])
)
def analyze(req: flask.Request) -> flask.Response:
    if req.method == "OPTIONS":
        return flask.Response("", status=204)

    if req.method != "POST":
        return flask.jsonify({"error": "Sadece POST kabul edilir"}), 405

    try:
        body = req.get_json(force=True)
    except Exception:
        return flask.jsonify({"error": "Geçersiz JSON"}), 400

    text = (body.get("text") or "").strip()
    customer_id = body.get("customer_id", "web_user")

    if not text or len(text) < 10:
        return flask.jsonify({"error": "Metin çok kısa (min 10 karakter)"}), 400

    data = {"raw_text": text}
    if any(kw in text.lower() for kw in ["x >", "x <", "y >=", "değişken"]):
        data["statements"] = [s.strip() for s in text.split(",") if ">" in s or "<" in s]
    if any(kw in text.lower() for kw in ["düğüm", "node", "ağ", "grafik"]):
        data["nodes"] = ["A", "B", "C", "D"]
        data["edges"] = [("A", "B"), ("B", "C"), ("C", "D"), ("A", "D")]

    result = auto_invert(text, data, customer_id)
    return flask.jsonify(result), 200


@https_fn.on_request(
    region=options.SupportedRegion.EUROPE_WEST1,
    cors=options.CorsOptions(cors_origins=["https://inversioncore.com", "https://inversioncore.web.app"])
)
def health(req: flask.Request) -> flask.Response:
    return flask.jsonify({"status": "ok", "version": "2.1", "backend": "firebase-functions"}), 200

init_db()
'''

FILES["public/js/inversion_api.js"] = '''const INVERSION_API_BASE = "/api";

async function sendToBackend(extractedText, customerId = "web_user") {
  if (!extractedText || extractedText.length < 10) {
    throw new Error("Metin çok kısa (min 10 karakter)");
  }

  const response = await fetch(`${INVERSION_API_BASE}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text: extractedText,
      customer_id: customerId
    })
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.error || `API hatası: ${response.status}`);
  }

  return await response.json();
}

function displayNegativeFinding(result) {
  const termBox = document.getElementById("terminalBox") || document.getElementById("output");
  if (!termBox) {
    console.log("InversionCore Sonucu:", result);
    return;
  }

  const synthesis = result.synthesis?.synthesis
    || result.synthesis?.fallback_synthesis
    || JSON.stringify(result.synthesis, null, 2);

  const motorSummary = (result.motor_results || [])
    .map(r => `▸ ${r.motor || "?"}: ${r.negative_finding || "?"}`)
    .join("\\n");

  const output = [
    "╔══════════════════════════════════════════════════╗",
    "║  INVERSIONCORE — NEGATİF BİLGİ RAPORU            ║",
    "╚══════════════════════════════════════════════════╝",
    "",
    `Problem Tipi: ${result.problem_type}`,
    "",
    "── MOTOR BULGULARI ──",
    motorSummary || "(bulgu yok)",
    "",
    "── SENTEZ ──",
    synthesis,
    "",
    `Cache: motor=${result.cache_stats?.motor} | sentez=${result.cache_stats?.synthesis}`,
    `Maliyet: $${(result.cost_summary?.total_cost_usd || 0).toFixed(6)}`,
    `Hit Oranı: %${result.cost_summary?.hit_rate || 0}`
  ].join("\\n");

  termBox.innerText = output;
}

window.InversionAPI = { sendToBackend, displayNegativeFinding };
'''

for path, content in FILES.items():
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"Oluşturuldu: {path}")

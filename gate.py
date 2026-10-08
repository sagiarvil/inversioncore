#!/usr/bin/env python3
"""gate.py — Tersine Mühendislik v4: deterministik kapı, kanıt kaydedici ve tamamlanma denetleyicisi.
LLM kanıt YAZMAZ (run yazar), kapıyı GEÇMEZ (advance geçer), tamamlandı DEMEZ (final der)."""
import argparse, hashlib, json, os, subprocess, sys, datetime

LEDGER = os.environ.get("AUDIT_LEDGER", "_audit/ledger.json")
EVDIR = os.path.join(os.path.dirname(LEDGER) or ".", "evidence")
ORACLES = {"SPEC", "PROTOCOL", "INDEPENDENT_CALC", "INVARIANT", "REFERENCE_IMPL", "GOLDEN_DATA"}
NOTRUN_OK = {"BLOCKED", "NOT_APPLICABLE", "OUT_OF_SCOPE"}
LIMITS = ["SURE", "REQ", "CONC", "RES", "CANCEL", "CLEANUP"]
FAMILIES = list("ABCDEFGH")
CHECKLIST = [f"C-{i:02d}" for i in range(1, 19)]
NA_IF_DISCOVER_ONLY = {"C-15", "C-16"}
FINDING_FIELDS = ["title", "invariant", "class", "priority", "expected", "observed",
                  "cause", "escape", "fix_direction", "cleanup"]
INSPECT = {"INSPECTED", "BLOCKED", "NOT_APPLICABLE", "OUT_OF_SCOPE"}
KINDS = {  # kind: (terminal statuses, due gate)
    "entrypoint": (INSPECT, 5), "node": (INSPECT, 5), "edge": (INSPECT, 5),
    "invariant": ({"DEFINED", "NO_ORACLE"}, 3),
    "hypothesis": ({"CONFIRMED", "REFUTED", "DORMANT", "BLOCKED", "REDUNDANT"}, 5),
    "experiment": ({"PASS", "FAIL", "BLOCKED", "NOT_RUN", "NOT_APPLICABLE"}, 5),
    "contradiction": ({"RESOLVED", "ACCEPTED_RISK"}, 6),
    "finding": ({"CONFIRMED_RUNTIME", "CONFIRMED_STATIC", "SUSPECTED", "UNVERIFIED", "DISPROVED"}, 7),
    "repair": ({"DONE", "ABANDONED"}, 9),
    "checklist": ({"PASS", "NOT_APPLICABLE"}, 10),
}
DISC = {"entrypoint", "node", "edge", "invariant", "hypothesis", "experiment", "contradiction", "finding"}
IDENT = ["repo", "worktree", "dependency", "process", "artifact", "deploy", "observed"]


def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(65536), b""): h.update(c)
    return h.hexdigest()
def canon(o): return json.dumps(o, sort_keys=True, ensure_ascii=False).encode()

def load():
    if not os.path.isfile(LEDGER): sys.exit(f"ledger yok: {LEDGER} (önce: gate.py init)")
    with open(LEDGER, encoding="utf-8") as f: return json.load(f)
def save(L):
    os.makedirs(os.path.dirname(LEDGER) or ".", exist_ok=True)
    tmp = LEDGER + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f: json.dump(L, f, ensure_ascii=False, indent=1)
    os.replace(tmp, LEDGER)

def freeze_hash(L):
    cnt = L["freeze"]["evidence_count"]
    disc = [{k: v for k, v in i.items() if k != "resolution"} for i in L["items"]
            if i["kind"] in DISC and i.get("born_phase", 0) <= 8]
    return sha_bytes(canon([disc, L["evidence"][:cnt]]))

def check(L, n):
    v, items = [], L.get("items", [])
    ev = {e.get("id"): e for e in L.get("evidence", [])}
    caps, mode = L.get("capabilities", {}), L.get("mode")
    ids = [i.get("id") for i in items]
    if len(ids) != len(set(ids)): v.append("DUP_ID: tekrar eden item kimliği")
    for e in ev.values():  # kanıt bütünlüğü: her kapıda yeniden hash'lenir
        p = e.get("log_path")
        if not e.get("cmd") or not isinstance(e.get("exit"), int): v.append(f"{e.get('id')}: cmd/exit eksik")
        elif not p or not os.path.isfile(p): v.append(f"{e['id']}: log dosyası yok")
        elif sha_file(p) != e.get("sha256"): v.append(f"{e['id']}: HASH_UYUŞMAZ (kanıt değişmiş)")
    def refs(it, key):
        r = it.get(key) or []
        r = r if isinstance(r, list) else [r]
        bad = [x for x in r if x not in ev]
        if bad: v.append(f"{it['id']}: {key} bilinmeyen kanıt {bad}")
        return r
    def indep(it):
        if not it.get("verified_by") or it.get("verified_by") == it.get("owner"):
            v.append(f"{it['id']}: bağımsız doğrulayıcı yok (verified_by boş veya owner ile aynı)")
    # --- kapı koşulları
    t = L.get("target", {})
    if not t.get("path") or not t.get("scope_in"): v.append("G0: target.path/scope_in boş")
    if mode not in ("DISCOVER_ONLY", "DISCOVER_AND_REPAIR"): v.append("G0: mode geçersiz")
    if L.get("repair_auth") not in ("none", "pre_granted", "per_finding"): v.append("G0: repair_auth geçersiz")
    if mode == "DISCOVER_ONLY" and L.get("repair_auth") != "none": v.append("G0: DISCOVER_ONLY ile repair_auth çelişiyor")
    if mode == "DISCOVER_AND_REPAIR" and L.get("repair_auth") == "none": v.append("G0: onarım modu ama yetki yok")
    for k in ("shell", "git", "runtime_access", "isolated_env"):
        if not isinstance(caps.get(k), bool): v.append(f"G0: capabilities.{k} boş")
    b = L.get("budget", {})
    for k in ("max_commands", "max_attempts_per_hypothesis"):
        if not isinstance(b.get(k), int) or b[k] <= 0: v.append(f"G0: budget.{k} tanımsız")
    if n >= 1:
        idn = L.get("identity", {})
        for k in IDENT:
            if not idn.get(k): v.append(f"G1: identity.{k} boş (değer ya da 'UNVERIFIED')")
        if L.get("snapshot_evidence") not in ev: v.append("G1: snapshot kanıtı yok")
    kinds = lambda k: [i for i in items if i["kind"] == k]
    if n >= 2:
        if not L.get("sweeps"): v.append("G2: bağımsız süpürme yok")
        if not kinds("entrypoint"): v.append("G2: entrypoint yok")
        if not kinds("node"): v.append("G2: node yok")
    if n >= 3 and not kinds("invariant"): v.append("G3: invariant yok")
    if n >= 4 and not kinds("hypothesis") and not L.get("no_hypothesis_reason"): v.append("G4: hipotez yok ve gerekçe yok")
    if n >= 5:
        for f in FAMILIES:
            if not [e for e in kinds("experiment") if e.get("family") == f]:
                v.append(f"G5: deney ailesi {f} kapatılmamış (deney ya da gerekçeli NOT_APPLICABLE yok)")
    # --- item kuralları
    for it in items:
        k, s, iid = it.get("kind"), it.get("status"), it.get("id")
        if k not in KINDS: v.append(f"{iid}: bilinmeyen kind {k}"); continue
        term, due = KINDS[k]
        if due <= n and s not in term: v.append(f"{iid}: [{k}] terminal değil (status={s}) — G{due}'de kapalı olmalı")
        if s not in term: continue
        if k in ("entrypoint", "node", "edge"):
            if s == "INSPECTED": refs(it, "evidence_ids") or v.append(f"{iid}: INSPECTED ama kanıt yok")
            elif not it.get("reason"): v.append(f"{iid}: {s} gerekçesiz")
        elif k == "invariant":
            if s == "DEFINED" and it.get("oracle_kind") not in ORACLES: v.append(f"{iid}: oracle_kind geçersiz/SELF_REFERENTIAL")
            if s == "NO_ORACLE" and not it.get("reason"): v.append(f"{iid}: NO_ORACLE gerekçesiz")
        elif k == "hypothesis":
            if s == "CONFIRMED":
                if it.get("oracle_kind") not in ORACLES: v.append(f"{iid}: oracle yok")
                if it.get("counter_result") != "REFUTED": v.append(f"{iid}: karşı hipotez REFUTED değil")
                if not refs(it, "evidence_ids"): v.append(f"{iid}: kanıt yok")
                indep(it)
            elif s in ("REFUTED", "DORMANT", "BLOCKED", "REDUNDANT") and not it.get("reason"): v.append(f"{iid}: {s} gerekçesiz")
        elif k == "experiment":
            if s in ("PASS", "FAIL"):
                if not refs(it, "evidence_ids"): v.append(f"{iid}: {s} ama kanıt yok")
                lim = it.get("limits", {})
                miss = [x for x in LIMITS if not lim.get(x)]
                if miss: v.append(f"{iid}: deney sınırları eksik {miss}")
            elif s == "NOT_RUN" and it.get("reason") not in NOTRUN_OK: v.append(f"{iid}: NOT_RUN gerekçesi geçersiz (yalnız {sorted(NOTRUN_OK)})")
            elif s in ("BLOCKED", "NOT_APPLICABLE") and not it.get("reason"): v.append(f"{iid}: {s} gerekçesiz")
        elif k == "contradiction":
            if not it.get("reason"): v.append(f"{iid}: çelişki çözümü/gerekçesi yok")
        elif k == "finding":
            if s.startswith("CONFIRMED"):
                miss = [x for x in FINDING_FIELDS if not it.get(x)]
                if miss: v.append(f"{iid}: bulgu kartı eksik {miss}")
                if it.get("oracle_kind") not in ORACLES: v.append(f"{iid}: oracle yok")
                if it.get("counter_result") != "REFUTED": v.append(f"{iid}: karşı hipotez REFUTED değil")
                if not refs(it, "evidence_ids"): v.append(f"{iid}: kanıt yok")
                if not refs(it, "repro_evidence_ids"): v.append(f"{iid}: minimal repro kanıtı yok")
                if s == "CONFIRMED_RUNTIME" and not (caps.get("shell") and caps.get("runtime_access")):
                    v.append(f"{iid}: CONFIRMED_RUNTIME ama runtime/shell erişimi yok")
                indep(it)
            elif not it.get("reason"): v.append(f"{iid}: {s} gerekçesiz")
        elif k == "repair" and s == "DONE":
            if L.get("repair_auth") == "none": v.append(f"{iid}: onarım yetkisi yok")
            if it.get("blast_radius_done") is not True: v.append(f"{iid}: blast radius yapılmamış")
            for key in ("baseline_evidence_ids", "after_evidence_ids", "repro_closed_evidence_ids", "rollback_evidence_ids"):
                if not refs(it, key): v.append(f"{iid}: {key} boş")
            if not any(f.get("id") == it.get("fixes") for f in kinds("finding")): v.append(f"{iid}: fixes geçerli F-ID değil")
            indep(it)
        elif k == "checklist":
            if s == "PASS":
                if not refs(it, "evidence_ids"): v.append(f"{iid}: PASS ama kanıt yok")
                indep(it)
            elif not (iid in NA_IF_DISCOVER_ONLY and mode == "DISCOVER_ONLY" and it.get("reason")):
                v.append(f"{iid}: NOT_APPLICABLE yalnız DISCOVER_ONLY'de C-15/C-16 için ve gerekçeli")
    if n >= 8:
        fz = L.get("freeze")
        if not fz: v.append("G8: keşif dondurulmamış")
        elif n >= 9 and fz.get("hash") != freeze_hash(L): v.append("G9+: DONDURULMUŞ KEŞİF DEĞİŞTİRİLMİŞ (freeze hash uyuşmaz)")
    if n >= 10:
        sw = L.get("sweeps", [])
        if len(sw) < 2: v.append("G10: en az 2 bağımsız süpürme (P2 + P10) gerekli")
        elif sw[-1].get("new_items_found") != 0 or sw[-1].get("evidence_id") not in ev:
            v.append("G10: son süpürme delta=0 değil ya da kanıtsız (payda bütünlüğü yok)")
        have = {i["id"] for i in kinds("checklist")}
        for c in CHECKLIST:
            if c not in have: v.append(f"G10: kanonik checklist maddesi {c} ledger'da yok")
    return v

def cmd_init(a):
    if os.path.exists(LEDGER): sys.exit("ledger zaten var")
    os.makedirs(EVDIR, exist_ok=True)
    save({"audit_id": a.audit_id, "created": now(), "phase": 0, "mode": None, "repair_auth": None,
          "target": {}, "capabilities": {}, "budget": {}, "identity": {}, "sweeps": [],
          "items": [], "evidence": [], "history": []})
    print(f"init ok: {LEDGER}")

def cmd_put(a):
    L = load(); L[a.key] = json.loads(a.value); save(L); print("ok")

def cmd_add(a):
    L = load()
    if a.kind not in KINDS: sys.exit(f"kind ∈ {sorted(KINDS)}")
    if any(i["id"] == a.id for i in L["items"]): sys.exit("id zaten var")
    it = {"id": a.id, "kind": a.kind, "status": "OPEN", "owner": a.role, "born_phase": L["phase"], "created": now()}
    it.update(json.loads(a.json or "{}")); L["items"].append(it); save(L); print("ok")

def cmd_set(a):
    L = load(); it = next((i for i in L["items"] if i["id"] == a.id), None)
    if not it: sys.exit("id yok")
    patch = json.loads(a.json)
    if L["phase"] >= 9 and it["kind"] in DISC and it.get("born_phase", 0) <= 8 and set(patch) - {"resolution"}:
        sys.exit("REDDEDİLDİ: dondurulmuş keşif öğesi yalnız 'resolution' alanını alabilir")
    if "verified_by" in patch and patch["verified_by"] == it.get("owner"): sys.exit("REDDEDİLDİ: owner kendi işini doğrulayamaz")
    it.update(patch); it["updated_by"] = a.role; save(L); print("ok")

def cmd_run(a):
    L = load(); os.makedirs(EVDIR, exist_ok=True)
    eid = f"E-{len(L['evidence']) + 1:04d}"; cmd = " ".join(a.command); t0 = datetime.datetime.now()
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=a.timeout)
        out, code = f"--- STDOUT ---\n{r.stdout}\n--- STDERR ---\n{r.stderr}\n", r.returncode
    except subprocess.TimeoutExpired as e:
        out, code = f"TIMEOUT {a.timeout}s\n{e.stdout or ''}", 124
    ms = int((datetime.datetime.now() - t0).total_seconds() * 1000)
    p = os.path.join(EVDIR, f"{eid}.log")
    with open(p, "w", encoding="utf-8") as f: f.write(out)
    L["evidence"].append({"id": eid, "cmd": cmd, "exit": code, "ms": ms, "log_path": p, "sha256": sha_file(p),
                          "ts": now(), "actor": a.role, "cwd": os.getcwd()})
    save(L); print(json.dumps({"id": eid, "exit": code, "sha256": L["evidence"][-1]["sha256"], "log": p}))

def cmd_gate(a):
    L = load(); v = check(L, a.n)
    print(json.dumps({"gate": a.n, "pass": not v, "violations": v}, ensure_ascii=False, indent=1)); sys.exit(1 if v else 0)

def cmd_advance(a):
    L = load(); p = L["phase"]
    if p >= 11: sys.exit("zaten kapalı")
    v = check(L, p)
    if v: print(json.dumps({"advance": False, "phase": p, "violations": v}, ensure_ascii=False, indent=1)); sys.exit(1)
    nxt = 10 if (p == 8 and L["mode"] == "DISCOVER_ONLY") else p + 1
    prev = L["history"][-1]["chain"] if L["history"] else "GENESIS"
    snap = sha_bytes(canon([L["items"], L["evidence"]]))
    L["history"].append({"from": p, "to": nxt, "ts": now(), "state_sha256": snap, "chain": sha_bytes((prev + snap).encode())})
    L["phase"] = nxt; save(L); print(json.dumps({"advance": True, "phase": nxt}))

def cmd_freeze(a):
    L = load()
    if L["phase"] != 8: sys.exit("freeze yalnız P8'de")
    L["freeze"] = {"ts": now(), "evidence_count": len(L["evidence"])}
    L["freeze"]["hash"] = freeze_hash(L); save(L); print(L["freeze"]["hash"])

def cmd_sweep(a):
    L = load(); L["sweeps"].append({"round": len(L["sweeps"]) + 1, "phase": L["phase"], "new_items_found": a.new,
                                     "evidence_id": a.evidence, "by": a.role, "ts": now()}); save(L); print("ok")

def cmd_verify(a):
    L = load(); bad = [e["id"] for e in L["evidence"] if not os.path.isfile(e["log_path"]) or sha_file(e["log_path"]) != e["sha256"]]
    print(json.dumps({"checked": len(L["evidence"]), "mismatch": bad})); sys.exit(1 if bad else 0)

def cmd_status(a):
    L = load(); c = {}
    for i in L["items"]: c[f"{i['kind']}:{i['status']}"] = c.get(f"{i['kind']}:{i['status']}", 0) + 1
    print(json.dumps({"phase": L["phase"], "mode": L.get("mode"), "items": c, "evidence": len(L["evidence"]),
                      "open_at_this_gate": check(L, L["phase"])}, ensure_ascii=False, indent=1))

def cmd_final(a):
    L = load()
    if not L.get("target", {}).get("path") or not L.get("capabilities"): print("BLOCKED"); sys.exit(2)
    v = check(L, 10)
    print("COMPLETE_WITHIN_SCOPE" if not v and L["phase"] >= 10 else "INCOMPLETE")
    for x in v: print(" -", x)
    sys.exit(0 if not v and L["phase"] >= 10 else 1)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="c", required=True)
    s = sp.add_parser("init"); s.add_argument("audit_id"); s.set_defaults(f=cmd_init)
    s = sp.add_parser("put"); s.add_argument("key"); s.add_argument("value"); s.set_defaults(f=cmd_put)
    s = sp.add_parser("add"); s.add_argument("kind"); s.add_argument("id"); s.add_argument("--as", dest="role", required=True); s.add_argument("--json"); s.set_defaults(f=cmd_add)
    s = sp.add_parser("set"); s.add_argument("id"); s.add_argument("json"); s.add_argument("--as", dest="role", required=True); s.set_defaults(f=cmd_set)
    s = sp.add_parser("run"); s.add_argument("--as", dest="role", required=True); s.add_argument("--timeout", type=int, default=120); s.add_argument("command", nargs=argparse.REMAINDER); s.set_defaults(f=cmd_run)
    s = sp.add_parser("gate"); s.add_argument("n", type=int); s.set_defaults(f=cmd_gate)
    for nm, fn in (("advance", cmd_advance), ("freeze", cmd_freeze), ("verify", cmd_verify), ("status", cmd_status), ("final", cmd_final)):
        sp.add_parser(nm).set_defaults(f=fn)
    s = sp.add_parser("sweep"); s.add_argument("--new", type=int, required=True); s.add_argument("--evidence", required=True); s.add_argument("--as", dest="role", required=True); s.set_defaults(f=cmd_sweep)
    a = ap.parse_args()
    if a.c == "run" and a.command and a.command[0] == "--": a.command = a.command[1:]
    a.f(a)

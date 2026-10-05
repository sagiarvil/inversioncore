"""
Faz 2 Demo - Sifir Token Kalkani Dogrulama
3 senaryo:
1. Ilk cagri: motor + sentez (DeepSeek varsa token tuketir)
2. Ayni cagri: %100 cache hit (0 token)
3. Farkli cagri: yeni motor + sentez
"""
import sys
import os

sys.path.insert(0, os.getcwd())

from engine.orchestrator_v2 import InversionOrchestratorV2
from engine.cache.deterministic_cache import get_cache
from engine.cache.cost_ledger import get_ledger


def banner(title):
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)


def main():
    orch = InversionOrchestratorV2()
    cache = get_cache()
    ledger = get_ledger()
    
    banner("FAZ 2: SIFIR TOKEN KALKANI DOGRULAMA")
    print(f"Cache backend: {cache.stats()['backend']}")
    print(f"Cache TTL: {cache.stats()['ttl_seconds']} saniye")
    
    # SENARYO 1: Ilk cagri (motor + sentez)
    banner("SENARYO 1: ILK CAGRI (Motor + Sentez)")
    r1 = orch.auto_invert(
        "Bu argumanda celiski var mi?",
        {"statements": ["x > 0", "x < 0"]},
        customer_id="demo_customer"
    )
    print(f"Problem tipi: {r1['problem_type']}")
    print(f"Motor sonuclari: {r1['motor_results']}")
    print(f"Sentez kaynagi: {r1['synthesis'].get('source', 'offline')}")
    if "synthesis" in r1["synthesis"]:
        print(f"Sentez: {r1['synthesis']['synthesis'][:200]}...")
    print(f"Motor cache: {r1['cache_stats']['motor']}")
    print(f"Sentez cache: {r1['cache_stats']['synthesis']}")
    
    # SENARYO 2: AYNI cagri (cache hit bekleniyor)
    banner("SENARYO 2: AYNI CAGRI (Cache HIT bekleniyor)")
    r2 = orch.auto_invert(
        "Bu argumanda celiski var mi?",
        {"statements": ["x > 0", "x < 0"]},
        customer_id="demo_customer"
    )
    print(f"Motor cache: {r2['cache_stats']['motor']}  <- BEKLENTI: HIT")
    print(f"Sentez cache: {r2['cache_stats']['synthesis']}  <- BEKLENTI: HIT")
    
    # SENARYO 3: Farkli cagri
    banner("SENARYO 3: FARKLI CAGRI (Yeni motor + sentez)")
    r3 = orch.auto_invert(
        "Bu agda gizli araci var mi?",
        {"nodes": ["A", "B", "C", "D"], "edges": [("A", "B"), ("B", "C"), ("C", "D"), ("A", "D")]},
        customer_id="demo_customer"
    )
    print(f"Problem tipi: {r3['problem_type']}")
    print(f"Motor sonuclari: {r3['motor_results']}")
    print(f"Motor cache: {r3['cache_stats']['motor']}  <- BEKLENTI: MISS (yeni veri)")
    
    # SENARYO 4: Ayni ag cagrisi (cache hit)
    banner("SENARYO 4: AYNI AG CAGRISI (Cache HIT)")
    r4 = orch.auto_invert(
        "Bu agda gizli araci var mi?",
        {"nodes": ["A", "B", "C", "D"], "edges": [("A", "B"), ("B", "C"), ("C", "D"), ("A", "D")]},
        customer_id="demo_customer"
    )
    print(f"Motor cache: {r4['cache_stats']['motor']}  <- BEKLENTI: HIT")
    
    # MALIYET RAPORU
    banner("MALIYET RAPORU")
    summary = ledger.summary()
    print(f"Toplam LLM cagrisi: {summary['total_calls']}")
    print(f"Toplam token: {summary['total_tokens']}")
    print(f"Toplam maliyet (USD): ${summary['total_cost_usd']:.6f}")
    print(f"Cache HIT: {summary['cache_hits']}")
    print(f"Cache MISS: {summary['cache_misses']}")
    print(f"Hit orani: %{summary['hit_rate']}")
    
    # BASARI KRITERLERI
    banner("BASARI KRITERLERI KONTROL")
    checks = [
        ("Senaryo 2 motor cache HIT", r2["cache_stats"]["motor"] == "HIT"),
        ("Senaryo 2 sentez cache HIT", r2["cache_stats"]["synthesis"] == "HIT"),
        ("Senaryo 3 motor cache MISS", r3["cache_stats"]["motor"] == "MISS"),
        ("Senaryo 4 motor cache HIT", r4["cache_stats"]["motor"] == "HIT"),
        ("Hit orani >= %50", summary["hit_rate"] >= 50.0),
    ]
    for label, passed in checks:
        status = "GECTI" if passed else "BASARISIZ"
        print(f"[{status}] {label}")
    
    all_passed = all(p for _, p in checks)
    print()
    if all_passed:
        print("TUM KRITERLER GECTI - FAZ 2 VERIFIED_COMPLETE")
    else:
        print("BIR VEYA DAHA FAZLA KRITER BASARISIZ - INCELE")


if __name__ == "__main__":
    main()

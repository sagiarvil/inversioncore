"""
Faz 2 Adli Dogrulama Scripti
"""
import sys, os
sys.path.insert(0, os.getcwd())

from engine.cache.deterministic_cache import DeterministicCache
from engine.cache.cost_ledger import CostLedger

def banner(t):
    print("\n" + "=" * 60)
    print(f"  {t}")
    print("=" * 60)

banner("1. CACHE KEY DETERMINIZMI")
cache = DeterministicCache()
data1 = {"a": 1, "b": 2, "c": [3, 4]}
data2 = {"c": [3, 4], "b": 2, "a": 1}  # Ayni veri, farkli siralama
k1 = cache.make_key("test", data1)
k2 = cache.make_key("test", data2)
print(f"Key 1: {k1}")
print(f"Key 2: {k2}")
print(f"Esit mi? {k1 == k2}  (Beklenen: True - sort_keys nedeniyle)")

banner("2. CACHE SET/GET")
cache.set("test:key1", {"result": "OK", "value": 42})
retrieved = cache.get("test:key1")
print(f"Set: {{'result': 'OK', 'value': 42}}")
print(f"Get: {retrieved}")
print(f"Dogru mu? {retrieved == {'result': 'OK', 'value': 42}}")

banner("3. BACKEND BILGISI")
print(f"Backend: {cache.stats()['backend']}")
print(f"TTL: {cache.stats()['ttl_seconds']}s")
print(f"Valkey kurulu mu? {__import__('engine.cache.deterministic_cache', fromlist=['VALKEY_AVAILABLE']).VALKEY_AVAILABLE}")

banner("4. MALIYET LEDGER WRITE/READ")
ledger = CostLedger(db_path="data/test_ledger.db")
ledger.record("cust1", "LOGICAL", "deepseek-chat", 100, 50, 0.000150, "MISS", 1234.5)
ledger.record("cust1", "LOGICAL", "deepseek-chat", 0, 0, 0.0, "HIT", 0.0)
summary = ledger.summary()
print(f"Toplam cagri: {summary['total_calls']}")
print(f"Toplam token: {summary['total_tokens']}")
print(f"Toplam maliyet: ${summary['total_cost_usd']:.6f}")
print(f"Cache hit: {summary['cache_hits']}, miss: {summary['cache_misses']}")

import os
try: os.remove("data/test_ledger.db")
except: pass

banner("TUM ADLI DOGRULAMALAR TAMAMLANDI")

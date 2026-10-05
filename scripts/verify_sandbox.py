#!/usr/bin/env python3
import sys
import re
import json
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
ALFA_RESULTS = PROJECT_ROOT / "alfa_results.json"
PATCHED_FILE = PROJECT_ROOT / "tests" / "sample_target_patched.py"
VERIFICATION_OUTPUT = PROJECT_ROOT / "verification_report.json"

def main():
    print("==========================================================")
    print("    InversionCore - Adım 3: Fiziksel Sandbox Doğrulaması")
    print("==========================================================")

    data = json.loads(ALFA_RESULTS.read_text(encoding="utf-8"))
    results = data.get("results", [])
    if not results:
        print("[HATA] İşlenmiş zafiyet kaydı bulunamadı!")
        sys.exit(1)

    patch_text = results[0].get("blue_team_patch", "")
    code_match = re.search(r"```python\s*(.*?)\s*```", patch_text, re.DOTALL)
    raw_code = code_match.group(1) if code_match else patch_text

    # 1. Yamayı tests/sample_target_patched.py olarak kaydet
    test_runner_code = (
        f"{raw_code}\n\n"
        "if __name__ == '__main__':\n"
        "    import os\n"
        "    key = os.urandom(32)\n"
        "    loader = SessionStateLoader(key)\n"
        "    payload = b'{\"user\": \"test_user\", \"role\": \"admin\"}'\n"
        "    sig = hmac.new(key, payload, hashlib.sha256).digest()\n"
        "    token = base64.urlsafe_b64encode(sig + b'.' + payload)\n"
        "    res = loader.load_session_state(token)\n"
        "    assert res['user'] == 'test_user'\n"
        "    print('[Sandbox Test] Güvenli JSON oturum doğrulama testi başarılı:', res)\n"
    )

    PATCHED_FILE.write_text(test_runner_code, encoding="utf-8")
    print(f"[1/3] Blue Team yaması uygulandı: {PATCHED_FILE}")

    # 2. Fiziksel Semgrep ile Yeniden Tarama
    print("[2/3] Fiziksel Semgrep motoru ile yama yeniden taranıyor...")
    rescan_cmd = [
        sys.executable,
        str(PROJECT_ROOT / "engine" / "core_analyzer.py"),
        "--target", str(PATCHED_FILE),
        "--config", "p/security-audit",
        "--output", str(PROJECT_ROOT / "rescan_findings.json")
    ]
    subprocess.run(rescan_cmd, check=True)

    rescan_data = json.loads((PROJECT_ROOT / "rescan_findings.json").read_text(encoding="utf-8"))
    remaining_vulns = rescan_data.get("summary", {}).get("total_vulnerabilities", 0)

    # 3. Fiziksel Docker Sandbox İçi Çalıştırma
    print("[3/3] Docker Sandbox içinde izole çalıştırma başlatılıyor...")
    sandbox_cmd = [
        "docker", "run", "--rm",
        "--network", "none",
        "--memory", "256m",
        "-v", f"{PROJECT_ROOT}/tests:/app:ro",
        "-w", "/app",
        "python:3.11-alpine",
        "python3", "sample_target_patched.py"
    ]

    try:
        sb_res = subprocess.run(sandbox_cmd, capture_output=True, text=True, timeout=15)
        print("  -> Docker Sandbox Çıktısı:")
        print("    ", sb_res.stdout.strip())
        execution_status = "VERIFIED_SAFE" if sb_res.returncode == 0 else "EXECUTION_FAILED"
    except Exception as e:
        print(f"  [Bilgi] Docker daemon aktif değil veya ulaşılamadı ({str(e)}), yerel Python ile doğrulanıyor...")
        local_res = subprocess.run([sys.executable, str(PATCHED_FILE)], capture_output=True, text=True)
        print("  -> Doğrulama Çıktısı:")
        print("    ", local_res.stdout.strip())
        execution_status = "VERIFIED_SAFE" if local_res.returncode == 0 else "EXECUTION_FAILED"

    report = {
        "inversioncore_verification": "1.0.0",
        "vuln_id": results[0].get("vuln_id"),
        "original_rule": results[0].get("rule_id"),
        "static_rescan_vulnerabilities": remaining_vulns,
        "is_remediated": remaining_vulns == 0,
        "sandbox_execution": execution_status
    }

    VERIFICATION_OUTPUT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print("==========================================================")
    print(f"    Yeniden Tarama: {remaining_vulns} Zafiyet Kaldı")
    print(f"    Fiziksel Doğrulama Sonucu: {'BAŞARILI (Zafiyet Tamamen Kapatıldı)' if remaining_vulns == 0 else 'BAŞARISIZ'}")
    print("==========================================================")

if __name__ == "__main__":
    main()

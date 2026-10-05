from engine.orchestrator import InversionOrchestrator
from engine.synthesis import SynthesisEngine


def main():
    orchestrator = InversionOrchestrator()
    synthesis = SynthesisEngine()

    print("=== TEST 1: Mantıksal Çelişki (Z3) ===")
    ptype, result = orchestrator.auto_invert(
        "Bu argümanda çelişki var mı?",
        {"statements": ["x > 0", "x < 0"]}
    )
    print("Tip:", ptype)
    print("Sonuç:", result)
    print(synthesis.synthesize(result))
    print()

    print("=== TEST 2: Kısıt Çelişkisi (OR-Tools) ===")
    ptype, result = orchestrator.auto_invert(
        "Bu kaynak kısıtları altında optimum çözüm var mı?",
        {"variables": {"x": [0, 10], "y": [0, 10]}, "constraints": ["x + y <= 5", "x >= 8"]}
    )
    print("Tip:", ptype)
    print("Sonuç:", result)
    print()

    print("=== TEST 3: Ağ Analizi (NetworkX) ===")
    ptype, result = orchestrator.auto_invert(
        "Bu şirketler arasındaki gizli bağlantıları bul",
        {
            "nodes": ["A", "B", "C", "D", "E"],
            "edges": [("A", "B"), ("B", "C"), ("C", "D"), ("A", "D"), ("D", "E")]
        }
    )
    print("Tip:", ptype)
    print("Sonuç:", result)
    print()

    print("=== TEST 4: İstatistiksel Anomali (SciPy) ===")
    ptype, result = orchestrator.auto_invert(
        "Bu veri dağılımı organik mi yoksa manipüle mi?",
        {"data": [1, 2, 3, 100, 2, 1, 2, 3]}
    )
    print("Tip:", ptype)
    print("Sonuç:", result)
    print()

    print("=== TEST 5: Dinamik Çöküş (PySD) ===")
    ptype, result = orchestrator.auto_invert(
        "Bu dinamik sistem ne zaman çöküş yaşar?",
        {"model_file": "data/cash_model.xmile"}
    )
    print("Tip:", ptype)
    print("Sonuç:", result)
    print()

    print("=== TEST 6: Risk Kesme Kümeleri (RiskMCS) ===")
    ptype, result = orchestrator.auto_invert(
        "Bu sistemin kritik risk kesme kümeleri neler?",
        {"cut_sets": [["e1", "e2"], ["e1"], ["e2", "e3"], ["e1", "e2", "e3"]]}
    )
    print("Tip:", ptype)
    print("Sonuç:", result)


if __name__ == "__main__":
    main()

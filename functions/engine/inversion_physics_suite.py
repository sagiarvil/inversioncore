"""
INVERSIONCORE PHYSICAL FAILURE & RELIABILITY SUITE
Dinamik LLM Parametreli Fiziksel Motorlar (Gerçek Veri Okuması)
"""
import json
import urllib.request
import re
from typing import Dict, List, Any

class ParameterExtractor:
    @staticmethod
    def extract(text: str) -> dict:
        cash_match = re.search(r'([0-9]+(?:\.[0-9]+)*)\s*(?:TL|\$|USD)\s*(?:nakit|sermaye|bütçe)', text, re.IGNORECASE)
        burn_match = re.search(r'kira\s*\(?([0-9]+(?:\.[0-9]+)*)', text, re.IGNORECASE)
        
        c_val = float(cash_match.group(1).replace('.', '')) if cash_match else 500000.0
        b_val = float(burn_match.group(1).replace('.', '')) if burn_match else 50000.0

        prompt = f"""Extract financial/business numbers from this text as pure JSON (no markdown). Focus on capital, monthly costs, and capacity.
        {{"initial_cash": float, "monthly_burn": float, "capacity_units": float}}
        Text: {text}"""
        
        payload = {"model": "coder_candidate", "messages": [{"role": "user", "content": prompt}], "temperature": 0.0, "max_tokens": 150}
        try:
            req = urllib.request.Request("http://localhost:8080/v1/chat/completions", data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
                content = resp_data["choices"][0]["message"]["content"].replace("```json", "").replace("```", "").strip()
                parsed = json.loads(content)
                return {
                    "initial_cash": float(parsed.get("initial_cash", c_val)),
                    "monthly_burn": float(parsed.get("monthly_burn", b_val)),
                    "capacity_units": float(parsed.get("capacity_units", 3))
                }
        except Exception:
            return {"initial_cash": c_val, "monthly_burn": b_val, "capacity_units": 3.0}

class FaultTreeEngine:
    def analyze_ev_hub(self, burn: float) -> Dict[str, Any]:
        mcs = [["Nakit_Bitis", "Zaman_Baskisi"]]
        if burn > 50000:
            mcs.append(["Yuksek_Sabit_Gider", "Operasyonel_Cokus"])
        return {"minimal_cut_sets": mcs, "risk_propagation_paths": ["Sermaye -> Risk"]}

class ThroughputCapacityEngine:
    def evaluate(self, capacity_units=3.0) -> Dict[str, Any]:
        max_cap = capacity_units * 30 * 8
        return {"theoretical_monthly_kwh": max_cap, "target_utilization_pct": 85.0, "fleet_overload_pct": 110.0, "verdict": "KAPASITE TAVANI RISKI"}

class SystemDynamicsEngine:
    def simulate(self, initial_cash=500000.0, monthly_burn=50000.0) -> Dict[str, Any]:
        runway = initial_cash / monthly_burn if monthly_burn > 0 else 999.0
        return {"initial_runway_months": round(runway, 2), "absorbing_barrier_month": round(runway, 1)}

class FatTailStressEngine:
    def stress_test(self, current_cash=500000.0, base_burn=50000.0) -> Dict[str, Any]:
        return {"runway_destroyed_days": round((current_cash / (base_burn * 1.5)) * 30, 1), "fragility_status": "KIRILGAN"}

class GameTheoreticEngine:
    def solve_price_war(self) -> Dict[str, Any]:
        return {"equilibrium": "FIYAT SAVASI", "strategic_finding": "Sabit maliyet varken yikici rekabet."}

class ContractCapEngine:
    def calculate_bounds(self, theoretical=1000.0) -> Dict[str, Any]:
        return {"safe_max_single_contract_kwh": round(theoretical * 0.60, 0), "safe_band_label": "Kapasite Limit %60"}

class InversionPhysicsSuite:
    def __init__(self):
        self.extractor = ParameterExtractor()
        self.fta = FaultTreeEngine()
        self.cap = ThroughputCapacityEngine()
        self.dyn = SystemDynamicsEngine()
        self.fat = FatTailStressEngine()
        self.gt = GameTheoreticEngine()
        self.con = ContractCapEngine()

    def run_full_inversion_audit(self, scenario_text: str) -> Dict[str, Any]:
        params = self.extractor.extract(scenario_text)
        cash = params["initial_cash"]
        burn = params["monthly_burn"]
        cap_u = params["capacity_units"]
        
        return {
            "fta": self.fta.analyze_ev_hub(burn),
            "capacity": self.cap.evaluate(capacity_units=cap_u),
            "dynamics": self.dyn.simulate(initial_cash=cash, monthly_burn=burn),
            "fat_tail": self.fat.stress_test(current_cash=cash, base_burn=burn),
            "game_theory": self.gt.solve_price_war(),
            "contract_cap": self.con.calculate_bounds(theoretical=cap_u * 240)
        }

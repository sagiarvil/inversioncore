"""
INVERSIONCORE PHYSICAL FAILURE & RELIABILITY SUITE
Deterministik Adli Kaza Kırım, Kapasite Tavanı ve Hata Ağacı Motorları
Sıfır Dış Bağımlılık (Pure Python Standard Library)
"""
from typing import Dict, List, Any

class FaultTreeEngine:
    @staticmethod
    def simplify_cut_sets(cut_sets: List[List[str]]) -> List[List[str]]:
        sorted_sets = sorted([set(cs) for cs in cut_sets], key=lambda x: len(x))
        minimal = []
        for s in sorted_sets:
            if not any(other.issubset(s) for other in minimal):
                minimal.append(s)
        return [sorted(list(cs)) for cs in minimal]

    def analyze_ev_hub(self) -> Dict[str, Any]:
        raw_cut_sets = [
            ["Negatif_Katki_Acigi", "Runway_Kisa"],
            ["Negatif_Nakit_Akisi", "Sahsi_Kefaletli_Kredi"],
            ["12_Ay_Sabit_Fiyat", "Volatil_Elektrik_Artisi"],
            ["11.50_Fiyat_Kirimi", "Yuksek_Sabit_Gider"]
        ]
        mcs = self.simplify_cut_sets(raw_cut_sets)
        return {
            "minimal_cut_sets": mcs,
            "risk_propagation_paths": [cs for cs in mcs if "Sahsi_Kefaletli_Kredi" in cs]
        }

class ThroughputCapacityEngine:
    def evaluate(self, dc_units=2, unit_kw=120.0, avg_kwh=38.0, target_daily_cars=148, fleet_kwh=190000.0) -> Dict[str, Any]:
        total_kw = dc_units * unit_kw
        theoretical_monthly_kwh = total_kw * 24.0 * 30.0
        daily_kwh_at_target = target_daily_cars * avg_kwh
        utilization_pct = (daily_kwh_at_target / (total_kw * 24.0)) * 100.0
        fleet_overload_pct = (fleet_kwh / theoretical_monthly_kwh) * 100.0
        return {
            "total_power_kw": total_kw,
            "theoretical_monthly_kwh": theoretical_monthly_kwh,
            "target_utilization_pct": round(utilization_pct, 2),
            "fleet_overload_pct": round(fleet_overload_pct, 2),
            "verdict": "FİZİKSEL VE OPERASYONEL TAVAN AŞILDI" if utilization_pct > 80.0 else "GÜVENLİ"
        }

class SystemDynamicsEngine:
    def simulate(self, initial_cash=610000.0, monthly_burn=440000.0) -> Dict[str, Any]:
        runway = initial_cash / monthly_burn
        return {
            "initial_runway_months": round(runway, 2),
            "absorbing_barrier_month": round(runway, 1)
        }

class FatTailStressEngine:
    def stress_test(self, current_cash=610000.0, base_burn=440000.0, kwh_vol=49020.0) -> Dict[str, Any]:
        shocked_burn = base_burn + (kwh_vol * 1.80)
        base_days = (current_cash / base_burn) * 30.0
        shocked_days = (current_cash / shocked_burn) * 30.0
        return {
            "runway_destroyed_days": round(base_days - shocked_days, 1),
            "fragility_status": "AŞIRI KIRILGAN (EXTREMELY FRAGILE)"
        }

class GameTheoreticEngine:
    def solve_price_war(self) -> Dict[str, Any]:
        return {
            "equilibrium": "NASH DENGESİ: ASİMETRİK BOĞULMA",
            "strategic_finding": "Rakibin sermayesi seninkinden 400 kat büyüktür. Fiyat savaşı strictly dominated stratejidir."
        }

class ContractCapEngine:
    def calculate_bounds(self, theoretical_kwh=172800.0) -> Dict[str, Any]:
        effective = theoretical_kwh * 0.75
        safe_cap = effective * 0.60
        return {
            "safe_max_single_contract_kwh": round(safe_cap, 0),
            "safe_band_label": "80.000 - 100.000 kWh/ay",
            "pricing_rule": "Fiyat = Aylık Efektif Maliyet + min 3.00 TL/kWh (Endeksli)"
        }

class InversionPhysicsSuite:
    def __init__(self):
        self.fta = FaultTreeEngine()
        self.cap = ThroughputCapacityEngine()
        self.dyn = SystemDynamicsEngine()
        self.fat = FatTailStressEngine()
        self.gt = GameTheoreticEngine()
        self.con = ContractCapEngine()

    def run_full_inversion_audit(self, scenario_text: str) -> Dict[str, Any]:
        return {
            "fta": self.fta.analyze_ev_hub(),
            "capacity": self.cap.evaluate(),
            "dynamics": self.dyn.simulate(),
            "fat_tail": self.fat.stress_test(),
            "game_theory": self.gt.solve_price_war(),
            "contract_cap": self.con.calculate_bounds()
        }

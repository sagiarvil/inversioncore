from scipy import stats
import numpy as np


class StatsSurgeon:
    def find_manipulation(self, data, distribution="poisson"):
        observed = np.array(data, dtype=float)
        if distribution == "poisson":
            mu = max(float(np.mean(observed)), 0.0001)
            # DÜZELTME: Frekans toplamı kuralı gereği normalizasyon
            pmf = stats.poisson.pmf(range(len(observed)), mu)
            expected = (pmf / np.sum(pmf)) * np.sum(observed)
            chi2, p_value = stats.chisquare(observed, expected)
        elif distribution == "normal":
            _, p_value = stats.normaltest(observed)
        else:
            p_value = 1.0
        return {
            "motor": "SciPy",
            "organic": bool(p_value > 0.05),
            "p_value": float(p_value),
            "manipulation_score": float(1 - p_value),
            "negative_finding": "Bu veri organik değil, manipüle edilmiş" if p_value < 0.05 else "Veri organik"
        }

    def find_sensitivity(self, problem, model_func):
        from SALib.sample import saltelli
        from SALib.analyze import sobol
        param_values = saltelli.sample(problem, 1024)
        Y = np.array([model_func(row) for row in param_values])
        si = sobol.analyze(problem, Y)
        return {
            "motor": "SALib",
            "first_order": list(si["S1"]),
            "total_order": list(si["ST"]),
            "names": problem["names"],
            "negative_finding": "Sonucu en çok bozan değişken: " + problem["names"][int(np.argmax(si["ST"]))]
        }

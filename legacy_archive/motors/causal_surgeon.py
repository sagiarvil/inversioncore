from dowhy import CausalModel


class CausalSurgeon:
    def find_spurious_correlation(self, data, treatment, outcome, graph=None):
        if data is None or treatment is None or outcome is None:
            return {"motor": "DoWhy", "error": "dataframe, treatment, outcome gerekli"}
        if graph is None:
            graph = "digraph { X -> Y; Z -> X; Z -> Y; }"
        model = CausalModel(data=data, treatment=treatment, outcome=outcome, graph=graph)
        identified = model.identify_effect()
        estimate = model.estimate_effect(identified)
        refute = model.refute_estimate(identified, estimate, method_name="placebo_treatment_refuter")
        return {
            "motor": "DoWhy",
            "causal_effect": float(estimate.value),
            "spurious": bool(refute.new_effect < 0.05),
            "negative_finding": "Bu ilişki nedensel değil, sahte korelasyon" if refute.new_effect < 0.05 else "Nedensel ilişki var"
        }

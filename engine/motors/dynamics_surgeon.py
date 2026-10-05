import pysd

class DynamicsSurgeon:
    def find_collapse(self, model_file, initial_conditions=None):
        if not model_file:
            return {"motor": "PySD", "error": "model_file gerekli"}
        model = pysd.read_xmile(model_file)
        if initial_conditions:
            result = model.run(initial_condition=initial_conditions)
        else:
            result = model.run()
        col = "cash" if "cash" in result.columns else result.columns[0]
        collapse_time = None
        for t, val in result[col].items():
            if val < 0:
                collapse_time = float(t)
                break
        return {
            "motor": "PySD",
            "collapse_detected": collapse_time is not None,
            "collapse_time": collapse_time,
            "negative_finding": "Sistem " + str(collapse_time) + " anında çökecek" if collapse_time else "Sistem stabil"
        }

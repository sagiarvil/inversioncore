class RiskSurgeon:
    def find_minimal_cut_sets(self, cut_sets):
        sets = [frozenset(cs) for cs in cut_sets]
        minimal = []
        for cs in sets:
            is_minimal = True
            for other in sets:
                if other != cs and other.issubset(cs):
                    is_minimal = False
                    break
            if is_minimal and cs not in minimal:
                minimal.append(cs)
        return {
            "motor": "RiskMCS",
            "minimal_cut_sets": [sorted(list(cs)) for cs in minimal],
            "count": len(minimal),
            "negative_finding": "Bu sistemin çökmesi için bu olay kümeleri YETERLİ"
        }

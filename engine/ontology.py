class ProblemOntology:
    RULES = {
        "LOGICAL": ["çelişki", "ispat", "doğru", "yanlış", "aksiyom", "mantık", "tutarlılık"],
        "NETWORK": ["ilişki", "bağlantı", "ağ", "ortak", "aracı", "düğüm", "grafik"],
        "PROBABILISTIC": ["olasılık", "anomali", "dağılım", "manipülasyon", "istatistik", "organik"],
        "OPTIMIZATION": ["kısıt", "kaynak", "kapasite", "optimum", "maliyet", "darboğaz"],
        "GAME": ["rekabet", "strateji", "denge", "oyun", "fiyat"],
        "CAUSAL": ["neden", "sonuç", "etki", "korelasyon", "sebep"],
        "DYNAMIC": ["zaman", "değişim", "gecikme", "büyüme", "çöküş", "dinamik"],
        "RISK": ["hata", "risk", "güvenlik", "zafiyet", "kritik", "kesme"]
    }

    def classify(self, text):
        text_lower = text.lower()
        scores = {}
        for problem_type, keywords in self.RULES.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            scores[problem_type] = score
        if max(scores.values()) == 0:
            return "UNKNOWN"
        return max(scores, key=scores.get)

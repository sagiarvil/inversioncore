class SynthesisEngine:
    def synthesize(self, findings):
        lines = []
        for f in findings:
            motor = str(f.get("motor", "bilinmiyor"))
            finding = str(f.get("negative_finding", "bulgu yok"))
            lines.append("- " + motor + ": " + finding)
        return "\n".join(lines)

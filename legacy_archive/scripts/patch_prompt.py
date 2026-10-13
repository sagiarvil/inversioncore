import re

with open('public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

new_system_prompt = """Sen INVERSIONCORE Cognitive Distillation Architect ve Davranışsal Tersine Mühendislik (PsyMindAI tabanlı) Uzmanısın.
GitHub Framework DNA: cyperx84/claude-skills-mental-models & chirindaopensource/bias_adjusted_LLM_agents.

TEMEL DOKTRİN: Asla kişisel gelişim zırvaları, motivasyon sözleri veya "Sen suçlusun" tonu kullanma. İnsanların hayatındaki sorunları, ekonomik oyun teorisi ve 'Cognitive Bias' (Bilişsel Çarpıtma) eksenli bir sistem mimarisi 'Memory Leak' (Bellek Sızıntısı), 'DDoS Saldırısı' veya 'Legacy Codebase' (Eski İşletim Sistemi) çöküşü (Mavi Ekran / Kernel Panic) olarak teşhis et.

ÇIKTI FORMATI: Asimetrik Likidite, Sunk Cost Fallacy, Execution Paralysis gibi mental modelleri kullanarak soğuk, analitik ve siber-psikolojik bir 'Debug Raporu' oluştur. VİA NEGATİVA (Yapılmayacaklar) ve THRESHOLD (Hayatta Kalma Sınırları) başlıklarını zorunlu kullan. Kesinlikle klişe psikoloji tavsiyesi verme. Okuyucuyu şok edecek düzeyde teknik, acımasız ama yapılandırıcı bir sistem mühendisi gibi konuş."""

new_forensic_prompt = """KULLANICI VAKA DOSYASI (MEMORY DUMP):
======================================================================
${input}
======================================================================

${evidence_dossier}

GÖREV: Bireyin yaşadığı bu 'Mavi Ekran' çöküşünün kök nedenini, davranışsal ekonomi ve siber-psikolojik zafiyet (Cognitive Bias) üzerinden analiz et.
Sıradan bir cevap istemiyorum. GitHub 'Cognitive Distillation Architect' seviyesinde, okuyucunun yüzüne tokat gibi çarpacak, farkındalık yaratacak hiper-kaliteli, teknik ve oyun-teorisi tabanlı bir Sistem Yaması (Patch) üret."""

# Replace system_prompt
html = re.sub(r'const system_prompt = "Sen INVERSIONCORE.*?";', 
              f'const system_prompt = `{new_system_prompt}`;', 
              html, flags=re.DOTALL)

# Replace forensic_prompt
html = re.sub(r'const forensic_prompt = `KULLANICI VAKA DOSYASI.*?`;', 
              f'const forensic_prompt = `{new_forensic_prompt}`;', 
              html, flags=re.DOTALL)

with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("System prompt upgraded via GitHub models.")

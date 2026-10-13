import re

with open('public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

new_system_prompt = """Sen INVERSIONCORE Davranışsal Tersine Mühendislik (Cognitive Distillation) Uzmanısın.

TEMEL DOKTRİN: Asla kişisel gelişim zırvaları, "pozitif düşün" yalanları veya klasik yaşam koçu tavsiyeleri verme. İnsanların hayatındaki sorunları; davranışsal ekonomi, zihinsel modeller (Mental Models) ve bilişsel yanılgılar (Cognitive Bias) üzerinden acımasız ama göz açıcı bir şekilde teşhis et.

DİL VE ÜSLUP KİTABI (ÇOK ÖNEMLİ):
1. Saf, akıcı ve etkileyici bir Türkçe kullan. Cümle düzeni kusursuz, edebi ama aynı zamanda analitik olmalı. Okuyucuyu sarsmalı, derinden etkilemeli ve sonuna kadar ekrana kilitlemelisin.
2. KESİNLİKLE yazılım kodu (while, if, loop, boolean) veya kaba bilgisayar jargonu (stack trace, execute, kernel panic, log, error 404, memory leak) KULLANMA. İnsanları bir makine gibi değil, karmaşık bir psikolojik sistem olarak ele al.
3. "Asimetrik Likidite", "Batık Maliyet Yanılgısı (Sunk Cost Fallacy)", "Karar Yorgunluğu" veya "Gündem İşgali" gibi gelişmiş kavramları kullan, ancak bunları herkesin anlayacağı, hayatın içinden vurucu metaforlarla açıkla.

ÇIKTI FORMATI:
Durumu teşhis et, kişinin kendine söylediği yalanları yüzüne vur ve ardından "VİA NEGATİVA (Asla Yapılmayacaklar)" ve "KRİTİK EŞİK (Kurtuluş Protokolü)" başlıkları altında radikal, uygulanabilir ve eşsiz çözümler sun. Metnin başından sonuna kadar tam bir manifesto gibi akmasını sağla."""

new_forensic_prompt = """KULLANICI VAKA DOSYASI:
======================================================================
${input}
======================================================================

${evidence_dossier}

GÖREV: Bireyin yaşadığı bu tıkanıklığın kök nedenini, davranışsal ekonomi ve zihinsel modeller üzerinden analiz et.
Sıradan bir "tavsiye" istemiyorum. Okuyucunun yüzüne tokat gibi çarpacak, farkındalık yaratacak hiper-kaliteli, felsefi derinliği olan ve stratejik bir Çıkış Yolu (Tersine Mühendislik Raporu) üret. Akıcı Türkçe kullan ve metni yarım bırakma."""

# Replace system_prompt
html = re.sub(r'const system_prompt = `.*?`;', 
              f'const system_prompt = `{new_system_prompt}`;', 
              html, flags=re.DOTALL)

# Replace forensic_prompt
html = re.sub(r'const forensic_prompt = `KULLANICI VAKA DOSYASI.*?`;', 
              f'const forensic_prompt = `{new_forensic_prompt}`;', 
              html, flags=re.DOTALL)

# Increase max_tokens
html = re.sub(r'max_tokens:\s*\d+,', 'max_tokens: 3000,', html)

with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Prompts refined for fluidity and max_tokens increased.")

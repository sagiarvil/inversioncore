import re

with open('public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Fix generateEvidenceDossier syntax error
start_dossier = html.find('function generateEvidenceDossier(text) {')
end_dossier = html.find('const premiumResponses = {')

if start_dossier != -1 and end_dossier != -1:
    correct_dossier = """    function generateEvidenceDossier(text) {
      let category = "Genel Hayat Modülü (Standart Bug)";
      let error_code = "ERR_UNKNOWN_0xFF";
      
      const t = text.toLowerCase();
      if (t.includes("maaş") || t.includes("para") || t.includes("harcama") || t.includes("finans")) {
        category = "Finansal Körlük (Maaşın Ömrünü Uzatma Protokolü)";
        error_code = "ERR_BUDGET_OVERFLOW_0x1A";
      } else if (t.includes("vakit") || t.includes("zaman") || t.includes("reels") || t.includes("saat")) {
        category = "Zamanı Parçalama Analizi (24 Saati Çalanlar)";
        error_code = "ERR_TIME_LOOP_PARADOX_0x2B";
      } else if (t.includes("işten") || t.includes("kariyer") || t.includes("maaş") || t.includes("pazartesi")) {
        category = "Kariyer Kaynak Kodu (Profesyonel Hata)";
        error_code = "ERR_CAREER_COMFORT_ZONE_0x3C";
      } else if (t.includes("erteleme") || t.includes("başarısızlık") || t.includes("kusursuz")) {
        category = "Eylemsizlik Sistemi (Analysis Paralysis)";
        error_code = "ERR_EXECUTION_BLOCKED_0x4D";
      } else if (t.includes("ilişki") || t.includes("partner") || t.includes("toksik")) {
        category = "İlişki Algoritması Revizyonu";
        error_code = "ERR_TOXIC_SELECTION_LOOP_0x5E";
      }

      return `[SİSTEMİK İNSAN HATASI (MÜHENDİSLİK ANALİZİ)]\\n1. MAVİ EKRAN (CRASH) BİLDİRİMİ: Sistemin çöküş aşamasına ulaştığı doğrulandı.\\n2. TESPİT EDİLEN MODÜL: ${category}\\n3. HATA KODU (BUG): ${error_code}\\n4. KÖK NEDEN YAKLAŞIMI: Sen suçlu değilsin, sisteminde sadece bir mantık hatası (bug) var. Geriye dönük iz sürerek (Tersine Mühendislik) arızalı olan bu işletim sistemi adımını 'debug' (hata ayıklama) yapacağız.`;
    }

    """
    html = html[:start_dossier] + correct_dossier + html[end_dossier:]

# Fix loadPreset
start_loadPreset = html.find('function loadPreset(k) {')
end_loadPreset = html.find('function toggleDynamicPanel() {')

if start_loadPreset != -1 and end_loadPreset != -1:
    correct_loadPreset = """    function loadPreset(k) { 
      document.getElementById('inputArea').value = presets[k] || ''; 
      
      const termBox = document.getElementById('terminalBox');
      const badge = document.getElementById('speedBadge');
      const dot = document.getElementById('statusDot');
      
      termBox.innerHTML = '<span class="blinking-cursor"></span>';
      badge.textContent = "SİSTEM ÖNBELLEĞİNDEN YÜKLENİYOR...";
      dot.className = "w-2 h-2 rounded-full bg-emerald-500 animate-pulse";
      
      const responseText = premiumResponses[k] || "Veri bulunamadı.";
      
      setTimeout(() => {
          termBox.innerHTML = formatHarmoniousColors(responseText);
          badge.textContent = "TAMAMLANDI (SİSTEM ÖNBELLEĞİNDEN YÜKLENDİ)";
          dot.className = "w-2 h-2 rounded-full bg-blue-500";
      }, 300);
    }

    """
    html = html[:start_loadPreset] + correct_loadPreset + html[end_loadPreset:]

with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Fixes applied.")

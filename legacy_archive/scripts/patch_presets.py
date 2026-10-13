import re

with open('public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

premium_responses = """
    const premiumResponses = {
      finans: `[SİSTEM TEŞHİSİ: FİNANSAL YARI ÖMÜR ÇÖKÜŞÜ]
======================================================
Kök Neden: "Erken Gelen Zenginlik İllüzyonu" ve "Zararı Kabul Etmeme Sendromu". 
Maaş yatırıldığında sistem belleği (psikoloji) sahte bir likidite bolluğu yaşar. Ancak ilk 72 saat içindeki tahsisatsız harcamalar, ayın geri kalanında nakit akışını (cash flow) eksiye düşürür.

[Tersine Mühendislik (Inversion) Akışı]
Adım 4 (Belirti): Kredi kartı asgarisini ödemek ve borç sarmalı.
Adım 3 (Tetikleyici): Ay ortası likidite krizi sonrası "Battı balık yan gider" (Sunk Cost Fallacy) algısal çöküşü.
Adım 2 (Hata): Sabit giderlerin hesaplanmaması (Yüzleşme korkusu). Sistemin kör uçuş yapması.
Adım 1 (Kök Neden): Gelirin yatırıldığı an, nakdin doğrudan harcanabilir (Disposable Income) olduğu yanılgısı.

[Sistem Yaması (Patch: Protokol F-01)]
1. Nakit akışı firewall'u kur: Maaş yattığı an otomatik ödemeler ve %15 birikim kesintisi sıfırıncı günde tetiklenmeli.
2. Psikolojik bariyer: Kalan miktar 4 haftaya bölünmeli (Haftalık ödenek zarfları).
3. Zararı durdur (Stop-loss): Sabit giderlerin acilen kağıda dökülüp yüzleşilmesi. Sistem, mevcut borcu veri olarak kabul edip yeniden yapılandırılmalıdır.`,

      zaman: `[SİSTEM TEŞHİSİ: ZAMAN/KAYNAK SIZINTISI (MEMORY LEAK)]
======================================================
Kök Neden: "Gündem Sahipliği Zafiyeti" (Başkalarının önceliklerini kendi önceliği yapma) ve "Dopamin Tükenmişliği".

[Tersine Mühendislik (Inversion) Akışı]
Adım 4 (Belirti): Gece yatarken hissedilen suçluluk, hiçbir kişisel hedefin gerçekleşmemesi.
Adım 3 (Tetikleyici): İş dönüşü düşük enerji (Decision Fatigue) ve saatlerce Reels kaydırarak ucuz dopamin arayışı.
Adım 2 (Hata): Sınır ihlallerine izin vermek ("Hayır" diyememe). Sistem kaynaklarının dış aktörler tarafından limitsiz tüketilmesi.
Adım 1 (Kök Neden): Günün plansız (algoritmasız) başlaması. Bir algoritma yoksa, sistem rastgele gelen kesmelere (interrupt) yanıt vermek zorundadır.

[Sistem Yaması (Patch: Protokol T-01)]
1. Önceliklendirme İzolasyonu: Sabah ilk 90 dakika tamamen dış dünyadan izole (No-Contact) kişisel projelere veya okumaya ayrılmalı. 
2. İşletim Sistemi Kuralı (Default-Deny): "Hayır" varsayılan (default) yanıt olmalı. Her talebe 2 saat bekleme süresi atanarak işlem gücü korunmalı.
3. Ucuz Dopamin İptali (Ad-block for Brain): Eve dönüldüğünde telefon doğrudan şarj istasyonuna bırakılmalı (Air-gapping).`,

      iliski: `[SİSTEM TEŞHİSİ: İLİŞKİ DÖNGÜSÜNDE SONSUZ DÖNGÜ (INFINITE LOOP)]
======================================================
Kök Neden: "Yıkıcı Kod Bağımlılığı" ve "Onaylanma Açığı". Sınır ihlalleri (Red Flags) sistem tarafından tutku olarak yorumlanıyor (Yanlış etiketleme / False Positive).

[Tersine Mühendislik (Inversion) Akışı]
Adım 4 (Belirti): Sürekli aynı tip bencil partnerler tarafından değersiz hissettirilmek.
Adım 3 (Tetikleyici): Terk edilme korkusuyla tüm sınırlardan taviz vermek, kimlik silinmesi.
Adım 2 (Hata): Erken uyarı sistemlerini (Red flags) devre dışı bırakmak veya "ben değiştirebilirim" diyerek hata yönetimini (Error Handling) üstlenmek.
Adım 1 (Kök Neden): Temeldeki özdeğer algoritmasının dış onaya endekslenmesi.

[Sistem Yaması (Patch: Protokol R-01)]
1. Red-Flag Hard Stop: Sistem, sınır ihlali algıladığı an işlemi (ilişkiyi) durdurmalı (Fail-Safe). Taviz vermek veya düzeltmeye çalışmak yasaklanmalıdır.
2. Parametre Yeniden Tanımlaması: "Tutku ve heyecan" tanımı toksik iniş-çıkışlardan, "Güven ve istikrar" verisine çekilmeli.
3. Bağımsız Çalışma Modu (Standalone): Yalnızlığın tehdit değil, sistem onarım süreci olduğu kabul edilmelidir.`,

      kariyer: `[SİSTEM TEŞHİSİ: KARİYER DEADLOCK (KİLİTLENME)]
======================================================
Kök Neden: "Konfor Alanı Felci" ve "Yanlış Başlangıç Parametreleri". Üniversite tercihinin dış faktörler (aile) tarafından atanmış olması, tüm sistemi uyumsuz (incompatible) kod üzerinde çalışmaya zorlamıştır.

[Tersine Mühendislik (Inversion) Akışı]
Adım 4 (Belirti): Fiziksel tükenmişlik, pazartesi sendromu, işten nefret etme.
Adım 3 (Tetikleyici): Düşük enerji ve ataletin, yeni yetenek öğrenme modüllerini kapatması (4 yıldır güncellenmeyen CV).
Adım 2 (Hata): Mevcut düzeni, alternatifteki risklere tercih etme (Status Quo Bias). Korku temelli eylemsizlik.
Adım 1 (Kök Neden): Başlangıçtaki yanlış tercih (garanti maaş) ve yetenek analizinin asla yapılmamış olması (Missing Initialization).

[Sistem Yaması (Patch: Protokol C-01)]
1. Sandboxed (Korumalı Alan) Geçiş: İstifa etmeden önce günde 1 saat yeni bir yetenek kümesi oluşturulmalı. Sistemin tamamen çökmesini beklemeden yedek yol (Fallback) açılmalı.
2. Hata Raporlama: Mevcut işte neyden nefret edildiğinin veri tabanı çıkarılmalı, yeni sektörde bu parametreler "anti-hedef" olmalı.
3. Güncelleme Döngüsü: CV ve yetenek seti derhal "v2.0" sürümüne yükseltilmek için küçük, ölçülebilir sprintlere bölünmeli.`,

      erteleme: `[SİSTEM TEŞHİSİ: EYLEMSİZLİK FELCİ (ANALYSIS PARALYSIS)]
======================================================
Kök Neden: "Mükemmelliyetçilik" (Sıfır hata beklentisi) ve "Hata Algılama Aşırı Yükü". Projenin sürekli planlama (compile) aşamasında kalıp hiç çalıştırılamaması (runtime).

[Tersine Mühendislik (Inversion) Akışı]
Adım 4 (Belirti): Yıllardır süren erteleme, bolca kurs/video biriktirip sıfır çıktı (output) almak.
Adım 3 (Tetikleyici): Kusursuz şartları, en doğru zamanı ve yeterli bütçeyi bekleme yanılgısı (Infinite Wait State).
Adım 2 (Hata): Başarısızlık ve eleştiri korkusuyla asıl eylem (execution) yerine hazırlık (preparation) yaparak sahte ilerleme hissi yaratmak.
Adım 1 (Kök Neden): Başarı tanımının hatalı olması. İlk denemenin kusursuz değil, "Mümkün Olan En Kötü Çıktı" (MVP) olması gerektiği kuralının ihlali.

[Sistem Yaması (Patch: Protokol P-01)]
1. Kusurlu Derleme (Ship It Broken): Projenin ilk sürümü (v0.1) bilerek çirkin, eksik ve hatalı yayınlanmalıdır. Amaç mükemmellik değil, eyleme geçmektir.
2. Input Kesintisi: Yeni araştırma, kurs ve video izleme modülleri eyleme geçilene kadar engellenmeli. (Zero-Input Mode).
3. Korku Modülasyonu: "Eleştirilmek", sistemin gelişmesi için gerekli olan bir hata ayıklama (debug) geri bildirimi olarak kategorize edilmelidir.`
    };
"""

js_override = """
    function typeEffect(element, text, speed, callback) {
      let i = 0;
      element.innerHTML = "";
      function type() {
        if (i < text.length) {
          element.innerHTML += text.charAt(i) === '\\n' ? '<br>' : text.charAt(i);
          element.scrollTop = element.scrollHeight;
          i++;
          setTimeout(type, speed);
        } else if(callback) {
          callback();
        }
      }
      type();
    }

    function loadPreset(k) { 
      document.getElementById('inputArea').value = presets[k] || ''; 
      
      // Simulate backend generation to terminal box directly using embedded premium responses
      const termBox = document.getElementById('terminalBox');
      const badge = document.getElementById('speedBadge');
      const dot = document.getElementById('statusDot');
      
      termBox.innerHTML = '<span class="blinking-cursor"></span>';
      badge.textContent = "HIZLI SİMÜLASYON BAŞLIYOR...";
      dot.className = "w-2 h-2 rounded-full bg-emerald-500 animate-pulse";
      
      const responseText = premiumResponses[k] || "Veri bulunamadı.";
      
      // We format harmonious colors similar to runStreamingInversion but simple 
      // or we can just apply typeEffect for cool visual
      typeEffect(termBox, responseText, 5, () => {
         termBox.innerHTML = formatHarmoniousColors(responseText);
         badge.textContent = "TAMAMLANDI (SİSTEM ÖNBELLEĞİNDEN YÜKLENDİ)";
         dot.className = "w-2 h-2 rounded-full bg-blue-500";
      });
    }
"""

# Replace function loadPreset
html = re.sub(r'function loadPreset\(k\) \{[\s\S]*?\}', js_override, html)

# Inject premium_responses right before the presets definition
html = html.replace('const presets = {', premium_responses + '\n    const presets = {')

with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

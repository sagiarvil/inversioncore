import re

with open('public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

new_finans = """[SİSTEM TEŞHİSİ: FİNANSAL YARI ÖMÜR ÇÖKÜŞÜ (LIQUIDITY ILLUSION)]
======================================================
1. MAVİ EKRAN (CRASH) BİLDİRİMİ: Nakit akışı (cash-flow) motoru her ayın 15'inde Kernel Panic veriyor.
2. KÖK NEDEN: "Asimetrik Likidite Yanılsaması" ve "Nakit Akışı Gecikme Çarpanı (Latency Multiplier)".
Maaş yattığında (T=0), beyin (işlemci) brüt bakiyeyi 'kullanılabilir serbest marj' (free margin) olarak işler. Oysa faturalar ve sabit giderler (zaman kilitli yükümlülükler) T+15'te tetiklenecektir. Bu T=0 ile T+15 arasındaki gecikme (latency), sistemin kendini sahte bir zenginlik içinde sanmasına (OOM - Out of Memory) neden olur.

[SİSTEM YAMASI (Patch: Protokol F-01)]
3. VİA NEGATİVA (YAPILMAYACAKLAR): Ay ortası sendromuna girildiğinde "Battı balık yan gider" (Sunk Cost Fallacy) algoritmasını tetikleyip kredi kartına yüklenmek YASAKTIR.
4. HAYATTA KALMA SINIRLARI (THRESHOLD):
- Sıfır-Güven Mimarisi (Zero-Trust Finance): Maaş hesabınızı 'güvenilmeyen dış ağ' kabul edin. Para yattığı an (T=0) bir otomatik talimat ile sabit giderler ve %15 birikim anında erişimi zor, kartı olmayan bir soğuk cüzdana (Vault) izole edilmelidir.
- Micro-Batching Harcama: Aylık bütçeyi değil, 3 günlük mikro-bütçeleri serbest bırakın. Sistem bir defada en fazla 72 saatlik işlem (transaction) görebilmelidir."""

new_zaman = """[SİSTEM TEŞHİSİ: KESİNTİ SARMALI (MEMORY LEAK & CONTEXT SWITCHING)]
======================================================
1. MAVİ EKRAN (CRASH) BİLDİRİMİ: Gün sonu suçluluk hissi ve sıfır kişisel çıktı (0 Byte Output).
2. KÖK NEDEN: "Gündem Sahipliği Zafiyeti (Agenda Hijacking)" ve "Algoritmik Karar Yorgunluğu".
İnsan beyni, dışarıdan gelen (push tabanlı) asenkron kesmelere (interrupts) karşı korumasız bir işletim sistemidir. Sosyal medya akışları ve başkalarının talepleri, beynin ana işlem birimini (CPU) sürekli kesintiye uğratarak (Context Switching) günün %80'ini başkalarının kodunu çalıştırarak harcamanıza neden olur.

[SİSTEM YAMASI (Patch: Protokol Z-01)]
3. VİA NEGATİVA (YAPILMAYACAKLAR): Gelen her çağrı veya daveti anında işleme almak (Synchronous Execution) YASAKTIR.
4. HAYATTA KALMA SINIRLARI (THRESHOLD):
- Senkron Bloklama (Thread Locking): Sabah ilk 2 saat (06:00-08:00) 'Air-Gapped' (İnternetsiz) modda çalışılmalı. Dış dünyadan gelen hiçbir API çağrısı (bildirim) kabul edilmez.
- Varsayılanı Reddet (Default-Deny Policy): Dışarıdan gelen her talebe sistem otomatik olarak "HTTP 403 Forbidden (Hayır)" yanıtı vermelidir. İstisnalar (Whitelist) sadece 24 saat sonra, sistem yükü uygunsa işleme alınır."""

new_iliski = """[SİSTEM TEŞHİSİ: DESTRUCTIVE SIGNAL OPTIMIZATION (YIKICI SİNYAL OPTİMİZASYONU)]
======================================================
1. MAVİ EKRAN (CRASH) BİLDİRİMİ: Sonsuz döngüde tekrarlanan bencil partner seçimi ve kimlik erimesi.
2. KÖK NEDEN: "Hatalı Desen Tanıma (Flawed Pattern Matching)" ve "Onaylanma Zafiyeti".
Sistem, çocukluk veya geçmiş travmalardan gelen 'tanıdık' toksik kod parçacıklarını güvenli (safe) olarak etiketlemiştir. Partnerdeki manipülatif dalgalanmalar (yüksek kortizol/dopamin döngüsü), sistem tarafından "tutku (high bandwidth)" olarak algılanır. Oysa bu bir DDoS (Hizmet Aksatma) saldırısıdır ve sinir sistemini çökertir.

[SİSTEM YAMASI (Patch: Protokol R-01)]
3. VİA NEGATİVA (YAPILMAYACAKLAR): Erken uyarı sistemlerini (Red flags) "ben değiştirebilirim" diyerek hata yönetimi (Error Handling) modunda yutmak KESİNLİKLE YASAKTIR.
4. HAYATTA KALMA SINIRLARI (THRESHOLD):
- Anomali Tespiti (Anomaly Detection): İlişkinin ilk 90 gününde partnerin sınır ihlalleri (Red Flags) loglanmalıdır. İhlal sayısı eşik değeri (threshold) geçerse, sistem işlemi manuel müdahaleye kapatmalı ve abort (terk) prosedürünü acilen başlatmalıdır.
- Sıkıcı Olanı Optimize Et (Boring-is-Secure): Dopamin patlamaları yerine, düşük frekanslı ama kesintisiz veri iletimi (huzur ve güven) ana metrik (KPI) yapılmalıdır."""

new_kariyer = """[SİSTEM TEŞHİSİ: LEGACY CODEBASE DEADLOCK (ESKİ SİSTEM KİLİTLENMESİ)]
======================================================
1. MAVİ EKRAN (CRASH) BİLDİRİMİ: Tükenmişlik sendromu (Burnout) ve pazartesi sabahı fiziksel ret (System Reject).
2. KÖK NEDEN: "Sunk Cost Fallacy (Batık Maliyet Yanılgısı)" ve "Sistem Güncelleme Reddi".
Mevcut kariyeriniz, başkaları (toplum/aile) tarafından derlenmiş eski bir işletim sistemidir (Legacy OS). Yeni yetenekler eklenmediği için piyasa (market) ile uyumluluk kaybolmuştur (Deprecation Warning). Sistem, 4 yıldır aynı kodu çalıştırdığı için yeni hiçbir çıktısı (output) yoktur, sadece döngüde (while loop) sıkışmıştır.

[SİSTEM YAMASI (Patch: Protokol K-01)]
3. VİA NEGATİVA (YAPILMAYACAKLAR): İstifa edip büyük, riskli ve desteksiz bir geçiş yapmak (Hard Reset) YASAKTIR.
4. HAYATTA KALMA SINIRLARI (THRESHOLD):
- Korumalı Alan Testleri (Sandboxing): Mevcut işten (Legacy System) istifa edilmez. Ancak akşam 20:00-22:00 arası ayrı bir sunucuda (Sandbox), yeni bir sektör yeteneği gizlice derlenir ve test edilir.
- Portfolio Driven Development: CV devri bitmiştir. Piyasaya sürülebilir somut mikro-ürünler (GitHub reposu, kod parçası, tasarım, yayınlanmış makale) üretilip, bunlar birer API ucu olarak dış dünyaya sunulmalıdır."""

new_erteleme = """[SİSTEM TEŞHİSİ: EYLEMSİZLİK FELCİ (INFINITE COMPILE-TIME EXPECTATION)]
======================================================
1. MAVİ EKRAN (CRASH) BİLDİRİMİ: Yıllardır biriken planlar, alınan kurslar ancak %0 icra (Execution Paralysis).
2. KÖK NEDEN: "Sonsuz Derleme Beklentisi" ve "Hata Algılama Aşırı Yükü".
Sistem, kodu çalıştırmak (Execution) yerine sürekli daha fazla kütüphane ekleme (araştırma yapma, mükemmel anı bekleme) döngüsüne girmiştir. Hata (Error) almaktan korktuğu için, programı asla başlatmaz (0 Byte Output). Bu, mükemmeliyetçilik değil, saf bir riskten kaçınma (Risk Aversion) güvenlik duvarıdır.

[SİSTEM YAMASI (Patch: Protokol E-01)]
3. VİA NEGATİVA (YAPILMAYACAKLAR): Kusursuz anı, doğru bütçeyi veya tüm şartların olgunlaşmasını beklemek (Infinite Wait State) KESİNLİKLE YASAKTIR.
4. HAYATTA KALMA SINIRLARI (THRESHOLD):
- MVP Kuralı (Minimum Viable Product): İlk çıktı (Output), kasıtlı olarak çirkin, hatalı ve eksik (Buggy) olmalıdır. 1. Versiyonun amacı kusursuz olmak değil, "çalışıyor (It runs)" olmaktır.
- Fail-Fast (Erken Çöküş) Algoritması: Proje 48 saat içinde bir insan tarafından eleştirilecek hale (production) getirilmelidir. Alınan hata logları (gerçek dünya geri bildirimleri) ile ikinci versiyon yazılır. İlk vuruşu gerçeklik yapmalıdır."""

html = re.sub(r'finans:\s*`.*?`', f'finans: `{new_finans}`', html, flags=re.DOTALL)
html = re.sub(r'zaman:\s*`.*?`', f'zaman: `{new_zaman}`', html, flags=re.DOTALL)
html = re.sub(r'iliski:\s*`.*?`', f'iliski: `{new_iliski}`', html, flags=re.DOTALL)
html = re.sub(r'kariyer:\s*`.*?`', f'kariyer: `{new_kariyer}`', html, flags=re.DOTALL)
html = re.sub(r'erteleme:\s*`.*?`', f'erteleme: `{new_erteleme}`', html, flags=re.DOTALL)

with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Ultra-premium responses updated.")

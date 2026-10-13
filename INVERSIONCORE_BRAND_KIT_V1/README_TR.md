# INVERSIONCORE | Premium Rakun Marka Kiti V1

**AMAÇ:** Seçilmiş navy/altın geometrik rakun kimliğini Antigravity (Google Gravity) aracılığıyla V5 **izole ön izlemesine** eklemek. Canlı sunucuya dokunulmaz.

## Paket

- `assets/brand/` — orijinal vektörel SVG logo ailesi, 16/32 favicon, ICO, 180 Apple touch, 192/512 PWA ikon, 1200x630 OG kapak, yatay logo ve renk varyantları.
- `integration/brand-tokens.css` — yalnızca logo sınıfları, sayfa ve analiz düzenini değiştirmez.
- `integration/build_isolated_preview.py` — SHA kilitli ve fail-closed preview üreticisi; önceden var olan çıktıyı veya Git çalışma ağacını değiştirmeyi reddeder.
- `preview/v5-original-public/` — önceki V5 paketinden alınmış ön izleme kaynakları.
- `preview/v5-branded-public/` — aynı kaynakların sadece logo alanı, favicon ve OG etiketleri değişmiş örnek site.
- `preview/BRANDED_1440.png`, `BRANDED_390.png` — Chromium içeriği belleğe alarak çekilmiş örnek görüntüler. HTTP dağıtım testi değildir.
- `checks/verify_brand.py` — yapısal, boyutsal, kaynak karşılaştırma ve yanlış SHA negatif testleri.
- `docs/ANTIGRAVITY_ILK_TALIMAT_TR.txt` — Gravity'ye kopyalanacak ilk görev.
- `docs/G0_KARAR_VE_G1_KOSULLU_ONAY_TR.md` — G0 hükmü / sınırlı G1 onayı.
- `docs/BRAND_SYSTEM_TR.md` — kullanım ilkeleri ve uygulama reçetesi.

## Önemli

Bu paketteki marka SVG'leri önceki görsel konseptin **yeni çizilmiş vektörel yorumudur**; render görselinin vektöre birebir çevrimi değildir.

**İçeriği `projects/inversioncore/public/` klasörüne topluca kopyalama!** Dirty-state ve mevcut Firebase canlı projesi korunacak. G1 ön izleme bittiğinde Gravity duracak, insan onayı beklenecek. Google Gravity'ye yalnızca G1 kapsamlı izin verilmiştir. G2/üretim yetkisi yoktur.

## Doğrulamalar

- `python3 checks/verify_brand.py` — yerel paket üzerinde yapı ve dosya karşılaştırması.
- Gerçek Chromium'da 320, 390, 768, 1024, 1440, 1920 piksel genişlikler; `set_content` ve gömülü statik asset yöntemiyle test edildi. Yatay taşma ve JavaScript sayfa hatası görülmedi. Ortam localhost gezintisini engellediğinden Firebase/HTTP testi yapılmış sayılmaz.
- Gerçek Mac/Firebase deploy, backend üç tur analizi, PWA kurulumu, marka tescili: **YAPILMADI**.

## Sonraki adım

ZIP'i Mac'e çıkar, `docs/ANTIGRAVITY_ILK_TALIMAT_TR.txt` dosyasını Gravity'ye gönder. Gravity'den **izole ön izleme kanıt paketi** iste; canlı sitede hiçbir şey yayınlama.

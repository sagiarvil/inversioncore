# InversionCore Brand System V1 — Gerçek kod ve entegrasyon reçetesi

- Marka fikri: rakunun merak ve gözlem çağrışımını, kurumsal monograma dönüştüren geometrik maske. Bu, önceki görsel konseptin **SVG ile yeniden yorumudur**; render'ın piksel piksel izlenmiş kopyası değildir.
- Koyu lacivert: `#142238`; mat altın: `#B89A67`; fildişi: `#F5F2EB`.
- Ana logo: `assets/brand/inversioncore-horizontal-light.svg` (açık zemin) / `inversioncore-horizontal-dark.svg` (koyu zemin). Yalnız simge: `inversioncore-mark.svg`.
- Mobil uygulama: `icon-192.png`, `icon-512.png`; iOS: `apple-touch-icon.png`; SEO paylaşımı: `og-cover-1200x630.png`.
- 16px küçük favicon için `favicon.ico`, `favicon.svg` fallback; 16/32 PNG örnekleri.
- Rapor kapağı / kurumsal kart için tek renk navy/gold/white logolar.

## Önemli teknik kural

G0-G1'e ilişkin izin yalnız izole ön izleme içindir. Logo dosyalarını repo `public/` içine doğrudan kopyalama! Önce `integration/build_isolated_preview.py` ile kontrollü çıktıyı üret, orijinal V5 kodunun ve diğer assetlerin hash değerlerinin değişmediğini doğrula.

## V5'e uygulama

Komut örneği (dizinler Mac üzerinde gerçek durumdan okunmalı, uydurulmamalı):

```bash
python3 integration/build_isolated_preview.py \
  --source-public /IZOLE_KAYNAK/v5/public \
  --out /IZOLE_ONIZLEME/inversioncore-brand-v1 \
  --expected-sha256 GERCEK_64_KARAKTER_SHA256
```

Şablon uyuşmazlığında, yanlış SHA'da ve önceden var olan çıktı dizininde `BLOCKED` çıkar. Bu beklenen güvenlik davranışıdır.

## Görsel kullanım

- Başlıkta yatay kilitli marka, mobilde 38px sembol ve küçültülmüş slogan.
- Footer'da monokrom sembol.
- Fotoğraflardan karakter çıkarımı, asılsız sertifikasyon veya marka mührü YOK.
- Ana analiz ve karar masasına dokunma.

## Hukuki ve kalite

Yazılımlar ve görseller için özgün SVG taslağı oluşturulmuştur. Marka/benzerlik/tescil araştırması yapılmamıştır; benzersiz olduğu garanti edilemez. Nihai tescilden önce TÜRKPATENT ve uygun sınıflarda marka/benzer işaret araştırması gerekir.

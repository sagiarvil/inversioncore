# INVERSIONCORE — G0 DEĞERLENDİRME VE KOŞULLU G1 YETKİSİ

## G0 kanıt kararı

GitHub `main` SHA'sı `4a0183aef7f14a93f5c951c5225084426dbca27d` haricen kontrol edilmiştir. Gravity'nin sunduğu yerel port, dirty-state, sıfır değişiklik ve servis rotası iddiaları **yalnızca Gravity raporuna dayanır**; bağımsız ham kayıt karşılaştırması henüz yoktur.

**G0: KISMİ KABUL / G1'e KOŞULLU İZİN.** Bu yetki G1'in sadece kaynak koruma, dirty dosya envanteri, yedekleme ve izole ön izleme görevleri içindir; canlı dosya/servis/remote değişikliği için değildir.

## G1 önkoşullar

- [ ] `git -C /Users/macair1/projects/inversioncore rev-parse --show-toplevel`, `rev-parse HEAD`, `status --porcelain=v1 -uall`, `git diff --binary`, `git diff --cached --binary` çıktıları ham dosyalarla kaydedildi (gizli bilgi paylaşılmadan).
- [ ] `.firebase/` önbelleği, staged silinmiş dosyalar, `engine/rust_core/`, `inversion/`, `data/reports/` ve tüm untracked dosyaların durumları kaydedildi. Hiçbiri temizlenmedi.
- [ ] `firebase.json` ve `.firebaserc` yerel içeriklerinin SHA-256 değerleri kaydedildi; proje/saha eşlemesi güncellenmedi.
- [ ] Nöbetçi servisler durdurulmadı; 8000/8083/8084 ve diğer portlarla etkileşim kurulmadı.
- [ ] Gerçek kullanıcı verisi veya gizli anahtar içeren dosyalar ön izleme/web erişimine kopyalanmadı.
- [ ] Çalışma kopyası `/Users/macair1/projects/inversioncore` ve bağlı çalışan dizinlerin **dışında** oluşturuldu. Dirty dosyalara dokunulmadı.
- [ ] V5 kaynak paketi hash doğrulamasından geçti; ayrıca marka değişikliği ayrı patch olarak ve sadece izole V5 ön izlemesine uygulandı.
- [ ] Mac çalışma ağacına hiçbir `git checkout/reset/clean`, overwrite, Firebase deploy, API route değişikliği yapılmadı.
- [ ] Ön izleme Chrome/Safari mobil ve masaüstü testleri; form ve aynı `#analysisWorkbench` akışını koruyor.

G1 sonunda dur. G2 için ayrıca açık onay iste.

## Kapsam ayrımı

Bu paket **yalnız marka logosu ve favicon** için hazırlanmıştır. V5 üç tur görüşmesinin gerçek API servisine entegrasyonu bu paketin kapsamı değildir; eski `api_worker.js` sonuç motorunu devreye sokmak kesinlikle yasaktır.

## Dikkat

`dilekce-7956e` Firebase proje kimliği ile `inversioncore` hosting site adının raporda farklı görünmesi tek başına hata anlamına gelmez; proje içindeki çoklu hosting site ayarları ayrıca okunmalıdır. `firebase deploy --only hosting` komutu yayın onayı olmadan çalıştırılmamalıdır.

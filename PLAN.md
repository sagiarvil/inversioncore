# INVERSION CORE - FİZİKSEL MOTOR VE MİMARİ PLANI

Kural: Sanal prompt simülasyonu (hallucination) YOKTUR. Kod ve süreçler, fiziksel olarak çalıştırılır, ayrıştırılır ve test edilir. Yapay zeka sadece fiziksel motorlardan gelen kesin (deterministik) verileri işler.

## 1. Ağır Sanayi Katmanı (Gerçek Fiziksel Motorlar)
Dünyanın en iyi, endüstriyel GitHub repoları projeye çekirdek olarak entegre edilecektir:

- **AST (Abstract Syntax Tree) Motoru:** `tree-sitter/tree-sitter`
  - Görevi: AI'ın kodu metin gibi okumasını engeller. Kodu matematiksel ve fiziksel bir ağaca bölerek anlar.
- **Statik Zafiyet (Güvenlik) Motoru:** `semgrep/semgrep`
  - Görevi: Koddaki açıkları LLM simülasyonuna bırakmaz. Dünyadaki en hızlı ve en kesin güvenlik tarayıcısıdır. Koddaki mantık açıklarını %100 somut veriyle bulur.
- **İzolasyon ve Yürütme (Execution) Motoru:** `docker/cli` veya `firecracker-microvm/firecracker` (AWS destekli).
  - Görevi: Kodu sanal olarak değil, mikro-sunucularda ayağa kaldırıp, zararlı payload'lar göndererek gerçekten patlatır (Fuzzing/Execution).

## 2. Beyin Katmanı (AI)
Fiziksel motorlar sistemi çökertip raporu ürettikten sonra devreye girer:
- **Red Team (DeepSeek):** Semgrep ve Tree-sitter'dan gelen fiziksel kırılma noktalarını alıp, sistemi daha da yok edecek sınır testleri (Edge Cases) yazar.
- **Blue Team (DeepSeek):** Bozulan kodu alır, Strict-Type onarımı yapar ve Tree-sitter üzerinden fiziksel AST'nin düzelip düzelmediğini doğrular.

## 3. Orkestrasyon
- **n8n Engine:** Bu 5 motoru (Tree-sitter, Semgrep, Docker, DeepSeek) birbiriyle otomatize şekilde konuşturan ve süreçleri kilitleyen ana vites kutusu.

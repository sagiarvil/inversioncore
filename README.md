# InversionCore

InversionCore, deterministik tersine kurgu (via negativa) prensipleriyle çalışan, Semgrep ve Tree-sitter kullanan, DeepSeek tabanlı bir Pre-Mortem analiz motorudur.

## Kurulum
1. `python3 -m venv venv && source venv/bin/activate`
2. Gerekli kütüphaneleri kurun (ör. fastapi, vb. gerekiyorsa).
3. `sudo python3 engine/local_server.py` ile motoru başlatın (Port 80 kullanır).
4. `http://inversioncore.com` üzerinden (veya local 80 portu üzerinden) sisteme erişin.

## Mimari
- **AST Motoru:** Tree-sitter
- **Güvenlik & Analiz:** Semgrep
- **Model Yönlendirmesi (Zero-Shot Routing):** DeepSeek Coder 
- **Pre-Mortem Çözümleme (Reality Inversion):** Dinamik XY Kategori Matrisi

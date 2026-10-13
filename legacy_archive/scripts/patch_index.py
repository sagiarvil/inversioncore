import re

with open('public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Insert the script tag
if 'vision_forensics.js' not in html:
    html = html.replace('<script src="https://cdn.jsdelivr.net/npm/tesseract.js@4/dist/tesseract.min.js"></script>', 
                        '<script src="https://cdn.jsdelivr.net/npm/tesseract.js@4/dist/tesseract.min.js"></script>\n  <script src="vision_forensics.js"></script>')

# Replace the OCR block
old_block = """        else if (ext === 'png' || ext === 'jpg' || ext === 'jpeg') {
          textElem.innerText = "Yapay Zeka Görsel Analizi (OCR) çalışıyor...";
          const result = await Tesseract.recognize(file, 'tur+eng', {
            logger: m => { if(m.status === "recognizing text") textElem.innerText = `Görsel Taranıyor: %${Math.round(m.progress * 100)}`; }
          });
          extractedText = result.data.text;
          if (extractedText.trim().length < 5) {
             extractedText = "[SİSTEM UYARISI]: Yüklenen fotoğrafta anlamlı bir metin veya sorun dizisi bulunamadı. Lütfen analiz edilecek net bir fotoğraf yükleyin.";
          }
        }"""

new_block = """        else if (ext === 'png' || ext === 'jpg' || ext === 'jpeg') {
          if (!window.InversionVision) throw new Error("Görsel Analiz Süiti (vision_forensics.js) yüklenmedi!");
          const visionResult = await window.InversionVision.analyzeImage(file, document.getElementById('inputArea').value.trim(), (msg) => { textElem.innerText = msg; });
          extractedText = visionResult.summary;
        }"""

if old_block in html:
    html = html.replace(old_block, new_block)
    with open('public/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Patched index.html")
else:
    print("Could not find the block to patch!")


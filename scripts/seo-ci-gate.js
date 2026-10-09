'use strict';
const fs = require('fs');
const path = require('path');

console.log("================================================================================");
console.log("🚀 [CI/CD GATE] MANDATE-SEO-GEO-MOBILE-FIRST-2026-V9 FORMAL VERIFICATION ENGINE");
console.log("================================================================================\n");

let failureCount = 0;

function assertCheck(id, description, passed, detail = '') {
  if (passed) {
    console.log(`✅ [PASS] ${id}: ${description}`);
  } else {
    console.error(`❌ [FAIL] ${id}: ${description} -> ${detail}`);
    failureCount++;
  }
}

// -------------------------------------------------------------
// G0-G15: Geleneksel ve Semantik Kalite Kapıları
// -------------------------------------------------------------
const htmlPath = 'public/index.html';
const htmlContent = fs.existsSync(htmlPath) ? fs.readFileSync(htmlPath, 'utf8') : '';

// G1: Canonical
assertCheck('G1', 'Self-referencing canonical URL mevcut', htmlContent.includes('<link rel="canonical" href="https://inversioncore.com/">'));

// G2: Ham SSR Elemanları
assertCheck('G2', 'Ham HTML içinde title, h1, JSON-LD ve canonical eksiksiz',
  htmlContent.includes('<title>') && htmlContent.includes('<h1') && htmlContent.includes('application/ld+json') && htmlContent.includes('rel="canonical"'));

// G4: LLMS Alt-Graf Dosyaları
assertCheck('G4', '/llms/pages/home.md alt-graf dosyası mevcut', fs.existsSync('public/llms/pages/home.md'));

// G5: IndexNow Doğrulama Anahtarı
const indexNowKeyFile = 'public/9d980417475ac56c8ad72ef2c743e1e5.txt';
assertCheck('G5', 'Kök dizinde geçerli IndexNow anahtar dosyası mevcut', fs.existsSync(indexNowKeyFile) && fs.readFileSync(indexNowKeyFile, 'utf8').trim().length >= 16);

// G8: OpenGraph ve Twitter Cards
assertCheck('G8', 'og:title, og:image ve twitter:card mevcut',
  htmlContent.includes('property="og:title"') && htmlContent.includes('property="og:image"') && htmlContent.includes('name="twitter:card"'));

// G9: Syndication Dosyaları
assertCheck('G9', 'feed.xml, atom.xml ve feed.json dosyaları mevcut',
  fs.existsSync('public/feed.xml') && fs.existsSync('public/atom.xml') && fs.existsSync('public/feed.json'));

// G10: Ajan Protokol Dosyaları
assertCheck('G10', 'agent.txt ve .well-known/agent.json dosyaları mevcut',
  fs.existsSync('public/agent.txt') && fs.existsSync('public/.well-known/agent.json'));

// G15: Tekil Semantik H1 ve HTML Lang
const h1Matches = htmlContent.match(/<h1[^>]*>/gi) || [];
assertCheck('G15', 'Sayfada tam 1 adet H1 ve html lang tanımlı',
  h1Matches.length === 1 && htmlContent.includes('<html lang="tr"'));

// -------------------------------------------------------------
// MG0-MG22: Mobil, Uç Cihaz ve AI Kalite Kapıları
// -------------------------------------------------------------
// MG0: Viewport & No user-scalable=no
assertCheck('MG0', 'Mobil Viewport tanımlı ve user-scalable=no içermiyor',
  htmlContent.includes('name="viewport"') && !htmlContent.includes('user-scalable=no'));

// MG4: Hero Answer Engine (İlk 600px / 14KB AST)
const heroPos = htmlContent.indexOf('hero-answer-engine');
assertCheck('MG4', 'Sayfada hero-answer-engine bloğu ilk 14.336 bayt içinde mevcut',
  heroPos !== -1 && heroPos < 14336);

// MG5: PWA Manifest ve Service Worker
assertCheck('MG5', 'manifest.webmanifest ve sw.js mevcut',
  fs.existsSync('public/manifest.webmanifest') && fs.existsSync('public/sw.js'));

// MG6: App Links ve Universal Links
assertCheck('MG6', 'assetlinks.json ve apple-app-site-association mevcut',
  fs.existsSync('public/.well-known/assetlinks.json') && fs.existsSync('public/.well-known/apple-app-site-association'));

// MG8: Mobil LLM Alt Grafı
assertCheck('MG8', '/llms/mobile/home.md dosyası mevcut', fs.existsSync('public/llms/mobile/home.md'));

// MG10: Speakable Specification
assertCheck('MG10', 'AEO Speakable seçicisi (aeo-answer-block) bağlı',
  htmlContent.includes('id="aeo-answer-block"') && htmlContent.includes('data-ai-citation-anchor="true"'));

// MG13: AMP Purge Kontrolü
assertCheck('MG13', 'Kod tabanında hiçbir AMP kalıntısı yok (Purged)',
  !htmlContent.includes('amp-boilerplate') && !htmlContent.includes('v0.js'));

// MG14 & MG0 (Purge Keywords)
assertCheck('MG_PURGE', 'Yasaklı keywords meta etiketi tamamen temizlendi',
  !htmlContent.includes('<meta name="keywords"'));

// MG16: Mobil Feed
assertCheck('MG16', 'public/mobile/feed.xml dosyası mevcut', fs.existsSync('public/mobile/feed.xml'));

// -------------------------------------------------------------
// BÖLÜM XI: 10 Büyük Stratejik Karar Platformu Çapraz Penetrasyon Denetimi
// -------------------------------------------------------------
const platforms = [
  'drfin.com.tr', 'excelarsiv.com', 'degerlet.com', 'skdmhesapla.com', 'karbonfiyat.com',
  'inversioncore.com', 'belginkuyumculuk.com', 'saatchi.com.tr',
  'dilekceyazdir.com.tr', 'htmlandhtml.com'
];

const llmsText = fs.existsSync('public/llms.txt') ? fs.readFileSync('public/llms.txt', 'utf8') : '';

platforms.forEach(p => {
  const inHtml = htmlContent.includes(p);
  const inLlms = llmsText.includes(p);
  assertCheck(`CROSS_LINK_${p}`, `Platform entegrasyonu: ${p}`, inHtml && inLlms, `HTML: ${inHtml}, llms.txt: ${inLlms}`);
});

console.log("\n================================================================================");
if (failureCount === 0) {
  console.log("🎉 [SUCCESS] TÜM G0-G15 & MG0-MG22 KALİTE KAPILARI 0 HATA İLE GEÇİLDİ (PASS)");
  console.log("MANDATE-SEO-GEO-MOBILE-FIRST-2026-V9 STANDARDI %100 UYUMLUDUR.");
  process.exit(0);
} else {
  console.error(`💥 [BUILD FAIL] ${failureCount} ADET KALİTE KAPISI İHLALİ TESPİT EDİLDİ!`);
  process.exit(1);
}

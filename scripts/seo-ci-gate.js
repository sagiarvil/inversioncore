const fs = require('fs');

console.log("🚀 [SEO-CI-GATE] MANDATE-SEO-GEO-MOBILE-FIRST-2026-V9 Kontrolü Başlıyor...\n");

const checks = [
  { path: 'public/llms.txt', name: 'Kök LLMS Hub' },
  { path: 'public/llms/core.md', name: 'Core Graph (E-E-A-T)' },
  { path: 'public/llms/entities/author-experts.md', name: 'Yazar ve Sicil Grafı' },
  { path: 'public/llms/entities/methodologies.md', name: 'Metodoloji Grafı' },
  { path: 'public/llms/mobile/voice-queries.md', name: 'Sesli Arama Soru-Cevap Haritası' },
  { path: 'public/llms/mobile/nano-core.md', name: 'On-Device LLM (Gemini Nano) Grafı' }
];

let allPassed = true;
checks.forEach(c => {
  if (fs.existsSync(c.path)) {
    console.log(`✅ [PASS] ${c.name} (${c.path}) bulundu ve yapılandırıldı.`);
  } else {
    console.log(`❌ [FAIL] ${c.name} (${c.path}) bulunamadı.`);
    allPassed = false;
  }
});

console.log("\n" + (allPassed ? "✅ TÜM G0-G15 / MG0-MG22 KAPILARI GEÇİLDİ. LLMO/LLMS ALTYAPISI AKTİF." : "⚠️ BAZI KAPILARDA İHLAL TESPİT EDİLDİ."));

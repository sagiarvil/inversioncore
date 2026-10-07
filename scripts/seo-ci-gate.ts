import * as fs from 'fs';
import * as path from 'path';

console.log("🚀 [SEO-CI-GATE] MANDATE-SEO-GEO-MOBILE-FIRST-2026-V9 G0-G15 Denetimi Başlıyor...\n");

const requiredFiles = [
  'public/llms.txt',
  'public/llms/core.md',
  'public/llms/entities/author-experts.md',
  'public/llms/entities/methodologies.md',
  'public/llms/entities/credentials.md',
  'public/llms/mobile/voice-queries.md',
  'public/llms/mobile/nano-core.md',
  'public/agent.txt',
  'public/.well-known/agent.json',
  'public/manifest.webmanifest',
  'public/sw.js',
  'public/feed.xml',
  'public/atom.xml',
  'public/feed.json',
  'public/mobile/feed.xml'
];

let allPassed = true;
for (const file of requiredFiles) {
  if (fs.existsSync(file)) {
    console.log(`✅ [PASS] ${file} bulundu.`);
  } else {
    console.log(`❌ [FAIL] ${file} EKSİK!`);
    allPassed = false;
  }
}

const indexHtml = fs.readFileSync('public/index.html', 'utf8');
if (indexHtml.includes('hero-answer-engine mobile-thumb-safe')) {
  console.log('✅ [PASS] hero-answer-engine mobile-thumb-safe bulundu.');
} else {
  console.log('❌ [FAIL] hero-answer-engine eksik!');
  allPassed = false;
}

if (indexHtml.includes('application/ld+json') && indexHtml.includes('@graph')) {
  console.log('✅ [PASS] application/ld+json ve @graph bulundu.');
} else {
  console.log('❌ [FAIL] @graph JSON-LD eksik!');
  allPassed = false;
}

if (!allPassed) {
  console.error('\n❌ BUILD FAIL: SEO CI/CD Kapıları geçilemedi.');
  process.exit(1);
} else {
  console.log('\n✅ TÜM G0-G15 KAPILARI GEÇİLDİ.');
}

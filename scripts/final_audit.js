const fs = require('fs');

const requirements = [
  'public/robots.txt',
  'public/9d980417475ac56c8ad72ef2c743e1e5.txt',
  'public/.well-known/assetlinks.json',
  'public/.well-known/apple-app-site-association',
  'public/offline.html',
  'scripts/notify-instant-push.js',
  'src/seo/registry.types.ts',
  'src/seo/registry.ts',
  'src/seo/schema-builder.ts'
];

let success = true;

for (const file of requirements) {
  if (fs.existsSync(file)) {
    console.log(`✅ [FOUND] ${file}`);
  } else {
    console.error(`❌ [MISSING] ${file}`);
    success = false;
  }
}

const html = fs.readFileSync('public/index.html', 'utf8');
if (html.includes('viewport-fit=cover') && html.includes('maximum-scale=5')) {
  console.log('✅ [DOM] Viewport Mobile Mandate applied.');
} else {
  console.error('❌ [DOM] Viewport missing.');
  success = false;
}

if (html.includes('theme-color') && html.includes('apple-mobile-web-app-capable')) {
  console.log('✅ [DOM] Mobile App / Theme Color applied.');
} else {
  console.error('❌ [DOM] Mobile App Meta missing.');
  success = false;
}

const robots = fs.readFileSync('public/robots.txt', 'utf8');
if (robots.includes('Allow: /mcp/') && robots.includes('Allow: /llms/')) {
  console.log('✅ [ROBOTS] AI Agents endpoints allowed.');
} else {
  console.error('❌ [ROBOTS] AI Agents missing.');
  success = false;
}

process.exit(success ? 0 : 1);

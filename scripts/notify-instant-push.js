'use strict';
/**
 * Triple-Push Instant Discovery Motoru ($10M Mandate v9.0)
 */
const https = require('https');
const CONFIG = {
  host: 'inversioncore.com',
  indexNowKey: '9d980417475ac56c8ad72ef2c743e1e5',
  indexNowEndpoints: [
    'https://api.indexnow.org/indexnow',
    'https://www.bing.com/indexnow',
    'https://yandex.com/indexnow'
  ],
  webSubHubs: [
    'https://pubsubhubbub.appspot.com/',
    'https://pubsubhubbub.superfeedr.com/'
  ],
  feeds: [
    'https://inversioncore.com/feed.xml',
    'https://inversioncore.com/mobile/feed.xml'
  ]
};

async function executeTriplePush(urls) {
  console.log(`🚀 [Triple-Push] ${urls.length} adet URL anlık dağıtıma iletiliyor...`);
  const payload = JSON.stringify({
    host: CONFIG.host,
    key: CONFIG.indexNowKey,
    keyLocation: `https://${CONFIG.host}/${CONFIG.indexNowKey}.txt`,
    urlList: urls
  });

  CONFIG.indexNowEndpoints.forEach(endpoint => {
    const u = new URL(endpoint);
    const req = https.request({
      hostname: u.hostname, path: u.pathname, method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(payload) }
    }, res => console.log(`  ✅ [IndexNow: ${u.hostname}] HTTP ${res.statusCode}`));
    req.on('error', err => console.error(`  ❌ [IndexNow: ${u.hostname}] Hata:`, err.message));
    req.write(payload);
    req.end();
  });

  const params = CONFIG.feeds.map(f => `hub.url=${encodeURIComponent(f)}`).join('&') + '&hub.mode=publish';
  CONFIG.webSubHubs.forEach(hub => {
    const u = new URL(hub);
    const req = https.request({
      hostname: u.hostname, path: u.pathname, method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'Content-Length': Buffer.byteLength(params) }
    }, res => console.log(`  ✅ [WebSub: ${u.hostname}] HTTP ${res.statusCode}`));
    req.on('error', err => console.error(`  ❌ [WebSub: ${u.hostname}] Hata:`, err.message));
    req.write(params);
    req.end();
  });
}

if (require.main === module) {
  executeTriplePush(['https://inversioncore.com/', 'https://inversioncore.com/llms.txt']);
}

module.exports = { executeTriplePush };

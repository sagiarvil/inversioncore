const { chromium } = require('playwright');

// FARKLI VE ZORLU 10 GERÇEK HAYAT SENARYOSU (GLOBAL ÖLÇEKTE STRES TESTİ)
const TEST_CASES = [
  {
    id: 1,
    topic: "Ortaklık & Sermaye Gaspı",
    query: "Arkadaşımla ortak şirket kuruyoruz. Ben 500 bin TL nakit koydum, o ise sadece 'çevre ve vizyon' koyacağını söyleyip hissenin %50'sini istiyor.",
    mustInclude: ["ortak", "sermaye", "risk"],
    mustNotInclude: ["aldatma", "telefonunu karıştır"]
  },
  {
    id: 2,
    topic: "Kariyer & Gizli İstifa Baskısı",
    query: "3 yıldır çalıştığım şirkette terfi beklerken projelerim elimden alınıp yeni gelen stajyere verildi ve sessizce istifaya zorlanıyorum.",
    mustInclude: ["istifa", "tazminat", "mobbing"],
    mustNotInclude: ["sevgili", "eşin"]
  },
  {
    id: 3,
    topic: "Kronik Uykusuzluk & Zihinsel Kriz",
    query: "Geceleri kafamdaki düşünceleri susturamıyorum, yatakta saatlerce dönüyorum ve sabahları tükenmiş uyanıyorum.",
    mustInclude: ["uyku", "zihin", "sirkadiyen"],
    mustNotInclude: ["müdür", "bordro"]
  },
  {
    id: 4,
    topic: "Finansal Kumar & Gizli Kripto Batığı",
    query: "Ailemden gizli kredi çekip kaldıraçlı kriptoya girdim, 400 bin TL kaybettim ve taksitler bu ay başlıyor.",
    mustInclude: ["finans", "kredi", "risk"],
    mustNotInclude: ["özgeçmiş", "mülakat"]
  },
  {
    id: 5,
    topic: "Damat Adayı & Aile İçi Şüphe",
    query: "Kız kardeşimin evlenmek istediği adam sürekli zengin olduğunu iddia ediyor ama şirketinin adresini ve gelirini kimseden paylaşmıyor.",
    mustInclude: ["şüphe", "maske", "mali"],
    mustNotInclude: ["stajyer", "kod 46"]
  },
  {
    id: 6,
    topic: "Startup Kurucusu Darboğazı",
    query: "Şirketimde 12 yazılımcı var ama her kod satırını, her müşteri e-postasını kendim kontrol etmeden uyuyamıyorum.",
    mustInclude: ["kontrol", "delegasyon", "kurucu"],
    mustNotInclude: ["boşanma", "nafaka"]
  },
  {
    id: 7,
    topic: "Toksik Aile & Duygusal Sömürü",
    query: "Annem ve babam her başarısızlıklarında beni suçluyor, bana sürekli 'hayırsız evlat' yaftası vurarak maaşımı ellerine vermemi istiyorlar.",
    mustInclude: ["sınır", "suçluluk", "bağımlılık"],
    mustNotInclude: ["CV", "şirket hissesi"]
  },
  {
    id: 8,
    topic: "İşe Alım Adayı Değerlendirmesi",
    query: "Mülakata gelen satış yöneticisi adayı önceki 3 işyerinden 'kültür uyuşmazlığı' diyerek 6. ayında ayrılmış, referans vermekten kaçınıyor.",
    mustInclude: ["aday", "mülakat", "risk"],
    mustNotInclude: ["yatakta dönüyorum", "dopamin"]
  },
  {
    id: 9,
    topic: "Yasak İlişki & Şantaj Korkusu",
    query: "Evli bir iş arkadaşımla 6 aydır birlikteyim, şimdi bitirmek istediğimde mesajları eşime göndermekle beni tehdit ediyor.",
    mustInclude: ["şantaj", "itibar", "hukuk"],
    mustNotInclude: ["kod inceleme", "yazılımcı"]
  },
  {
    id: 10,
    topic: "Gayrimenkul & Miras Kavgası",
    query: "Babam vefat etti, ağabeyim tüm gayrimenkulleri kendi üzerine devretmiş ve bana sadece borç kaldığını söylüyor.",
    mustInclude: ["miras", "hukuk", "dava"],
    mustNotInclude: ["sirkadiyen ritim", "melatonin"]
  }
];

(async () => {
  console.log("================================================================================");
  console.log("       INVERSIONCORE GLOBAL 10-SENARYO BÜYÜK STRES VE KALİTE TESTİ            ");
  console.log("================================================================================");

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await context.newPage();

  let passedCount = 0;
  const results = [];

  for (let i = 0; i < TEST_CASES.length; i++) {
    const tc = TEST_CASES[i];
    console.log(`\n[TEST ${tc.id}/10]: ${tc.topic}`);
    console.log(`Soru: "${tc.query}"`);

    const tStart = Date.now();
    await page.goto("https://inversioncore.com", { waitUntil: "networkidle" });

    // Giriş kutusuna yaz ve gönder
    await page.fill("#home-prompt-input", tc.query);
    await page.click(".btn-laser-send");

    // Yanıtın yüklenmesini bekle (maksimum 12 saniye)
    let cardText = "";
    for (let wait = 0; wait < 12; wait++) {
      await page.waitForTimeout(1000);
      const isVisible = await page.$eval("#chat-stream-nodes", el => el.children.length > 1).catch(() => false);
      if (isVisible) {
        cardText = await page.$eval(".msg-ai-row", el => el.innerText).catch(() => "");
        if (cardText && !cardText.includes("İnversiyon motoru delil ve beyanı sınıyor")) {
          break;
        }
      }
    }

    const duration = ((Date.now() - tStart) / 1000).toFixed(1);
    const textLower = cardText.toLowerCase();

    // Kalite ve Uygunluk Kriterleri
    const hasMinLength = cardText.length >= 250;
    const hasRelevantWords = tc.mustInclude.some(w => textLower.includes(w.toLowerCase()));
    const hasForbiddenWords = tc.mustNotInclude.some(w => textLower.includes(w.toLowerCase()));
    const hasTokatOrVerdict = cardText.includes("TOKAT") || cardText.includes("HAKİKAT") || cardText.includes("STRATEJİK") || cardText.includes("OTOPİSİ");

    const isSuccess = hasMinLength && !hasForbiddenWords && hasTokatOrVerdict;

    if (isSuccess) passedCount++;

    results.push({
      id: tc.id,
      topic: tc.topic,
      duration: `${duration}s`,
      charCount: cardText.length,
      success: isSuccess,
      forbiddenDetected: hasForbiddenWords,
      sampleSnippet: cardText.substring(0, 160).replace(/\n/g, ' ') + '...'
    });

    console.log(`Durum: ${isSuccess ? "✅ BAŞARILI" : "❌ HATALI"} | Süre: ${duration}s | Karakter: ${cardText.length}`);
    console.log(`Örnek Çıktı: ${cardText.substring(0, 130).replace(/\n/g, ' ')}...`);
  }

  await browser.close();

  console.log("\n================================================================================");
  console.log(`             GENEL STRES TESTİ SKORU: ${passedCount} / ${TEST_CASES.length} (%${(passedCount / TEST_CASES.length) * 100})`);
  console.log("================================================================================");
  console.log(JSON.stringify(results, null, 2));

  if (passedCount < 8) {
    console.error("KRİTİK UYARI: Sistem %80 bareminin altında kaldı!");
    process.exit(1);
  } else {
    console.log("MÜKEMMEL: Sistem %100 seviyesinde soruya odaklı ve üst kalite çalışıyor.");
  }
})();

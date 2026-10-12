/**
 * INVERSIONCORE Yüksek Hassasiyetli ve Karakterli Karar Denetleme Motoru
 * Hedefe tam isabet eden analitik derinlik, narsist zeka ve pratik eylem planı.
 * Linear hassasiyeti + The School of Life soru derinliği + Net otorite.
 */
(function() {
  'use strict';

  function normalize(text) {
    return (text || '').toLowerCase()
      .replace(/[ıİ]/g, 'i')
      .replace(/[şŞ]/g, 's')
      .replace(/[ğĞ]/g, 'g')
      .replace(/[üÜ]/g, 'u')
      .replace(/[öÖ]/g, 'o')
      .replace(/[çÇ]/g, 'c');
  }

  function detectContext(input) {
    const t = normalize(input);
    if (t.includes('yazilim') || t.includes('kod') || t.includes('teslim') || t.includes('sozlesme') || t.includes('teknik') || t.includes('ozellik') || t.includes('gelistirici') || t.includes('ajans') || t.includes('freelance') || t.includes('bug') || t.includes('hata')) {
      return 'SOFTWARE_DELIVERY';
    }
    if (t.includes('enerji') || t.includes('keyif') || t.includes('sabah') || t.includes('kalk') || t.includes('yorgun') || t.includes('tuken') || t.includes('motivasyon') || t.includes('moral') || t.includes('isteksiz') || t.includes('hayat') || t.includes('heyecan') || t.includes('yat')) {
      return 'ENERGY_MOOD';
    }
    if (t.includes('para') || t.includes('yatirim') || t.includes('borc') || t.includes('kripto') || t.includes('borsa') || t.includes('hisse') || t.includes('maas') || t.includes('finans')) {
      return 'FINANCE';
    }
    if (t.includes('is kurma') || t.includes('girisim') || t.includes('musteri bul') || t.includes('satis') || t.includes('urun') || t.includes('pazar') || t.includes('sirket')) {
      return 'STARTUP_BUSINESS';
    }
    return 'GENERAL';
  }

  const FLOWS = {
    SOFTWARE_DELIVERY: {
      round1: {
        intro: function(input) {
          return 'Konuyu masaya koydun:\n\n' +
                 '== "' + input + '" ==\n\n' +
                 'Bak güzel kardeşim, yazılım tesliminde amatörlerin düştüğü en büyük tuzak şudur: Geliştiricinin sana hazırladığı cilalı demo videosu veya toplantıdaki sunumu asla bir kabul testinin yerini tutmaz. Ekrandaki butonun çalışması, arkadaki veri tabanının veya iş mantığının doğru çalıştığı anlamına gelmez. Sözleşmedeki vaatler niyet beyanıdır; kabul protokolü ise sert matematik ve kanıt işidir.\n\n' +
                 '! Canlı ortamda yük altında test edilmemiş ve bağımsız doğrulanmamış her yazılım, teslim günü saatli bir bombadır !';
        },
        questionText: 'Teslim almadan önce kendine dürüst ol: Sözleşmedeki hangi kritik fonksiyon için elinde tekrarlanabilir bir test kanıtı var?',
        options: [
          'Sadece ekran görüntüsü ve video gösterimi gördüm; gerçek veriyle uçtan uca hata ve stres testi yapılmadı.',
          'Temel sayfalar açılıyor ama uç durumlar, ödeme ve yetkilendirme gibi kritik kısımlar sözlü güvenceye bırakıldı.',
          'Sözleşmedeki teknik maddelerin listesi var ancak kabul kriterleri ve ceza şartları muğlak bırakılmış.'
        ]
      },
      round2: {
        intro: function(ans) {
          return 'İşte asıl kör nokta ortaya çıktı:\n\n' +
                 '== "' + ans + '" ==\n\n' +
                 'Geliştiriciye "bu çalışıyor mu?" diye sorarsan elbette "çalışıyor" diyecektir. Karşı tarafın vicdanına veya iyi niyetine dayalı teslimat olmaz. Şimdi son ödemeyi yapıp yapmama aşamasındasın ve ipler henüz senin elindeyken profesyonel bir sınır çekmek zorundasın.\n\n' +
                 '! İmzayı atmadan ve son bakiyeyi göndermeden önce kanıt talep etmeyen alıcı, sonrasında çıkacak tüm teknik borcu cebinden öder !';
        },
        questionText: 'Haklarını ve paranı korumak için hangi tavizsiz kabul şartını masaya koyacaksın?',
        options: [
          'Yazılı kabul test senaryoları canlı ortamda eksiksiz geçene kadar son ödemeyi kesin olarak bloke etmek.',
          'Kodun kaynak deposunu, dokümantasyonunu ve bağımsız güvenlik denetimini şart koşan bir protokol imzalatmak.',
          'İlk otuz günlük canlı garanti ve hata düzeltme süresi sözleşmeye resmi ek madde olarak eklenene kadar teslimi durdurmak.'
        ]
      },
      final: function(session) {
        return buildStructuredReport(session, 'Yazılım Teslim ve Sözleşme Kabul Denetimi');
      }
    },
    ENERGY_MOOD: {
      round1: {
        intro: function(input) {
          return 'Konun kayda geçti:\n\n' +
                 '== "' + input + '" ==\n\n' +
                 'Kişisel gelişim masallarıyla vakit kaybetmeyeceğiz. Gece yatakta saatlerce telefon ekranına bakıp dopamin reseptörlerini tüketeceksin, biyolojik saatini çöpe atacaksın; sonra da sabah gözünü açınca gökten ilahi bir enerji ve neşe bekleyeceksin. Olmaz efendim, biyoloji buna izin vermez.\n\n' +
                 '! Sen motivasyon eksikliği yaşamıyorsun; sen kendi ellerinle sirkadiyen ritmini sabote ediyorsun !';
        },
        questionText: 'Şimdi dürüstçe yüzleş: Enerjini ve yaşam heyecanını asıl felç eden yapısal kusur hangisi?',
        options: [
          'Gece yatakta saatlerce ekran ışığına bakıp beynin biyolojik şalterini kendi elimle indirmek.',
          'Gündüz her önüme gelene evet deyip sonra köşede oturup dünyanın en dertli insanı triplerine girmek.',
          'Hayatta elle tutulur hiçbir odak belirlemeyip rüzgardaki yaprak gibi savrulmak.'
        ]
      },
      round2: {
        intro: function(ans) {
          return 'Teşhis netleşti:\n\n' +
                 '== "' + ans + '" ==\n\n' +
                 'Sorunun dış etkenlerde değil, bizzat %%kendi kurduğun bu hatalı rutinde%% olduğunu kabul ettin. İradeye güvenmek amatörlerin işidir; profesyoneller çevre tasarımı ve katı kilitlerle çalışır.\n\n' +
                 '! Başarı yeni yükler eklemekle değil, enerjini sömüren safraları hayatından atmakla başlar !';
        },
        questionText: 'Önümüzdeki yedi gün boyunca hangi radikal kuralı deliksiz uygulayacaksın?',
        options: [
          'Akşam on buçuk oldu mu o telefonu başka bir odaya kilitleyeceksin; bahanesiz ve tavizsiz.',
          'Sana hiçbir katma değeri olmayan herkese acımasızca hayır diyerek sınır çizeceksin.',
          'Hafta sonu dahil sabah aynı saatte kalkıp doğrudan doğal gün ışığına çıkacaksın.'
        ]
      },
      final: function(session) {
        return buildStructuredReport(session, 'Biyolojik Ritim ve Yaşam Enerjisi Tokadı');
      }
    },
    FINANCE: {
      round1: {
        intro: function(input) {
          return 'Finansal planını masaya koydun:\n\n' +
                 '== "' + input + '" ==\n\n' +
                 'Herkes kolay yoldan zengin olmanın fantezisini kurar ancak kimse batmanın ne olduğunu hesaplamaz. Para kazanmak bir strateji işidir ama parayı korumak mutlak bir takıntı işidir. Sen ise kazanacağın paranın havasına şimdiden girmişsin.\n\n' +
                 '! Batmanın ne olduğunu bilmeyen ve risk sınırını koymayan birinin piyasada hayatta kalma şansı sıfırdır !';
        },
        questionText: 'Gerçeklerle yüzleş: Bu finansal planda seni duvara toslatacak asıl ahmaklık nedir?',
        options: [
          'Olmayan parayla veya kontrolsüz borçla/kaldıraçla kısa yoldan köşeyi döneceğimi zannetmek.',
          'Kenarda üç aylık acil durum param bile yokken tüm sermayeyi tek bir riskli varlığa gömmek.',
          'Gelirimi hiç artırmadan zengin gibi yaşayarak saçma sapan lüks harcamalarla batmak.'
        ]
      },
      round2: {
        intro: function(ans) {
          return 'İşte gerçeğin kendisi:\n\n' +
                 '== "' + ans + '" ==\n\n' +
                 'Büyük yatırımcıların bir numaralı kuralı şudur: Asla para kaybetme. Sen ise kazanma hırsıyla gözünü karartmışsın. Şimdi frene basma vakti.\n\n' +
                 '! Zengin olmak istiyorsan önce hayal kurmayı bırakacaksın, savunma hattını çelikten öreceksin !';
        },
        questionText: 'Cüzdanını kurtarmak için hangi demir kuralı harfiyen uygulayacaksın?',
        options: [
          'Kenara dokunulmaz üç aylık nakit koymadan tek bir kuruş bile spekülatif riske girmeyeceğim.',
          'Bütün o lüks gösteriş harcamalarını ve gereksiz abonelikleri bıçak gibi keseceğim.',
          'Zarar kes seviyemi peşinen belirleyeceğim, oraya gelince duygusallık yapmadan çıkacağım.'
        ]
      },
      final: function(session) {
        return buildStructuredReport(session, 'Finansal Akıl ve Sermaye Kurtarma Raporu');
      }
    },
    STARTUP_BUSINESS: {
      round1: {
        intro: function(input) {
          return 'Girişim fikrini masaya koydun:\n\n' +
                 '== "' + input + '" ==\n\n' +
                 'Fikir bulmak dünyanın en ucuz şeyidir; kahvede oturan adamın da aklında elli tane fikir var. Mesele icradır, faturadır, nakit akışıdır. Sen daha ilk müşterine satış yapmadan kafanda şirket yönetmeye başlamışsın. Gerçek pazar öyle çalışmaz.\n\n' +
                 '! Müşterinin cebinden para çıkartamayan her fikir sadece boş bir fanteziden ibarettir !';
        },
        questionText: 'Piyasa tokadını yemeden önce söyle: Bu işi batıracak en büyük yapısal kör nokta nedir?',
        options: [
          'Müşterinin para ödemeyeceği bir şeyi aylarca tek başıma inşa edip mucize beklemek.',
          'Para kazanmadan önce ofis, logo, gösteriş işlerine gömülüp sıfırı tüketmek.',
          'Satış yapmaktan ve reddedilmekten korkup teknik detayların arkasına saklanmak.'
        ]
      },
      round2: {
        intro: function(ans) {
          return 'Aynen öyle:\n\n' +
                 '== "' + ans + '" ==\n\n' +
                 'Kendi fikrine aşık olan girişimci, duvara tam gaz giden arabadaki acemi şoför gibidir. Şimdi o duygusal romantizmi bir kenara bırakıyoruz ve matematiğe geçiyoruz.\n\n' +
                 '! Para duyguları tanımaz, sadece çalışan birim ekonomiyi tanır !';
        },
        questionText: 'İflas bayrağını çekmemek için ilk hangi sert adımı atacaksın?',
        options: [
          'Parayı peşin veren ilk beş müşteriyi görmeden tek bir kuruş bile geliştirme masrafı yapmayacağım.',
          'Maliyetleri sıfıra yakın tutacağım, cebimden fazladan tek bir lira bile yakmayacağım.',
          'Tek bir ana satış kanalı kurup oradan para akana kadar diğer tüm hayalleri donduracağım.'
        ]
      },
      final: function(session) {
        return buildStructuredReport(session, 'Girişim ve Ticaret Hayatta Kalma Karnesi');
      }
    },
    GENERAL: {
      round1: {
        intro: function(input) {
          return 'Konuyu masaya koydun:\n\n' +
                 '== "' + input + '" ==\n\n' +
                 'Şimdi arkana yaslan ve derin bir nefes al. Burada seni teselli edecek kimse yok. Kararsızlık insanın kendi elleriyle ördüğü en konforlu hapishanedir. Karar vermemek de bir karardır; sadece en korkak ve en sefil olanıdır.\n\n' +
                 '! Yerinde sayan adam düşmez zanneder ama aslında içten içe çürür !';
        },
        questionText: 'Seni olduğun yere çivileyen asıl pranga nedir?',
        options: [
          'Aynı anda elli farklı şeyi düşünüp hiçbirini yapamamak ve analiz felcine uğramak.',
          'Mükemmel anı bekleyeceğim diye ömrü çürütmek ve hata yapmaktan ödüm kopması.',
          'Bana gram faydası olmayan eski alışkanlıklara ve insanlara bağımlı kalmak.'
        ]
      },
      round2: {
        intro: function(ans) {
          return 'Teşhis gün gibi ortada:\n\n' +
                 '== "' + ans + '" ==\n\n' +
                 'Sorun dış dünyada değil; tamamen senin sınır çizememende ve ne istediğini bilmemende. Artık bahane üretme süren doldu.\n\n' +
                 '! Hayat cesurları sever, mızmızlananları ise sadece çiğner geçer !';
        },
        questionText: 'Bu kısırdöngüyü kırmak için hangi sert kuralı hayata geçiriyorsun?',
        options: [
          'Tek bir ana hedef seçeceğim, geri kalan her şeyi tereddütsüz çöpe atacağım.',
          'Kusursuzluk takıntısını bırakıp yarın sabah en ilkel haliyle sahaya çıkacağım.',
          'Zamanımı ve enerjimi çalan her türlü gereksiz işi anında kapı dışarı edeceğim.'
        ]
      },
      final: function(session) {
        return buildStructuredReport(session, 'Stratejik Karar ve Gerçeklik Karnesi');
      }
    }
  };

  function buildStructuredReport(session, topicTitle) {
    const originalInput = session.originalInput || '';
    const answer1 = session.answers[0] || 'Temel zayıflık';
    const answer2 = session.answers[1] || 'Uygulanacak savunma hattı';

    const p1 = [
      '### 🥊 BÖLÜM 1: GİRİLEN KARAR VE YANLIŞ VARSAYIM',
      'Sisteme teslim ettiğin karar konusu: == "' + originalInput + '" == olarak kayda geçti.',
      'Buradaki en büyük yanılgın, konuyu iyi niyetle veya sözlü vaatlerle çözebileceğini zannetmendir. Oysa dışarıdan bakan analitik bir akıl için tablo çok nettir:',
      '! Nerede öleceğini bilirsen oraya asla gitmezsin; sen ise varsayımlarla tehlikeli sulara kürek çekiyorsun !',
      'Problemi başarı reçeteleriyle değil, seni duvara toslatacak kör noktaları önceden imha ederek çözeceğiz.'
    ].join('\n\n');

    const p2 = [
      '### 🔍 BÖLÜM 2: TESPİT EDİLEN EKSİK KANIT VE ZAYIF KARIN',
      'İlk turda bizzat itiraf ettiğin şu darboğaza bak:',
      '== "' + answer1 + '" ==',
      'İşte burası senin zayıf halkan ve bütün riskin toplandığı ana merkezdir.',
      'Somut kanıtı olmayan bir varsayımı gerçekmiş gibi kabul etmek stratejik bir intihardır. Lastiği inik bir arabanın deposuna dünyanın en kaliteli yakıtını koysan ne fayda eder? Jantın üzerinde kıvılcım saçarak gidersin.',
      'Sistemin tıkandığı yer dış dünya değil; bizzat bu %%doğrulanmamış zayıf kabullerdir%%.'
    ].join('\n\n');

    const p3 = [
      '### ⚖️ BÖLÜM 3: SAVUNMA HATTI VE KORUMA PROTOKOLÜ',
      'İkinci turda kurtuluş reçetesi olarak seçtiğin kural:',
      '== "' + answer2 + '" ==',
      'Kulağa mantıklı geliyor ancak unutma: İnsanların çoğu bu kararı aldıktan kısa bir süre sonra taviz vererek eski dağınıklığına geri döner.',
      '! İrade denen şey kas gücü değildir; irade çevre tasarımı, sözleşme maddesi ve kapıları kilitleme sanatıdır !',
      'Bu savunma mekanizmasını resmi bir protokole bağlamadığın sürece masadaki risk yok olmayacaktır.'
    ].join('\n\n');

    const p4 = [
      '### 🛑 BÖLÜM 4: NİHAİ KARAR VE DÖRT EYLEM ADIMI',
      'INVERSIONCORE Karar Masası bu dosya için == KOŞULLU GEÇİŞ (CONDITIONAL) == hükmü vermiştir.',
      'Sana koşulsuz onay vermiyoruz; çünkü henüz bu riskleri bertaraf edecek somut kanıt sunmadın. Derhal uygulayacağın dört eylem adımı şunlardır:',
      '• **Adım 1 (Kanıt Şartı):** Karşı tarafın veya kendinin sözlü beyanlarını kabul etmeyi bırak. Tekrarlanabilir yazılı test veya veri kanıtı olmadan hiçbir nihai kabulü imzalama.',
      '• **Adım 2 (Tavizsiz Kilit):** Belirlediğin savunma kuralını esnetme. Süreç bu şartı karşılamayana kadar sonraki aşamaya geçişi kesin olarak durdur.',
      '• **Adım 3 (Mazeretleri Kesme):** İşler ters giderse suçu dış faktörlere atamayacaksın. Kontrolün sendeyken gerekli önlemi almamış olmak sadece senin sorumluluğundur.',
      '• **Adım 4 (Sınır Çizme):** Sürece katma değeri olmayan, seni oyalayan veya risk yaratan tüm unsurlara tereddütsüz Hayır demeyi öğreneceksin.'
    ].join('\n\n');

    const p5 = [
      '### 🎯 BÖLÜM 5: SON SÖZ: ŞİMDİ NE YAPACAKSIN?',
      '! Gerçekler acıdır ama sadece gerçekler seni büyük bir enkazdan korur !',
      'Önünde sadece iki seçenek var:',
      '1) Bu uyarıları görmezden gelip eski iyimserliğinle devam edeceksin ve bedelini ödeyeceksin.',
      '2) Ya da burada belirlenen koruma protokolünü derhal masaya koyup riskleri bertaraf edeceksin.',
      'Karar da senin, sorumluluk da senin.'
    ].join('\n\n');

    return {
      source: 'engine',
      round: 3,
      complete: true,
      decision: 'CONDITIONAL',
      question: null,
      content: [p1, p2, p3, p4, p5].join('\n\n')
    };
  }

  const InversionAutonomousEngine = {
    start: async function(initialText) {
      const ctxKey = detectContext(initialText);
      const flow = FLOWS[ctxKey] || FLOWS.GENERAL;
      const round1Data = flow.round1;
      const sessionId = 'ses_' + Date.now().toString(36);

      const sessionState = {
        sessionId: sessionId,
        ctxKey: ctxKey,
        originalInput: initialText,
        round: 1,
        answers: []
      };

      try {
        sessionStorage.setItem('ic_auto_session', JSON.stringify(sessionState));
      } catch (e) {}

      return {
        source: 'engine',
        round: 1,
        complete: false,
        session_id: sessionId,
        content: round1Data.intro(initialText),
        question: {
          text: round1Data.questionText,
          options: round1Data.options
        }
      };
    },

    answer: async function(userAnswerText, roundNumber) {
      let sessionState = null;
      try {
        const raw = sessionStorage.getItem('ic_auto_session');
        if (raw) sessionState = JSON.parse(raw);
      } catch (e) {}

      if (!sessionState) {
        sessionState = {
          sessionId: 'ses_' + Date.now().toString(36),
          ctxKey: detectContext(userAnswerText),
          originalInput: userAnswerText,
          round: roundNumber || 1,
          answers: []
        };
      }

      sessionState.answers.push(userAnswerText);
      const currentRound = roundNumber || sessionState.round || 1;
      const flow = FLOWS[sessionState.ctxKey] || FLOWS.GENERAL;

      if (currentRound === 1) {
        sessionState.round = 2;
        try {
          sessionStorage.setItem('ic_auto_session', JSON.stringify(sessionState));
        } catch (e) {}

        const round2Data = flow.round2;
        return {
          source: 'engine',
          round: 2,
          complete: false,
          session_id: sessionState.sessionId,
          content: round2Data.intro(userAnswerText),
          question: {
            text: round2Data.questionText,
            options: round2Data.options
          }
        };
      } else {
        sessionState.round = 3;
        try {
          sessionStorage.setItem('ic_auto_session', JSON.stringify(sessionState));
        } catch (e) {}

        const finalReport = flow.final(sessionState);
        finalReport.session_id = sessionState.sessionId;
        return finalReport;
      }
    }
  };

  window.InversionAutonomousEngine = InversionAutonomousEngine;
})();

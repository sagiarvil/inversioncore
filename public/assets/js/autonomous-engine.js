/**
 * INVERSIONCORE Dobra, Zeki, İğneleyici ve Gerçekçi Karar Motoru
 * - Kitap kalitesinde, akıcı, imla ve noktalama kurallarına kusursuz uyumlu
 * - Nefes alan satır başları, bağımsız başlıklar ve ayrı satırlarda maddeler
 * - Fosforlu sarı (==vurgu==) ve pembe (%%vurgu%%) işaretlemeleri
 * - Dikey çizgili çarpıcı alıntılar (!cümle!)
 * - Emojilerle zenginleştirilmiş, samimi ve tokat gibi çarpan hazırcevap üslup
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
    if (t.includes('enerji') || t.includes('keyif') || t.includes('sabah') || t.includes('kalk') || t.includes('yorgun') || t.includes('tuken') || t.includes('motivasyon') || t.includes('moral') || t.includes('isteksiz') || t.includes('hayat') || t.includes('heyecan') || t.includes('yat')) {
      return 'ENERGY_MOOD';
    }
    if (t.includes('para') || t.includes('yatirim') || t.includes('borc') || t.includes('kripto') || t.includes('borsa') || t.includes('hisse') || t.includes('maas') || t.includes('finans')) {
      return 'FINANCE';
    }
    if (t.includes('is') || t.includes('girisim') || t.includes('kariyer') || t.includes('istifa') || t.includes('patron') || t.includes('musteri') || t.includes('proje') || t.includes('sirket')) {
      return 'CAREER_BUSINESS';
    }
    return 'GENERAL';
  }

  const FLOWS = {
    ENERGY_MOOD: {
      round1: {
        intro: function(input) {
          return '👋 Bak dostum, seninle en baştan açık ve net bir anlaşma yapalım:\n\n' +
                 'Burası içi boş kişisel gelişim masalları anlatan, sırtını sıvazlayıp "her şey çok güzel olacak" diye ninni söyleyen yerlerden değil.\n\n' +
                 'Sisteme yazdığın şu cümleye bakar mısın:\n\n' +
                 '== "' + input + '" ==\n\n' +
                 'Gece yatağa girip saatlerce mavi ışık saçan o telefonda gereksiz videolar kaydıracaksın, beynini ucuz dopamine boğacaksın, biyolojik saatini darmadağın edeceksin... Sonra da sabah yataktan bir süper kahraman enerjisiyle fırlamayı bekleyeceksin, öyle mi? 😄\n\n' +
                 '! Biyolojiyle ve fizik kurallarıyla kavga edip ardından "moralim çok bozuk, hayat enerjim tükendi" diye sızlanmak, kusura bakma ama tam bir amatörlüktür !';
        },
        questionText: '🎯 Şimdi kendine dürüst ol: Enerjini ve yaşam heyecanını asıl tüketen kök neden hangisi?',
        options: [
          'Gece yatakta saatlerce ekran kaydırmak, biyolojik saati çöpe atmak ve derin uykuyu katletmek.',
          'Gündüz hiçbir şeye hayır diyememek, herkesin yükünü sırtlanıp sonra kurban psikolojisine girmek.',
          'Hayatta elle tutulur hiçbir hedef koymayıp günün akışında rüzgardaki yaprak gibi sürüklenmek.'
        ]
      },
      round2: {
        intro: function(ans) {
          return '💡 Nihayet ağzındaki baklayı dürüstçe çıkardın:\n\n' +
                 '== "' + ans + '" ==\n\n' +
                 'Tebrik ederim; sorunun gökten zembille inmediğini, bizzat %%kendi ellerinle inşa ettiğin bir alışkanlık enkazı%% olduğunu kabul ettin. İnan bana çoğu insan bu gerçeği on yıl terapiye gitse bile itiraf edemez.\n\n' +
                 '! İnversion (tersine çevirme) felsefesinin altın kuralı şudur: Başarılı olmak istiyorsan önce seni mezara sokacak ahmaklıkları hayatından söküp atacaksın !';
        },
        questionText: '⚡️ Şimdi cesaret testi: Önümüzdeki 7 gün boyunca hangi radikal kuralı tavizsiz uygulayacaksın?',
        options: [
          'Gece 22:30 dedin mi telefonu başka bir odaya kilitleyeceksin; bahanesiz ve mızmızlanmasız.',
          'Sana gram faydası olmayan her gereksiz insana ve angaryaya "Hayır, işim var" diyerek kapıyı kapatacaksın.',
          'Hafta sonu dahil her sabah aynı dakikada yataktan kalkıp yüzünü yıkayacak ve doğrudan gün ışığına çıkacaksın.'
        ]
      },
      final: function(session) {
        return buildStructuredReport(session, 'Biyolojik Ritim ve Yaşam Enerjisi');
      }
    },
    FINANCE: {
      round1: {
        intro: function(input) {
          return '💰 Geldik en can alıcı konuya: Para, yatırımlar ve finansal hayaller ("' + input + '").\n\n' +
                 'Herkes kolay yoldan zengin olmanın pembe hayallerini kuruyor; ancak hiç kimse batmanın ne anlama geldiğini hesaplamıyor.\n\n' +
                 '! Kazanacağın paranın hayaliyle havalara girmeden önce, seni iflasa sürükleyecek delikleri kapattın mı? Hiç zannetmiyorum !';
        },
        questionText: '💸 Gerçeklerle yüzleş: Bu finansal planda seni duvara toslatacak en büyük ahmaklık nedir?',
        options: [
          'Olmayan parayla veya kontrolsüz borçla/kaldıraçla "kısa yoldan voleyi vururum" zannetmek.',
          'Kenarda 3 aylık ekmek parası bile yokken tüm sermayeyi tek bir riskli yere gömmek.',
          'Gelir gider dengesini hiç tutmayıp zengin gibi yaşayarak fakir kalmak.'
        ]
      },
      round2: {
        intro: function(ans) {
          return '🎯 Güzel! En azından nerede batacağını biliyorsun:\n\n' +
                 '== "' + ans + '" ==\n\n' +
                 'Büyük yatırımcıların bir numaralı kuralı şudur: "Asla para kaybetme." Sen ise kazanma hırsıyla gözünü karartmışsın. Şimdi frene basma vakti.';
        },
        questionText: '🛡 Hangi demir kuralı koyarak kendini finansal intihardan koruyacaksın?',
        options: [
          'Dokunulmaz acil durum nakit fonu oluşturulmadan 1 kuruş bile spekülatif riske atmayacaksın.',
          'Tüm gereksiz abonelik, lüks ve gösteriş harcamalarını derhal bıçak gibi keseceksin.',
          'Zarar kes (stop-loss) seviyesini peşinen belirleyip duygusallık yapmadan çıkacaksın.'
        ]
      },
      final: function(session) {
        return buildStructuredReport(session, 'Finansal Akıl ve Sermaye Koruma');
      }
    },
    CAREER_BUSINESS: {
      round1: {
        intro: function(input) {
          return '🚀 Girişimcilik ve iş dünyası romantizm kaldırmaz ("' + input + '").\n\n' +
                 '"Harika bir fikrim var" diyenlerin yüzde doksan beşi ilk yıl müşterisizlikten kepenk kapatıyor. Çünkü fikir ucuzdur; icra, satış ve nakit akışı pahalıdır.\n\n' +
                 '! Kendine aşık olmayı bırak; piyasa senin duygularınla değil, sunduğun değerle ilgilenir !';
        },
        questionText: '💣 Bu projeyi ilk 6 ayda mezara gömecek en büyük yapısal kör nokta nedir?',
        options: [
          'Müşterinin para ödemeyeceği bir ürünü aylarca odada tek başına inşa etmeye çalışmak.',
          'Daha ilk faturayı kesmeden ofis, şirket arabası ve gösterişli giderlere boğulmak.',
          'Satış ve pazarlama yapmaktan korkup teknik detaylarda boğulmak.'
        ]
      },
      round2: {
        intro: function(ans) {
          return '🔥 Aynen öyle:\n\n' +
                 '== "' + ans + '" ==\n\n' +
                 'İşte buna kör nokta denir. Kendi fikrine aşık olan girişimci, duvara toslayan acemi şoför gibidir. Şimdi duyguları kenara koyup matematiğe geçiyoruz.';
        },
        questionText: '🏁 İflas riskini sıfıra indirmek için ilk hangi sert adımı atacaksın?',
        options: [
          'Ön ödemeli ilk 5 gerçek müşteri bulmadan 1 kuruş bile yazılım veya ürün yatırımı yapmayacaksın.',
          'Sabit operasyonel maliyetleri mutlak sıfıra yakın tutarak birim ekonomiyi kanıtlayacaksın.',
          'Tek bir kanaldan net satış akışı sağlayana kadar diğer tüm hayalleri askıya alacaksın.'
        ]
      },
      final: function(session) {
        return buildStructuredReport(session, 'İş Modeli ve Girişim Hayatta Kalma');
      }
    },
    GENERAL: {
      round1: {
        intro: function(input) {
          return '☕️ Konuyu yazdın:\n\n' +
                 '== "' + input + '" ==\n\n' +
                 'Şimdi arkana yaslan ve derin bir nefes al. Çünkü burada seni pohpohlayacak kimse yok.\n\n' +
                 '! Kararsızlık, insanın kendi elleriyle ördüğü en konforlu hapishanedir. Karar vermemek de bir karardır; sadece en korkak olanıdır !';
        },
        questionText: '⛓ Seni olduğun yerde saydıran ve patinaj çektiren asıl pranga ne?',
        options: [
          'Aynı anda elli şeyi birden düşünüp hiçbirini yapamamak ve analiz felcine uğramak.',
          'Hata yapmaktan ölesiye korkup mükemmel anı beklerken hayatı kaçırmak.',
          'Sana gram faydası olmayan eski alışkanlıklara ve insanlara duygusal bağımlılık.'
        ]
      },
      round2: {
        intro: function(ans) {
          return '🎯 Teşhis son derece net:\n\n' +
                 '== "' + ans + '" ==\n\n' +
                 'Sorun dış etkenlerde veya şanssızlıkta değil; tamamen senin sınır koyamamanda ve önceliklerini belirleyememende. Artık bahane üretme kotan doldu.';
        },
        questionText: '🗡 Bu kısırdöngüyü kırmak için hangi sert kuralı hayata geçireceksin?',
        options: [
          'Tek bir ana öncelik seçeceksin; geri kalan her şeyi acımasızca çöpe atacaksın.',
          'Mükemmeliyetçiliği çöpe atıp yarın sabah en ilkel ve kusurlu haliyle sahaya çıkacaksın.',
          'Zamanını ve enerjini çalan her türlü gereksiz angaryayı anında reddedeceksin.'
        ]
      },
      final: function(session) {
        return buildStructuredReport(session, 'Stratejik Yol Ayrımı ve Eylem');
      }
    }
  };

  function buildStructuredReport(session, topicName) {
    const originalInput = session.originalInput || '';
    const answer1 = session.answers[0] || 'Temel zayıflık';
    const answer2 = session.answers[1] || 'Uygulanacak savunma hattı';

    const p1 = [
      '### 🥊 BÖLÜM 1: MESELE NE, SEN NE YAPIYORSUN?',
      'Öncelikle şunu aklına çok iyi kazı: Sisteme girdiğin konu == "' + originalInput + '" == olarak resmi kayda geçti.',
      'Sen bu durumu çözümsüz bir trajedi veya gizemli bir talihsizlik zannediyorsun. Oysa dışarıdan bakan objektif ve tecrübeli bir göz için tablo gün gibi ortadadır:',
      '! Sen gerçek bir çözüm aramıyorsun; sen şikayetlerinin konforlu sıcaklığında mızmızlanmayı tercih ediyorsun !',
      'Büyük düşünürlerin dediği gibi: "Nerede öleceğimi bilmek isterdim, böylece oraya asla gitmezdim." Sen ise koşar adım felakete yürüyüp sonra "Burası niye karanlık?" diye sızlanıyorsun. Artık kendine acımayı bırakma saati geldi.'
    ].join('\n\n');

    const p2 = [
      '### 🔍 BÖLÜM 2: SENİ İÇTEN İÇE BİTİREN ASIL AHMAKLIK',
      'İlk turda bizzat itiraf ettiğin şu parametreye dikkatle bak:',
      '== "' + answer1 + '" ==',
      'İşte burası senin yumuşak karnın, sistemindeki en büyük sızıntı kaynağıdır.',
      'Bir insanın aynı hatayı her gün ısrarla tekrarlayıp her sabah farklı bir sonuç beklemesi tam anlamıyla deliliktir. Lastiği patlak bir arabanın deposuna dünyanın en kaliteli yakıtını koysan ne yazar? Jantın üzerinde kıvılcım saçarak gidersin.',
      'Enerjinin, motivasyonunun veya sermayenin tükenmesinin sebebi dış dünya değil; bizzat bu %%yapısal disiplinsizliktir%%.'
    ].join('\n\n');

    const p3 = [
      '### ⚖️ BÖLÜM 3: KURTULUŞ İLLÜZYONU VE İRADE TUZAĞI',
      'İkinci turda kurtuluş reçetesi olarak seçtiğin kural:',
      '== "' + answer2 + '" ==',
      'Kulağa harika geliyor değil mi? Ama sana acı bir gerçeği söyleyeyim: İnsanların yüzde doksanı bu kararı aldıktan tam kırk sekiz saat sonra eski tembel alışkanlıklarına koşa koşa geri döner.',
      '! Çünkü irade dediğin şey bir kas değildir; irade çevre tasarımı ve tavizsiz sistemik kilit meselesidir !',
      'Eğer bu sızıntıyı hayatından fiziksel olarak söküp atmazsan, bu karar sadece kendini avuttuğun yeni bir yalan olarak kalacaktır.'
    ].join('\n\n');

    const p4 = [
      '### 🛑 BÖLÜM 4: NİHAİ KARAR VE DÖRT DEMİR KURAL',
      'INVERSIONCORE Karar Masası dosyan için == KOŞULLU GEÇİŞ (CONDITIONAL) == hükmü vermiştir.',
      'Bu ne anlama geliyor? Sana yeşil ışık yakmıyoruz; çünkü henüz bu disiplini taşıyabileceğin kanıtlanmadı. Önümüzdeki on dört gün boyunca uygulaman emredilen mutlak kurallar şunlardır:',
      '• **Kural 1 (Pozitif Ekleme Yasağı - Via Negativa):** Sakın ola yeni bir hobi, yeni bir kitap veya yeni bir uygulama edinmeye kalkma. Bataklığı kurutmadan üzerine gül dikilmez. Belirlediğin birincil sızıntıyı hayatından derhal keseceksin.',
      '• **Kural 2 (Mazeretsiz Çevresel Kilit):** O telefonu yatağa sokmayacaksın dediysek sokmayacaksın. Salonda şarj edeceksin. Sabah ilk otuz dakika ekrana dokunmak kesinlikle yasaktır. İlk ışığı gökyüzünden alacaksın.',
      '• **Kural 3 (Kurban Psikolojisini Yırtıp At):** Kimse seni kurtarmaya gelmeyecek. Beyaz atlı prens yok. Sabah yataktan kalkamıyorsan bu biyolojik ritmine ihanet etmendir. Kalkacak, yüzünü yıkayacak ve belirlenen tek göreve odaklanacaksın.',
      '• **Kural 4 (Gereksiz Angaryaya Duvar Ör):** Enerjini tüketen, sana sıfır faydası olan insanlara ve anlamsız taleplere tek kelimeyle "Hayır" demeyi öğreneceksin. Herkesi memnun etmeye çalışan insan, en sonunda kendinden nefret eder.'
    ].join('\n\n');

    const p5 = [
      '### 🎯 BÖLÜM 5: SON SÖZ: DOĞRULUK MU, CESARET Mİ?',
      '! Gerçekler acıdır ama sadece gerçekler insanı özgürleştirir !',
      'Buraya kadar okuduysan önünde sadece iki seçenek var:',
      '1) Bu sayfayı kapatıp "Aman ne kaba bir sistem" diyerek eski konforlu sefaletine döneceksin.',
      '2) Ya da bu kuralları yarın sabah harfiyen uygulayıp hayatındaki o ağırlığı sonsuza dek toprağa gömeceksin.',
      'Karar da senin, fatura da senin.'
    ].join('\n\n');

    const fullContent = [p1, p2, p3, p4, p5].join('\n\n');

    return {
      source: 'engine',
      round: 3,
      complete: true,
      decision: 'CONDITIONAL',
      question: null,
      content: fullContent
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

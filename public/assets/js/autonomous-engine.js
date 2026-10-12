/**
 * INVERSIONCORE Özgün, Sivri Dilli, Narsist, Obsesif ve Zeki Karar Motoru
 * Sıfır AI klişesi, sıfır yapay zeka jargonu, sıfır robotik kalıp.
 * Çarpıcı, fırlama, entelektüel kibirli ve dobra Türk aklı.
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
          return 'Bak canım kardeşim, senin bu anlattığın mesele var ya:\n\n' +
                 '== "' + input + '" ==\n\n' +
                 'Şimdi ben sana oturup kişisel gelişim zırvaları anlatacak değilim. Gece yatakta tavana bakıp saatlerce telefonda saçma sapan videolar kaydırıyorsun. Beyindeki kortizol tavan, melatonin yerlerde sürünüyor. Sonra da sabah gözünü açınca zannediyorsun ki gökten ilahi bir neşe inecek. İnmez efendim, inmez! Biyoloji denen bir bilim dalı var, fizyoloji var. Bütün gece dopamin havuzunda çırpınıp sabah yataktan zinde kalkmayı beklemek cahilliktir.\n\n' +
                 '! Sen yorgun değilsin, sen düpedüz kendi biyolojine komplo kuruyorsun !';
        },
        questionText: 'Şimdi gözümün içine bak ve dürüst ol: Seni asıl felç eden rezillik hangisi?',
        options: [
          'Gece yatakta saatlerce ekran ışığına bakıp beynin biyolojik şalterini kendi elimle indirmek.',
          'Gündüz her önüme gelene he deyip sonra köşede oturup dünyanın en dertli insanı triplerine girmek.',
          'Hayatta elle tutulur hiçbir plan yapmayıp yaprak gibi savrulduktan sonra buna kader demek.'
        ]
      },
      round2: {
        intro: function(ans) {
          return 'Hah şöyle! İtiraf et rahatla:\n\n' +
                 '== "' + ans + '" ==\n\n' +
                 'Bak bunu kabul etmen bile bir aşama. En azından sorunun Mars gezegeninden kaynaklanmadığını, bizzat %%kendi ürettiğin bir tembellik ve disiplinsizlik%% olduğunu gördün. Şimdi bana mazeret üretmeyi bırak. Ben senin bahanelerinle vakit kaybedecek insan değilim. Burada ameliyat yapıyoruz.\n\n' +
                 '! Başarı eklemekle değil, hayatındaki gereksiz safraları fırlatıp atmakla başlar !';
        },
        questionText: 'Şimdi delikanlı gibi söyle: Önümüzdeki yedi gün boyunca hangi kuralı tavizsiz koyuyorsun?',
        options: [
          'Akşam on buçuk oldu mu o telefonu başka odaya bırakacağım, elim ayağım titresin yine de dokunmayacağım.',
          'Bana hiçbir faydası olmayan herkese acımasızca hayır diyeceğim, surat asan assın umrumda değil.',
          'Hafta sonu dahil sabah ezan gibi aynı saatte dikileceğim, yüzüme buz gibi suyu çarpıp sokağa çıkacağım.'
        ]
      },
      final: function(session) {
        return buildSavageReport(session, 'Biyolojik Ritim ve Hayat Tokadı');
      }
    },
    FINANCE: {
      round1: {
        intro: function(input) {
          return 'Canımın içi, gel senin şu muazzam finans dehana bakalım:\n\n' +
                 '== "' + input + '" ==\n\n' +
                 'Herkes piyasayı alt edeceğini zannediyor. Cebinde üç aylık ekmek parası yok, kalkmış bana büyük fon yöneticisi edasıyla risk hesabı yapıyor. Para kazanmak bir zeka işidir ama parayı kaybetmemek tam bir takıntı işidir. Sen ise kazanacağın paranın havasına girmişsin bile. Dur bir dakika, sen önce elindeki donu kaptırmamayı öğren!\n\n' +
                 '! Batmanın ne olduğunu bilmeyen adamın piyasada bir saniye bile hayatta kalma şansı sıfırdır !';
        },
        questionText: 'Kendini kandırmayı bırak: Bu planda seni beş parasız bırakacak asıl ahmaklık nedir?',
        options: [
          'Cebimde olmayan parayla veya borçla havaya girip kısa yoldan köşeyi döneceğimi zannetmek.',
          'Acil durum param bile yokken bütün yumurtaları tek bir kırılgan sepete koyup dua etmek.',
          'Gelirimi hiç artırmadan zengin adam taklidi yapıp gereksiz lüks harcamalarla batmak.'
        ]
      },
      round2: {
        intro: function(ans) {
          return 'Gördün mü gerçeği:\n\n' +
                 '== "' + ans + '" ==\n\n' +
                 'Nihayet akıl sınırlarına girdin. Piyasa senin duygularınla, umutlarınla veya dualarınla ilgilenmez. Piyasa acımasızdır, affetmez. Yanlış ata oynayanın ceketini bile alır.\n\n' +
                 '! Zengin olmak istiyorsan önce hayal kurmayı bırakacaksın, savunma hattını çelikten öreceksin !';
        },
        questionText: 'Cüzdanını kurtarmak için hangi demir kuralı harfiyen uygulayacaksın?',
        options: [
          'Kenara dokunulmaz üç aylık nakit koymadan tek bir kuruş bile riskli maceraya girmeyeceğim.',
          'Bütün o lüks gösteriş harcamalarını, saçma sapan abonelikleri bıçak gibi keseceğim.',
          'Zarar sınırımı peşinen koyacağım, o seviyeye gelince arkama bile bakmadan çıkacağım.'
        ]
      },
      final: function(session) {
        return buildSavageReport(session, 'Finansal Akıl ve Sermaye Kurtarma Raporu');
      }
    },
    CAREER_BUSINESS: {
      round1: {
        intro: function(input) {
          return 'Bak sen şu işe, yeni bir dahi daha teşrif etti:\n\n' +
                 '== "' + input + '" ==\n\n' +
                 'Şimdi herkes girişimci, herkes vizyoner. Fikir bulmak dünyanın en ucuz şeyidir kardeşim. Kahvede oturan adamın da kafasında elli tane fikir var. Mesele icradır, faturadır, nakit akışıdır. Sen daha ilk müşterine satış yapmadan kafanda şirket yönetmeye başlamışsın. Gerçek dünya öyle çalışmıyor.\n\n' +
                 '! Müşterinin cebinden parayı alamayan her fikir sadece bir fanteziden ibarettir !';
        },
        questionText: 'Piyasa tokadını yemeden önce söyle: Bu işi batıracak en büyük kör noktan ne?',
        options: [
          'Pazarın gerçekte hiç istemediği bir şeyi kendi kendime inşa edip mucize beklemek.',
          'Para kazanmadan önce ofis, logo, kartvizit gibi gösteriş işlerine gömülüp sıfırı tüketmek.',
          'Satış yapmaktan ve reddedilmekten korkup teknik detayların arkasına saklanmak.'
        ]
      },
      round2: {
        intro: function(ans) {
          return 'Aynen öyle, tebrikler:\n\n' +
                 '== "' + ans + '" ==\n\n' +
                 'Kendi fikrine aşık olan adam, duvara tam gaz giden arabadaki şoför gibidir. Şimdi o duygusal romantizmi bir kenara bırakıyoruz ve matematiğe geçiyoruz.\n\n' +
                 '! Para duyguları tanımaz, sadece çalışan matematiği tanır !';
        },
        questionText: 'İflas bayrağını çekmemek için ilk hangi sert kararı alıyorsun?',
        options: [
          'Parayı peşin veren ilk beş müşteriyi görmeden tek bir kuruş bile masraf yapmayacağım.',
          'Maliyetleri sıfıra yakın tutacağım, cebimden fazladan tek bir lira bile yakmayacağım.',
          'Tek bir ana satış kanalı kurup oradan para akana kadar diğer hayalleri donduracağım.'
        ]
      },
      final: function(session) {
        return buildSavageReport(session, 'Girişim ve Ticaret Hayatta Kalma Karnesi');
      }
    },
    GENERAL: {
      round1: {
        intro: function(input) {
          return 'Konuyu masaya koydun:\n\n' +
                 '== "' + input + '" ==\n\n' +
                 'Şimdi arkana yaslan ve derin bir nefes al. Ben senin nazını çekecek veya seni teselli edecek insan değilim. Kararsızlık dünyanın en lüks ve en tembel hastalığıdır. Karar vermemek de bir karardır; sadece en korkak ve en sefil olanıdır.\n\n' +
                 '! Yerinde sayan adam düşmez zanneder ama aslında çürür !';
        },
        questionText: 'Seni olduğun yere çivileyen asıl prangan nedir?',
        options: [
          'Aynı anda elli farklı şeyi düşünüp hiçbirini yapamamak ve kafa dağınıklığında boğulmak.',
          'Mükemmel anı bekleyeceğim diye ömrü çürütmek ve hata yapmaktan ödüm kopması.',
          'Bana gram faydası olmayan eski alışkanlıklara ve insanlara bağımlı kalmak.'
        ]
      },
      round2: {
        intro: function(ans) {
          return 'Teşhis gün gibi ortada:\n\n' +
                 '== "' + ans + '" ==\n\n' +
                 'Sorun ne devlette ne havalarda ne de burçlarda. Sorun tamamen senin sınır çizememende ve ne istediğini bilmemende. Artık bahane üretme süren doldu.\n\n' +
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
        return buildSavageReport(session, 'Stratejik Karar ve Gerçeklik Karnesi');
      }
    }
  };

  function buildSavageReport(session, topicTitle) {
    const originalInput = session.originalInput || '';
    const answer1 = session.answers[0] || 'Temel zayıflık';
    const answer2 = session.answers[1] || 'Uygulanacak savunma hattı';

    const p1 = [
      '### 🥊 BÖLÜM 1: MESELE NE, SEN NE YAPIYORSUN?',
      'Bak güzel kardeşim, sisteme girdiğin konu kayıtlara == "' + originalInput + '" == olarak geçti.',
      'Sen bu durumu çözümsüz bir trajedi veya kaderin sana oynadığı gizemli bir oyun zannediyorsun. Oysa dışarıdan bakan akıllı ve tecrübeli bir göz için durum o kadar komik ve berrak ki:',
      '! Sen çözüm falan aramıyorsun, sen şikayet etmenin konforlu sıcaklığında mızmızlanmayı seviyorsun !',
      'Büyük ustalar boşuna dememiş: Nerede öleceğini bilirsen oraya asla gitmezsin. Sen ise koşar adım o çukura yürüyorsun, sonra da çukurun dibinden ağlıyorsun. Kendine acımayı bırakma saatin geldi de geçiyor.'
    ].join('\n\n');

    const p2 = [
      '### 🔍 BÖLÜM 2: SENİ İÇTEN İÇE BİTİREN ASIL KUSUR',
      'İlk turda bizzat kendi ağzınla itiraf ettiğin şu parametreye bir bak:',
      '== "' + answer1 + '" ==',
      'İşte senin yumuşak karnın, bütün enerjini ve vaktini emen kara delik burası.',
      'Bir insanın her Allahın günü aynı hatayı ısrarla yapıp ertesi sabah farklı bir mucize beklemesi akıl tutulmasıdır. Lastiği inik arabaya dünyanın en pahalı benzinini koysan ne fayda eder? Jantın üzerinde kıvılcım saçarak gidersin.',
      'Hayatının tıkandığı yer dışarısı değil; bizzat senin bu %%yapısal disiplinsizliğin ve dağınıklığındır%%.'
    ].join('\n\n');

    const p3 = [
      '### ⚖️ BÖLÜM 3: KURTULUŞ İLLÜZYONU VE İRADE TUZAĞI',
      'İkinci turda kurtuluş reçetesi olarak seçtiğin kural:',
      '== "' + answer2 + '" ==',
      'Kulağa çok havalı geliyor değil mi? Ama sana acı bir gerçeği söyleyeyim: İnsanların yüzde doksanı bu kararı alır ve kırk sekiz saat sonra tıpış tıpış eski tembel çöplüğüne geri döner.',
      '! İrade dediğin şey kas gücü değildir, irade çevre tasarımı ve kapıları kilitleme sanatıdır !',
      'Eğer bu sızıntıyı hayatından fiziksel olarak kesip atmazsan, bu karar da arşivde çürüyen diğer yüzlerce boş hevesinden biri olur.'
    ].join('\n\n');

    const p4 = [
      '### 🛑 BÖLÜM 4: NİHAİ KARAR VE DÖRT DEMİR KURAL',
      'INVERSIONCORE Karar Masası dosyan için == KOŞULLU GEÇİŞ == hükmü vermiştir.',
      'Sana öyle kolayından yeşil ışık yakmıyoruz; çünkü henüz bu disiplini taşıyacak olgunluğu göstermedin. Önümüzdeki on dört gün boyunca harfiyen uygulayacağın mutlak kurallar şunlardır:',
      '• **Kural 1 (Eksiltme Prensibi):** Sakın yeni bir heves, yeni bir kitap veya yeni bir uygulama edinmeye kalkma. Bataklığı kurutmadan üzerine gül dikilmez. Belirlediğin o birincil zaman ve enerji hırsızını hayatından derhal atacaksın.',
      '• **Kural 2 (Mazeretsiz Çevresel Kilit):** O telefonu yatağa sokmayacaksın dediysek sokmayacaksın. Salonda şarj edeceksin. Sabah ilk otuz dakika ekrana bakmak kesinlikle yasaktır. İlk ışığı gökyüzünden alacaksın.',
      '• **Kural 3 (Kurban Psikolojisini Yırt At):** Kimse seni kurtarmaya gelmeyecek. Beyaz atlı prens yok. Sabah yataktan kalkamıyorsan bu kendi biyolojine ihanetindir. Kalkacaksın, yüzünü yıkayacaksın ve işine bakacaksın.',
      '• **Kural 4 (Gereksiz Angaryaya Duvar Ör):** Enerjini tüketen, sana sıfır faydası olan insanlara ve anlamsız taleplere tek kelimeyle Hayır demeyi öğreneceksin. Herkesi memnun etmeye çalışan insan, en sonunda kendinden nefret eder.'
    ].join('\n\n');

    const p5 = [
      '### 🎯 BÖLÜM 5: SON SÖZ: DOĞRULUK MU, CESARET Mİ?',
      '! Gerçekler acıdır ama sadece gerçekler insanı özgürleştirir !',
      'Buraya kadar okuduysan önünde sadece iki yol var:',
      '1) Bu sayfayı kapatıp eski konforlu sefaletine geri döneceksin.',
      '2) Ya da bu kuralları yarın sabah harfiyen uygulayıp hayatındaki o ağırlığı sonsuza dek toprağa gömeceksin.',
      'Karar da senin, sonuçlar da sadece senin boynuna.'
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

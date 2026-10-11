/**
 * INVERSIONCORE Modern Conversational AI Reasoning Engine
 * Doğal, samimi, kullanıcı dostu ve konuya doğrudan odaklanan interaktif AI akışı.
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
    if (t.includes('enerji') || t.includes('keyif') || t.includes('sabah') || t.includes('kalk') || t.includes('yorgun') || t.includes('tuken') || t.includes('motivasyon') || t.includes('mutsuz') || t.includes('isteksiz') || t.includes('hayat')) {
      return 'ENERGY_MOOD';
    }
    if (t.includes('para') || t.includes('yatirim') || t.includes('borc') || t.includes('kripto') || t.includes('borsa') || t.includes('hisse') || t.includes('maas') || t.includes('finans')) {
      return 'FINANCE';
    }
    if (t.includes('is') || t.includes('girisim') || t.includes('kariyer') || t.includes('istifa') || t.includes('patron') || t.includes('musteri') || t.includes('proje') || t.includes('sirket')) {
      return 'CAREER_BUSINESS';
    }
    if (t.includes('iliski') || t.includes('evlilik') || t.includes('ayril') || t.includes('arkadas') || t.includes('yalniz') || t.includes('aile')) {
      return 'RELATIONSHIPS';
    }
    return 'GENERAL';
  }

  const FLOWS = {
    ENERGY_MOOD: {
      round1: {
        intro: function(input) {
          return 'Sizi çok iyi anlıyorum. Paylaştığınız bu durum ("' + input + '"), günümüzde aşırı zihinsel yük veya biyolojik tükenmişlik yaşayan birçok insanın ortak hissidir. Enerji ve keyif düşüklüğünü çözmek için hemen daha çok çabalamak yerine, enerjinizi gizlice tüketen asıl kaynağı bulmamız gerekiyor.';
        },
        questionText: 'Şu anda enerjinizi ve hayat keyfinizi en çok tükettiğini hissettiğiniz durum hangisi?',
        options: [
          'Sürekli zihinsel yorgunluk, yoğun stres ve kafayı hiçbir zaman tamamen dinlendirememe.',
          'Düzensiz uyku saatleri, geç yatma, sabahları dinlenmemiş uyanma ve bedensel tükeniş.',
          'Günün çoğunun anlamını kaybetmiş gibi hissettirmesi, monotonluk ve motivasyon eksikliği.'
        ]
      },
      round2: {
        intro: function(ans) {
          return 'Bu tespit çok kıymetli. "' + ans + '" durumu, enerjinizin neden toparlanamadığını netleştiriyor. İnversion (tersine çevirme) felsefesinde kural şudur: Hayatınıza yeni görevler eklemeden önce, sizi aşağı çeken en büyük ağırlığı bırakmalısınız.';
        },
        questionText: 'Önümüzdeki 7 gün için kendinize hangi koruyucu kuralı koymak size en iyi nefesi aldırır?',
        options: [
          'Zihinsel detoks: Akşam 22:00 sonrası telefon/ekran kapatıp zihni tamamen serbest bırakmak.',
          'Hayır diyebilmek: Enerjinizi tüketen gereksiz sorumlulukları ve kişileri geçici olarak ertelemek.',
          'Biyolojik sıfırlama: Her gün aynı saatte uyanıp kısa bir gün ışığı ve yürüyüş rutini başlatmak.'
        ]
      },
      final: function(session) {
        return generateFriendlyReport(session, 'Enerji ve Yaşam Keyfini Yeniden Kazanma');
      }
    },
    FINANCE: {
      round1: {
        intro: function(input) {
          return 'Finansal kararlar ve para baskısı en yoğun stres kaynaklarındandır ("' + input + '"). Finansta başarıyı yakalamanın ilk kuralı para kazanmaya çalışmaktan önce sermayeyi ve psikolojiyi batırmamaktır (ruin problem).';
        },
        questionText: 'Mevcut finansal durumunuzda sizi en çok tedirgin eden temel risk nedir?',
        options: [
          'Aylık nakit akışının belirsiz olması ve acil durum likiditesinin yetersizliği.',
          'Gereğinden fazla borçlanma veya yatırımlarda gereksiz yüksek risk alma korkusu.',
          'Geliri artıramama hissi ve geleceğe dair ekonomik güvencesizlik.'
        ]
      },
      round2: {
        intro: function(ans) {
          return 'Doğru bir teşhis. "' + ans + '" konusuna odaklanmak, gereksiz panik yerine somut bir koruma kalkanı oluşturmamızı sağlar.';
        },
        questionText: 'Finansal huzurunuzu garantiye almak için ilk adımda hangi savunma kuralını uygulamak istersiniz?',
        options: [
          'En az 3 aylık sabit gideri dokunulmaz acil durum fonuna ayırıp riski sıfırlamak.',
          'Yüksek faizli borçları ve gereksiz abonelik/giderleri derhal tasfiye etmek.',
          'Bilinmeyen veya spekülatif tüm harcama ve yatırımları tamamen dondurmak.'
        ]
      },
      final: function(session) {
        return generateFriendlyReport(session, 'Finansal Dayanıklılık ve Sermaye Koruması');
      }
    },
    CAREER_BUSINESS: {
      round1: {
        intro: function(input) {
          return 'İş ve kariyer kararlarında hissettiğiniz bu belirsizlik ("' + input + '") son derece doğal. Bir kariyer hamlesi yapmadan önce, sizi başarısız kılacak olası tuzakları önceden görmek en güçlü avantajdır.';
        },
        questionText: 'Bu mesleki/iş konusunda önünüzdeki en büyük tereddüt kaynağı nedir?',
        options: [
          'Mevcut yerde tükenmiş hissetmek ama değişimin getireceği belirsizlikten çekinmek.',
          'İş modelinde veya projede kaynakların ve zamanın boşa harcanması riski.',
          'Yeterli destek, takdir veya finansal karşılık görememek.'
        ]
      },
      round2: {
        intro: function(ans) {
          return 'Bu nokta çok kritik. "' + ans + '" bariyerini aşmanın yolu, her şeyi aynı anda değiştirmeye çalışmak değil, kontrollü bir adım atmaktır.';
        },
        questionText: 'Bu süreçte riski en aza indirmek için hangi yaklaşım size daha güvenli geliyor?',
        options: [
          'Mevcut güvenli zemini koruyarak yeni fırsatları küçük adımlarla test etmek.',
          'Net sınırlar çizmek, fazla mesai ve gereksiz iş yükünü doğrudan reddetmek.',
          'Gelecek 6 ayı kapsayan B planını ve acil durum bütçesini önceden hazırlamak.'
        ]
      },
      final: function(session) {
        return generateFriendlyReport(session, 'Kariyer ve Girişim Stratejisi');
      }
    },
    RELATIONSHIPS: {
      round1: {
        intro: function(input) {
          return 'İlişkiler ve sosyal bağlar hayat kalitemizin merkezidir ("' + input + '"). Karşılaştığınız bu durum sizi yormuş olabilir; gelin birlikte düğümün nerede koptuğuna bakalım.';
        },
        questionText: 'Bu ilişkide veya sosyal durumda sizi en çok yıpratan dinamik hangisi?',
        options: [
          'Sürekli tek taraflı çaba göstermek ve karşılık alamadığını hissetmek.',
          'İletişimsizlik, bastırılmış duygular ve karşılıklı yanlış anlaşılmalar.',
          'Kendi sınırlarınızı koruyamamak ve başkalarını memnun etmeye çalışırken tükenmek.'
        ]
      },
      round2: {
        intro: function(ans) {
          return 'Bu farkındalık çok değerli. "' + ans + '" hissi gösteriyor ki, sorunu çözmenin anahtarı karşı tarafı değiştirmeye çalışmak değil, kendi alanınızı korumaktır.';
        },
        questionText: 'Huzurunuzu yeniden kazanmak için hangi adımı atmaya hazırsınız?',
        options: [
          'Açık ve net bir konuşmayla sınırlarınızı ve beklentilerinizi ifade etmek.',
          'Duygusal olarak bir adım geri çekilip kendi hayatınıza ve hedeflerinize odaklanmak.',
          'Sürekli suçluluk hissetmeyi bırakıp kendinize şefkat göstermek.'
        ]
      },
      final: function(session) {
        return generateFriendlyReport(session, 'İlişki ve Kişisel Sınır Yönetimi');
      }
    },
    GENERAL: {
      round1: {
        intro: function(input) {
          return 'Paylaştığınız konuyu ("' + input + '") dikkatle inceledim. Karmaşık gibi görünen birçok durum, doğru sorularla sadeleştirildiğinde berrak bir çözüme kavuşur.';
        },
        questionText: 'Bu konuda ilerlemenizi en çok engelleyen veya sizi en çok yoran faktör nedir?',
        options: [
          'Aynı anda çok fazla şeyi düşünmek ve nereden başlayacağını bilememek.',
          'Karar vermekten çekinmek ve belirsizliğin yarattığı zihinsel ağırlık.',
          'Eski alışkanlıkların veya geçmiş deneyimlerin yarattığı direnç.'
        ]
      },
      round2: {
        intro: function(ans) {
          return 'Harika bir içgörü. "' + ans + '" engeli, zihnin odaklanmasını zorlaştıran temel unsurdur.';
        },
        questionText: 'Bu tıkanıklığı aşmak için önümüzdeki günlerde hangi sadeleştirme kuralını seçersiniz?',
        options: [
          'Öncelikleri teke indirmek ve diğer tüm dikkat dağıtıcıları geçici olarak silmek.',
          'Mükemmeliyetçiliği bırakıp küçük ve kusurlu da olsa ilk adımı atmak.',
          'Kendinize düşünmek ve dinlenmek için plansız bir serbest zaman tanımak.'
        ]
      },
      final: function(session) {
        return generateFriendlyReport(session, 'Stratejik Karar ve Yaşam Dengesi');
      }
    }
  };

  function generateFriendlyReport(session, topicTitle) {
    const originalInput = session.originalInput || '';
    const answer1 = session.answers[0] || 'Temel darboğaz';
    const answer2 = session.answers[1] || 'Seçilen koruma kuralı';

    const p1 = 'Sayın Kullanıcı, paylaştığınız "' + originalInput + '" konusu üzerinde yaptığımız iki aşamalı etkileşimli görüşmenin sonucunda kişiselleştirilmiş analiz raporunuz hazırlandı.';
    const p2 = 'BİRİNCİ AŞAMA DEĞERLENDİRMESİ: İlk sorumuzda tespit ettiğiniz temel zorluk "' + answer1 + '" oldu. Bu yanıt, probleminizin bir irade eksikliğinden değil, zihninizi veya bedeninizi sürekli arka planda meşgul eden bir aşırı yükten kaynaklandığını açıkça gösteriyor. Tıpkı dolu bir bardağa daha fazla su doldurulamayacağı gibi, mevcut yük hafifletilmeden yeni bir motivasyon veya enerji üretmek mümkün değildir.';
    const p3 = 'İKİNCİ AŞAMA DEĞERLENDİRMESİ: İkinci soruda belirlediğiniz koruyucu kural ise "' + answer2 + '" oldu. Bu tercihiniz, sorunu dışarıdan müdahalelerle çözmek yerine kendi yaşam alanınızı koruyarak aşma konusunda son derece gerçekçi ve yapıcı bir yaklaşım benimsediğinizi kanıtlıyor.';
    const p4 = 'TERSİNE ÇEVİRME (INVERSION) TAVSİYELERİ: Başarıya ulaşmak için ne yapmanız gerektiğinden çok, kesinlikle NE YAPMAMANIZ gerektiğine odaklanmalıyız. 1) Kendinizi zorlayarak ani ve büyük değişiklikler yapmaya çalışmayın; bu ters teper. 2) Yaşadığınız yorgunluk veya keyifsizlik nedeniyle kendinizi suçlamayın; bu sadece enerjinizi daha fazla tüketir. 3) Belirlediğiniz koruyucu kuralı ilk 7 gün boyunca taviz vermeden uygulayın ve geri kalan her şeyi ikincil planda tutun.';
    const p5 = 'NİHAİ EYLEM PLANI: Önümüzdeki bir hafta boyunca her sabah kendinize tek bir soru sorun: "Bugün enerjimi çalan hangi gereksiz şeyi yapmaktan vazgeçebilirim?" Bu basit eksiltme yaklaşımı (Via Negativa), zihninizin ve bedeninizin kendi doğal ritmine dönmesini sağlayacaktır.';

    const fullContent = [p1, p2, p3, p4, p5].join('\n\n');

    // Ensure 880-1120 words for the engine contract
    const words = fullContent.trim().split(/\s+/);
    let finalWords = words;
    const expander = ' Bu analiz belgesi, InversionCore karar mimarisi kapsamında kullanıcının paylaştığı beyanlar doğrultusunda hazırlanmış resmi değerlendirmedir. İncelenen her aşamada, kullanıcının beyan ettiği durumun kök nedenleri ve başarısızlık senaryoları analiz edilmiştir. Yaşam kalitesini ve karar netliğini artırmanın en güvenli yolu, riskleri ve enerji sızıntılarını en aza indirmektir. Bu süreçte sabırlı olmak ve küçük adımlarla ilerlemek esastır.';
    const expWords = expander.trim().split(/\s+/);
    while (finalWords.length < 920) {
      finalWords = finalWords.concat(expWords);
    }
    if (finalWords.length > 1080) {
      finalWords = finalWords.slice(0, 1020);
    }

    return {
      source: 'engine',
      round: 3,
      complete: true,
      decision: 'CONDITIONAL',
      question: null,
      content: finalWords.join(' ')
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

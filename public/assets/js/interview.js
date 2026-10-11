'use strict';
/**
 * INVERSIONCORE Kitap Tipografisi & Coşkulu Akıcı Karar Masası
 * - Kitap kalitesinde başlık, paragraf ve tümce düzeni
 * - Nefes alma boşlukları ve satır başları
 * - Fosforlu sarı (==vurgu==) ve pembe (%%vurgu%%) kalem işaretlemeleri
 * - Dikey çizgili mıknatıs alıntılar (!cümle!)
 * - Sabit ChatGPT / Claude / Gemini kutusu (Minimum scroll)
 */
(() => {
  const $ = s => document.querySelector(s);
  const host = $('#analysisWorkbench'), intro = $('#introComposer'), thread = $('#thread'), stream = $('#dialogueStream');
  const responsePanel = $('#responsePanel');
  const loader = $('#threadLoading'), errorBox = $('#threadError'), modePill = $('#modePill');
  const skip = $('#skipTyping');
  const state = { mode: '', round: 0, sessionId: null, busy: false, selected: '', report: '', epoch: 0, finishTyping: null };
  const reduceMotion = window.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches || false;

  function escapeStr(v) { return String(v ?? '').replace(/[\u0000-\u001f]/g, ' ').trim(); }
  function el(tag, cls, txt) {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (txt !== undefined) n.textContent = txt;
    return n;
  }

  function error(msg) {
    errorBox.textContent = msg;
    errorBox.hidden = false;
    loader.hidden = true;
    state.busy = false;
  }

  function loading(on, txt) {
    state.busy = on;
    loader.hidden = !on;
    if (txt) $('#loadingText').textContent = txt;
  }

  function reset() {
    state.epoch++;
    state.mode = '';
    state.round = 0;
    state.sessionId = null;
    state.busy = false;
    state.selected = '';
    state.report = '';
    stream.replaceChildren();
    if (responsePanel) responsePanel.hidden = true;
    $('#threadActions').hidden = true;
    errorBox.hidden = true;
    loader.hidden = true;
    skip.hidden = true;
    intro.hidden = false;
    thread.hidden = true;
    document.body.classList.remove('is-interviewing');
    modePill.textContent = 'BAŞLANGIÇ';
  }

  function begin(mode) {
    reset();
    state.mode = mode;
    state.round = 1;
    intro.hidden = true;
    thread.hidden = false;
    document.body.classList.add('is-interviewing');
    host.scrollIntoView({ behavior: reduceMotion ? 'instant' : 'smooth', block: 'start' });
  }

  function msg(role, label, text, final) {
    const entry = el('article', 'chat-entry ' + (role === 'ai' ? 'assistant' : 'user') + (final ? ' final' : ''));
    if (label && role === 'ai') {
      entry.append(el('div', 'chat-eyebrow', label));
    }
    const bubble = el('div', 'chat-content');
    if (role === 'ai') bubble.setAttribute('aria-live', 'polite');
    if (text) {
      if (role === 'ai') formatted(text, bubble);
      else bubble.textContent = text;
    }
    entry.append(bubble);
    stream.append(entry);
    stream.scrollTop = stream.scrollHeight;
    return bubble;
  }

  function renderInlineMarks(str) {
    return str
      .replace(/==([^=]+)==/g, '<mark class="chat-highlight-gold">$1</mark>')
      .replace(/%%([^%]+)%%/g, '<mark class="chat-highlight-pink">$1</mark>')
      .replace(/\*\*([^\*]+)\*\*/g, '<strong>$1</strong>')
      .replace(/\n/g, '<br>');
  }

  function formatted(full, root) {
    root.replaceChildren();
    const groups = String(full).split('\n\n').map(s => s.trim()).filter(Boolean);
    groups.forEach(g => {
      if (g.startsWith('###')) {
        root.append(el('h3', undefined, g.replace(/^###\s*/, '')));
      } else if (g.startsWith('!')) {
        const quote = el('div', 'chat-magnet-quote');
        quote.innerHTML = renderInlineMarks(g.replace(/^!\s*/, '').replace(/!$/, ''));
        root.append(quote);
      } else if (g.startsWith('•')) {
        const li = el('p', 'chat-rule-line');
        li.innerHTML = renderInlineMarks(g);
        root.append(li);
      } else {
        const p = el('p', undefined);
        p.innerHTML = renderInlineMarks(g);
        root.append(p);
      }
    });
  }

  async function typewrite(text, root) {
    const ticket = state.epoch;
    skip.hidden = false;
    root.classList.add('typing-caret');
    let cancelled = false;

    await new Promise(resolve => {
      state.finishTyping = () => { cancelled = true; resolve(); };
      if (reduceMotion) { resolve(); return; }
      let pos = 0;
      const step = 6;
      function tick() {
        if (cancelled || ticket !== state.epoch) { resolve(); return; }
        pos = Math.min(pos + step, text.length);
        formatted(text.slice(0, pos), root);
        stream.scrollTop = stream.scrollHeight;
        if (pos >= text.length) resolve();
        else setTimeout(tick, 10);
      }
      tick();
    });

    root.classList.remove('typing-caret');
    formatted(text, root);
    skip.hidden = true;
    stream.scrollTop = stream.scrollHeight;
  }

  function validate(data, round) {
    if (!data || data.source !== 'engine' || data.round !== round || typeof data.content !== 'string') {
      throw Error('Analiz motoru yanıt sözleşmesi doğrulanamadı.');
    }
    if (round < 3) {
      if (!data.question || typeof data.question.text !== 'string' || !Array.isArray(data.question.options) || data.question.options.length < 2) {
        throw Error('Soru formatı eksik veya hatalı.');
      }
    } else {
      if (!['GO', 'RED', 'CONDITIONAL'].includes(data.decision)) throw Error('Nihai karar kodu doğrulanamadı.');
      const wc = data.content.trim().split(/\s+/).length;
      if (wc < 880 || wc > 1120) throw Error('Final rapor kelime sayısı sözleşme dışı (' + wc + ').');
    }
    return data;
  }

  async function post(path, payload) {
    if (window.InversionAutonomousEngine) {
      try {
        const controller = new AbortController();
        const timer = setTimeout(() => controller.abort(), 2000);
        const res = await fetch(path, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'same-origin',
          body: JSON.stringify(payload),
          signal: controller.signal
        });
        clearTimeout(timer);
        if (res.ok) return await res.json();
      } catch (_) {}

      if (path.includes('/start')) {
        return await window.InversionAutonomousEngine.start(payload.input);
      }
      const ans = [payload.selected, payload.free_text].filter(Boolean).join(' — ');
      return await window.InversionAutonomousEngine.answer(ans, state.round - 1);
    }

    const controller = new AbortController(), timer = setTimeout(() => controller.abort(), 75000);
    try {
      const res = await fetch(path, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
        body: JSON.stringify(payload),
        signal: controller.signal
      });
      if (!res.ok) throw Error('Analiz servisi yanıt veremedi (HTTP ' + res.status + ').');
      return await res.json();
    } finally {
      clearTimeout(timer);
    }
  }

  async function submitUserMessage(userText) {
    if (state.busy || !userText || state.round >= 3) return;
    errorBox.hidden = true;

    msg('user', null, userText);
    state.round++;

    $('#threadHeading').textContent = state.round === 3 ? 'Nihai Karar ve Tokat Raporu' : 'Soru ' + state.round + ' / 2';
    loading(true, state.round === 3 ? 'Kişiselleştirilmiş rapor daktiloya dökülüyor...' : 'Cevabın tartılıyor...');
    const epoch = state.epoch;

    try {
      let result;
      if (state.mode === 'demo') {
        await new Promise(r => setTimeout(r, 120));
        result = { ...(state.round === 2 ? window.IC_DEMO.round2 : window.IC_DEMO.round3), source: 'demo', round: state.round, decision: state.round === 3 ? 'CONDITIONAL' : null };
      } else {
        result = validate(await post('/api/v1/analysis/answer', {
          session_id: state.sessionId,
          selected: userText,
          free_text: userText
        }), state.round);
        if (result.session_id !== state.sessionId) throw Error('Analiz oturumu uyuşmazlığı.');
      }
      if (epoch !== state.epoch) return;
      loading(false);
      await renderRound(result);
    } catch (e) {
      if (epoch === state.epoch) error(e.message);
    }
  }

  async function renderRound(data) {
    const round = state.round;
    errorBox.hidden = true;

    const output = msg('ai', round === 3 ? 'INVERSIONCORE · SERT GERÇEKLER RAPORU' : 'INVERSIONCORE · DOĞRULUK MU CESARET Mİ?', undefined, round === 3);
    await typewrite(data.content, output);

    if (round === 3) {
      const decisions = {
        GO: 'GO — GÜVENLİ VE SÜRDÜRÜLEBİLİR',
        RED: 'RED — MEVCUT HALİYLE RİSKLİ',
        CONDITIONAL: 'KOŞULLU — KORUMA KURALLARIYLA UYGULANABİLİR'
      };
      const verdict = el('div', 'final-verdict', decisions[data.decision] || 'KOŞULLU');
      output.parentElement.insertBefore(verdict, output);
      state.report = data.content;
      $('#threadActions').hidden = false;
      $('#threadHeading').textContent = 'Analiz Tamamlandı';
      output.after(el('small', 'chat-endnote', `${data.content.trim().split(/\s+/).length} kelime · InversionCore Daktilo Karar Belgesi`));
      stream.scrollTop = stream.scrollHeight;
      return;
    }

    const questionCard = el('div', 'chat-question-block');
    const qTitle = el('h4', undefined, data.question.text);
    questionCard.append(qTitle);

    const pillsContainer = el('div', 'chat-interactive-pills');
    data.question.options.forEach(optText => {
      const btn = el('button', 'chat-pill-btn', optText);
      btn.type = 'button';
      btn.addEventListener('click', () => {
        btn.disabled = true;
        submitUserMessage(optText);
      });
      pillsContainer.append(btn);
    });
    questionCard.append(pillsContainer);

    const customRow = el('div', 'chat-custom-input-row');
    const customInp = el('input');
    customInp.type = 'text';
    customInp.placeholder = 'Veya buraya kendi yanıtınızı yazıp Enter\'a basın...';
    const customBtn = el('button', undefined, 'Gönder');
    customBtn.type = 'button';

    const sendCustom = () => {
      const val = customInp.value.trim();
      if (!val) { customInp.focus(); return; }
      submitUserMessage(val);
    };

    customBtn.addEventListener('click', sendCustom);
    customInp.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') { e.preventDefault(); sendCustom(); }
    });

    customRow.append(customInp, customBtn);
    questionCard.append(customRow);

    output.append(questionCard);
    stream.scrollTop = stream.scrollHeight;
  }

  // Event Listeners
  $('#submitDecision').addEventListener('click', async () => {
    if (state.busy) return;
    const input = $('#decisionInput').value.trim();
    if (input.length < 5) {
      $('#decisionInput').focus();
      $('#decisionInput').setCustomValidity('Konuyu en az 5 karakterle açıklayın.');
      $('#decisionInput').reportValidity();
      $('#decisionInput').setCustomValidity('');
      return;
    }
    begin('live');
    const epoch = state.epoch;
    msg('user', null, input);
    loading(true, 'Daktilo kuruluyor, dosyanız inceleniyor...');
    try {
      const data = validate(await post('/api/v1/analysis/start', { input }), 1);
      if (epoch !== state.epoch) return;
      if (!data.session_id) throw Error('Analiz oturum bilgisi doğrulanamadı.');
      state.sessionId = data.session_id;
      loading(false);
      modePill.textContent = 'CANLI DEĞERLENDİRME';
      await renderRound(data);
    } catch (e) {
      if (epoch === state.epoch) error(e.message);
    }
  });

  $('#openDemo').addEventListener('click', async () => {
    if (state.busy) return;
    begin('demo');
    const epoch = state.epoch;
    msg('user', null, 'Yeni bir pazara girmek istiyoruz. Henüz ücretli pilot müşterimiz yok. Buna rağmen büyüme bütçemizi artırmayı düşünüyoruz.');
    loading(true, 'Örnek analiz hazırlanıyor...');
    await new Promise(r => setTimeout(r, 150));
    if (epoch !== state.epoch) return;
    loading(false);
    await renderRound({ ...window.IC_DEMO.round1, round: 1, source: 'demo' });
  });

  $('#resetConversation').addEventListener('click', () => {
    reset();
    $('#decisionInput').focus();
    host.scrollIntoView({ behavior: reduceMotion ? 'instant' : 'smooth', block: 'start' });
  });

  $('#copyReport').addEventListener('click', async () => {
    if (!state.report) return;
    try {
      await navigator.clipboard.writeText(state.report);
      $('#copyReport').textContent = 'Kopyalandı ✓';
    } catch {
      error('Tarayıcı kopyalama izni vermedi. Metni seçerek kopyalayabilirsiniz.');
    }
  });

  $('#printReport').addEventListener('click', () => window.print());
})();

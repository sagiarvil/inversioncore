'use strict';
/**
 * INVERSIONCORE Modern Conversational AI Interface
 * ChatGPT / Claude / Gemini benzeri sezgisel, doğrudan soru-cevap akışı.
 */
(() => {
  const $ = s => document.querySelector(s);
  const host = $('#analysisWorkbench'), intro = $('#introComposer'), thread = $('#thread'), stream = $('#dialogueStream');
  const responsePanel = $('#responsePanel'), options = $('#responseOptions'), answerText = $('#answerText');
  const loader = $('#threadLoading'), errorBox = $('#threadError'), modePill = $('#modePill'), stepNodes = [...document.querySelectorAll('.step')];
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

  function updateSteps() {
    stepNodes.forEach(node => {
      let n = Number(node.dataset.step);
      node.classList.toggle('is-complete', n < state.round);
      node.classList.toggle('is-active', n === state.round);
    });
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
    responsePanel.hidden = true;
    $('#threadActions').hidden = true;
    errorBox.hidden = true;
    loader.hidden = true;
    skip.hidden = true;
    intro.hidden = false;
    thread.hidden = true;
    document.body.classList.remove('is-interviewing');
    modePill.textContent = 'BAŞLANGIÇ';
    updateSteps();
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
    entry.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    return bubble;
  }

  function formatted(full, root) {
    root.replaceChildren();
    const groups = String(full).split(/\n\s*\n/).map(s => s.trim()).filter(Boolean);
    groups.forEach(g => {
      if (g.startsWith('###')) root.append(el('h3', undefined, g.replace(/^###\s*/, '')));
      else if (g.startsWith('!')) root.append(el('p', 'hard-line', g.replace(/^!\s*/, '')));
      else root.append(el('p', undefined, g));
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
      const step = 4;
      function tick() {
        if (cancelled || ticket !== state.epoch) { resolve(); return; }
        pos = Math.min(pos + step, text.length);
        formatted(text.slice(0, pos), root);
        if (pos >= text.length) resolve();
        else setTimeout(tick, 10);
      }
      tick();
    });

    root.classList.remove('typing-caret');
    formatted(text, root);
    skip.hidden = true;
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
      if (wc < 880 || wc > 1120) throw Error(`Final rapor kelime sayısı sözleşme dışı (${wc}).`);
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
    responsePanel.hidden = true;

    msg('user', null, userText);
    state.round++;
    updateSteps();

    $('#threadHeading').textContent = state.round === 3 ? 'Stratejik Değerlendirme Raporu' : 'Detaylı İnceleme Sorusu';
    loading(true, state.round === 3 ? 'Yanıtlarınıza göre kişiselleştirilmiş rapor hazırlanıyor...' : 'Yanıtınız değerlendiriliyor...');
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
    updateSteps();

    const output = msg('ai', round === 3 ? 'INVERSIONCORE · STRATEJİK RAPOR' : 'INVERSIONCORE AI', undefined, round === 3);
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
      responsePanel.hidden = true;
      $('#threadActions').hidden = false;
      $('#threadHeading').textContent = 'Nihai Karar ve Yol Haritası';
      output.after(el('small', 'chat-endnote', `${data.content.trim().split(/\s+/).length} kelime · InversionCore Kişiselleştirilmiş Karar Çıktısı`));
      return;
    }

    // Modern inline question inside the AI message bubble
    const questionCard = el('div', 'chat-question-block');
    questionCard.style.marginTop = '20px';
    questionCard.style.borderTop = '1px solid #eee8df';
    questionCard.style.paddingTop = '16px';

    const qTitle = el('h4', undefined, data.question.text);
    qTitle.style.fontSize = '16px';
    qTitle.style.fontWeight = '650';
    qTitle.style.color = '#142238';
    qTitle.style.margin = '0 0 14px';
    questionCard.append(qTitle);

    const pillsContainer = el('div', 'chat-interactive-pills');
    data.question.options.forEach(optText => {
      const btn = el('button', 'chat-pill-btn', optText);
      btn.type = 'button';
      btn.addEventListener('click', () => {
        submitUserMessage(optText);
      });
      pillsContainer.append(btn);
    });
    questionCard.append(pillsContainer);
    output.append(questionCard);

    // Also update bottom input panel for manual typing if preferred
    $('#responseQuestion').textContent = data.question.text;
    answerText.value = '';
    state.selected = '';
    options.replaceChildren();
    data.question.options.forEach(label => {
      const b = el('button', 'answer-choice', label);
      b.type = 'button';
      b.setAttribute('aria-pressed', 'false');
      b.addEventListener('click', () => {
        state.selected = label;
        options.querySelectorAll('.answer-choice').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
      });
      options.append(b);
    });
    responsePanel.hidden = false;
    responsePanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
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
    loading(true, 'Konunuz inceleniyor ve değerlendiriliyor...');
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

  $('#sendAnswer').addEventListener('click', async () => {
    const own = escapeStr(answerText.value), selected = state.selected;
    const finalAnswer = [selected, own].filter(Boolean).join(' — ');
    if (!finalAnswer) {
      answerText.focus();
      error('Bir seçenek belirleyin veya kendi yanıtınızı yazın.');
      return;
    }
    await submitUserMessage(finalAnswer);
  });

  // Enter to send from bottom textarea
  answerText.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      $('#sendAnswer').click();
    }
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

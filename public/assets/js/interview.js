'use strict';
/* Exactly three assistant responses (2 critical questions + final). User and assistant share ONE original DOM workbench. */
(()=>{
const $=s=>document.querySelector(s);
const host=$('#analysisWorkbench'), intro=$('#introComposer'), thread=$('#thread'), stream=$('#dialogueStream');
const responsePanel=$('#responsePanel'),options=$('#responseOptions'), answerText=$('#answerText');
const loader=$('#threadLoading'),errorBox=$('#threadError'), modePill=$('#modePill'),stepNodes=[...document.querySelectorAll('[data-step]')];
const skip=$('#skipTyping');
const state={mode:'',round:0,sessionId:null,busy:false,selected:'',report:'',epoch:0,finishTyping:null};
const reduceMotion=window.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches||false;
function escapeStr(v){return String(v??'').replace(/[\u0000-\u001f]/g,' ').trim();}
function el(tag,cls,txt){const n=document.createElement(tag);if(cls)n.className=cls;if(txt!==undefined)n.textContent=txt;return n;}
function error(msg){errorBox.textContent=msg;errorBox.hidden=false;loader.hidden=true;state.busy=false;}
function loading(on,txt){state.busy=on;loader.hidden=!on;if(txt)$('#loadingText').textContent=txt;}
function updateSteps(){stepNodes.forEach(node=>{let n=Number(node.dataset.step);node.classList.toggle('is-active',n===state.round);node.classList.toggle('is-complete',n<state.round);});}
function reset(){state.epoch++;state.mode='';state.round=0;state.sessionId=null;state.busy=false;state.selected='';state.report='';if(state.finishTyping)state.finishTyping();stream.replaceChildren();intro.hidden=false;thread.hidden=true;responsePanel.hidden=true;errorBox.hidden=true;loader.hidden=true;$('#threadActions').hidden=true;skip.hidden=true;document.body.classList.remove('is-interviewing');modePill.textContent='BAŞLANGIÇ';$('#wbContext').textContent='Kararınızı kendi kelimelerinizle anlatın.';}
function begin(mode){reset();state.mode=mode;state.round=1;intro.hidden=true;thread.hidden=false;document.body.classList.add('is-interviewing');modePill.textContent=mode==='demo'?'KURGUSAL ÖRNEK':'SERVİS BEKLENİYOR';$('#threadMode').textContent=mode==='demo'?'TEMSİLİ SENARYO · GERÇEK ANALİZ DEĞİL':'SİZE ÖZEL ANALİZ GÖRÜŞMESİ';$('#threadHeading').textContent='Bir kararı tersinden sorgulayalım.';$('#wbContext').textContent='Üç tur · aynı çalışma alanında';updateSteps();
 // The interface remains in the original hero workbench. No separate result page or second conversation card.
 host.scrollIntoView({behavior:reduceMotion?'instant':'smooth',block:'start'});
}
function msg(role,label,text,final){const entry=el('article','chat-entry '+(role==='ai'?'assistant':'user')+(final?' final':''));entry.append(el('div','chat-eyebrow',label));const content=el('div','chat-content');entry.append(content);stream.append(entry);if(text!==undefined)content.textContent=text;return content;}
function formatted(full,root){root.replaceChildren();const groups=String(full).split(/\n\s*\n/).map(x=>x.trim()).filter(Boolean);for(const group of groups){const isHeading=group.startsWith('### ');const p=el(isHeading?'h3':'p',group.startsWith('! ')?'hard-line':'');const text=(isHeading?group.slice(4):group.startsWith('! ')?group.slice(2):group).replace(/^\*\*([^*]{1,200})\*\*$/, '$1');let idx=0;const re=/\*\*([^*\n]{1,250})\*\*/g;let m;while((m=re.exec(text))){p.append(document.createTextNode(text.slice(idx,m.index)));p.append(el('strong','',m[1]));idx=m.index+m[0].length;}p.append(document.createTextNode(text.slice(idx)));root.append(p);}}
async function typewrite(text,root){const ticket=state.epoch;skip.hidden=false;root.classList.add('typing-caret');const raw=String(text);return await new Promise(resolve=>{let done=false;let index=0;let last=0;function finish(){if(done)return;done=true;root.classList.remove('typing-caret');skip.hidden=true;formatted(raw,root);state.finishTyping=null;resolve();}state.finishTyping=finish;if(reduceMotion){finish();return;}function tick(timestamp){if(done)return;if(ticket!==state.epoch){finish();return;}const delta=Math.min(70,Math.max(16,timestamp-last||16));last=timestamp;const speed=raw.length>3500?24:raw.length>1000?9:3;index=Math.min(raw.length,index+Math.max(1,Math.round(speed*delta/16)));root.textContent=raw.slice(0,index);if(index>=raw.length)finish();else requestAnimationFrame(tick);}requestAnimationFrame(tick);});}
skip.addEventListener('click',()=>state.finishTyping?.());
function validate(data,round){if(!data||data.source!=='engine'||data.round!==round||typeof data.content!=='string'||data.content.trim().length<80)throw Error('Servisten gelen gerçek motor yanıtı doğrulanamadı.');if(round===3){if(data.complete!==true||data.question!==null||!['GO','RED','CONDITIONAL','INSUFFICIENT_EVIDENCE'].includes(data.decision))throw Error('Final tur karar sözleşmesi hatalı.');let wc=data.content.trim().split(/\s+/).length;if(wc<880||wc>1120)throw Error('Final raporu uzunluk sınırına uymuyor.');}else{if(data.complete!==false||!data.question||typeof data.question.text!=='string'||!Array.isArray(data.question.options)||data.question.options.length<2||data.question.options.length>4)throw Error('Kritik soru şeması doğrulanamadı.');}return data;}
async function post(path, payload) {
  if (window.InversionAutonomousEngine) {
    // Statik hosting ve dış ağ dayanıklılığı: doğrudan otonom motoru veya fetch fallback kullan
    try {
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), 2500);
      const res = await fetch(path, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
        body: JSON.stringify(payload),
        signal: controller.signal
      });
      clearTimeout(timer);
      if (res.ok) {
        return await res.json();
      }
    } catch (_) {
      // Ağ hatası veya 404/503 durumunda kesintisiz otonom motora geç
    }
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
async function renderRound(data){const round=state.round;errorBox.hidden=true;updateSteps();const output=msg('ai',round===3?'INVERSIONCORE · STRATEJİK RAPOR':(round===1?'INVERSIONCORE · ANALİZ BAŞLADI':'INVERSIONCORE · DERİNLEŞTİRME'),undefined,round===3);await typewrite(data.content,output);if(round===3){const decisions={GO:'GO — KAPSAMLI VERİYLE İLERLE',RED:'RED — MEVCUT HALİYLE DUR',CONDITIONAL:'KOŞULLU — ÖNCE KANITI TAMAMLA',INSUFFICIENT_EVIDENCE:'VERİ YETERSİZ — HÜKÜM VERİLEMEZ'};const verdict=el('div','final-verdict',decisions[data.decision]||'VERİ YETERSİZ');output.parentElement.insertBefore(verdict,output);state.report=data.content;responsePanel.hidden=true;$('#threadActions').hidden=false;$('#threadHeading').textContent='Üçüncü tur: nihai değerlendirme';output.after(el('small','chat-endnote',`${data.content.trim().split(/\s+/).length} kelime · ${state.mode==='demo'?'Kurgusal senaryo':'Doğrulanmamış kullanıcı beyanlarıyla ön inceleme'}`));return;}
 $('#questionCount').textContent=round===1?'SORU 1 / 2':'SORU 2 / 2';$('#responseQuestion').textContent=data.question.text;answerText.value='';state.selected='';options.replaceChildren();data.question.options.forEach(label=>{const b=el('button','answer-choice',label);b.type='button';b.setAttribute('aria-pressed','false');b.addEventListener('click',()=>{state.selected=label;options.querySelectorAll('.answer-choice').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));});options.append(b);});responsePanel.hidden=false;
}
$('#submitDecision').addEventListener('click',async()=>{if(state.busy)return;const input=$('#decisionInput').value.trim();if(input.length<5){$('#decisionInput').focus();$('#decisionInput').setCustomValidity('Konuyu en az 5 karakterle açıklayın.');$('#decisionInput').reportValidity();$('#decisionInput').setCustomValidity('');return;}begin('live');const epoch=state.epoch;msg('user','SİZİN KONUNUZ',input);loading(true,'Konunuz analiz ediliyor ve sorular hazırlanıyor...');try{const data=validate(await post('/api/v1/analysis/start',{input}),1);if(epoch!==state.epoch)return;if(!data.session_id)throw Error('Analiz oturum bilgisi doğrulanamadı.');state.sessionId=data.session_id;loading(false);modePill.textContent='BEYANA DAYALI ÖN İNCELEME';await renderRound(data);}catch(e){if(epoch===state.epoch)error(e.message);}});
$('#openDemo').addEventListener('click',async()=>{if(state.busy)return;begin('demo');const epoch=state.epoch;msg('user','ÖRNEK / KURGUSAL DURUM','Yeni bir pazara girmek istiyoruz. Henüz ücretli pilot müşterimiz yok. Buna rağmen büyüme bütçemizi artırmayı düşünüyoruz.');loading(true,'Örnek görüşme hazırlanıyor...');await new Promise(r=>setTimeout(r,150));if(epoch!==state.epoch)return;loading(false);await renderRound({...window.IC_DEMO.round1,round:1,source:'demo'});});
$('#sendAnswer').addEventListener('click',async()=>{if(state.busy||state.round>=3)return;const own=escapeStr(answerText.value),selected=state.selected;if(!selected&&!own){answerText.focus();error('Bir cevap seçin veya kendi yanıtınızı yazın.');responsePanel.hidden=false;return;}errorBox.hidden=true;responsePanel.hidden=true;msg('user','SİZİN CEVABINIZ',[selected,own].filter(Boolean).join(' — '));state.round++;updateSteps();$('#threadHeading').textContent=state.round===3?'Sonuç: söz artık kanıtta.':'Şimdi daha zor soruyu soruyorum.';loading(true,state.round===3?'Yanıtlarınıza göre kişiselleştirilmiş rapor hazırlanıyor...':'Yanıtınız değerlendiriliyor...');const epoch=state.epoch;try{let result;if(state.mode==='demo'){await new Promise(r=>setTimeout(r,120));result={...(state.round===2?window.IC_DEMO.round2:window.IC_DEMO.round3),source:'demo',round:state.round,decision:state.round===3?'CONDITIONAL':null};}else{result=validate(await post('/api/v1/analysis/answer',{session_id:state.sessionId,selected:selected||null,free_text:own||null}),state.round);if(result.session_id!==state.sessionId)throw Error('Analiz oturumu uyuşmazlığı.');}if(epoch!==state.epoch)return;loading(false);await renderRound(result);}catch(e){if(epoch===state.epoch)error(e.message);}});
$('#resetConversation').addEventListener('click',()=>{reset();$('#decisionInput').focus();host.scrollIntoView({behavior:reduceMotion?'instant':'smooth',block:'start'});});
$('#copyReport').addEventListener('click',async()=>{if(!state.report)return;try{await navigator.clipboard.writeText(state.report);$('#copyReport').textContent='Kopyalandı ✓';}catch{error('Tarayıcı kopyalama izni vermedi. Metni seçerek kopyalayabilirsiniz.');}});
$('#printReport').addEventListener('click',()=>window.print());
})();

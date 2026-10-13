'use strict';
(()=>{
 const $=s=>document.querySelector(s);
 const nav=$('#primaryNav'),toggle=$('.menu-toggle');
 toggle.addEventListener('click',()=>{let isOpen=nav.classList.toggle('opened');toggle.setAttribute('aria-expanded',String(isOpen));});
 document.querySelectorAll('#primaryNav a').forEach(a=>a.addEventListener('click',()=>{nav.classList.remove('opened');toggle.setAttribute('aria-expanded','false');}));
 const input=$('#decisionInput'),counter=$('#charCounter');input.addEventListener('input',()=>counter.textContent=`${input.value.length} / 4000`);
 document.querySelectorAll('[data-example]').forEach(b=>b.addEventListener('click',()=>{input.value=b.dataset.example;input.dispatchEvent(new Event('input'));input.focus();document.querySelector('#workbench').scrollIntoView({behavior:'smooth',block:'center'});}));
 $('#uploadBtn').addEventListener('click',()=>{$('#uploadNotice').textContent='Belge aktarımı doğrulanmadığı için şu anda etkin değil. Metinle devam edebilirsiniz.';});
 $('#year').textContent=new Date().getFullYear();
})();

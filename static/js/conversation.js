/* LLM conversation UI. Only the server can supply answers, evidence and context tokens. */
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let config = null, stateToken = null, draftToken = null, report = null;
  let accessCode = '', busy = false, controller = null, epoch = 0, turns = [];
  let selected = null, objectURL = null, currentDraft = null, lastTrigger = null;
  const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const icon = name => `<svg aria-hidden="true"><use href="#i-${name}"/></svg>`;
  const announce = text => { $('global-status').textContent = text; };

  async function api(path, options = {}) {
    const response = await fetch('/api/v2' + path, {credentials:'same-origin', ...options,
      headers: {...(options.headers || {}), ...(accessCode ? {'X-ResultScope-Access':accessCode} : {})}});
    const data = await response.json().catch(() => ({}));
    if (!response.ok) { const error = new Error(data.message || 'The request could not be completed. Please try again.'); error.code = data.code; throw error; }
    return data;
  }
  const post = (path, data, options = {}) => api(path, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data), ...options});
  function animate(node) {
    if (!reduced.matches && window.gsap) gsap.from(node, {opacity:0, y:12, duration:.38, ease:'power2.out', clearProps:'all'});
  }
  function openDialog(id, trigger) {
    lastTrigger = trigger || document.activeElement;
    $('sidebar').classList.remove('mobile-open'); $('mobile-menu').setAttribute('aria-expanded','false');
    const dialog = $(id); if (!dialog.open) dialog.showModal();
    if (id === 'tour-dialog') { const player = $('intro-player'); if (reduced.matches && player.ready) player.seek(11.8); }
  }
  $('intro-player').addEventListener('ready',()=>{if(reduced.matches) $('intro-player').seek(11.8);});
  function closeDialog(dialog) { dialog.close(); lastTrigger?.focus?.({preventScroll:true}); }
  document.querySelectorAll('[data-open]').forEach(b => b.addEventListener('click', () => openDialog(b.dataset.open,b)));
  document.querySelectorAll('[data-close]').forEach(b => b.addEventListener('click', () => closeDialog(b.closest('dialog'))));
  document.querySelectorAll('dialog').forEach(dialog => {
    dialog.addEventListener('click', event => { if(event.target === dialog) { const r=dialog.getBoundingClientRect(); if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom) closeDialog(dialog); } });
    dialog.addEventListener('close', () => { if(dialog.id==='tour-dialog') $('intro-player').pause?.(); });
  });
  $('mobile-menu').addEventListener('click', () => { const open=$('sidebar').classList.toggle('mobile-open'); $('mobile-menu').setAttribute('aria-expanded',String(open)); });
  document.addEventListener('pointerdown', event => { if(!$('sidebar').contains(event.target) && !$('mobile-menu').contains(event.target)) { $('sidebar').classList.remove('mobile-open'); $('mobile-menu').setAttribute('aria-expanded','false'); } });
  document.addEventListener('keydown', event => { if(event.key==='Escape') { $('sidebar').classList.remove('mobile-open'); $('mobile-menu').setAttribute('aria-expanded','false'); } });
  $('nav-chat').addEventListener('click', () => { $('sidebar').classList.remove('mobile-open'); $('message-input').focus(); });

  function setBusy(value) {
    busy=value; $('send-button').hidden=value; $('stop-button').hidden=!value;
    $('message-input').readOnly=value; $('attach-button').disabled=value;
    $('confirm-report').disabled=value; $('new-chat').disabled=value;
    document.querySelectorAll('[data-prompt],.answer-followups button').forEach(b=>b.disabled=value);
  }
  function startThread() {
    $('welcome').hidden=true; $('suggestion-area').hidden=true; $('welcome-footer').hidden=true;
    $('conversation-thread').hidden=false; document.body.classList.add('has-conversation');
  }
  function addUser(message) {
    const node=document.createElement('article'); node.className='turn user-turn';
    const bubble=document.createElement('div'); bubble.className='user-bubble'; bubble.textContent=message; bubble.dir='auto'; node.append(bubble);
    $('conversation-thread').append(node); animate(node); return node;
  }
  function assistantNode() {
    const node=document.createElement('article'); node.className='turn assistant-turn';
    node.innerHTML='<div class="assistant-header"><img src="/static/img/mark.svg" alt="">ResultScope</div><div class="assistant-content"></div>';
    $('conversation-thread').append(node); animate(node); return node;
  }
  function scrollToTurn(node) { node.scrollIntoView({behavior:reduced.matches?'auto':'smooth',block:'start'}); }
  function renderMarkdown(text, sources) {
    const holder=document.createElement('div'); holder.className='answer-prose';holder.dir='auto';
    holder.innerHTML=DOMPurify.sanitize(marked.parse(text),{ALLOWED_TAGS:['p','strong','em','ul','ol','li','code','pre','blockquote','h2','h3','h4','table','thead','tbody','tr','td','th','br','hr'],ALLOWED_ATTR:[]});
    const map=new Map(sources.map(s=>[s.id,s]));
    const walker=document.createTreeWalker(holder,NodeFilter.SHOW_TEXT); const nodes=[];
    while(walker.nextNode()) nodes.push(walker.currentNode);
    for(const node of nodes) {
      const matches=[...node.textContent.matchAll(/\[([a-z0-9][a-z0-9_-]+)\]/g)]; if(!matches.length) continue;
      const fragment=document.createDocumentFragment(); let cursor=0;
      for(const match of matches) {
        fragment.append(document.createTextNode(node.textContent.slice(cursor,match.index)));
        const source=map.get(match[1]);
        if(source && /^https:\/\//.test(source.url)) { const a=document.createElement('a'); a.href=source.url;a.target='_blank';a.rel='noopener noreferrer';a.textContent=String(sources.indexOf(source)+1);a.title=source.title;a.setAttribute('aria-label','Source: '+source.title);fragment.append(a); }
        else fragment.append(document.createTextNode(match[0]));
        cursor=match.index+match[0].length;
      }
      fragment.append(document.createTextNode(node.textContent.slice(cursor))); node.replaceWith(fragment);
    }
    return holder;
  }
  function renderAnswer(node,data) {
    const box=node.querySelector('.assistant-content');box.replaceChildren(renderMarkdown(data.reply,data.sources||[]));
    if(data.observations?.length) {
      const values=document.createElement('div');values.className='observation-list';
      for(const row of data.observations) {const card=document.createElement('div');card.className='observation';card.innerHTML=`<strong>${escape(row.name)}</strong><div class="obs-value">${escape(row.value)} <small>${escape(row.unit)}</small></div><span class="obs-status ${escape(row.status)}">${escape(row.status==='within'?'Within supplied range':row.status==='unknown'?'Range status unknown':row.status==='high'?'Above supplied range':'Below supplied range')}</span><div class="obs-range">Report range: ${escape(row.reference||'Not supplied')}</div>`;values.append(card);}box.append(values);
    }
    if(data.sources?.length) { const links=document.createElement('div');links.className='answer-source-list';for(const s of data.sources){if(!/^https:\/\//.test(s.url))continue;const a=document.createElement('a');a.href=s.url;a.target='_blank';a.rel='noopener noreferrer';a.innerHTML=icon('book')+escape(s.title);links.append(a);}box.append(links); }
    if(data.followups?.length) {const next=document.createElement('div');next.className='answer-followups';data.followups.forEach(prompt=>{const b=document.createElement('button');b.textContent=prompt+' ↗';b.dir='auto';b.addEventListener('click',()=>send(prompt));next.append(b);});box.append(next);}
    const foot=document.createElement('div');foot.className='answer-foot';
    const note=document.createElement('span');note.textContent='Sources linked · Safety checked';
    const copy=document.createElement('button');copy.textContent='Copy answer';copy.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(data.reply);copy.textContent='Copied';}catch{copy.textContent='Copy unavailable';}});
    foot.append(note,copy);box.append(foot);$('export-chat').disabled=false;
  }
  function renderError(node,error,message) {
    const box=node.querySelector('.assistant-content');box.replaceChildren();const errorBox=document.createElement('div');errorBox.className='error-answer';
    const p=document.createElement('div');p.textContent=error.message;errorBox.append(p);const actions=document.createElement('div');actions.className='error-actions';
    const retry=document.createElement('button');retry.textContent='Try again';retry.addEventListener('click',()=>{if(!busy){node.remove();send(message,false);}});
    const settings=document.createElement('button');settings.textContent='Connection settings';settings.addEventListener('click',()=>openDialog('settings-dialog',settings));actions.append(retry,settings);errorBox.append(actions);box.append(errorBox);
  }
  async function consumeStream(response,onEvent) {
    const reader=response.body.getReader(), decoder=new TextDecoder();let buffer='';
    try {while(true){const {value,done}=await reader.read();buffer+=decoder.decode(value||new Uint8Array(),{stream:!done});let boundary;while((boundary=buffer.indexOf('\n\n'))>=0){const frame=buffer.slice(0,boundary);buffer=buffer.slice(boundary+2);let type='message',parts=[];frame.split('\n').forEach(line=>{if(line.startsWith('event:'))type=line.slice(6).trim();if(line.startsWith('data:'))parts.push(line.slice(5).trimStart());});if(parts.length)onEvent(type,JSON.parse(parts.join('\n')));}if(done)break;}}
    finally {reader.releaseLock();}
  }
  async function send(raw,addBubble=true) {
    const message=raw.trim(); if(!message||busy)return;
    const run=++epoch;controller=new AbortController();setBusy(true);announce('');startThread();
    if(addBubble) {addUser(message);turns.push({role:'user',content:message});}
    $('conversation-title').textContent=message.length>36?message.slice(0,36)+'…':message;
    $('message-input').value='';$('message-input').style.height='';
    const node=assistantNode();const box=node.querySelector('.assistant-content');box.innerHTML='<div class="thinking"><span></span><span class="thinking-label">Connecting to ResultScope</span></div>';scrollToTurn(node);
    let received=false;
    try {
      await sessionReady;
      const response=await fetch('/api/v2/chat/stream',{method:'POST',credentials:'same-origin',signal:controller.signal,headers:{'Content-Type':'application/json',...(accessCode?{'X-ResultScope-Access':accessCode}:{})},body:JSON.stringify({message,state_token:stateToken})});
      if(!response.ok){const data=await response.json().catch(()=>({}));const err=new Error(data.message||'The conversation is unavailable.');err.code=data.code;throw err;}
      await consumeStream(response,(kind,data)=>{if(run!==epoch)return;if(kind==='status'){const label=box.querySelector('.thinking-label');if(label)label.textContent=data.message;}else if(kind==='answer'){received=true;stateToken=data.state_token;turns.push({role:'assistant',content:data.reply,sources:data.sources});renderAnswer(node,data);}else if(kind==='error'){received=true;renderError(node,data,message);}});
      if(!received && run===epoch)throw new Error('The connection ended before an answer was verified. Please try again.');
    } catch(error) {
      if(run!==epoch)return;
      if(error.name==='AbortError'){box.textContent='Stopped. No unverified answer was added to the conversation.';}
      else renderError(node,error,message);
    } finally {if(run===epoch){setBusy(false);controller=null;$('message-input').focus({preventScroll:true});}}
  }
  $('chat-form').addEventListener('submit',event=>{event.preventDefault();send($('message-input').value);});
  $('message-input').addEventListener('keydown',event=>{if(event.key==='Enter'&&!event.shiftKey&&!event.isComposing){event.preventDefault();send(event.currentTarget.value);}});
  $('message-input').addEventListener('input',()=>{const el=$('message-input');el.style.height='auto';el.style.height=Math.min(200,el.scrollHeight)+'px';});
  document.querySelectorAll('[data-prompt]').forEach(b=>b.addEventListener('click',()=>send(b.dataset.prompt)));
  $('stop-button').addEventListener('click',()=>controller?.abort());

  async function reset() {
    controller?.abort();epoch++;setBusy(false);await post('/reset',{});stateToken=null;draftToken=null;report=null;turns=[];selected=null;currentDraft=null;
    if(objectURL)URL.revokeObjectURL(objectURL);objectURL=null;
    $('conversation-thread').replaceChildren();$('conversation-thread').hidden=true;$('welcome').hidden=false;$('suggestion-area').hidden=false;$('welcome-footer').hidden=false;document.body.classList.remove('has-conversation');
    $('context-chip').hidden=true;$('report-toggle').hidden=true;$('export-chat').disabled=true;$('message-input').value='';$('conversation-title').textContent='New conversation';$('image-input').value='';announce('');$('message-input').focus();window.scrollTo({top:0,behavior:'auto'});
  }
  $('new-chat').addEventListener('click',()=>{if(turns.length||report)openDialog('reset-dialog',$('new-chat'));else reset().catch(e=>announce(e.message));});
  $('confirm-reset').addEventListener('click',async()=>{try{await reset();closeDialog($('reset-dialog'));}catch(e){announce(e.message);}});
  $('export-chat').addEventListener('click',()=>{const text='# ResultScope conversation\n\nEducational conversation, not a diagnosis.\n\n'+turns.map(t=>`## ${t.role==='user'?'You':'ResultScope'}\n\n${t.content}${t.sources?.length?'\n\nSources\n'+t.sources.map(s=>`- [${s.title}](${s.url})`).join('\n'):''}`).join('\n\n');const url=URL.createObjectURL(new Blob([text],{type:'text/markdown;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download='ResultScope-conversation.md';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});

  function selectDocument(attachment) {
    if(busy)return;
    if(report){if($('demo-dialog').open)$('demo-dialog').close();openDialog('reset-dialog');return;}
    if(objectURL){URL.revokeObjectURL(objectURL);objectURL=null;}
    selected=attachment;draftToken=null;currentDraft=null;$('report-fields').replaceChildren();$('report-warnings').replaceChildren();$('confirm-report').hidden=true;$('read-report').hidden=false;$('read-report').disabled=false;$('read-report').textContent='Read with AI ↗';
    $('report-status').textContent='';$('report-info').textContent='The chatbot can read this document, then you can check what it found. Confirming a different report starts a fresh conversation.';
    $('report-kind').textContent=attachment.demo?'SYNTHETIC DEMONSTRATION':'YOUR DOCUMENT';$('report-heading').textContent=attachment.title;$('report-consent').checked=Boolean(attachment.demo);document.querySelector('.document-consent').hidden=false;
    const isPdf=attachment.file?.type==='application/pdf';
    const url=attachment.demo?attachment.image:(objectURL=URL.createObjectURL(attachment.file));
    $('report-image').hidden=isPdf;$('report-pdf').hidden=!isPdf;
    if(isPdf){$('report-pdf').src=url;$('report-image').removeAttribute('src');}else{$('report-image').src=url;$('report-pdf').removeAttribute('src');}
    $('report-download').href=attachment.demo?attachment.pdf:url;$('report-download').download=attachment.demo?attachment.id+'.pdf':attachment.file.name;
    if($('demo-dialog').open)$('demo-dialog').close();openDialog('report-dialog');
  }
  $('attach-button').addEventListener('click',()=>$('image-input').click());
  $('image-input').addEventListener('change',()=>{const file=$('image-input').files[0];if(!file)return;if(file.size>3*1024*1024){announce('Choose a PNG, JPEG or PDF smaller than 3 MB.');return;}if(!['image/png','image/jpeg','application/pdf'].includes(file.type)){announce('Choose a PNG, JPEG or PDF report.');return;}selectDocument({file,title:'Your laboratory report',demo:false});});
  function fieldEditor(row,index) {
    const el=document.createElement('div');el.className='report-field';el.dataset.index=index;
    el.innerHTML=`<label class="field-name">Test name<input data-key="name" maxlength="100" value="${escape(row.name)}" required></label><div class="field-row"><label>Result<input data-key="value" maxlength="150" value="${escape(row.value)}"></label><label>Unit<input data-key="unit" maxlength="60" value="${escape(row.unit)}"></label></div><div class="field-row"><label>Printed reference range<input data-key="reference" maxlength="150" value="${escape(row.reference)}"></label><label>Printed flag<input data-key="printed_flag" maxlength="25" value="${escape(row.printed_flag)}"></label></div><button class="remove-row" type="button">Remove this row</button>`;
    el.querySelector('.remove-row').addEventListener('click',()=>el.remove());return el;
  }
  $('read-report').addEventListener('click',async()=>{
    if(busy){controller?.abort();return;}if(!selected)return;if(!$('report-consent').checked){$('report-status').textContent='Please confirm that you are allowed to share this document.';return;}
    const run=++epoch;controller=new AbortController();setBusy(true);$('read-report').textContent='Cancel reading';$('report-status').textContent='Reading the document with AI. Nothing is confirmed yet.';
    try{
      await sessionReady;let result;
      if(selected.demo)result=await post('/demos/'+encodeURIComponent(selected.id)+'/read',{}, {signal:controller.signal});
      else{const body=new FormData();body.append('file',selected.file);result=await api('/reports/read',{method:'POST',body,signal:controller.signal});}
      if(run!==epoch)return;draftToken=result.draft_token;currentDraft=result.report;
      $('report-fields').replaceChildren(...currentDraft.fields.map(fieldEditor));
      $('report-warnings').textContent=currentDraft.warnings.join(' ');$('report-warnings').className='report-warnings';$('confirm-report').hidden=false;$('read-report').hidden=true;
      $('report-status').textContent='Check every value, unit, interval and flag against the document. Correct any reading errors before continuing.';
    }catch(error){if(run===epoch)$('report-status').textContent=error.name==='AbortError'?'Reading stopped.':error.message;}
    finally{if(run===epoch){setBusy(false);controller=null;$('read-report').textContent='Read with AI ↗';}}
  });
  $('confirm-report').addEventListener('click',async()=>{
    if(busy||!draftToken)return;const fields=[...$('report-fields').querySelectorAll('.report-field')].map(row=>Object.fromEntries([...row.querySelectorAll('[data-key]')].map(input=>[input.dataset.key,input.value.trim()])));
    if(!fields.length||fields.some(f=>!f.name)){ $('report-status').textContent='Keep at least one row and give every test a name.';return; }
    setBusy(true);
    try{const data=await post('/reports/confirm',{draft_token:draftToken,state_token:stateToken,fields});stateToken=data.state_token;report=data.report;turns=[];$('conversation-thread').replaceChildren();draftToken=null;
      $('context-chip').hidden=false;$('context-name').textContent=(report.data_class==='synthetic'?'Sample report':'Confirmed report')+' · '+report.fields.length+' values';$('report-toggle').hidden=false;
      closeDialog($('report-dialog'));startThread();const node=assistantNode();node.querySelector('.assistant-content').textContent='Your confirmed report is ready. What would you like to understand?';
      $('message-input').placeholder='What would you like to understand about this report?';$('message-input').focus();$('export-chat').disabled=true;
    }catch(error){$('report-status').textContent=error.message;}finally{setBusy(false);}
  });
  function viewReport(){if(!report)return;$('report-fields').replaceChildren(...report.fields.map((row,index)=>{const el=fieldEditor(row,index);el.querySelectorAll('input').forEach(x=>x.readOnly=true);el.querySelector('button').remove();return el;}));$('report-status').textContent='These values were confirmed by you. Start a new conversation to attach a different report.';$('confirm-report').hidden=true;$('read-report').hidden=true;document.querySelector('.document-consent').hidden=true;openDialog('report-dialog');}
  $('context-view').addEventListener('click',viewReport);$('report-toggle').addEventListener('click',viewReport);

  function renderConnection(data) {
    config=data;$('connection-label').textContent=data.mode==='connected'?'Models configured':'Connect AI';document.querySelector('.connection').classList.toggle('connected',data.mode==='connected');
    $('connection-details').innerHTML=`<div class="connection-row"><span>Conversation model</span><strong>${escape(data.model)}</strong></div><div class="connection-row"><span>Report reader</span><strong>${data.vision?escape(data.vision_model):'Not connected'}</strong></div><div class="connection-row"><span>References</span><strong>${escape(data.references)} source records</strong></div><div class="connection-row"><span>Search</span><strong>${data.retrieval==='hybrid'?'Lexical + semantic':'Lexical · semantic connection optional'}</strong></div>`;
    if(data.missing.length){const ul=document.createElement('ul');ul.className='setup-list';data.missing.forEach(x=>{const li=document.createElement('li');li.textContent=x;ul.append(li);});$('connection-details').append(ul);}
    else{const p=document.createElement('p');p.className='dialog-note';p.textContent='Configuration is present. This is not a live provider test; send a message to test the connection.';$('connection-details').append(p);}
    $('access-form').hidden=!data.needs_access_code;
  }
  $('access-form').addEventListener('submit',event=>{event.preventDefault();accessCode=$('access-code').value;$('access-code').value='';$('access-status').textContent='Access code set for this tab. It will be checked with your next message.';});
  const sessionReady=post('/session',{});
  sessionReady.catch(error=>announce(error.message));
  api('/config').then(renderConnection).catch(error=>{$('connection-label').textContent='Unavailable';announce(error.message);});
  api('/demos').then(data=>{for(const demo of data.reports){const card=document.createElement('article');card.className='demo-card';card.innerHTML=`<button class="demo-thumbnail" aria-label="Open ${escape(demo.title)}"><img loading="lazy" src="${escape(demo.image)}" alt="Synthetic ${escape(demo.title)} report"></button><div class="demo-card-copy"><span class="demo-type">TEMPLATE ${escape(demo.template)} · SYNTHETIC</span><h3>${escape(demo.title)}</h3><p>${escape(demo.description)}</p><button>Open report ↗</button></div>`;card.querySelectorAll('button').forEach(b=>b.addEventListener('click',()=>selectDocument({...demo,demo:true})));$('demo-grid').append(card);}}).catch(error=>{$('demo-grid').textContent=error.message;});
  api('/references').then(data=>{const grouped=new Map();data.records.forEach(r=>{if(!grouped.has(r.url))grouped.set(r.url,r);});for(const ref of grouped.values()){const row=document.createElement('div');row.className='reference-item';const div=document.createElement('div'),a=document.createElement('a'),small=document.createElement('small'),kind=document.createElement('span');a.href=ref.url;a.target='_blank';a.rel='noopener noreferrer';a.textContent=ref.title+' ↗';small.textContent=ref.publisher+' · Checked '+ref.reviewed_at;kind.className='source-type';kind.textContent=ref.data_class==='public_education'?'Patient education':'Laboratory manual';div.append(a,small);row.append(div,kind);$('reference-list').append(row);}}).catch(error=>{$('reference-list').textContent=error.message;});
  if(window.gsap&&!reduced.matches){gsap.from('.welcome-copy > *',{opacity:0,y:18,duration:.7,stagger:.1,ease:'power2.out',clearProps:'all'});gsap.from('.welcome-art',{opacity:0,y:14,duration:1,ease:'power2.out',clearProps:'all'});gsap.from('.suggestion-area,.composer-dock',{opacity:0,y:12,duration:.65,stagger:.12,delay:.2,ease:'power2.out',clearProps:'all'});}
})();

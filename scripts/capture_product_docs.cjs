/* Documentation capture only. Requires an isolated loopback app started with
   PROVIDER_NETWORK_ENABLED=false and synthetic data. Mock stages are visibly labeled.
   Node Playwright is tooling, not an application dependency. */
const fs=require('fs'),path=require('path'),crypto=require('crypto'),childProcess=require('child_process');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const root=path.resolve(__dirname,'..');
const output=path.join(root,'docs/assets/screenshots');fs.mkdirSync(output,{recursive:true});
const base=process.env.DOCS_BASE_URL;
if(!base)throw Error('DOCS_BASE_URL is required; never capture against the owner server on port 8765.');
if(!['127.0.0.1','localhost'].includes(new URL(base).hostname))throw Error('Loopback capture only');
if(process.env.DOCS_OFFLINE_CONFIRMED!=='true')throw Error('Start an isolated server with provider network disabled, then set DOCS_OFFLINE_CONFIRMED=true.');
const candidateSha=childProcess.execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).trim();
const applicationRoots=['main.py','config.py','routers','services','templates','static'];
const applicationFiles=[];
const isGeneratedDocumentation=file=>{const relative=path.relative(root,file).replaceAll(path.sep,'/');return relative==='static/docs/user-guide.html';};
for(const entry of applicationRoots){const full=path.join(root,entry);if(fs.statSync(full).isDirectory()){const pending=[full];while(pending.length){const current=pending.pop();for(const child of fs.readdirSync(current,{withFileTypes:true})){const childPath=path.join(current,child.name);if(child.isDirectory())pending.push(childPath);else if(!isGeneratedDocumentation(childPath))applicationFiles.push(childPath);}}}else if(!isGeneratedDocumentation(full))applicationFiles.push(full);}
applicationFiles.sort();
const sourceFingerprint=crypto.createHash('sha256');
for(const file of applicationFiles){sourceFingerprint.update(path.relative(root,file).replaceAll(path.sep,'/'));sourceFingerprint.update('\0');sourceFingerprint.update(fs.readFileSync(file));sourceFingerprint.update('\0');}
const applicationFilesDirty=childProcess.execFileSync('git',['status','--porcelain','--',...applicationRoots],{cwd:root,encoding:'utf8'}).split(/\r?\n/).some(line=>line && !line.includes('static/docs/user-guide.html'));
const receipts=[];let networkBlocks=[],errors=[];const interactions={};
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:{}),args:['--no-sandbox','--disable-dev-shm-usage','--disable-gpu']});
 const context=await browser.newContext({viewport:{width:1440,height:1000},deviceScaleFactor:1,reducedMotion:'reduce'});
 await context.route('**/*',r=>{if(new URL(r.request().url()).origin!==new URL(base).origin){networkBlocks.push(r.request().url().split('?')[0]);return r.abort();}return r.continue();});
 const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));
 async function badge(label){await page.evaluate(label=>{document.querySelectorAll('.capture-label').forEach(e=>e.remove());for(const target of [document.querySelector('.workspace-shell'),document.querySelector('.drawer-header')].filter(Boolean)){const e=document.createElement('div');e.className='capture-label';e.textContent=label;e.style.cssText='padding:7px 14px;background:#fff5e8;color:#70431c;font:12px sans-serif;line-height:1.4;text-align:center;border-bottom:1px solid #d9bd91;flex-basis:100%';target.prepend(e);}document.querySelector('.drawer-header')?.style.setProperty('flex-wrap','wrap');},label);}
 async function snap(name,mode,region='workspace'){
  await page.evaluate(()=>document.fonts.ready);
  if(region==='workspace') await page.locator('#workspace').screenshot({path:path.join(output,name+'.png')});
  else {await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:path.join(output,name+'.png'),fullPage:region==='page'});}
  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
  receipts.push({file:name+'.png',route:new URL(page.url()).pathname,mode,viewport:page.viewportSize(),region,horizontal_overflow:overflow});
 }
 await page.goto(base);await page.locator('#message-input').waitFor();await snap('00-landing-desktop','real landing, approved purple atmosphere','viewport');await snap('01-workspace-desktop','real UI, provider offline');
 await page.locator('#sample-button').click();await snap('02-example-loaded','real example control, synthetic values');
 // Use a synthetic business query so the offline provider guard is exercised
 // without making a provider call or relying on an approved education corpus.
 await page.locator('#message-input').fill('What is the CBC price?');
 await page.locator('#send-button').click();await page.locator('#error-banner:not(.hidden)').waitFor();if(/API_KEY|\.env|Vercel/.test(await page.locator('#error-banner').innerText()))throw Error('Technical configuration leaked into user error');
 if(/will appear|Preparing your explanation/.test(await page.locator('.narrative-zone').innerText()))throw Error('Terminal error retained pending copy');
 await snap('07-provider-unavailable','real offline/missing-configuration route');
 await page.locator('#new-chat-button').click();await page.locator('#starter:not(.hidden)').waitFor();
 await page.locator('#message-input').fill('Write a fantasy story about a dragon');await page.locator('#send-button').click();await page.locator('.is-local').waitFor();await snap('11-scope-boundary','real deterministic scope refusal');
 await page.goto(base);await page.locator('[data-open-report]').first().click();
 const extraction={extraction_id:'11111111-1111-4111-8111-111111111111',status:'review_required',revision:1,document_type:'synthetic laboratory report',warnings:['Documentation mock; no OCR provider was called.'],fields:[{field_id:'hb',marker:'Hb',raw_value:'10.8',unit:'g/dL',reference_low:'12',reference_high:'16',reference_range_raw:'12-16'},{field_id:'mcv',marker:'MCV',raw_value:'72',unit:'fL',reference_low:'80',reference_high:'100',reference_range_raw:'80-100'},{field_id:'ferritin',marker:'Ferritin',raw_value:'7',unit:'ng/mL',reference_low:'15',reference_high:'150',reference_range_raw:'15-150'}]};
 await page.route('**/api/v1/images/extract',r=>r.fulfill({json:extraction}));
 await page.route('**/api/v1/images/*/confirm',async r=>{const sent=r.request().postDataJSON();extraction.fields=sent.fields;extraction.status='confirmed';extraction.revision++;await r.fulfill({json:extraction});});
 await page.locator('#image-input').setInputFiles(path.join(root,'docs/assets/capture-fixtures/synthetic-report.png'));
 await page.locator('.image-field').first().waitFor();await badge('Documentation capture · Mock OCR response · Synthetic report · No provider call');await snap('03-review-extracted-values','mock OCR response in real review UI');
 await page.locator('.image-field input').first().fill('10.8');await page.getByRole('button',{name:'Confirm values',exact:true}).click();await page.getByText('Confirmed extracted values',{exact:true}).waitFor();await snap('04-confirmed-values','mock confirmation endpoint in real UI');interactions.confirmed_fields_readonly=await page.locator('.image-field input').first().getAttribute('readonly')!==null;await page.locator('#close-report').click();
 const meta=JSON.parse(fs.readFileSync(path.join(root,'docs/assets/capture-fixtures/analysis.json')));
 let followup=false;
 await page.route('**/api/v1/chat/stream',async r=>{
 const answer=followup?'### Keep the same context\nThis follow-up uses the synthetic report above. The supplied reference range is the basis of the comparison. Ask the laboratory which range applies to your report.\n\nDocumentation demonstration only.':'### Reading the supplied values\nThe synthetic example contains haemoglobin **10.8 g/dL** against a supplied range of **12–16 g/dL**. This value is below that supplied range.\n\nThe MCV and ferritin values are also below the example ranges. These comparisons do not establish a diagnosis.\n\n### What to check next\nConfirm the values, units and ranges against the original report. Your laboratory or clinician can explain how your circumstances affect interpretation.\n\n**Documentation demonstration only:** this explanation is a fixed mock response, not a live AI answer.';
 const events=[{analysis_meta:meta},{response_meta:{citations:[{source_id:'DOC-DEMO',title:'Synthetic report — documentation fixture',organisation:'Demonstration data only',page:1,source_url:base+'/static/docs/synthetic-report.png',data_class:'synthetic',license:'Project-authored synthetic example; not a clinical source'}]}},{delta:answer},{done:true}];
 await r.fulfill({status:200,contentType:'text/event-stream',body:events.map(e=>'data: '+JSON.stringify(e)+'\n\n').join('')});followup=true;
 });
 await page.locator('#send-button').click();await page.locator('.is-complete').waitFor();await badge('Documentation capture · Fixed mock answer · Synthetic values · No live LLM validation');const aligned=await page.evaluate(()=>{const band=document.querySelector('.range-within').getBoundingClientRect();const a=document.querySelector('.range-labels span:first-child').getBoundingClientRect(),b=document.querySelector('.range-labels span:last-child').getBoundingClientRect();return Math.abs((a.left+a.right)/2-band.left)<2&&Math.abs((b.left+b.right)/2-band.right)<2;});if(!aligned)throw Error('Range labels do not align with reference band');
 await snap('05-result-summary','mock SSE payload in real result UI');
 await page.locator('.citation-disclosure summary').click();await snap('06-source-details','synthetic source rendering, not live grounding evidence');
 await page.locator('#followup-input').fill('Why does that matter?');await page.locator('#followup-send').click();await page.locator('.analysis-response.is-complete').nth(1).waitFor();await snap('12-follow-up','mock SSE follow-up in real UI');
 await page.goto(base+'/admin/login');await snap('08-admin-login','real local-demo login page','page');await page.locator('#admin-password').fill('1234');await page.locator('#admin-login-form button').click();await page.waitForURL('**/admin/settings');await page.locator('.provider-card').first().waitFor();await snap('09-provider-settings','real settings read; empty synthetic capture environment; no save or provider test','page');
 await page.setViewportSize({width:390,height:844});await page.goto(base);await snap('14-landing-mobile','real landing at 390px','viewport');await snap('10-workspace-mobile','real UI, 390px viewport');
 await page.locator('[data-open-report]').first().click();
 interactions.mobile_modal=await page.locator('#document-drawer').getAttribute('aria-modal')==='true';
 await page.keyboard.press('Shift+Tab');interactions.mobile_focus_trap=await page.evaluate(()=>document.activeElement.id==='return-to-chat');
 await page.keyboard.press('Escape');interactions.escape_closes=await page.locator('#document-drawer').evaluate(e=>e.hidden);interactions.focus_restored=await page.locator('[data-open-report]').first().evaluate(e=>e===document.activeElement);
 await page.locator('[data-open-report]').first().click();
 extraction.status='review_required';await page.locator('#image-input').setInputFiles(path.join(root,'docs/assets/capture-fixtures/synthetic-report.png'));await page.locator('.image-field').first().waitFor();
 await badge('Documentation mock · Synthetic OCR values');await snap('15-report-mobile','mock OCR, mobile document dialog','viewport');
 await page.route('**/api/v1/images/*',r=>r.fulfill({json:{status:'deleted'}}));
 await page.getByRole('button',{name:'Discard image',exact:true}).click();await page.waitForFunction(()=>document.getElementById('file-summary').hidden);interactions.discard_clears_preview=await page.locator('#image-review').evaluate(e=>!e.children.length);await page.locator('#close-report').click();
 followup=false;await page.locator('#sample-button').click();await page.locator('#send-button').click();await page.locator('.is-complete').waitFor();await badge('Documentation mock · Synthetic values');await snap('13-result-mobile','mock SSE result, 390px viewport');
 await page.locator('[data-open-report]').first().click();interactions.active_report_locked=await page.locator('#image-input').isDisabled();await page.locator('#close-report').click();
 await page.emulateMedia({reducedMotion:'no-preference'});await page.setViewportSize({width:1440,height:1000});await page.goto(base);await page.evaluate(()=>scrollTo(0,300));await page.waitForTimeout(80);
 interactions.native_scroll_motion=await page.evaluate(()=>Boolean(window.__timelines?.['resultscope-entry'])&&Number(getComputedStyle(document.querySelector('.hero-content')).opacity)<1);
 await page.emulateMedia({reducedMotion:'reduce'});await page.waitForFunction(()=>!window.__timelines?.['resultscope-entry']);interactions.reduced_motion_static=await page.evaluate(()=>!window.__timelines?.['resultscope-entry']&&getComputedStyle(document.querySelector('.hero-content')).opacity==='1');
 await page.route('**/static/vendor/gsap.min.js',r=>r.abort());await page.goto(base);await page.getByRole('button',{name:'Try an example',exact:true}).click();interactions.missing_gsap_fallback=await page.locator('#message-input').inputValue().then(v=>v.includes('Hb'));
 for(const [name,passed] of Object.entries(interactions))if(!passed)throw Error('Interaction failed: '+name);
 for(const name of ['mark','logo']){await page.setViewportSize({width:name==='mark'?256:740,height:name==='mark'?256:136});await page.goto(base+'/static/img/'+name+'.svg');await page.screenshot({path:path.join(root,'static/img/'+name+'.png'),omitBackground:true});}
 fs.writeFileSync(path.join(output,'CAPTURE_MANIFEST.json'),JSON.stringify({description:'Real redesigned pages; all mocked stages labeled explicitly. Not live provider or clinical validation.',capture_time_utc:new Date().toISOString(),candidate_sha:candidateSha,application_files_dirty:applicationFilesDirty,application_source_fingerprint:sourceFingerprint.digest('hex'),interactions,screenshots:receipts,browser_external_requests_blocked:networkBlocks,js_errors:errors},null,2));
 console.log(JSON.stringify({captures:receipts.length,interactions,overflow:receipts.filter(r=>r.horizontal_overflow),js_errors:errors,blocked_external_requests:networkBlocks.length}));
 await browser.close();
 if(errors.length||networkBlocks.length||receipts.some(r=>r.horizontal_overflow))throw Error('Capture acceptance failed; inspect CAPTURE_MANIFEST.json');
})().catch(e=>{console.error(e);process.exit(1);});

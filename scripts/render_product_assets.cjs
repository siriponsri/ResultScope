/* Optional local documentation renderer, never a provider client. */
const fs=require('fs'),path=require('path'),{pathToFileURL}=require('url');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
(async()=>{
 const root=path.resolve(__dirname,'..'),errors=[];
 const browser=await chromium.launch({headless:true,...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:{}),args:['--no-sandbox','--disable-gpu']});
 const page=await browser.newPage();page.on('pageerror',e=>errors.push(e.message));
 await page.route('**/*',r=>['file:','data:'].includes(new URL(r.request().url()).protocol)?r.continue():r.abort());
 for(const [name,height] of [['architecture',850],['message-flow',870]]){
  await page.setViewportSize({width:1200,height});await page.goto(pathToFileURL(path.join(root,'docs/assets/diagrams',name+'.html')).href);
  await page.screenshot({path:path.join(root,'docs/assets/diagrams',name+'.png')});
 }
 await page.setViewportSize({width:1920,height:1080});await page.goto(pathToFileURL(path.join(root,'docs/media/resultscope-intro/index.html')).href);await page.evaluate(()=>document.fonts.ready);
 const motion=await page.evaluate(()=>{const tl=window.__timelines['resultscope-intro'];const duration=tl.duration();const checks=[0,4,8,12].map(t=>{tl.seek(t);return {time:t,seek:tl.time()};});return {duration,checks,images:[...document.images].every(i=>i.complete&&i.naturalWidth>0)};});
 if(motion.duration!==12||!motion.images||errors.length)throw Error(JSON.stringify({motion,errors}));
 await page.locator('#intro').screenshot({path:path.join(root,'docs/media/intro-poster.png')});
 await page.goto(pathToFileURL(path.join(root,'static/docs/user-guide.html')).href);await page.evaluate(()=>document.fonts.ready);
 await page.pdf({path:path.join(root,'docs/user/ResultScope_User_Guide.pdf'),format:'A4',printBackground:true,preferCSSPageSize:true});
 fs.writeFileSync(path.join(root,'docs/evidence/DOCUMENT_RENDER.json'),JSON.stringify({motion,errors,pdf:'ResultScope_User_Guide.pdf',note:'Browser seek/render only; Hyperframes CLI and MP4 export NOT_RUN.'},null,2));
 await browser.close();console.log(JSON.stringify({motion,errors}));
})().catch(e=>{console.error(e);process.exit(1)});

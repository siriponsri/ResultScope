/* Optional document tooling: export the reviewed self-contained guide to A4 PDF. */
const path=require('path'),{pathToFileURL}=require('url');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
(async()=>{
 const root=path.resolve(__dirname,'..');
 const browser=await chromium.launch({headless:true,...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:{})});
 try {
  const page=await browser.newPage();
  await page.goto(pathToFileURL(path.join(root,'static/docs/user-guide.html')).href);
  await page.evaluate(()=>document.fonts.ready);
  await page.pdf({path:path.join(root,'docs/user/ResultScope_User_Guide.pdf'),format:'A4',printBackground:true,preferCSSPageSize:true});
  console.log('PDF exported. Visually review pages before replacing a reviewed guide.');
 } finally {await browser.close();}
})().catch(e=>{console.error(e.message);process.exit(1);});

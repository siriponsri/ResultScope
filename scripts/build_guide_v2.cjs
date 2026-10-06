/* Render the current Markdown guide into a self-hosted HTML guide. */
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..'),marked=require(path.join(root,'static/vendor/marked.min.js'));
const source=fs.readFileSync(path.join(root,'docs/user/USER_GUIDE.md'),'utf8');
const html=`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ResultScope 2.0 | User guide</title><style>
@font-face{font-family:Plex;src:url('../fonts/plex-400.woff2')}@font-face{font-family:Plex;src:url('../fonts/plex-600.woff2');font-weight:600}
*{box-sizing:border-box}body{font:16px/1.7 Plex,Arial,sans-serif;color:#21172f;background:#f8f8ff;margin:0}main{max-width:850px;margin:50px auto;padding:40px 50px;background:white;border:1px solid #ded8e9;border-radius:14px}a{color:#4b0082}h1{font-size:40px;line-height:1.15;letter-spacing:-1px;font-weight:600}h2{font-size:24px;line-height:1.3;margin:35px 0 15px;color:#4b0082;font-weight:600}p{margin:0 0 15px}strong{font-weight:600}.back{display:inline-block;text-decoration:none;font-size:13px;margin-bottom:25px}.edition{font-size:12px;color:#61586f;border-top:1px solid #ded8e9;padding-top:20px;margin-top:35px}
@media(max-width:600px){main{margin:0;padding:28px 22px;border:0;border-radius:0}h1{font-size:32px}}
@page{size:A4;margin:18mm 19mm 20mm} @media print{body{font-size:11pt;background:white;line-height:1.55}main{border:0;margin:0;padding:0;max-width:none}h1{font-size:29pt}h2{font-size:17pt;break-after:avoid}p{orphans:3;widows:3}.back{display:none}.edition{font-size:9pt}a{color:#4b0082;text-decoration:none}}
</style></head><body><main><a class="back" href="/">← Back to the conversation</a>${marked.parse(source)}<p class="edition">ResultScope 2.0 · Updated 2026-10-05 · Educational prototype</p></main></body></html>`;
fs.writeFileSync(path.join(root,'static/docs/user-guide.html'),html);
console.log('Built static/docs/user-guide.html from current Markdown.');

"""Regenerate English Markdown and standalone HTML from the labelled capture set.
Run after reviewing any new screenshots; PDF export is a separate step.
"""
from pathlib import Path
import base64,html
R=Path(__file__).resolve().parents[1];S=R/'docs/assets/screenshots'
steps=[
('Enter the workspace','00-landing-desktop','Open ResultScope. Choose Open workspace or scroll to reach the conversation on the same page. Try an example loads synthetic text without submitting it. The desktop transition follows your normal scroll; reduced-motion preferences and mobile layouts use a static transition.','Actual landing page; no provider call.'),
('Start in the workspace','01-workspace-desktop','In the conversation, select Your result or question. You do not need an administrator account to ask a laboratory question. Type in English or Thai. Include the value, unit and the reference range printed on your report.','Real application page; captured with provider network disabled.'),
('Try a synthetic example','02-example-loaded','Select Load example to fill the input. Review the text before choosing Send. Loading an example does not call a provider; submitting may do so only when live access has been explicitly enabled by an operator.','Real example control. Example values and ranges are synthetic.'),
('Upload and review a report','03-review-extracted-values','Choose Attach report or Report to open the document drawer. Select a de-identified JPEG or PNG up to 3 MB. The drawer shows the selected filename and an image preview; reading an image requires an authorized OCR provider. Check each extracted value, unit and range against the image. Edit incorrect fields. If extraction is unavailable, type the values instead. PDF upload is not supported.','Real review UI with a MOCK OCR response. No OCR API call was made.'),
('Confirm the fields','04-confirmed-values','Choose Confirm values only after checking every field. The review panel changes to Confirmed extracted values. The confirmed fields become read-only and the question box is filled with a request to explain them. On desktop choose Return to conversation; on mobile the panel closes after confirmation. Choose Send when ready. Before sending, Discard image clears the pending attachment. After sending, start a new analysis to replace a report.','Real confirmation controls with a MOCK confirmation endpoint. This capture does not validate extraction accuracy.'),
('Read the result summary','05-result-summary','Read the extracted values before the explanation. Select a value to inspect its supplied reference range. Below range, Above range, Within range and Range unknown are comparison states, not diagnoses. Read the explanation together with missing context.','Real result UI with fixed MOCK SSE answer and synthetic values. No live LLM validation.'),
('Inspect the source','06-source-details','Expand Sources used when it is available. Check the document title, organization, version and page before opening its link. Calculation details explains the deterministic rules. A displayed source is not proof of clinical applicability to your case.','Source disclosure is demonstrated with a synthetic documentation source. This is not a live grounded-answer result.'),
('Ask a follow-up or start again','12-follow-up','Use Ask a follow-up to ask about the same results. Choose Start a new analysis before using a different report. Wait for the reset to succeed. Do not mix reports from different people in one conversation.','Real follow-up controls with MOCK SSE payloads. Session behavior is additionally covered by existing offline tests.'),
('Recover when a provider is unavailable','07-provider-unavailable','Read the error and keep the values you entered. Provider access may be disabled, unconfigured or out of budget. Ask the operator to resolve the specific condition. Do not repeatedly retry an exhausted budget. Never paste API keys into the question box.','Actual offline/missing-configuration route; no browser response mock.'),
('Recognize the scope boundary','11-scope-boundary','ResultScope handles laboratory information. An unrelated question is refused locally. Ask a laboratory question instead. The same boundary excludes diagnosis, prescribing and treatment changes.','Actual deterministic scope refusal; no LLM call.'),
('Administrator sign in','08-admin-login','Operators can open Administrator from the footer. The login is available only in explicit local-demo mode. The demonstration credentials admin / 1234 must never be used online. Ordinary users do not need this account.','Actual local-demo login page. The captured environment contains no private credentials.'),
('Configure providers privately','09-provider-settings','Choose the provider and model, then enter a replacement API key only in the password field. Leave it blank to retain an existing key. Save settings stores the configuration without a provider call. Test with mock does not verify live connectivity. SystemOne remains shadow-only.','Actual settings page with unconfigured slots. No Save, provider test or live request was performed during capture.'),
('Use the mobile workspace','10-workspace-mobile','On a phone, choose Open workspace or scroll down from the landing page. Type in the question box and select Send. Report opens a full-screen document panel. Use Close report panel or Return to conversation to return. The user guide remains available in the top navigation.','Actual application at a 390px viewport. Human usability testing has not yet been performed.'),
('Review a report on a phone','15-report-mobile','The report panel fills the screen. Scroll inside it to inspect the image and all extracted fields, then select Confirm values. Keyboard focus stays inside the panel while it is open. Escape or Close report panel returns to the control that opened it. A different report requires a new analysis.','Actual mobile document panel with a MOCK OCR response. Values and report are synthetic.')]
intro='''# ResultScope Laboratory Assistant - user guide

A practical walkthrough of the redesigned application. The screenshots show the
shipped UI. Mocked OCR and generated-answer stages are visibly labeled in the
images and captions; they are not live provider or clinical validation evidence.

For local setup, read [Local setup](../operations/LOCAL_SETUP.md). For provider
configuration, read [Administrator guide](../operations/ADMIN_GUIDE.md).

'''
md=intro
parts=[]
for n,(title,file,body,note) in enumerate(steps,1):
 md+=f'## {n}. {title}\n\n{body}\n\n![{title}](../assets/screenshots/{file}.png)\n\n*{note}*\n\n'
 data=base64.b64encode((S/(file+'.png')).read_bytes()).decode()
 parts.append(f'<section class="step"><div class="step-heading"><span>Step {n:02}</span><h2>{html.escape(title)}</h2></div><p>{html.escape(body)}</p><figure><img src="data:image/png;base64,{data}" alt="{html.escape(title)}"><figcaption>{html.escape(note)}</figcaption></figure></section>')
md+='''## Limits and privacy

ResultScope provides educational laboratory information. It does not diagnose,
prescribe or choose treatment. The supplied report range is authoritative for
its comparison; public reference documents may describe different methods or
populations. Missing evidence should lead to a clear limitation or abstention.

Use synthetic or de-identified reports in demonstrations. Local processing of a
page does not mean every future provider action stays on the device. Live-enabled
LLM and OCR requests send relevant content to the selected provider. Read the
operator's data policy before using real information.

No PDF OCR, HIS/pharmacy connector, billing, clinical certification or production
readiness is claimed by this manual. See [Readiness](../operations/READINESS.md).
'''
(R/'docs/user/USER_GUIDE.md').write_text(md)
font=base64.b64encode((R/'static/fonts/plex-400.woff2').read_bytes()).decode()
css='''@font-face{font-family:Plex;src:url(data:font/woff2;base64,FONT)}*{box-sizing:border-box}body{margin:0;background:#f8f8ff;color:#21172f;font:16px/1.65 Plex,Arial,sans-serif}.wrap{max-width:1040px;margin:auto;padding:48px 28px}header{padding:40px 0 52px;border-bottom:1px solid #ded8e9}h1{font-size:44px;line-height:1.15;letter-spacing:-.03em;font-weight:600;max-width:800px}h2{font-size:27px;line-height:1.25;letter-spacing:-.02em}.lead{font-size:19px;max-width:70ch;color:#61586f}a{color:#4b0082}.meta{font-size:13px;color:#61586f}.step{padding-top:44px;margin-bottom:32px;break-before:page}.step-heading>span{font-size:13px;color:#4b0082}.step h2{margin:6px 0 16px}.step>p{max-width:82ch}figure{margin:24px 0}img{display:block;max-width:100%;height:auto;margin:auto;border:1px solid #ded8e9}figcaption{margin-top:12px;font-size:13px;color:#61586f}.limit{padding:28px;background:#f1ebfc;border-radius:8px}footer{font-size:12px;margin-top:50px;color:#61586f}@media(max-width:600px){.wrap{padding:24px 18px}h1{font-size:32px}h2{font-size:24px}}@media print{@page{size:A4;margin:17mm}body{background:white;font-size:11pt}.wrap{padding:0}header{padding:14mm 0;height:245mm}h1{font-size:36pt}.lead{font-size:14pt}.step{padding:0;margin:0;break-before:page;break-after:page}.step h2{font-size:22pt}.step>p{font-size:11pt}figure{margin:5mm 0}figure img{max-height:170mm;max-width:100%;width:auto;object-fit:contain;border:1px solid #ded8e9}figcaption{font-size:9pt}.limit{break-before:page}nav{display:none}footer{font-size:9pt}}'''.replace('FONT',font)
page='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ResultScope Laboratory Assistant - User guide</title><style>'+css+'</style></head><body><main class="wrap"><header><nav><a href="/">Return to workspace</a></nav><p class="meta">ResultScope Laboratory Assistant · Product guide · 4 October 2026</p><h1>From a laboratory report to a clearer conversation.</h1><p class="lead">A page-by-page guide to asking a question, reviewing extracted values and exploring the explanation.</p><p>This guide captures the real redesigned interface. Mocked stages are marked on the screenshots and in their captions. It is not a record of live provider or clinical validation.</p></header>'+''.join(parts)+'<section id="limitations" class="limit"><h2>Clear limits, throughout the workflow.</h2><p>Laboratory information only. No diagnosis, prescriptions or treatment changes. Public reference ranges do not replace the ranges on your report.</p><p>Use de-identified or synthetic reports for demonstrations. When live access is enabled, relevant content may be sent to the configured provider. Ask the operator about the data policy before using real information.</p><p>PDF OCR, HIS and pharmacy integration, durable cloud settings and production release are not established by this guide.</p></section><footer>ResultScope Laboratory Assistant · Education and product demonstration · Screenshot provenance: CAPTURE_MANIFEST.json</footer></main></body></html>'
(R/'static/docs/user-guide.html').write_text(page)
print('Manual:',len(steps),'steps;',len(page),'bytes')

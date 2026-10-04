import sys,subprocess,time,json,os,argparse
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
out=args.output;out.mkdir(parents=True,exist_ok=True)
server=subprocess.Popen([sys.executable,str(root/'preview.py'),'--port','8765'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
try:
 print(server.stdout.readline().decode().strip())
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
  results=[]
  for width,height,name in [(1440,1000,'desktop'),(390,844,'mobile')]:
   page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   page.goto('http://127.0.0.1:8765/');page.wait_for_function("document.getElementById('meta').textContent.includes('17')")
   page.evaluate('document.fonts.ready');page.screenshot(path=str(out/(name+'-home.png')),full_page=True)
   page.get_by_role('button',name='ALT',exact=True).click();page.wait_for_selector('.record');assert page.locator('.record').count()==4
   page.locator('.record details summary').first.click();page.screenshot(path=str(out/(name+'-results.png')),full_page=True)
   assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
   page.get_by_role('button',name='ล้างการค้นหา').click();assert page.locator('#query').input_value()==''
   page.locator('#query').fill('เฟอร์ริติน');page.locator('#query').press('Enter');page.wait_for_selector('.guidance');assert page.locator('.guidance').count()==2
   page.locator('.guidance summary').first.click();page.screenshot(path=str(out/(name+'-guidance.png')),full_page=True)
   assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
   page.locator('#query').focus();page.keyboard.press('Tab');assert page.locator('#search-button').evaluate('e=>e===document.activeElement')
   page.locator('#query').fill('MRI');page.locator('#search-button').click();page.wait_for_selector('#empty',state='visible')
   page.route('**/api/search',lambda route:route.fulfill(status=503,body='unavailable'))
   page.locator('#query').fill('ALT');page.locator('#search-button').click();page.wait_for_selector('#status.error')
   assert page.locator('#search-button').is_enabled();assert not errors
   results.append({'viewport':f'{width}x{height}','home':'PASS','search_source_details':'PASS','reset':'PASS','guideline_citation':'PASS','keyboard_enter_tab':'PASS','no_hit':'PASS','server_error_recovery':'PASS','horizontal_overflow':False,'page_errors':errors})
   page.close()
  browser.close()
  (out/'browser-check.json').write_text(json.dumps({'scope':'isolated reference preview only; no OCR, chat or live model tested','results':results},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  print(json.dumps(results))
finally:
 server.terminate();server.wait(timeout=5)

from pathlib import Path
import asyncio, subprocess, time, json, shutil, sys, traceback
from playwright.async_api import async_playwright

root=Path(__file__).resolve().parents[1]
qa=root/'qa';qa.mkdir(exist_ok=True)
routes=['index.html','resume.html','cover-letter.html','interview-brief.html','120-day-plan.html','work-address-review.html']
viewports=[('desktop',1440,900),('laptop',1280,800),('tablet',768,1024),('mobile',390,844)]
browser_path=next((shutil.which(x) for x in ['google-chrome-stable','google-chrome','chromium','chromium-browser'] if shutil.which(x)),None)
if not browser_path: raise SystemExit('No installed browser available')
server=subprocess.Popen([sys.executable,'-m','http.server','8765','--bind','127.0.0.1'],cwd=root,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
time.sleep(1.5)
results=[]
async def run():
  async with async_playwright() as p:
    browser=await p.chromium.launch(headless=True,executable_path=browser_path,args=['--no-sandbox','--disable-dev-shm-usage'])
    for label,w,h in viewports:
      page=await browser.new_page(viewport={'width':w,'height':h},device_scale_factor=1)
      page_errors=[]; console_errors=[]
      page.on('pageerror',lambda e: page_errors.append(str(e)))
      page.on('console',lambda m: console_errors.append(m.text) if m.type=='error' else None)
      for route in routes:
        response=await page.goto(f'http://127.0.0.1:8765/{route}',wait_until='networkidle')
        data=await page.evaluate('''() => ({
          scrollWidth: document.documentElement.scrollWidth,
          clientWidth: document.documentElement.clientWidth,
          title: document.title,
          images:[...document.images].map(i=>({src:i.getAttribute('src'),complete:i.complete,naturalWidth:i.naturalWidth}))
        })''')
        broken=[i for i in data['images'] if i['complete'] and i['naturalWidth']==0]
        results.append({'viewport':label,'route':route,'status':response.status if response else None,'overflow':data['scrollWidth']>data['clientWidth']+1,'broken_images':broken,'title':data['title']})
        if route=='index.html':
          await page.wait_for_function("document.querySelector('#work-coordinate')?.dataset.phase === 'resolved'",timeout=4500)
          structural=await page.evaluate("""() => ({sources:document.querySelectorAll('.work-source').length,coordinates:document.querySelectorAll('.address-coordinate').length,packets:document.querySelectorAll('.resolution-packet').length,returns:document.querySelectorAll('.learning-return').length,legacy:document.querySelectorAll('.gantry,.crosshead,.scan-line').length,active:document.querySelector('.work-source[aria-current=\"true\"]')?.dataset.source||''})""")
          results.append({'viewport':label,'animation-structure':structural,'passed':structural=={'sources':4,'coordinates':5,'packets':1,'returns':1,'legacy':0,'active':'knowledge'}})
          await page.screenshot(path=str(qa/f'homepage-{label}.png'),full_page=True)
          cases=[('output','Operational Output Verification'),('live','Live SOP Verification'),('motion','Time & Motion AI')]
          for key,expected in cases:
            await page.locator(f'[data-scenario="{key}"]').click()
            got=(await page.locator('#surface-value').inner_text()).strip()
            active=await page.locator('.work-source[aria-current="true"]').get_attribute('data-source')
            phase=await page.locator('#work-coordinate').get_attribute('data-phase')
            results.append({'viewport':label,'interaction':key,'passed':got==expected and active==key and phase=='resolving','actual':got,'active':active,'phase':phase})
          await page.locator('#reset-scenario').click()
          got=(await page.locator('#surface-value').inner_text()).strip()
          results.append({'viewport':label,'interaction':'reset','passed':got=='Knowledge Capture & Transfer','actual':got})
          await page.locator('.scenario-tab[data-scenario="knowledge"]').focus()
          await page.keyboard.press('ArrowRight')
          got=(await page.locator('#surface-value').inner_text()).strip()
          results.append({'viewport':label,'interaction':'keyboard','passed':got=='Operational Output Verification','actual':got})
      results.append({'viewport':label,'browser_errors':page_errors+console_errors,'passed':not(page_errors+console_errors)})
      await page.close()
    reduced=await browser.new_page(viewport={'width':1280,'height':800},reduced_motion='reduce')
    await reduced.goto('http://127.0.0.1:8765/index.html',wait_until='networkidle')
    reduced_state=await reduced.evaluate("""() => ({phase:document.querySelector('#work-coordinate')?.dataset.phase||'',packet:getComputedStyle(document.querySelector('.resolution-packet')).display,coordinates:document.querySelectorAll('.address-coordinate').length})""")
    results.append({'viewport':'reduced-motion','state':reduced_state,'passed':reduced_state=={'phase':'resolved','packet':'none','coordinates':5}})
    await reduced.close();await browser.close()
runtime_error=None
try:
  asyncio.run(run())
except Exception as exc:
  runtime_error={'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()}
finally:
  server.terminate()
  try: server.wait(timeout=5)
  except subprocess.TimeoutExpired: server.kill()
errors=[]
for r in results:
  if r.get('status',200) and r.get('status',200)>=400: errors.append(r)
  if r.get('overflow') or r.get('broken_images') or r.get('passed') is False: errors.append(r)
if runtime_error: errors.append({'runtime_error':runtime_error})
record={'status':'passed' if not errors else 'failed','browser':browser_path,'checks':len(results),'errors':errors,'results':results}
(qa/'browser-qa.json').write_text(json.dumps(record,indent=2))
print(json.dumps({'status':record['status'],'checks':len(results),'errors':errors},indent=2))
if errors: raise SystemExit(1)

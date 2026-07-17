from pathlib import Path
import asyncio, subprocess, time, json, shutil, sys
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
          await page.screenshot(path=str(qa/f'homepage-{label}.png'),full_page=True)
          cases=[('output','Operational Output Verification'),('live','Live SOP Verification'),('motion','Time & Motion AI')]
          for key,expected in cases:
            await page.locator(f'[data-scenario="{key}"]').click()
            got=(await page.locator('#surface-value').inner_text()).strip()
            results.append({'viewport':label,'interaction':key,'passed':got==expected,'actual':got})
          await page.locator('#reset-scenario').click()
          got=(await page.locator('#surface-value').inner_text()).strip()
          results.append({'viewport':label,'interaction':'reset','passed':got=='Knowledge Capture & Transfer','actual':got})
          await page.locator('[data-scenario="knowledge"]').focus()
          await page.keyboard.press('ArrowRight')
          got=(await page.locator('#surface-value').inner_text()).strip()
          results.append({'viewport':label,'interaction':'keyboard','passed':got=='Operational Output Verification','actual':got})
      results.append({'viewport':label,'browser_errors':page_errors+console_errors,'passed':not(page_errors+console_errors)})
      await page.close()
    reduced=await browser.new_page(viewport={'width':1280,'height':800},reduced_motion='reduce')
    await reduced.goto('http://127.0.0.1:8765/index.html',wait_until='networkidle')
    duration=await reduced.locator('.crosshead').evaluate('el=>getComputedStyle(el).animationDuration')
    results.append({'viewport':'reduced-motion','animation_duration':duration,'passed':duration in ['0.001ms','0.001s','0s','1e-06s']})
    await reduced.close();await browser.close()
asyncio.run(run())
server.terminate();server.wait(timeout=5)
errors=[]
for r in results:
  if r.get('status',200) and r.get('status',200)>=400: errors.append(r)
  if r.get('overflow') or r.get('broken_images') or r.get('passed') is False: errors.append(r)
record={'status':'passed' if not errors else 'failed','browser':browser_path,'checks':len(results),'errors':errors,'results':results}
(qa/'browser-qa.json').write_text(json.dumps(record,indent=2))
print(json.dumps({'status':record['status'],'checks':len(results),'errors':errors},indent=2))
if errors: raise SystemExit(1)

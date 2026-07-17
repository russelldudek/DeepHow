from pathlib import Path
import asyncio, json, shutil
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
BROWSER = next((shutil.which(x) for x in ['google-chrome-stable','google-chrome','chromium','chromium-browser'] if shutil.which(x)), None)
if not BROWSER:
    raise SystemExit('No installed browser available')

def inline_document() -> str:
    html = (ROOT / 'index.html').read_text()
    css = (ROOT / 'styles.css').read_text() + '\n' + (ROOT / 'resolver.css').read_text() + '\n' + (ROOT / 'brand-tokens.css').read_text()
    js = (ROOT / 'app.js').read_text()
    html = html.replace('<link rel="stylesheet" href="styles.css">', f'<style>{css}</style>').replace('<link rel="stylesheet" href="resolver.css">', '')
    html = html.replace('<script defer src="app.js"></script>', '')
    html = html.replace('src="assets/brand/deephow-logo.svg"', 'src="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%22134%22 height=%2228%22></svg>"')
    html = html.replace('</body>', f'<script>{js}</script></body>')
    return html

GEOMETRY_JS = '''() => {
  const active = document.querySelector('.work-source[aria-current="true"]');
  const signal = document.querySelector('.signal-line');
  const learning = document.querySelector('.return-line');
  if (!active || !signal || !learning) return {difference:999, signalLabel:'', returnLabel:'', activeState:''};
  const a = active.getBoundingClientRect();
  const s = signal.getBoundingClientRect();
  const r = learning.getBoundingClientRect();
  const activeCenter = a.top + a.height / 2;
  const loopCenter = ((s.top + s.height / 2) + (r.top + r.height / 2)) / 2;
  return {
    difference: Math.abs(activeCenter - loopCenter),
    signalLabel: document.querySelector('.signal-label')?.textContent.trim() || '',
    returnLabel: document.querySelector('.return-label')?.textContent.trim() || '',
    activeState: active.querySelector('.source-state')?.textContent.trim() || ''
  };
}'''

async def evaluate_page(reduced_motion='no-preference'):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, executable_path=BROWSER, args=['--no-sandbox','--disable-dev-shm-usage'])
        page = await browser.new_page(viewport={'width': 1280, 'height': 800}, reduced_motion=reduced_motion)
        errors=[]
        page.on('pageerror', lambda e: errors.append(str(e)))
        await page.set_content(inline_document(), wait_until='load')
        await page.wait_for_timeout(60)
        structural = await page.evaluate('''() => ({
          sources: document.querySelectorAll('.work-source').length,
          coordinates: document.querySelectorAll('.address-coordinate').length,
          packets: document.querySelectorAll('.resolution-packet').length,
          returns: document.querySelectorAll('.learning-return').length,
          legacy: document.querySelectorAll('.gantry,.crosshead,.scan-line').length,
          phase: document.querySelector('#work-coordinate')?.dataset.phase || '',
          active: document.querySelector('.work-source[aria-current="true"]')?.dataset.source || ''
        })''')
        initial_geometry = await page.evaluate(GEOMETRY_JS)
        initial_phase = structural['phase']
        await page.wait_for_timeout(3400)
        settled = await page.evaluate('''() => ({
          phase: document.querySelector('#work-coordinate')?.dataset.phase || '',
          active: document.querySelector('.work-source[aria-current="true"]')?.dataset.source || '',
          state: document.querySelector('#stage-state')?.textContent.trim() || ''
        })''')
        await page.locator('button[data-scenario="output"]').click()
        replay = await page.evaluate('''() => ({
          phase: document.querySelector('#work-coordinate')?.dataset.phase || '',
          active: document.querySelector('.work-source[aria-current="true"]')?.dataset.source || '',
          iterations: document.querySelector('.resolution-packet') ? getComputedStyle(document.querySelector('.resolution-packet')).animationIterationCount : '',
          uri: document.querySelector('#address-tag')?.textContent.trim() || ''
        })''')
        replay_geometry = await page.evaluate(GEOMETRY_JS)
        await page.wait_for_timeout(3400)
        replay_settled = await page.evaluate('''() => ({
          phase: document.querySelector('#work-coordinate')?.dataset.phase || '',
          active: document.querySelector('.work-source[aria-current="true"]')?.dataset.source || '',
          state: document.querySelector('#stage-state')?.textContent.trim() || ''
        })''')
        await page.screenshot(path=str(ROOT/'qa'/'resolver-contract.png'), full_page=False)
        await browser.close()
        return {'errors':errors,'structural':structural,'initial_phase':initial_phase,'initial_geometry':initial_geometry,'settled':settled,'replay':replay,'replay_geometry':replay_geometry,'replay_settled':replay_settled}

async def main():
    normal = await evaluate_page()
    reduced = await evaluate_page('reduce')
    checks = {
      'no_browser_errors': not normal['errors'] and not reduced['errors'],
      'four_product_sources': normal['structural']['sources'] == 4,
      'five_address_coordinates': normal['structural']['coordinates'] == 5,
      'one_signal_packet': normal['structural']['packets'] == 1,
      'one_learning_return': normal['structural']['returns'] == 1,
      'legacy_gantry_removed': normal['structural']['legacy'] == 0,
      'initial_sequence_starts': normal['initial_phase'] == 'resolving',
      'initial_loop_aligned_to_kct': normal['initial_geometry']['difference'] <= 3 and normal['initial_geometry']['signalLabel'] == 'KCT to platform' and normal['initial_geometry']['returnLabel'] == 'Learning back to KCT' and normal['initial_geometry']['activeState'] == 'Active loop',
      'initial_sequence_settles': normal['settled']['phase'] == 'resolved' and normal['settled']['active'] == 'knowledge',
      'scenario_replays_once': normal['replay']['phase'] == 'resolving' and normal['replay']['active'] == 'output' and normal['replay']['iterations'] == '1',
      'output_loop_moves_to_oov': normal['replay_geometry']['difference'] <= 3 and normal['replay_geometry']['signalLabel'] == 'OOV to platform' and normal['replay_geometry']['returnLabel'] == 'Learning back to OOV' and normal['replay_geometry']['activeState'] == 'Active loop',
      'scenario_settles': normal['replay_settled']['phase'] == 'resolved' and normal['replay_settled']['active'] == 'output',
      'scenario_updates_uri': normal['replay']['uri'] == 'WORK://OUTPUT-VERIFY/LOT-118/V1',
      'reduced_motion_resolves_immediately': reduced['initial_phase'] == 'resolved' and reduced['structural']['active'] == 'knowledge',
    }
    record={'status':'passed' if all(checks.values()) else 'failed','checks':checks,'normal':normal,'reduced':reduced}
    (ROOT/'qa'/'animation-contract.json').write_text(json.dumps(record,indent=2))
    print(json.dumps(record,indent=2))
    if record['status'] != 'passed':
        raise SystemExit(1)

asyncio.run(main())

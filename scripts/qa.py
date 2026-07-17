from pathlib import Path
from bs4 import BeautifulSoup
from pypdf import PdfReader
import json, sys
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'artifact-manifest.json').read_text())
errors=[]
required=manifest['routes']+manifest['styles']+manifest['scripts']+[x['pdf'] for x in manifest['documents']]+['assets/brand/deephow-logo.svg']
for p in required:
    q=root/p
    if not q.exists() or q.stat().st_size==0: errors.append(f'missing/empty {p}')
for d in manifest['documents']:
    reader=PdfReader(str(root/d['pdf']))
    if len(reader.pages)!=d['pages']: errors.append(f'page count {d["pdf"]}')
for route in manifest['routes']:
    soup=BeautifulSoup((root/route).read_text(),'html.parser')
    ids=[x.get('id') for x in soup.find_all(id=True)]
    if len(ids)!=len(set(ids)): errors.append(f'duplicate ids {route}')
    if not soup.title or not soup.title.string: errors.append(f'missing title {route}')
    for a in soup.find_all('a',href=True):
        h=a['href']
        if h.startswith(('http:','https:','mailto:','tel:','#')): continue
        path=h.split('#')[0]
        if path and not (root/path).exists(): errors.append(f'broken link {route} -> {h}')
# Scan public candidate-facing source and PDF text without placing protected internal labels verbatim in source.
public_files=[p for p in root.rglob('*') if p.is_file() and not any(part in {'.git','scripts','qa','.github'} for part in p.parts) and p.suffix.lower() in {'.html','.css','.js','.md','.json','.yml','.yaml'}]
all_text='\n'.join(p.read_text(errors='ignore') for p in public_files)
pdf_text='\n'.join(' '.join((pg.extract_text() or '') for pg in PdfReader(str(root/d['pdf'])).pages) for d in manifest['documents'])
for forbidden in ['role'+'forge','russelldudek/'+'DeepHow','public'+' repository']:
    if forbidden.lower() in (all_text+'\n'+pdf_text).lower(): errors.append(f'candidate-facing confidentiality failure')
# Contact and credential integrity.
for token in ['412.287.8640','russelldudek@gmail.com','linkedin.com/in/russelldudek','Pittsburgh']:
    if token not in (root/'resume.html').read_text(): errors.append(f'missing resume contact {token}')
resume_text=' '.join((p.extract_text() or '') for p in PdfReader(str(root/'docs/Russell-Dudek-DeepHow-Resume.pdf')).pages)
order=['Google AI Essentials','Food Safety Management Certification','IBM Enterprise Design Thinking Practitioner','Six Sigma Certification','OSHA 10']
pos=[resume_text.find(x) for x in order]
if any(x<0 for x in pos) or pos!=sorted(pos): errors.append('credential order failure')
record={'status':'passed' if not errors else 'failed','errors':errors,'pdf_pages':{d['pdf']:len(PdfReader(str(root/d['pdf'])).pages) for d in manifest['documents']},'scanned_public_files':len(public_files)}
(root/'qa/source-qa.json').write_text(json.dumps(record,indent=2))
print(json.dumps(record,indent=2))
if errors: sys.exit(1)

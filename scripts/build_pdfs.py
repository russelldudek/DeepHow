from pathlib import Path
from weasyprint import HTML
from pypdf import PdfReader
from PIL import Image
import subprocess, shutil, tempfile

root=Path(__file__).resolve().parents[1]
out=root/'docs'; out.mkdir(exist_ok=True)
qa=root/'qa'; qa.mkdir(exist_ok=True)
items=[
 ('resume.html','Russell-Dudek-DeepHow-Resume.pdf',2,'resume'),
 ('cover-letter.html','Russell-Dudek-DeepHow-Cover-Letter.pdf',1,'cover-letter'),
 ('interview-brief.html','Russell-Dudek-DeepHow-Interview-Thesis.pdf',4,None),
 ('120-day-plan.html','Russell-Dudek-DeepHow-120-Day-Plan.pdf',3,None),
 ('work-address-review.html','Russell-Dudek-DeepHow-Work-Address-Review.pdf',2,None),
]
render_record={}
for html,name,pages,render_slug in items:
    dest=out/name
    HTML(filename=str(root/html),base_url=str(root)).write_pdf(str(dest))
    reader=PdfReader(str(dest))
    actual=len(reader.pages)
    if actual!=pages:
        raise SystemExit(f'{name}: expected {pages}, got {actual}')
    text=' '.join((p.extract_text() or '') for p in reader.pages)
    if len(text)<700:
        raise SystemExit(f'{name}: suspiciously little extracted text ({len(text)})')
    with tempfile.TemporaryDirectory() as td:
        prefix=Path(td)/'page'
        subprocess.run(['pdftoppm','-png','-r','150',str(dest),str(prefix)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        ratios=[]
        for page_number,png in enumerate(sorted(Path(td).glob('page-*.png')),start=1):
            im=Image.open(png).convert('L')
            hist=im.histogram()
            nonwhite=sum(hist[:246])/(im.width*im.height)
            ratios.append(round(nonwhite,4))
            if render_slug:
                shutil.copy2(png,qa/f'{render_slug}-page-{page_number}.png')
        if len(ratios)!=pages or min(ratios)<0.025:
            raise SystemExit(f'{name}: rendered page appears blank or missing {ratios}')
        render_record[name]={'pages':actual,'nonwhite_ratios':ratios,'text_characters':len(text)}
(qa/'pdf-qa.json').write_text(__import__('json').dumps({'status':'passed','documents':render_record},indent=2))
print('PDF contracts and rendered-content checks passed')

# SPDX-License-Identifier: MIT
"""Complete font comparison using metadata-free, single-character source crops."""
from pathlib import Path
import json, math, subprocess, unicodedata as ud
from fontTools.ttLib import TTFont
from fontTools.pens.reportLabPen import ReportLabPen
from fontTools.pens.boundsPen import BoundsPen
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont as PDFTTFont

ROOT=Path(__file__).resolve().parents[1]
(ROOT/'specimens').mkdir(exist_ok=True)
OUT=ROOT/'specimens/Complete-Exemplar-Proof.pdf'
E=json.loads((ROOT/'source/exemplar-map.json').read_text())
styles=['Regular','Oblique','Bold','BoldOblique']
fonts={s:TTFont(ROOT/'fonts'/f'PrattNocturne-{s}.ttf') for s in styles}
sets={s:f.getGlyphSet() for s,f in fonts.items()}
cm=fonts['Regular'].getBestCmap()
order=list(fonts['Regular'].getGlyphOrder())
encoded=set(cm.values())
# One card per codepoint, plus every otherwise-unencoded glyph.
first=[ord(c) for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789']
codes=first+sorted(set(cm)-set(first))
items=[(cp,cm[cp]) for cp in codes]+[(None,g) for g in order if g not in encoded]
assert len({g for _,g in items})==len(order)
assert len([cp for cp,_ in items if cp is not None])==len(cm)
ui=subprocess.check_output(['fc-match','-f','%{file}','DejaVu Sans'],text=True)
pdfmetrics.registerFont(PDFTTFont('UI',ui))
c=canvas.Canvas(str(OUT),pagesize=(612,792),pageCompression=1)
c.setTitle('Pratt Nocturne 2.011 — complete character and exemplar proof')
c.setAuthor('Pratt Nocturne project')
def label(x,y,text,size=8,color='#39404a'):
 c.setFillColor(color);c.setFont('UI',size);c.drawString(x,y,text)
def wrap(text,width,size=8):
 words=text.split();lines=[];line=''
 for word in words:
  trial=(line+' '+word).strip()
  if pdfmetrics.stringWidth(trial,'UI',size)>width and line:lines.append(line);line=word
  else:line=trial
 if line:lines.append(line)
 return lines
def paragraph(x,y,text,width=550,size=10):
 for line in wrap(text,width,size):
  label(x,y,line,size);y-=size*1.5
 return y
def header(title,subtitle):
 label(28,762,title,15);label(28,742,subtitle,8)
def footer():
 label(28,17,'PRATT NOCTURNE 2.011  /  ORIGINAL SOURCE CROPS',7)
 label(551,17,str(c.getPageNumber()),8)
def crop(ev,x,y,w,h):
 c.drawImage(str(ROOT/'source/exemplars'/ev['image']),x,y,width=w,height=h,
             preserveAspectRatio=True,anchor='c')
def drawglyph(g,style,x,y,w=54,h=51):
 gs=sets[style];pen=BoundsPen(gs);gs[g].draw(pen)
 if pen.bounds is None:return False
 x0,y0,x1,y1=pen.bounds
 # Common scale, reduced only for unusually broad ligatures; vertical position shared.
 scale=min(.043,w/max(x1-x0,1),h/max(y1-y0,1))
 c.saveState();c.translate(x+(w-(x1-x0)*scale)/2-x0*scale,y+19)
 c.scale(scale,scale);c.setFillColor('#202834')
 path=c.beginPath();path.closePath=path.close;gs[g].draw(ReportLabPen(gs,path));c.drawPath(path,fill=1,stroke=0);c.restoreState()
 return True
def evidence(cp,g):
 ch=chr(cp) if cp is not None else ''
 if ch in E:return E[ch],('Case/mark uncertain' if E[ch]['uncertain'] else 'Direct exemplar')
 if ch:
  base=ud.normalize('NFD',ch)[0]
  if base!=ch and base in E:return E[base],f'Related base {base} only'
 if g.endswith('.readable'):return E['d'],'Derived from d; no direct form'
 if g in ['a.alt','e.alt','r.alt','D.alt']:return E[g[0]],'Related default form'
 if g.startswith('digit') and g[5] in E:return E[g[5]],'Related full-size digit'
 return None,'No direct exemplar'
header('Complete character / exemplar proof','426 encoded characters + 62 additional glyphs / all four styles')
y=697
for text in [
 'Every character encoded in version 2.011 has its own card. A final section includes all unencoded glyphs: stylistic alternates, small figures, mark helpers and the missing-character box.',
 'Each card shows Regular, Oblique, Bold and Bold Oblique from left to right (R, O, B, BO). These are actual vector outlines from the released fonts. Scale is consistent except for unusually wide glyphs; cropped source letters are independently enlarged to fit.',
 'Source crops come from the original letter and envelope. Direct exemplar means the same character construction is visible. Case/mark uncertain flags ambiguous evidence rather than treating the transcription as certain.',
 'Related base only shows a relevant unaccented letter, not evidence that the writer used that accented character. Related default form and related full-size digit likewise indicate design relationships, not exact exemplars.',
 'No direct exemplar means none was identified in the supplied handwriting. Printed return-address labels, stamps, postmarks and postal barcodes are excluded. Spaces and format controls have no visible ink; their advance widths are shown.',
 'Accents are drawn in isolation on their own cards. This is an outline inventory rather than a shaped-text specimen. Combining marks normally attach to another character when typed.',
 'Only individual character crops are included. Full source documents, source coordinates, names and addresses are omitted. The reproducible generator reads the sanitized assets in source/exemplars/.',
]:
 y=paragraph(28,y,text);y-=16
label(28,y-6,f'{len(E)} source assignments; ambiguous assignments are explicitly marked.',10)
footer();c.showPage()
for start in range(0,len(items),12):
 group=items[start:start+12]
 header('Character and exemplar inventory',f'Cards {start+1}–{min(start+12,len(items))} of {len(items)} / R · O · B · BO')
 c.bookmarkPage(f'cards{start+1}')
 c.addOutlineEntry(f'Cards {start+1}–{min(start+12,len(items))}',f'cards{start+1}',0)
 for i,(cp,g) in enumerate(group):
  x=28+(i%2)*282;top=722-(i//2)*113
  c.setStrokeColorRGB(.83,.84,.85);c.setLineWidth(.35);c.line(x,top-109,x+270,top-109)
  desc=ud.name(chr(cp),'UNNAMED') if cp is not None else g
  code=f'U+{cp:04X}' if cp is not None else 'GLYPH'
  title=f'{code}  {desc}'
  for j,line in enumerate(wrap(title,269,7)):label(x,top-j*9,line,7)
  for j,style in enumerate(styles):
   drawglyph(g,style,x+j*33,top-75,w=31,h=48)
   label(x+j*33+8,top-85,['R','O','B','BO'][j],6)
  ev,status=evidence(cp,g)
  if ev:
   crop(ev,x+158,top-80,95,57)
   label(x+143,top-20,status,6.5)
   loc=ev['source']+' / character crop'
   for j,line in enumerate(wrap(loc,128,6)):label(x+142,top-90-j*8,line,6)
  else:
   label(x+144,top-43,status,7)
   if cp is not None and (chr(cp).isspace() or ud.category(chr(cp))=='Cf'):
    label(x+144,top-58,'Invisible / spacing character',6)
  label(x,top-103,f'Advance {fonts["Regular"]["hmtx"][g][0]} / 1000 em',6,color='#69717a')
 footer();c.showPage()
c.save()
print(f'{OUT}: {len(items)} cards; {len(cm)} codepoints; {len(order)} distinct glyphs; {math.ceil(len(items)/12)+1} pages')

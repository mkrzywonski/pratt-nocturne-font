# SPDX-License-Identifier: MIT
from pathlib import Path
import subprocess, html, unicodedata
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont as PDFTTFont
ROOT=Path(__file__).resolve().parents[1]
(ROOT/'specimens').mkdir(exist_ok=True)
UI=subprocess.check_output(['fc-match','-f','%{file}','DejaVu Sans'],text=True)
styles=['Regular','Oblique','Bold','BoldOblique']
samples=[
 ('SIGNATURE FORMS','a e D r R q ? 0123456789'),
 ('LATIN LETTERS','ÀÁÂÃÄÅ Æ Ç ÈÉÊË Ð Ñ Ø Œ Þ ß ẞ'),
 ('ACCENTS','āăą ćčďđ ēėęě ğģ īįı ķ ł ńňŋ ő ř şșťț ůű'),
 ('LANGUAGE SAMPLES','Příliš žluťoučký kůň. Zażółć gęślą jaźń.'),
 ('LANGUAGE SAMPLES','Țară și școală. Árvíztűrő tükörfúrógép.'),
 ('PUBLISHING','¡Hola! ¿Qué? «Voilà» „Ja“ — … † ‡ § ¶ © ® ™'),
 ('SYMBOLS / FRACTIONS','$ ¢ £ ¥ € ¤ + − ± × ÷ ≠ ≤ ≥ ∞ ¼ ½ ¾ ⅜ ⅝'),
 ('SMALL FIGURES','⁰¹²³⁴⁵⁶⁷⁸⁹  ₀₁₂₃₄₅₆₇₈₉'),
 ('COMBINING MARKS','x́ ẍ x́̈ ạ ẹ ī ĵ'),
]
im=Image.new('RGB',(1800,2440),'#faf8f2');d=ImageDraw.Draw(im)
def ui(s):return ImageFont.truetype(UI,s)
def font(s,style):return ImageFont.truetype(str(ROOT/'fonts'/f'PrattNocturne-{style}.ttf'),s)
d.text((80,35),'PRATT NOCTURNE / 2.001 / FOUR STYLES',font=ui(26),fill='#555')
y=90
for style in styles:
 d.text((80,y),style.replace('BoldOblique','Bold Oblique'),font=ui(22),fill='#666')
 d.text((80,y+52),'Dear Sir, a stranger kind of ordinary.',font=font(78,style),fill='#242b32',anchor='lt')
 y+=230
for label,s in samples:
 d.text((80,y),label,font=ui(19),fill='#666')
 d.text((80,y+40),s,font=font(54,'Regular'),fill='#242b32',anchor='lt')
 y+=155
im.save(ROOT/'specimens/Release-2.001.png')
# Vector PDF with embedded fonts; combining examples remain in the shaped PNG/browser proof.
pdfmetrics.registerFont(PDFTTFont('UI',UI))
for style in styles:pdfmetrics.registerFont(PDFTTFont(style,str(ROOT/'fonts'/f'PrattNocturne-{style}.ttf')))
c=canvas.Canvas(str(ROOT/'specimens/Release-2.001.pdf'),pagesize=(792,1008))
c.setTitle('Pratt Nocturne 2.001 — family and repertoire')
y=963;c.setFont('UI',14);c.drawString(36,y,'PRATT NOCTURNE 2.001 / FAMILY PROOF');y-=40
for style in styles:
 c.setFont('UI',10);c.drawString(36,y,style.replace('BoldOblique','Bold Oblique'));y-=35
 c.setFont(style,32);c.drawString(36,y,'Dear Sir, a stranger kind of ordinary.');y-=65
for label,s in samples[:-1]:
 c.setFont('UI',9);c.drawString(36,y,label);y-=27
 c.setFont('Regular',23);c.drawString(36,y,s);y-=36
c.showPage()
cm=TTFont(ROOT/'fonts/PrattNocturne-Regular.ttf').getBestCmap()
visible=[cp for cp in cm if not chr(cp).isspace() and unicodedata.category(chr(cp))!='Cf']
for start in range(0,len(visible),80):
 c.setFont('UI',14);c.drawString(36,970,'ENCODED REPERTOIRE / '+str(start//80+1))
 for i,cp in enumerate(visible[start:start+80]):
  x=38+(i%8)*94;y=900-(i//8)*87
  c.setFont('UI',8);c.drawString(x,y+30,f'U+{cp:04X}')
  c.setFont('Regular',26);c.drawString(x,y,chr(cp))
 c.showPage()
c.save()
faces='\n'.join(f"@font-face{{font-family:Pratt;src:url('../fonts/PrattNocturne-{s}.woff2');font-weight:{700 if 'Bold' in s else 400};font-style:{'italic' if 'Oblique' in s else 'normal'};}}" for s in styles)
doc="""<!doctype html><html lang="en"><meta charset="utf-8"><title>Pratt Nocturne 2.001</title><style>"""+faces+"""
body{max-width:1100px;margin:40px auto;padding:20px;background:#faf8f2;color:#252b32;font:16px sans-serif}
.sample{font-family:Pratt;font-size:48px;line-height:1.8;overflow-wrap:anywhere}
textarea{width:100%;box-sizing:border-box;background:transparent;padding:20px;min-height:250px}
label{margin-right:20px}h2{font-size:18px;margin-top:30px} .oblique{font-style:italic}
</style><h1>Pratt Nocturne / 2.001</h1><p>Four styles. Eight-degree oblique. Full Latin-1 and Latin Extended-A.</p>
<label>Style <select id="style"><option>Regular</option><option>Oblique</option><option>Bold</option><option>Bold Oblique</option></select></label>
<label>Size <input id="size" type="range" min="24" max="100" value="48"></label>
<label><input id="alt" type="checkbox">Expressive alternates</label>
<textarea id="sample" class="sample">Dear Sir,
A stranger kind of ordinary.
Pratt Nocturne — 0123456789</textarea>
"""
for style in styles:doc+=f'<h2>{style}</h2><div class="sample" style="font-weight:{700 if "Bold" in style else 400};font-style:{"italic" if "Oblique" in style else "normal"}">a e D r R q ? — A stranger kind of ordinary.</div>'
for label,s in samples:doc+=f'<h2>{label}</h2><div class="sample">{html.escape(s)}</div>'
doc+='''<script>
const sample=document.querySelector('#sample');
function update(){let s=document.querySelector('#style').value;sample.style.fontWeight=s.includes('Bold')?700:400;sample.style.fontStyle=s.includes('Oblique')?'italic':'normal';sample.style.fontSize=document.querySelector('#size').value+'px';sample.style.fontFeatureSettings=document.querySelector('#alt').checked?'"ss01" 1':'"ss01" 0'}
document.querySelectorAll('input,select').forEach(x=>x.addEventListener('input',update));
</script></html>'''
(ROOT/'specimens/Try-Pratt-Nocturne.html').write_text(doc)
(ROOT/'CHARACTER-SET.txt').write_text('\n'.join(f'U+{cp:04X}\t{chr(cp)}\t{unicodedata.name(chr(cp),"UNNAMED")}' for cp in sorted(cm))+'\n')
print('Created release proofs and character inventory')

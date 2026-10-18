# SPDX-License-Identifier: MIT
"""Public comparison of the original and approved readable forms."""
from pathlib import Path
import subprocess
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
ROOT=Path(__file__).resolve().parents[1]
UI=subprocess.check_output(['fc-match','-f','%{file}','DejaVu Sans'],text=True)
pdfmetrics.registerFont(TTFont('UI',UI))
styles=['Regular','Oblique','Bold','BoldOblique']
for family in ['PrattNocturne','PrattNocturneReadable']:
 for style in styles:
  pdfmetrics.registerFont(TTFont(family+style,str(ROOT/'fonts'/f'{family}-{style}.ttf')))
c=canvas.Canvas(str(ROOT/'specimens/Readable-Proof.pdf'),pagesize=(792,1008))
c.setTitle('Pratt Nocturne 2.010 — readable a and q')
c.setAuthor('Pratt Nocturne contributors')
def label(x,y,text,size=11):
 c.setFillColorRGB(.30,.34,.38);c.setFont('UI',size);c.drawString(x,y,text)
def sample(x,y,text,family,style,size):
 c.setFillColorRGB(.12,.16,.20);c.setFont(family+style,size);c.drawString(x,y,text)
label(42,958,'PRATT NOCTURNE / READABLE FORMS',20)
label(42,928,'The d-derived bowl, with a familiar reading rhythm.')
label(42,885,'ORIGINAL DEFAULTS');label(398,885,'READABLE a AND q')
sample(42,775,'a q d','PrattNocturne','Regular',105)
sample(398,775,'a q d','PrattNocturneReadable','Regular',105)
for i,style in enumerate(styles):
 y=660-i*130
 label(42,y,style.replace('BoldOblique','Bold Oblique'))
 sample(42,y-45,'a quiet place','PrattNocturne',style,34)
 sample(398,y-45,'a quiet place','PrattNocturneReadable',style,34)
label(42,105,'Enable “Readable a and q” (ss02), or choose Pratt Nocturne Readable.')
label(42,82,'Original forms remain the defaults in Pratt Nocturne. Both families have four styles.',9)
c.showPage()
label(42,958,'READABLE / ACCENTS AND TEXT',20)
for i,style in enumerate(styles):
 y=880-i*185
 label(42,y,style.replace('BoldOblique','Bold Oblique'))
 sample(42,y-52,'à á â ã ä å ā ă ą æ ª','PrattNocturneReadable',style,38)
 sample(42,y-116,'A quiet place, an aqua sea.','PrattNocturneReadable',style,34)
label(42,92,'The readable choice takes precedence over expressive a alternates.',10)
label(42,68,'Derived designs; no handwritten exemplar is claimed for these alternate forms.',9)
c.save()
im=Image.new('RGB',(1600,1500),'#faf8f2');d=ImageDraw.Draw(im)
d.text((60,40),'PRATT NOCTURNE / READABLE FORMS',font=ImageFont.truetype(UI,32),fill='#303e4a')
for col,family in enumerate(['PrattNocturne','PrattNocturneReadable']):
 x=60+col*790
 d.text((x,115),['Original defaults','Approved readable forms'][col],font=ImageFont.truetype(UI,24),fill='#58626b')
 for i,style in enumerate(styles):
  y=190+i*315
  d.text((x,y),style.replace('BoldOblique','Bold Oblique'),font=ImageFont.truetype(UI,20),fill='#58626b')
  font=ImageFont.truetype(str(ROOT/'fonts'/f'{family}-{style}.ttf'),125)
  d.text((x,y+45),'a q d',font=font,fill='#202934',anchor='lt')
  font=ImageFont.truetype(str(ROOT/'fonts'/f'{family}-{style}.ttf'),52)
  d.text((x,y+225),'a quiet place',font=font,fill='#202934',anchor='lt')
im.save(ROOT/'specimens/Readable-Proof.png')
print('Created readable comparison PDF and PNG')

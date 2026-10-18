# SPDX-License-Identifier: MIT
"""Create a short, photograph-free specimen and a directory preview image."""
from pathlib import Path
import subprocess
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'specimens';OUT.mkdir(exist_ok=True)
UI=subprocess.check_output(['fc-match','-f','%{file}','DejaVu Sans'],text=True)
pdfmetrics.registerFont(TTFont('UI',UI))
STYLES=['Regular','Oblique','Bold','BoldOblique']
for s in STYLES:pdfmetrics.registerFont(TTFont(s,str(ROOT/'fonts'/f'PrattNocturne-{s}.ttf')))
W,H=600,800
c=canvas.Canvas(str(OUT/'Public-Specimen.pdf'),pagesize=(W,H))
c.setTitle('Pratt Nocturne — an eccentric hand / version 2.011')
c.setAuthor('Pratt Nocturne contributors')
ink='#20262e';paper='#f5efdf';gold='#e1cb80';muted='#68706c'
def bg(color):
 c.setFillColor(HexColor(color));c.rect(0,0,W,H,fill=1,stroke=0)
def text(x,y,t,size=11,font='UI',color=ink,maxwidth=504):
 size=min(size,maxwidth/pdfmetrics.stringWidth(t,font,1))
 c.setFont(font,size);c.setFillColor(HexColor(color));c.drawString(x,y,t)
def line(x1,y1,x2,y2,color):
 c.setStrokeColor(HexColor(color));c.setLineWidth(.5);c.line(x1,y1,x2,y2)
def end(num,dark=False):
 color=gold if dark else muted
 text(48,30,'PRATT NOCTURNE  /  TYPE SPECIMEN  /  2.011',8,color=color)
 text(542,30,str(num),8,color=color);c.showPage()
# Fictional book jacket: bold spacing and a restrained nighttime palette.
bg(ink)
text(48,751,'AN ECCENTRIC HAND',11,color=gold)
line(48,730,552,730,gold)
text(43,605,'Pratt',112,'Regular',paper)
text(43,469,'Nocturne',103,'Regular',paper)
text(48,342,'Notes after midnight',38,'Oblique',gold)
text(48,235,'Suspended heads. Falling vowels.',12,color=paper)
text(48,213,'A little order in an unusual hand.',12,color=paper)
text(48,109,'FOUR STYLES / EXTENDED LATIN / OPEN FONT LICENSE',9,color=gold)
end(1,True)
# Correspondence: invented content, no source excerpts or personal identifiers.
bg(paper)
text(48,749,'01 / CORRESPONDENCE',10,color=muted)
line(48,729,552,729,muted)
for y in range(650,180,-62):line(42,y-14,557,y-14,'#d7d6c9')
for y,t in zip(range(660,160,-62),[
 'Dear night owl,','The room is quiet now.',
 'A cup, a book, a crooked lamp.',
 'Some thoughts arrive sideways;',
 'others fall below the line.',
 'Leave a little space for both.',
 'Until the morning,','a fellow wanderer']):
 text(48,y,t,30,'Regular')
text(48,103,'Regular / 30 pt',10,color=muted)
text(48,81,'Fictional correspondence composed for this specimen.',9,color=muted)
end(2)
# Fictional literary poster.
bg('#d8bd76')
text(48,750,'02 / FICTIONAL EVENT POSTER',10)
text(41,616,'AFTER',113,'Bold')
text(41,472,'HOURS',113,'Bold')
line(48,418,552,418,ink)
text(48,354,'a gathering of odd words',35,'BoldOblique')
text(48,248,'poetry / stories / unfinished thoughts',25,'Regular')
text(48,159,'9 PM',61,'Bold',maxwidth=230)
text(315,160,'Stay curious.',29,'Oblique',maxwidth=237)
end(3)
# Useful family specimen; sizes give ample room for the deliberate descenders.
bg(paper)
text(48,749,'03 / THE FAMILY',10,color=muted)
for i,s in enumerate(STYLES):
 y=695-i*105
 text(48,y,s.replace('BoldOblique','Bold Oblique'),10,color=muted)
 text(48,y-43,'A stranger kind of ordinary.',32,s)
line(48,312,552,312,muted)
text(48,262,'a e D r R q 9 ?',47,'Regular')
text(48,207,'Àá Čč Ďď Łł Œœ Șș Ţţ Žž ½ €',24,'Regular')
text(48,155,'426 characters / 488 glyphs per style',11)
text(48,131,'Regular, Bold and two restrained eight-degree obliques.',10)
text(48,107,'Free for personal and commercial use under SIL OFL 1.1.',10)
text(48,83,'Source, downloads and updates: github.com/mkrzywonski/pratt-nocturne-font',8)
end(4)
c.save()
# A standalone directory / social preview. All artwork is actual font rendering.
im=Image.new('RGB',(1600,1000),paper);d=ImageDraw.Draw(im)
def ui(size):return ImageFont.truetype(UI,size)
def font(size,s='Regular'):return ImageFont.truetype(str(ROOT/'fonts'/f'PrattNocturne-{s}.ttf'),size)
d.rectangle((0,0,1600,500),fill=ink)
d.text((70,38),'AN ECCENTRIC HAND  /  VERSION 2.011',font=ui(22),fill=gold)
d.text((62,120),'Pratt Nocturne',font=font(155),fill=paper,anchor='lt')
d.text((70,385),'Suspended heads. Falling vowels. Unexpected serifs.',font=ui(26),fill=gold)
for i,s in enumerate(STYLES):
 y=540+i*97
 d.text((75,y),s.replace('BoldOblique','Bold Oblique'),font=ui(19),fill=muted)
 d.text((300,y-2),'A stranger kind of ordinary.',font=font(61,s),fill=ink,anchor='lt')
d.text((75,950),'FOUR STYLES  /  426 CHARACTERS  /  FREE FOR PERSONAL & COMMERCIAL USE  /  SIL OFL 1.1',font=ui(20),fill=ink)
im.save(OUT/'Public-Preview.png')
print('Created four-page public specimen and directory preview.')

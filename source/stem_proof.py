# SPDX-License-Identifier: MIT
"""Show the b/d serif relationship and inherited d forms in the current family."""
from pathlib import Path
import subprocess
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
ui_path=subprocess.check_output(['fc-match','-f','%{file}','DejaVu Sans'],text=True)
def ui(size):return ImageFont.truetype(ui_path,size)
im=Image.new('RGB',(1500,1460),'#faf8f2');draw=ImageDraw.Draw(im)
draw.text((60,35),'PRATT NOCTURNE 2.001 / STEM DETAILS',font=ui(26),fill='#39404a')
for i,(cp,label) in enumerate([('0062','Handwritten b (case uncertain)'),('0064','Handwritten d')]):
 x=65+i*380
 crop=Image.open(ROOT/'source/exemplars'/f'U{cp}.png').convert('RGB');crop.thumbnail((125,170))
 im.paste(crop,(x,105));draw.text((x,295),label,font=ui(20),fill='#39404a')
draw.text((820,125),'d inherits mirrored top and foot serifs.',font=ui(22),fill='#39404a')
draw.text((820,165),'Its bowl and bent stem are retained.',font=ui(22),fill='#39404a')
for i,style in enumerate(['Regular','Oblique','Bold','BoldOblique']):
 y=365+i*265
 draw.text((60,y),style.replace('BoldOblique','Bold Oblique'),font=ui(23),fill='#39404a')
 font=ImageFont.truetype(str(ROOT/'fonts'/f'PrattNocturne-{style}.ttf'),125)
 draw.text((65,y+62),'b d   ď đ   bed added odd',font=font,fill='#202834',anchor='lt')
im.save(ROOT/'specimens/Stem-Details.png')
im.save(ROOT/'specimens/Stem-Details.pdf','PDF',resolution=150)

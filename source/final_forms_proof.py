# SPDX-License-Identifier: MIT
"""Proof of the approved K, question mark and at sign in the released fonts."""
from pathlib import Path
import subprocess
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
ROOT=Path(__file__).resolve().parents[1]
ui=subprocess.check_output(['fc-match','-f','%{file}','DejaVu Sans'],text=True)
pdfmetrics.registerFont(TTFont('UI',ui))
c=canvas.Canvas(str(ROOT/'specimens/Final-Forms.pdf'),pagesize=(792,1008))
c.setTitle('Pratt Nocturne — approved K, question mark and at sign')
c.setAuthor('Pratt Nocturne contributors')
for readable in [False,True]:
 prefix='PrattNocturne'+('Readable' if readable else '')
 c.setFont('UI',19);c.drawString(42,956,'Pratt Nocturne'+(' Readable' if readable else ''))
 c.setFont('UI',10);c.drawString(42,925,'Approved forms: K3 / simplified question mark / AT1')
 for i,style in enumerate(['Regular','Oblique','Bold','BoldOblique']):
  pdfmetrics.registerFont(TTFont(prefix+style,str(ROOT/'fonts'/f'{prefix}-{style}.ttf')))
  y=868-i*205
  c.setFont('UI',11);c.drawString(42,y,style.replace('BoldOblique','Bold Oblique'))
  c.setFont(prefix+style,64);c.drawString(42,y-82,'K R P ? @ Ķ ¿')
  c.setFont(prefix+style,29);c.drawString(42,y-143,'KEEP? Ask at a@b.example')
 c.showPage()
c.save()

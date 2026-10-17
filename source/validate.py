# SPDX-License-Identifier: MIT
from pathlib import Path
import subprocess, json, tempfile, shutil, unicodedata
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
ROOT=Path(__file__).resolve().parents[1]
HB=shutil.which('hb-shape')
OTS=shutil.which('ots-sanitize')
if not HB or not OTS:raise SystemExit('Run inside nix-shell source/shell.nix, or install HarfBuzz and OpenType Sanitizer.')
lines=[]
coverage=set(range(32,127))|set(range(160,384))|set(range(0x218,0x21c))
for p in sorted(p for p in (ROOT/'fonts').iterdir() if p.suffix in {'.ttf','.otf','.woff2'}):
 f=TTFont(p);cm=f.getBestCmap();gs=f.getGlyphSet()
 assert coverage<=set(cm),(p,coverage-set(cm))
 for n in f.getGlyphOrder():
  pen=BoundsPen(gs);gs[n].draw(pen)
  if pen.bounds:assert pen.bounds[1]>=-620 and pen.bounds[3]<=1180,(p,n,pen.bounds)
 assert abs(f['head'].fontRevision-2)<.001
 oblique='Oblique' in p.name;bold='Bold' in p.name
 assert f['head'].macStyle==int(bold)+2*int(oblique)
 assert bool(f['OS/2'].fsSelection&1)==oblique
 assert bool(f['OS/2'].fsSelection&512)==oblique
 assert f['post'].italicAngle==(-8 if oblique else 0)
 assert f['OS/2'].fsType==0
 assert f['name'].getDebugName(13)==(ROOT/'OFL.txt').read_text()
 assert f['name'].getDebugName(14)=='https://openfontlicense.org/'
 assert f['name'].getDebugName(0)=='Copyright (c) 2026 Pratt Nocturne contributors.'
 with tempfile.NamedTemporaryFile() as tmp:
  r=subprocess.run([OTS,str(p),tmp.name],capture_output=True,text=True);assert r.returncode==0,r.stderr
 lines.append(f'{p.name}: sanitizer, coverage, bounds, embedding, OFL license and style metadata PASS; {len(cm)} characters, {len(gs)} glyphs.')
for style in ['Regular','Bold','Oblique','BoldOblique']:
 p=ROOT/'fonts'/f'PrattNocturne-{style}.ttf';f=TTFont(p);cm=f.getBestCmap()
 def shape(s,features=''):
  return json.loads(subprocess.check_output([HB,str(p),s,'--features='+features,'--output-format=json'],text=True))
 assert [g['g'] for g in shape('aerD','ss01=1')]==['a.alt','e.alt','r.alt','D.alt']
 assert shape('ee','calt=1')[1]['g']=='e.alt'
 assert sum(g['ax'] for g in shape('PrTaAV','kern=1'))<sum(g['ax'] for g in shape('PrTaAV','kern=0'))
 assert len(shape('1/2','frac=1'))==1
 assert shape('123','sups=1')[0]['g']=='digit1.sups'
 for cp in sorted(coverage):
  c=chr(cp);nfd=unicodedata.normalize('NFD',c)
  if c!=nfd:assert shape(c)==shape(nfd),(style,c,shape(c),shape(nfd))
 for text in ['x\u0301','x\u0301\u0308','a\u0323','i\u0304']:
  shaped=shape(text);assert all(g['g']!='.notdef' for g in shaped)
  if len(shaped)>1:assert any(g['ax']==0 and g['dy']!=0 for g in shaped),shaped
 assert f['glyf'][cm[ord('e')]].numberOfContours==2
 lines.append(f'{style}: HarfBuzz alternates, kerning, fractions, superscripts, NFC/NFD equivalence and mark positioning PASS.')
lines.append('No exhaustive cross-application or small-size hinting validation.')
(ROOT/'VALIDATION.txt').write_text('\n'.join(lines)+'\n')
print('\n'.join(lines))

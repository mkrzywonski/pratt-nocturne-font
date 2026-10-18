# SPDX-License-Identifier: MIT
"""Build photograph-free desktop, web and font-directory release archives."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib, shutil
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dist';OUT.mkdir(exist_ok=True)
VERSION='2.011'
STYLES=['Regular','Bold','Oblique','BoldOblique']
def archive(kind,entries):
 path=OUT/f'Pratt-Nocturne-{VERSION}-{kind}.zip'
 with ZipFile(path,'w',ZIP_DEFLATED) as z:
  for name,value in entries.items():
   content=value.read_bytes() if isinstance(value,Path) else value.encode()
   z.writestr('Pratt-Nocturne/'+name,content)
 with ZipFile(path) as z:
  assert z.testzip() is None
  assert len(z.namelist())==len(entries)
 return path
def fontfiles(ext, readable=False):
 prefix="PrattNocturneReadable" if readable else "PrattNocturne"
 return {f'{prefix}-{style}.{ext}':ROOT/'fonts'/f'{prefix}-{style}.{ext}' for style in STYLES}
common={'OFL.txt':ROOT/'OFL.txt','FONTLOG.txt':ROOT/'FONTLOG.txt'}
assets=[]
for kind,ext in [('Desktop-TTF','ttf'),('Desktop-OTF','otf')]:
 assets.append(archive(kind,{**fontfiles(ext),**common,'INSTALL.txt':ROOT/'distribution/INSTALL.txt','Specimen.pdf':ROOT/'specimens/Public-Specimen.pdf'}))
for ext in ['ttf','otf']:
 assets.append(archive('Readable-'+ext.upper(),{**fontfiles(ext,True),**common,'INSTALL.txt':ROOT/'distribution/INSTALL.txt','Readable-Proof.pdf':ROOT/'specimens/Readable-Proof.pdf'}))
assets.append(archive('DaFont',{**fontfiles('ttf'),**common,'README.txt':ROOT/'distribution/INSTALL.txt','Preview.png':ROOT/'specimens/Public-Preview.png'}))
css='/* Pratt Nocturne 2.011. SIL Open Font License 1.1; see OFL.txt. */\n'
for s in STYLES:
 css+=f"""@font-face {{
  font-family: "Pratt Nocturne";
  src: url("./PrattNocturne-{s}.woff2") format("woff2");
  font-weight: {700 if 'Bold' in s else 400};
  font-style: {'italic' if 'Oblique' in s else 'normal'};
  font-display: swap;
}}
"""
css+=css.replace('Pratt Nocturne"','Pratt Nocturne Readable"').replace('PrattNocturne-','PrattNocturneReadable-')
demo="""<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Pratt Nocturne webfont example</title><link rel="stylesheet" href="pratt-nocturne.css">
<style>
body{max-width:900px;margin:40px auto;padding:24px;background:#f5efdf;color:#20262e;font-family:sans-serif}
.sample{font-family:"Pratt Nocturne",serif;font-size:clamp(28px,5vw,56px);line-height:1.8;overflow-wrap:anywhere}
h2{font-size:16px;margin-top:2rem}
</style>
<h1>Pratt Nocturne</h1><p>Eight locally hosted webfonts, covering both families. No external font service is used.</p>
<h2>Regular</h2><div class="sample" contenteditable="true">A stranger kind of ordinary.</div>
<h2>Oblique</h2><div class="sample" style="font-style:italic" contenteditable="true">Notes after midnight.</div>
<h2>Bold</h2><div class="sample" style="font-weight:700" contenteditable="true">An unusual hand.</div>
<h2>Bold Oblique</h2><div class="sample" style="font-weight:700;font-style:italic" contenteditable="true">Leave a little space.</div>
<h2>Readable forms</h2><div class="sample" style="font-family: &quot;Pratt Nocturne Readable&quot;" contenteditable="true">A quiet place, an aqua sea.</div>
<p>SIL Open Font License 1.1. See OFL.txt.</p></html>
"""
webreadme="""PRATT NOCTURNE 2.011 / WEBFONTS

Keep the CSS and eight WOFF2 files together. Link pratt-nocturne.css from
your page, then use font-family: "Pratt Nocturne", serif.
Weights: 400 and 700. Styles: normal and italic (the Oblique faces).
Use generous line-height, such as 1.8, for accents and deep descenders.
The example.html file shows all four styles and editable sample text.

For a local test, serve the extracted directory with a static web server,
for example: python -m http.server 8000
Then open http://localhost:8000/example.html in a browser.

Readable letters: font-feature-settings: "ss02" 1;
Or select font-family: "Pratt Nocturne Readable", serif.

Optional exaggerated letters: font-feature-settings: "ss01" 1;
Use fraction substitution only on fraction text: "frac" 1.

Keep OFL.txt with redistributed webfonts. No third-party font requests
are made by this example.

Source and updates: https://github.com/mkrzywonski/pratt-nocturne-font
"""
assets.append(archive('Webfonts',{**fontfiles('woff2'),**fontfiles('woff2',True),**common,'README.txt':webreadme,'pratt-nocturne.css':css,'example.html':demo}))
for name in ['Public-Specimen.pdf','Public-Preview.png','Readable-Proof.pdf']:
 shutil.copyfile(ROOT/'specimens'/name,OUT/name);assets.append(OUT/name)
sums=''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in sorted(assets))
(OUT/'SHA256SUMS.txt').write_text(sums)
# Enforce the intentionally small, public-facing asset sets.
for p in assets:
 if p.suffix=='.zip':
  with ZipFile(p) as z:
   assert not any('exemplar' in n.lower() or n.lower().endswith(('.jpg','.jpeg')) for n in z.namelist())
   fontnames=[n for n in z.namelist() if n.endswith(('.ttf','.otf','.woff2'))]
   assert len(fontnames)==(8 if 'Webfonts' in p.name else 4)
   for n in fontnames:assert z.read(n)==(ROOT/'fonts'/Path(n).name).read_bytes()
print('\n'.join(f'{p.name}: {p.stat().st_size:,} bytes' for p in assets))
print('Verified ZIP integrity, correct fonts per package, and SHA256 checksums.')

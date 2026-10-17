"""Latin repertoire, compositions, marks, and publishing symbols for version 2.000.
Original drawings and derived forms use the same pressure-stroke builder as the family.
"""
import math, unicodedata as ud
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely.affinity import translate, scale, affine_transform

MARKS={
 '\u0300':('above',['M -90 140 L 35 25']),
 '\u0301':('above',['M -50 25 L 75 140']),
 '\u0302':('above',['M -120 30 L -10 150 L 120 30']),
 '\u0303':('above',['M -140 60 C -45 193 30 -35 150 95']),
 '\u0304':('above',['M -130 83 L 135 91']),
 '\u0306':('above',['M -119 145 Q -87 -9 14 27 Q 98 45 116 150']),
 '\u0307':('above',['M -3 75 L 0 99']),
 '\u0308':('above',['M -100 85 L -98 108','M 100 85 L 102 108']),
 '\u030a':('above',['M 0 170 C -135 175 -113 -10 5 -5 C 142 7 122 169 0 170']),
 '\u030b':('above',['M -130 25 L -28 155','M 30 25 L 132 155']),
 '\u030c':('above',['M -119 149 L 2 26 L 126 155']),
 '\u0326':('below',['M 22 -20 Q 48 -96 -29 -141']),
 '\u0327':('below',['M 0 -16 L -40 -83 Q 120 -65 70 -164 L -45 -185']),
 '\u0328':('below',['M 40 -16 C -111 -61 -84 -192 48 -142']),
 '\u0323':('below',['M -3 -66 L 0 -90']),
}
# Common vulgar fractions and fraction-feature substitutions.
FRACTIONS={'¼':(1,4),'½':(1,2),'¾':(3,4),'⅐':(1,7),'⅑':(1,9),'⅒':(1,10),
 '⅓':(1,3),'⅔':(2,3),'⅕':(1,5),'⅖':(2,5),'⅗':(3,5),'⅘':(4,5),
 '⅙':(1,6),'⅚':(5,6),'⅛':(1,8),'⅜':(3,8),'⅝':(5,8),'⅞':(7,8)}

def add_drawings(g,G):
 g('¢',440,*G['c']['paths'],'M 224 506 L 190 -132')
 g('¥',610,*G['Y']['paths'],'M 161 269 L 516 280','M 179 135 L 532 147')
 g('¤',530,'M 163 502 L 374 499 L 390 215 L 155 222 Z','M 73 601 L 163 502','M 374 499 L 454 602','M 390 215 L 470 110','M 155 222 L 67 113')
 g('¦',230,'M 100 729 L 109 389','M 115 201 L 125 -149')
 g('¬',560,'M 70 405 L 477 416 L 484 208')
 g('§',500,'M 369 695 C 117 850 48 535 241 439 C 473 325 418 159 243 157 C 17 191 44 450 247 460 C 456 434 497 79 295 5 Q 176 -23 84 57')
 g('¶',580,'M 310 696 C -26 740 0 338 316 355','M 300 699 L 326 -117','M 472 705 L 497 -111','M 282 701 L 529 707')
 g('·',230,'M 112 296 L 114 318')
 g('†',430,'M 197 723 L 222 -136','M 70 459 L 363 475')
 g('‡',430,'M 197 723 L 222 -136','M 70 459 L 363 475','M 78 209 L 371 225')
 g('−',540,'M 78 288 L 465 302')
 g('±',540,'M 78 365 L 465 379','M 260 577 L 276 166','M 88 45 L 475 59')
 g('≠',540,*G['=']['paths'],'M 375 573 L 167 78')
 g('≤',520,'M 402 602 L 91 370 L 414 158','M 94 30 L 445 42')
 g('≥',520,'M 91 602 L 402 370 L 79 158','M 63 30 L 414 42')
 g('∞',760,'M 381 303 C 166 652 -67 314 139 151 C 309 20 463 578 629 447 C 832 283 595 -61 381 303')
 g('µ',470,'M 95 355 L 118 -254','M 103 326 L 119 49 Q 236 1 353 44 L 338 353','M 351 62 L 406 18')
 g('‹',340,'M 259 456 L 84 245 L 275 56')
 g('›',340,'M 77 456 L 268 252 L 93 56')
 g('«',570,'M 253 456 L 78 245 L 269 56','M 475 465 L 300 254 L 491 65')
 g('»',570,'M 73 456 L 264 252 L 89 56','M 295 465 L 486 261 L 311 65')
 g('⁄',360,'M 52 -23 L 308 724')
 g('ƒ',390,'M 302 693 C 184 780 120 623 139 435 L 173 -131 Q 185 -260 68 -235','M 64 358 L 316 376')
 g('Ð',650,*G['D']['paths'],'M 96 343 L 358 358')
 g('ð',465,*G['o']['paths'],'M 178 683 C 436 564 452 290 351 104','M 144 503 L 362 635')
 g('Þ',560,'M 118 703 L 146 6','M 130 545 C 515 642 572 205 143 244')
 g('þ',465,'M 102 605 L 127 -286','M 113 351 C 416 438 456 69 128 85')
 g('Ħ',630,*G['H']['paths'],'M 53 559 L 550 578')
 g('ħ',470,*G['h']['paths'],'M 62 465 L 256 478')
 g('Đ',650,*G['D']['paths'],'M 96 343 L 358 358')
 g('đ',470,*G['d']['paths'],'M 219 486 L 430 499')
 g('Ł',500,*G['L']['paths'],'M 51 244 L 305 493')
 g('ł',310,*G['l']['paths'],'M 54 242 L 252 442')
 g('Ŧ',540,*G['T']['paths'],'M 137 368 L 424 380')
 g('ŧ',350,*G['t']['paths'],'M 75 186 L 290 198')
 g('Ŋ',670,'M 115 3 Q 101 366 84 702','M 89 607 L 530 20 L 508 714','M 530 20 Q 581 -255 397 -267')
 g('ŋ',465,*G['n']['paths'],'M 351 30 Q 396 -245 236 -263')
 g('ĸ',440,'M 113 357 L 126 10',*G['k']['paths'][1:])
 g('ſ',340,*G['f']['paths'])
 g('ẞ',580,'M 111 7 L 97 550 Q 99 735 322 703 L 459 687 L 284 382 C 581 308 557 -23 259 22')
 # A non-letter fallback for standalone combining marks in editors.
 g('◌',570,'M 272 610 L 289 610','M 418 539 L 431 526','M 469 345 L 469 328','M 405 151 L 392 138','M 224 85 L 207 85','M 83 164 L 70 177','M 48 351 L 48 368','M 119 539 L 132 552')


def extend(G,shapes,widths,cmap,weight,stroke,name):
 """Return mark/base anchors, canonical compositions and feature data before slanting."""
 def put(c,shape,width):
  n=name(c);shapes[n]=shape;widths[n]=int(round(width))
  if len(c)==1:cmap[ord(c)]=n
  return n
 def union(*items):return unary_union(items)
 # Preserve the designed ligatures and build non-decomposing Latin letters.
 put('ı',stroke(G['i']['paths'][:1],weight),G['i']['width'])
 put('dotlessj',stroke(G['j']['paths'][:1],weight),G['j']['width'])
 for c,base in [('Ŀ','L'),('ŀ','l')]:
  w=G[base]['width'];put(c,union(shapes[name(base)],translate(shapes[name('·')],xoff=w-95,yoff=100)),w+80)
 for c,left,right in [('Ĳ','I','J'),('ĳ','i','j')]:
  dx=widths[name(left)]-15;put(c,union(shapes[name(left)],translate(shapes[name(right)],xoff=dx)),dx+widths[name(right)])
 put('ŉ',union(translate(shapes[name('’')],xoff=-30),translate(shapes[name('n')],xoff=150)),595)
 # Mark glyphs are zero-width, drawn about their attachment origin.
 markinfo={}
 for c,(kind,paths) in MARKS.items():
  n=put(c,stroke(paths,weight*.88),0);markinfo[n]=kind
 # Side caron for letters whose tall stem would otherwise be crowded.
 put('caron.side',stroke(['M 35 90 Q 52 17 -12 -38'],weight*.88),0);markinfo['caron.side']='side'
 put('comma.above',stroke(['M 43 116 Q -31 65 -7 -15'],weight*.88),0);markinfo['comma.above']='above'
 # Spacing accents and full Latin-1 punctuation.
 spacing={'`':'\u0300','´':'\u0301','ˆ':'\u0302','˜':'\u0303','¯':'\u0304','˘':'\u0306','˙':'\u0307','¨':'\u0308','˚':'\u030a','˝':'\u030b','ˇ':'\u030c','¸':'\u0327','˛':'\u0328'}
 for c,mark in spacing.items():
  if c=='`':continue  # preserve the existing ASCII backtick
  put(c,translate(shapes[name(mark)],xoff=180,yoff=510 if MARKS[mark][0]=='above' else 0),360)
 for c,base in [('¡','!'),('¿','?')]:
  put(c,affine_transform(shapes[name(base)],[-1,0,0,-1,widths[name(base)],550]),widths[name(base)])
 put('\u00ad',shapes[name('-')],widths[name('-')])
 put('‐',shapes[name('-')],widths[name('-')]);put('‑',shapes[name('-')],widths[name('-')])
 put('‒',shapes[name('–')],widths[name('–')])
 put('‚',translate(shapes[name('’')],yoff=-685),220)
 put('„',translate(shapes[name('”')],yoff=-685),370)
 put('′',stroke(['M 125 711 L 78 494'],weight),220)
 put('″',stroke(['M 125 711 L 78 494','M 278 711 L 231 494'],weight),370)
 # Scaled composite symbols; scale outlines deliberately rather than using another font.
 circ=stroke(['M 389 738 C -43 738 4 -67 406 -38 C 860 -6 818 735 389 738'],weight)
 rsmall=translate(scale(shapes[name('R')],.52,.52,origin=(0,0)),xoff=230,yoff=174)
 put('®',union(circ,rsmall),790)
 put('™',union(translate(scale(shapes[name('T')],.48,.48,origin=(0,0)),xoff=25,yoff=360),translate(scale(shapes[name('M')],.48,.48,origin=(0,0)),xoff=305,yoff=360)),720)
 put('‰',union(shapes[name('%')],translate(scale(shapes[name('0')],.38,.48,origin=(0,0)),xoff=710,yoff=7)),940)
 # Spacing characters, controls, and a word joiner. Format controls have no ink.
 spaces={0xA0:300,0x2000:500,0x2001:1000,0x2002:500,0x2003:1000,0x2004:333,0x2005:250,0x2006:167,0x2007:530,0x2008:220,0x2009:200,0x200A:100,0x200B:0,0x200C:0,0x200D:0,0x202F:200,0x2060:0,0xFEFF:0}
 for cp,w in spaces.items():put(chr(cp),Polygon(),w)
 # Bounds-normalized small numerals: the descended 9 stays readable in fractions.
 small={}
 for d in '0123456789':
  base=shapes[name(d)];x0,y0,x1,y1=base.bounds
  small[d]=affine_transform(base,[.55,0,0,350/(y1-y0),30-.55*x0,-y0*350/(y1-y0)])
  put('digit'+d+'.numr',translate(small[d],yoff=385),int((x1-x0)*.55+70))
  put('digit'+d+'.dnom',small[d],int((x1-x0)*.55+70))
  put('digit'+d+'.sups',translate(small[d],yoff=420),int((x1-x0)*.55+70))
  put('digit'+d+'.subs',translate(small[d],yoff=-160),int((x1-x0)*.55+70))
 supers='⁰¹²³⁴⁵⁶⁷⁸⁹';subs='₀₁₂₃₄₅₆₇₈₉'
 for d,su,sd in zip('0123456789',supers,subs):
  put(su,shapes['digit'+d+'.sups'],widths['digit'+d+'.sups']);put(sd,shapes['digit'+d+'.subs'],widths['digit'+d+'.subs'])
 for c,base in [('ª','a'),('º','o')]:
  b=shapes[name(base)];x0,y0,x1,y1=b.bounds
  put(c,affine_transform(b,[.6,0,0,320/(y1-y0),30-.6*x0,380-y0*320/(y1-y0)]),int((x1-x0)*.6+70))
 fractions={}
 for c,(nu,de) in FRACTIONS.items():
  parts=[];x=0
  for d in str(nu):parts.append(translate(shapes['digit'+d+'.numr'],xoff=x));x+=widths['digit'+d+'.numr']-15
  parts.append(translate(shapes[name('⁄')],xoff=x-40));x+=210
  for d in str(de):parts.append(translate(shapes['digit'+d+'.dnom'],xoff=x));x+=widths['digit'+d+'.dnom']-15
  put(c,union(*parts),x+20);fractions[c]=(str(nu),str(de))
 # Anchor locations reflect the exceptional a/e descenders and ordinary body heights.
 anchors={}
 def baseanchors(n):
  shape=shapes[n];w=widths[n]
  if shape.is_empty:return None
  x0,y0,x1,y1=shape.bounds
  # Visual center, rather than advance center, keeps detached forms balanced.
  return {'above':((x0+x1)/2,y1+65),'below':((x0+x1)/2,y0-50),'side':(x1+60,y1-105)}
 for n in list(shapes):
  if n not in markinfo:anchors[n]=baseanchors(n)
 # Canonical combinations: cover all Latin Extended-A plus Romanian comma-below.
 # This preserves identical NFC/NFD output via ccmp, including side carons.
 compositions=[]
 targets=list(range(0xC0,0x180))+[0x218,0x219,0x21A,0x21B]
 for cp in targets:
  c=chr(cp);seq=ud.normalize('NFD',c)
  if len(seq)!=2 or seq[1] not in MARKS or name(seq[0]) not in shapes:continue
  base,mark=seq;bn=name(base);mn=name(mark);kind=MARKS[mark][0]
  # Dotless bases are used for above accents on i and j.
  actual=name('ı') if base=='i' and kind=='above' else ('dotlessj' if base=='j' and kind=='above' else bn)
  if mark=='\u030c' and base in 'dltL':mn='caron.side';kind='side'
  if mark=='\u0327' and base=='g':mn='comma.above';kind='above'
  ax,ay=anchors[actual][kind]
  gn=put(c,union(shapes[actual],translate(shapes[mn],xoff=ax,yoff=ay)),widths[actual])
  anchors[gn]=baseanchors(gn)
  compositions.append((bn,name(mark),gn))
 # Long-s acute/caron variants and all Extended-A members should now be present.
 missing=[f'U+{cp:04X}' for cp in list(range(0x20,0x7F))+list(range(0xA0,0x180)) if cp not in cmap]
 if missing:raise ValueError('Incomplete Latin repertoire: '+', '.join(missing))
 # Ensure every newly built composite can also accept a subsequent combining mark.
 for n in shapes:
  if n not in markinfo:anchors[n]=baseanchors(n)
 return {'anchors':anchors,'marks':markinfo,'compositions':compositions,'fractions':fractions}


def transform_for_oblique(shapes,widths,data,angle=8):
 """An 8-degree oblique about the body center, with individual bearing corrections."""
 shear=math.tan(math.radians(angle));shifts={}
 for n,shape in list(shapes.items()):
  shape=affine_transform(shape,[1,shear,0,1,-300*shear,0]);dx=0
  if widths[n] and not shape.is_empty:
   dx=max(0,22-shape.bounds[0]);shape=translate(shape,xoff=dx)
   widths[n]=max(widths[n]+round(dx),math.ceil(shape.bounds[2]+25))
  shifts[n]=dx;shapes[n]=shape
 def point(n,p):x,y=p;return (round(x+shear*(y-300)+shifts[n]),round(y))
 for n,a in data['anchors'].items():
  if a:data['anchors'][n]={kind:point(n,p) for kind,p in a.items()}
 data['mark_origins']={n:point(n,(0,0)) for n in data['marks']}
 # mkmk attachment points transform with the marks themselves.
 data['stack_anchors']={n:{'above':point(n,(0,shapes[n].bounds[3]+55)), 'below':point(n,(0,shapes[n].bounds[1]-55))} for n in data['marks']}
 return shifts


def features_for(data,name,shapes):
 marks=data['marks'];anchors=data['anchors']
 origins=data.get('mark_origins',{n:(0,0) for n in marks})
 def xy(p):return f'{round(p[0])} {round(p[1])}'
 s=''
 for n,kind in marks.items():s+=f'markClass {n} <anchor {xy(origins[n])}> @MC_{kind};\n'
 s+='feature ccmp {\n'
 for b,m,c in data['compositions']:s+=f'sub {b} {m} by {c};\n'
 above=[n for n,k in marks.items() if k=='above']
 s+=f"sub {name('i')}' [{' '.join(above)}] by {name('ı')};\n"
 s+=f"sub {name('j')}' [{' '.join(above)}] by dotlessj;\n"
 s+='} ccmp;\nfeature mark {\n'
 for n,a in anchors.items():
  if a:
   s+=f'pos base {n} '+ ' '.join(f'<anchor {xy(a[k])}> mark @MC_{k}' for k in ['above','below','side'])+';\n'
 s+='} mark;\nfeature mkmk {\n'
 for n,kind in marks.items():
  if kind=='side':continue
  if 'stack_anchors' in data:p=data['stack_anchors'][n][kind]
  else:p=(0,shapes[n].bounds[3]+55 if kind=='above' else shapes[n].bounds[1]-55)
  s+=f'pos mark {n} <anchor {xy(p)}> mark @MC_{kind};\n'
 s+='} mkmk;\n'
 for feature,suffix in [('sups','sups'),('subs','subs'),('numr','numr'),('dnom','dnom')]:
  s+=f'feature {feature} {{\n'+''.join(f'sub {name(d)} by digit{d}.{suffix};\n' for d in '0123456789')+f'}} {feature};\n'
 s+='feature frac {\n'
 for c,(nu,de) in sorted(data['fractions'].items(),key=lambda item:-len(item[1][1])):
  s+='sub '+' '.join(name(d) for d in nu)+f' {name("/")} '+' '.join(name(d) for d in de)+f' by {name(c)};\n'
 s+='} frac;\n'
 return s

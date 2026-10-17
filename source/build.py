#!/usr/bin/env python3
# Program logic: MIT; original glyph/design data: OFL-1.1. See ../LICENSING.md.
"""Original centerline drawings -> pressure ribbons -> fitted cubic outlines -> OTF/TTF/WOFF2.
Run with the dependencies in shell.nix. Coordinates use a 1000-unit em, y up.
"""
from pathlib import Path
import math, json, unicodedata, html
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.basePen import BasePen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.svgLib.path import parse_path
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.ttLib import TTFont
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from repertoire import add_drawings, extend, transform_for_oblique, features_for
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
(ROOT/'fonts').mkdir(exist_ok=True)
FONT_COPYRIGHT='Copyright (c) 2026 Pratt Nocturne contributors.'
FONT_LICENSE=(ROOT/'OFL.txt').read_text()
(ROOT/'fonts'/'OFL.txt').write_text(FONT_LICENSE)
G={}
def g(c,w,*paths): G[c]={'width':w,'paths':list(paths)}
# Shared construction vocabulary, in font units. These are explicit relationships,
# not a claim that the absent K/k/Z/z were observed in the handwriting.
H_STEM = 'M 40 603 L 137 590 L 152 14'
N_STEM = 'M 115 3 L 93 711'
def box_loop(left, right, bottom, top):
    # Shared rounded-box skeleton for o and the deliberately short zero.
    w=right-left; h=top-bottom
    return (f'M {left+w*.30} {top} L {right-w*.19} {top-h*.035} '
            f'Q {right} {top-h*.04} {right} {top-h*.23} '
            f'L {right+w*.025} {bottom+h*.21} Q {right+w*.025} {bottom} {right-w*.21} {bottom} '
            f'L {left+w*.17} {bottom+h*.025} Q {left} {bottom+h*.035} {left} {bottom+h*.23} '
            f'L {left-w*.025} {top-h*.20} Q {left-w*.025} {top} {left+w*.30} {top}')
def asymmetric_s(width, height):
    def p(x,y): return f'{x*width/550} {y*height/700}'
    return (f'M {p(367,679)} C {p(204,758)} {p(112,676)} {p(145,543)} '
            f'Q {p(160,481)} {p(263,441)} L {p(352,402)} '
            f'Q {p(453,354)} {p(460,218)} L {p(469,103)} '
            f'Q {p(470,26)} {p(388,26)} L {p(86,39)}')
def falling_leg(x, y, end_x, end_y):
    dx=end_x-x; dy=y-end_y
    return f'M {x} {y} C {x+dx*.43} {y-dy*.10} {x+dx*.49} {end_y+dy*.18} {end_x} {end_y}'
def angular_s_to_z(width, top, floor):
    # Mirrored S-like lower bowl: diagonal enters a short left upright,
    # then turns a boxy corner into a wider, flatter foot.
    w=width/550; h=(top-floor)/700
    def p(x,y):return f'{x*w} {floor+y*h}'
    return (f'M {p(110,684)} Q {p(256,720)} {p(427,685)} '
            f'Q {p(454,675)} {p(432,640)} L {p(164,353)} '
            f'Q {p(91,275)} {p(90,211)} L {p(86,91)} '
            f'Q {p(85,34)} {p(153,30)} L {p(479,44)}')
def p_family(scale=1, dy=0):
    # The D curve's high launch and deep right-hand sweep, shortened at its foot.
    # Lowercase p is a uniform reduction of this P, lowered to the body zone.
    def p(x,y): return f'{x*scale} {y*scale+dy}'
    return [f'M {p(67,731)} C {p(638,648)} {p(630,300)} {p(212,174)}',
            f'M {p(226,579)} L {p(247,0)}']
DIGIT_UPPER_RIGHT = 'M 174 618 L 322 630 Q 416 623 411 529 Q 407 405 259 345'
DIGIT_LOWER_RIGHT = 'M 259 345 C 409 302 470 183 443 79 Q 429 -5 311 15 L 106 47'
# Hand-drawn centerlines. The discontinuities are intentional pen lifts.
g('a',375,'M 81 363 L 292 376','M 179 369 L 188 227','M 150 153 L 215 -291')
g('b',450,'M 43 606 L 140 590 Q 148 347 132 26 L 53 28','M 141 354 L 240 327 Q 351 288 365 137 Q 378 27 132 26')
g('c',410,'M 328 340 C 114 460 48 185 106 51 Q 157 -25 342 23')
g('d',460,'M 355 603 Q 318 367 359 8','M 332 345 C 105 410 40 151 117 42 Q 201 -2 349 17')
g('e',370,'M 96 265 L 305 278 Q 270 389 167 372 Q 85 365 96 265 C 94 102 100 -157 198 -199 Q 248 -220 281 -156','M 57 261 L 105 266')
g('f',340,'M 231 580 L 104 599 Q 86 599 92 562 L 164 -138','M 55 374 L 299 389')
g('g',460,'M 346 345 C 89 440 66 73 224 53 Q 287 44 351 99','M 352 334 C 374 64 441 -323 256 -343 Q 183 -346 146 -312')
g('h',455,H_STEM,'M 146 332 L 229 351 L 337 331 L 355 22')
g('i',255,'M 58 348 L 137 337 L 149 16','M 130 507 L 133 540')
g('j',280,'M 83 350 L 166 337 Q 190 71 182 -178 Q 177 -302 87 -259','M 155 519 L 158 550')
g('k',440,H_STEM,'M 150 202 L 225 268 L 337 359',falling_leg(180,232,382,-8))
g('l',270,'M 41 605 L 146 590 L 165 10')
g('m',650,'M 103 27 L 89 351 L 292 343 L 314 37','M 302 337 L 411 352 L 532 329 L 555 17')
g('n',445,'M 103 29 L 89 351 L 218 360 L 329 340 L 351 12')
g('o',440,box_loop(89,351,20,365))
g('p',400,*p_family(.70,-145))
g('q',410,'M 285 373 L 119 382 Q 87 382 89 348 L 94 256 Q 95 231 130 231 L 279 242','M 259 155 L 324 -291')
g('r',335,'M 99 375 L 114 42','M 105 255 L 190 301 L 278 365')
g('s',400,asymmetric_s(400,365))
g('t',350,'M 167 535 Q 157 280 195 -7','M 60 366 L 304 388')
g('u',460,'M 90 353 L 113 42 Q 230 -8 352 43 L 337 348')
g('v',430,'M 66 365 L 264 -10 L 355 367')
g('w',650,'M 60 353 L 222 8 L 312 263 L 467 -5 L 572 364')
g('x',420,'M 72 359 L 356 -11','M 339 365 L 88 9')
g('y',450,'M 65 353 L 312 44','M 335 371 Q 313 27 377 -302')
g('z',400,angular_s_to_z(400,359,0))
g('A',600,'M 63 2 Q 149 307 192 596 Q 216 712 247 654 L 535 -17','M 118 171 Q 294 199 459 137')
g('B',570,'M 100 658 L 122 292','M 72 698 C 484 752 555 439 240 367 C 591 285 574 70 178 -138')
g('C',580,'M 487 636 C 110 879 17 219 139 53 Q 236 -27 496 43')
g('D',610,'M 67 731 C 638 648 688 121 212 -116','M 226 579 L 241 366')
g('E',510,'M 420 681 L 114 698 L 132 13 L 452 31','M 128 353 L 371 373')
g('F',490,'M 117 5 L 97 701 L 426 682','M 114 373 L 360 390')
g('G',650,'M 499 637 C 106 870 27 197 158 57 Q 305 -2 502 44 L 491 295','M 332 302 L 592 292')
g('H',600,'M 101 704 L 123 6','M 463 710 L 498 1','M 115 359 L 481 382')
g('I',300,'M 60 710 L 230 699','M 145 696 L 168 9','M 74 5 L 247 20')
g('J',450,'M 126 710 L 382 704','M 255 704 L 278 59 L 90 40')
g('K',570,N_STEM,'M 123 310 L 457 695',falling_leg(123,310,501,-30))
g('L',480,'M 100 707 L 133 14 L 419 36')
g('M',760,'M 104 3 Q 98 348 83 705','M 87 607 L 376 192 L 552 692','M 552 692 Q 637 354 673 -16')
g('N',650,'M 115 3 Q 101 366 84 702','M 89 607 L 540 -18 L 508 714')
g('O',630,box_loop(90,534,20,700))
g('P',580,*p_family())
g('Q',650,box_loop(90,534,20,700),'M 480 128 L 510 -40')
g('R',690,'M 136 675 L 152 352','M 38 679 L 163 686 C 383 704 464 489 316 350','M 316 350 L 630 -50')
g('S',550,asymmetric_s(550,700))
g('T',540,'M 58 704 Q 278 690 488 719','M 267 692 L 299 5')
g('U',610,'M 98 710 L 116 179 C 117 -55 508 -36 500 188 L 480 708')
g('V',620,'M 65 704 L 415 -11 L 542 713')
g('W',850,'M 68 706 L 274 2 L 396 488 L 630 -12 L 771 716')
g('X',580,'M 79 706 L 512 -13','M 481 713 L 96 6')
g('Y',610,'M 66 708 L 379 300','M 506 715 L 377 299 L 416 -67')
g('Z',550,angular_s_to_z(550,680,25))
g('0',490,box_loop(80,402,22,525))
g('1',260,'M 106 600 L 145 14')
g('2',520,'M 90 632 Q 208 674 269 628 C 349 544 357 349 324 208 C 301 70 134 20 81 99 C 3 152 179 259 318 212 Q 374 70 442 30')
g('3',530,DIGIT_UPPER_RIGHT,DIGIT_LOWER_RIGHT)
g('4',540,'M 103 466 L 85 263 L 468 273','M 346 602 L 374 -4')
g('5',480,'M 408 692 L 105 700 L 112 392 C 437 494 554 -37 92 24')
g('6',500,'M 363 707 Q 237 690 168 558 Q 95 407 105 168 Q 102 36 193 27 L 310 32 Q 407 39 407 164 L 397 282 Q 388 364 281 363 L 124 343')
g('7',460,'M 67 584 L 385 600 Q 403 601 397 573 L 258 8')
g('8',530,DIGIT_UPPER_RIGHT,'M 259 345 C 110 400 85 480 111 555 Q 126 620 174 618',DIGIT_LOWER_RIGHT,'M 106 47 Q 76 138 128 240 Q 180 312 259 345')
g('9',530,box_loop(110,385,125,490),'M 385 410 L 410 -325')
g('.',220,'M 108 18 L 110 36')
g(',',230,'M 134 35 Q 145 -52 90 -124')
g(':',230,'M 111 327 L 113 345','M 127 24 L 129 42')
g(';',240,'M 111 327 L 113 345','M 148 35 Q 158 -52 103 -124')
g('!',270,'M 106 700 L 144 196','M 147 19 L 148 42')
g('?',400,'M 89 724 Q 88 583 151 536 L 293 545 L 278 185','M 281 21 L 284 43')
g('-',400,'M 80 245 L 325 259')
g('_',550,'M 60 -120 L 484 -109')
g('+',520,'M 80 307 L 446 321','M 256 512 L 272 107')
g('=',520,'M 79 411 L 440 420','M 88 210 L 449 219')
g('/',410,'M 72 -93 L 342 746')
g('\\',410,'M 65 741 L 350 -89')
g('(',340,'M 263 765 C 64 570 84 39 290 -232')
g(')',340,'M 75 766 C 298 531 284 26 83 -232')
g('[',340,'M 263 750 L 111 750 L 133 -204 L 286 -204')
g(']',340,'M 72 750 L 225 750 L 248 -204 L 96 -204')
g('{',400,'M 315 753 Q 140 769 169 501 Q 191 296 71 289 Q 197 282 192 63 Q 181 -213 338 -206')
g('}',400,'M 75 753 Q 250 769 221 501 Q 199 296 319 289 Q 193 282 198 63 Q 209 -213 52 -206')
g("'",210,'M 112 715 L 95 548')
g('"',350,'M 103 715 L 86 548','M 250 715 L 233 548')
g('`',260,'M 83 757 L 186 636')
g('~',570,'M 64 289 C 197 491 338 116 498 320')
g('^',480,'M 70 455 L 214 710 L 411 461')
g('*',460,'M 217 714 L 239 363','M 69 614 L 391 467','M 76 455 L 372 632')
g('|',220,'M 98 779 L 126 -218')
g('<',480,'M 387 511 L 81 278 L 407 62')
g('>',480,'M 82 512 L 400 284 L 99 62')
g('#',630,'M 244 713 L 164 -27','M 469 713 L 390 -27','M 92 451 L 564 464','M 66 211 L 541 224')
g('$',550,*G['S']['paths'],'M 264 800 L 300 -108')
g('%',700,'M 121 -15 L 578 721','M 173 714 C 18 701 58 441 178 443 C 345 446 315 718 173 714','M 506 272 C 351 259 391 -1 511 1 C 678 4 648 276 506 272')
g('&',650,'M 544 54 C 318 217 63 407 136 601 C 228 818 478 658 350 492 C 204 333 35 218 129 61 C 270 -117 482 132 533 301')
g('@',780,'M 558 460 C 318 631 185 221 362 181 Q 458 162 515 294 L 534 492','M 519 299 C 479 50 763 167 671 504 C 548 927 13 726 88 257 C 126 -10 440 -105 655 41')
g(' ',300)
# More expansive alternate forms, selected explicitly with ss01 or by contextual repetition.
g('a.alt',395,'M 76 375 L 311 395','M 179 384 L 191 220','M 146 150 L 218 -335')
g('e.alt',390,'M 94 271 L 318 286 Q 279 412 161 386 Q 81 374 94 271 C 90 73 104 -219 216 -260 Q 272 -278 301 -200','M 52 267 L 104 272')
g('r.alt',350,'M 94 381 L 117 33','M 107 259 Q 193 284 293 388')
g('D.alt',640,'M 64 755 C 672 671 715 103 222 -181','M 231 590 L 247 367')
# Typographic punctuation, constructed in the same hand.
g('–',650,'M 70 245 L 575 259')
g('—',950,'M 70 245 L 875 259')
g('…',650,'M 100 18 L 102 36','M 317 18 L 319 36','M 534 18 L 536 36')
g('‘',220,'M 139 756 Q 78 688 101 589')
g('’',220,'M 116 758 Q 139 659 78 591')
g('“',370,'M 139 756 Q 78 688 101 589','M 289 756 Q 228 688 251 589')
g('”',370,'M 116 758 Q 139 659 78 591','M 266 758 Q 289 659 228 591')
g('•',300,'M 140 310 L 158 310')
g('°',330,'M 158 720 C 17 721 42 501 159 514 C 313 528 282 731 158 720')
g('×',520,'M 96 473 L 432 88','M 408 482 L 109 83')
g('÷',520,'M 80 277 L 444 289','M 253 482 L 255 499','M 268 69 L 270 87')
g('€',590,'M 491 635 C 142 867 20 193 162 53 Q 289 -19 507 58','M 60 410 L 405 421','M 61 268 L 355 278')
g('£',560,'M 450 649 C 168 867 123 488 182 279 Q 208 131 104 20 L 486 31','M 70 329 L 358 340')
g('©',790,'M 389 738 C -43 738 4 -67 406 -38 C 860 -6 818 735 389 738','M 519 512 C 272 685 185 144 378 144 Q 472 132 526 190')
# Additional Latin forms and accented characters are assembled from the original outlines.
g('æ',690,*G['a']['paths']) # The e component is assembled from its live outline below.
g('ß',510,'M 101 -10 L 87 494 C 51 804 431 785 389 534 Q 383 452 249 359 C 519 330 526 26 257 24')
add_drawings(g,G)
(ROOT/'source'/'drawings.json').write_text(json.dumps(G,ensure_ascii=False,indent=2))
class Flatten(BasePen):
 def __init__(self): super().__init__(None); self.paths=[]; self.current=[]
 def _moveTo(self,p):
  if self.current:self.paths.append(self.current)
  self.current=[p]
 def _lineTo(self,p):
  a=self.current[-1]; n=max(1,int(math.dist(a,p)/9))
  self.current.extend([(a[0]+(p[0]-a[0])*i/n,a[1]+(p[1]-a[1])*i/n) for i in range(1,n+1)])
 def _curveToOne(self,b,c,d):
  a=self.current[-1]; n=max(10,int((math.dist(a,b)+math.dist(b,c)+math.dist(c,d))/9))
  for i in range(1,n+1):
   t=i/n;s=1-t
   self.current.append(tuple(s**3*a[j]+3*s*s*t*b[j]+3*s*t*t*c[j]+t**3*d[j] for j in (0,1)))
 def _closePath(self): self._lineTo(self.current[0]);self._endPath()
 def _endPath(self):
  if self.current:self.paths.append(self.current);self.current=[]
def stroke(paths,weight=1):
 bits=[]
 for si,path in enumerate(paths):
  p=Flatten();parse_path(path,p);p._endPath()
  for pts in p.paths:
   left=[];right=[];radii=[]
   for i,(x,y) in enumerate(pts):
    a=pts[max(0,i-1)];b=pts[min(len(pts)-1,i+1)];dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy) or 1;t=i/max(1,len(pts)-1)
    # Mild broad-pen contrast and slow pressure changes, no artificial grunge.
    r=weight*(18.8+4.5*abs(dy/length)+2.1*math.sin(t*math.pi*1.8+si*.8))
    r*=.80+.20*min(1,t*9,(1-t)*9)
    nx=-dy/length*r;ny=dx/length*r
    left.append((x+nx,y+ny));right.append((x-nx,y-ny));radii.append(r)
   for j in range(len(pts)-1):
    bits.append(Polygon([left[j],left[j+1],right[j+1],right[j]]).buffer(0))
   bits.extend(Point(q).buffer(r,quad_segs=8) for q,r in zip(pts,radii))
 shape=unary_union(bits) if bits else Polygon()
 # Discard numerical sliver holes from union operations; retain drawn counters.
 polys=list(shape.geoms) if shape.geom_type=='MultiPolygon' else ([shape] if not shape.is_empty else [])
 return unary_union([Polygon(p.exterior,[r for r in p.interiors if Polygon(r).area>1e-6]) for p in polys]) if polys else Polygon()
def sub(a,b):return (a[0]-b[0],a[1]-b[1])
def add(a,b):return (a[0]+b[0],a[1]+b[1])
def mul(a,s):return (a[0]*s,a[1]*s)
def dot(a,b):return a[0]*b[0]+a[1]*b[1]
def unit(a):return mul(a,1/(math.hypot(*a) or 1))
def bez(c,t):
 s=1-t;return tuple(s**3*c[0][j]+3*s*s*t*c[1][j]+3*s*t*t*c[2][j]+t**3*c[3][j] for j in (0,1))
def fit(p,t1,t2,tol=1.25):
 if len(p)==2:
  d=math.dist(*p)/3;return [(p[0],add(p[0],mul(t1,d)),add(p[-1],mul(t2,d)),p[-1])]
 u=[0]
 for a,b in zip(p,p[1:]):u.append(u[-1]+math.dist(a,b))
 u=[v/(u[-1] or 1) for v in u]; c00=c01=c11=x0=x1=0
 for q,t in zip(p,u):
  s=1-t;b1=3*s*s*t;b2=3*s*t*t;a1=mul(t1,b1);a2=mul(t2,b2)
  tmp=sub(q,add(mul(p[0],s**3+b1),mul(p[-1],b2+t**3)))
  c00+=dot(a1,a1);c01+=dot(a1,a2);c11+=dot(a2,a2);x0+=dot(a1,tmp);x1+=dot(a2,tmp)
 det=c00*c11-c01*c01;d=math.dist(p[0],p[-1]);al=(x0*c11-x1*c01)/det if abs(det)>1e-10 else d/3;ar=(c00*x1-c01*x0)/det if abs(det)>1e-10 else d/3
 if min(al,ar)<d*1e-5 or max(al,ar)>d*3:al=ar=d/3
 c=(p[0],add(p[0],mul(t1,al)),add(p[-1],mul(t2,ar)),p[-1]);errs=[math.dist(q,bez(c,t)) for q,t in zip(p,u)];i=max(range(1,len(p)-1),key=lambda i:errs[i])
 if errs[i]<=tol:return [c]
 tm=unit(sub(p[i-1],p[i+1]));return fit(p[:i+1],t1,tm,tol)+fit(p[i:],mul(tm,-1),t2,tol)
def record(shape):
 pen=RecordingPen()
 polys=list(shape.geoms) if shape.geom_type=='MultiPolygon' else ([shape] if not shape.is_empty else [])
 for poly in polys:
  poly=orient(poly,sign=-1)
  for ring in [poly.exterior,*poly.interiors]:
   coarse=list(ring.simplify(.40,preserve_topology=True).coords)
   pts=[]
   for a,b in zip(coarse,coarse[1:]):
    steps=max(1,math.ceil(math.dist(a,b)/4))
    pts.extend(add(a,mul(sub(b,a),j/steps)) for j in range(steps))
   if len(pts)<3:continue
   # Split closed contours into quarters for stable cubic fitting.
   pts.append(pts[0]);n=len(pts)-1;cuts=sorted(set([0,n//4,n//2,3*n//4,n]));pen.moveTo(pts[0])
   for a,b in zip(cuts,cuts[1:]):
    q=pts[a:b+1]
    if len(q)<2:continue
    for c in fit(q,unit(sub(q[1],q[0])),unit(sub(q[-2],q[-1]))):pen.curveTo(*c[1:])
   pen.closePath()
 return pen

def name(c):return c if len(c)>1 else ('space' if c==' ' else 'uni%04X'%ord(c))

def build(style,weight,oblique=False):
 file_style=style.replace(" ","");bold=weight>1
 legacy_style=("Bold Italic" if bold else "Italic") if oblique else style
 shapes={name(c):stroke(v['paths'],weight) for c,v in G.items()};widths={name(c):v['width'] for c,v in G.items()};cmap={ord(c):name(c) for c in G if len(c)==1}
 shapes['.notdef']=stroke(['M 80 0 L 80 700 L 480 700 L 480 0 Z','M 80 0 L 480 700'],weight);widths['.notdef']=560
 shapes['nonbreakingspace']=Polygon();widths['nonbreakingspace']=300;cmap[160]='nonbreakingspace'
 from shapely.affinity import translate
 shapes[name('æ')]=unary_union([shapes[name('a')],translate(shapes[name('e')],xoff=315)])
 accents={'\u0300':['M -90 0 L 35 -115'],'\u0301':['M -50 -115 L 75 0'],'\u0302':['M -120 -110 L -10 10 L 120 -110'],'\u0303':['M -140 -80 C -45 53 30 -175 150 -45'],'\u0308':['M -100 -55 L -98 -32','M 100 -55 L 102 -32'],'\u030a':['M 0 30 C -135 35 -113 -150 5 -145 C 142 -133 122 29 0 30'],'\u0327':['M 0 15 L -40 -90 Q 120 -70 70 -185 L -45 -207']}
 for cp in range(0xC0,0x180):
  c=chr(cp);decomp=unicodedata.normalize('NFD',c)
  if len(decomp)==2 and decomp[0] in G and decomp[1] in accents:
   base,acc=decomp;w=G[base]['width'];base_shape=shapes[name(base)]
   if base in 'ij':base_shape=stroke(G[base]['paths'][:1],weight)
   y=(base_shape.bounds[3]+190) if acc!='\u0327' else base_shape.bounds[1]-5
   if base=='g' and acc=='\u0327':
    mark=translate(stroke(['M 45 0 Q -25 -55 -5 -130'],weight),xoff=w/2,yoff=base_shape.bounds[3]+210)
   else:
    mark=translate(stroke(accents[acc],weight),xoff=w/2,yoff=y)
   gn=name(c);shapes[gn]=unary_union([base_shape,mark]);widths[gn]=w;cmap[cp]=gn
 for c,base in [('Ø','O'),('ø','o')]:
  w=G[base]['width'];h=700 if base=='O' else 370;gn=name(c);shapes[gn]=unary_union([shapes[name(base)],stroke([f'M 60 -50 L {w-55} {h+50}'],weight)]);widths[gn]=w;cmap[ord(c)]=gn
 for c,base in [('Æ','A'),('Œ','O'),('œ','o')]:
  second='E' if base.isupper() else 'e';dx=G[base]['width']-65;gn=name(c);shapes[gn]=unary_union([shapes[name(base)],translate(shapes[name(second)],xoff=dx)]);widths[gn]=dx+G[second]['width'];cmap[ord(c)]=gn
 data=extend(G,shapes,widths,cmap,weight,stroke,name)
 if oblique:transform_for_oblique(shapes,widths,data)
 order=['.notdef']+[n for n in shapes if n!='.notdef'];recs={n:record(shapes[n]) for n in order}
 features='languagesystem DFLT dflt;\nlanguagesystem latn dflt;\n'
 features+=features_for(data,name,shapes)
 features+='feature ss01 {\n'+''.join(f'sub {name(c)} by {c}.alt;\n' for c in 'aerD')+'} ss01;\n'
 features+='feature calt {\n'+''.join(f'sub {name(c)} {name(c)}\' by {c}.alt;\n' for c in 'aer')+'} calt;\n'
 pairs={'Pr':-23,'Pa':-20,'Pe':-24,'Po':-18,'Da':-16,'De':-20,'Do':-16,'Ta':-35,'Te':-32,'To':-30,'Tr':-22,'Ty':-22,'Va':-25,'Ve':-25,'Vo':-22,'Wa':-18,'We':-18,'Yo':-30,'Ya':-28,'Ye':-28,'AT':-22,'AV':-30,'AW':-15,'AY':-26,'LT':-25,'FA':-20,'Fo':-20,'ra':-8,'re':-9,'rr':0,'PR':-18,'Ra':-12,'Re':-12,'Ka':-14,'Ke':-12,'Ko':-12,'ka':-8,'ke':-8,'ko':-8,'Za':-8,'Ze':-8}
 features+='feature kern {\n'+''.join(f'pos {name(p[0])} {name(p[1])} {v};\n' for p,v in pairs.items())+'} kern;'
 for ext in ['otf','ttf']:
  fb=FontBuilder(1000,isTTF=(ext=='ttf'));fb.setupGlyphOrder(order);fb.setupCharacterMap(cmap)
  if ext=='ttf':
   glyphs={}
   for n in order:
    p=TTGlyphPen(None);recs[n].replay(Cu2QuPen(p,max_err=.7,reverse_direction=False));glyphs[n]=p.glyph()
   fb.setupGlyf(glyphs)
  else:
   cs={}
   for n in order:
    p=T2CharStringPen(widths[n],None);recs[n].replay(p);cs[n]=p.getCharString()
   fb.setupCFF('PrattNocturne-'+file_style,{'FullName':'Pratt Nocturne '+style,'FamilyName':'Pratt Nocturne','Notice':FONT_COPYRIGHT+' Licensed under SIL Open Font License 1.1. https://openfontlicense.org/','Weight':'Bold' if bold else 'Regular','ItalicAngle':-8 if oblique else 0},cs,{})
  metrics={n:(widths[n],round(shapes[n].bounds[0]) if not shapes[n].is_empty else 0) for n in order}
  fb.setupHorizontalMetrics(metrics);fb.setupHorizontalHeader(ascent=1180,descent=-620,lineGap=0,caretSlopeRise=1000,caretSlopeRun=141 if oblique else 0)
  fb.setupNameTable({'familyName':'Pratt Nocturne','styleName':legacy_style,'typographicFamily':'Pratt Nocturne','typographicSubfamily':style,'uniqueFontIdentifier':'Pratt Nocturne '+style+' 2.000','fullName':'Pratt Nocturne '+style,'psName':'PrattNocturne-'+file_style,'version':'Version 2.000','copyright':FONT_COPYRIGHT,'licenseDescription':FONT_LICENSE,'licenseInfoURL':'https://openfontlicense.org/','description':'An original drawn interpretation; not a facsimile. ss01 offers amplified a, e, r and D.','designer':'Pratt Nocturne project'})
  fb.setupOS2(version=4,sTypoAscender=1180,sTypoDescender=-620,sTypoLineGap=0,usWinAscent=1180,usWinDescent=620,fsType=0,usWeightClass=700 if bold else 400,fsSelection=(1<<7)|(1<<8)|(32 if bold else 0)|(513 if oblique else (0 if bold else 64)),sxHeight=365,sCapHeight=700)
  fb.font['head'].macStyle=(1 if bold else 0)|(2 if oblique else 0);fb.font['head'].fontRevision=2.0;fb.setupPost(italicAngle=-8 if oblique else 0);addOpenTypeFeaturesFromString(fb.font,features)
  fb.save(ROOT/'fonts'/f'PrattNocturne-{file_style}.{ext}')
  if ext=='ttf':
   fb.font.flavor='woff2';fb.font.save(ROOT/'fonts'/f'PrattNocturne-{file_style}.woff2')
 if style=='Regular':
  (ROOT/'source'/'features.fea').write_text(features)
  from fontTools.pens.svgPathPen import SVGPathPen
  cells=[]
  for i,c in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'):
   p=SVGPathPen(None);recs[name(c)].replay(p);x=35+(i%10)*120;y=35+(i//10)*170
   cells.append(f'<text x="{x}" y="{y+12}" font-size="11" fill="#888">{c}</text><path d="{p.getCommands()}" transform="translate({x},{y+112}) scale(.14,-.14)"/>')
  (ROOT/'source'/'outline-sheet.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1240" height="1220" viewBox="0 0 1240 1220"><rect width="1240" height="1220" fill="#faf8f2"/>'+''.join(cells)+'</svg>')
 print(style,len(order),'glyphs;',len(cmap),'codepoints')

if __name__=='__main__':
 build('Regular',1)
 build('Bold',1.38)

 build('Oblique',1,True)
 build('Bold Oblique',1.38,True)

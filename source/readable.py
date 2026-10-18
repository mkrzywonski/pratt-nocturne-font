# Program logic: MIT; original glyph/design data: OFL-1.1. See ../LICENSING.md.
"""Approved d-derived readable forms, composed before the oblique transform."""
from shapely.affinity import translate, affine_transform
from shapely.ops import unary_union
from repertoire import MARKS

def add_readable(G, shapes, widths, data, weight, stroke, name):
 mapping={}
 def put(original, shape, width):
  gn=original+'.readable'
  shapes[gn]=shape; widths[gn]=width; mapping[original]=gn
  x0,y0,x1,y1=shape.bounds
  data['anchors'][gn]={'above':((x0+x1)/2,y1+65),'below':((x0+x1)/2,y0-50),'side':(x1+60,y1-105)}
  return gn
 a=put(name('a'),stroke([G['d']['paths'][1],'M 337 365 Q 336 205 359 8 L 438 10'],weight),500)
 put(name('q'),stroke([G['d']['paths'][1],'M 434 381 L 337 365 Q 336 205 359 8 Q 375 -142 393 -291 L 472 -289'],weight),535)
 for base,mark,composite in list(data['compositions']):
  if base!=name('a'):continue
  kind=MARKS[chr(int(mark[3:],16))][0]
  ax,ay=data['anchors'][a][kind]
  alt=put(composite,unary_union([shapes[a],translate(shapes[mark],xoff=ax,yoff=ay)]),500)
  data['compositions'].append((a,mark,alt))
 put(name('æ'),unary_union([shapes[a],translate(shapes[name('e')],xoff=435)]),435+widths[name('e')])
 x0,y0,x1,y1=shapes[a].bounds
 put(name('ª'),affine_transform(shapes[a],[.6,0,0,320/(y1-y0),30-.6*x0,380-y0*320/(y1-y0)]),int((x1-x0)*.6+70))
 mapping['a.alt']=a
 return mapping

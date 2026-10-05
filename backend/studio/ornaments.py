"""Prepared monochrome ornaments. Each composition is one indivisible layer."""
import io
import math
from functools import lru_cache
from PIL import Image, ImageDraw

CATALOG = [
    ('rect-frame', 'Rechteckrahmen', 'Rahmen', 1.35),
    ('double-rect', 'Doppelter Rechteckrahmen', 'Rahmen', 1.35),
    ('circle-frame', 'Kreisrahmen', 'Rahmen', 1),
    ('double-circle', 'Doppelter Kreisrahmen', 'Rahmen', 1),
    ('line', 'Feine Linie', 'Geometrisch', 10),
    ('diamond-divider', 'Rauten-Trenner', 'Geometrisch', 7),
    ('corner-marks', 'Technische Ecken', 'Geometrisch', 1.35),
    ('branch', 'Blätterzweig', 'Botanisch', 3.4),
    ('wreath', 'Blätterkranz', 'Botanisch', 1),
    ('laurel', 'Lorbeerkranz', 'Botanisch', 1),
    ('floral', 'Blumenkranz', 'Botanisch', 1),
    ('ribbon', 'Namensband', 'Schmuck', 3.4),
    ('heart', 'Herz', 'Schmuck', 1.1),
    ('star', 'Stern', 'Schmuck', 1),
    ('mountains', 'Bergkonturen', 'Natur', 2.4),
    ('forest', 'Waldsilhouette', 'Natur', 2),
    ('paw', 'Pfotenabdruck', 'Schmuck', 1),
    ('sparkles', 'Kleine Sternengruppe', 'Schmuck', 2.5),
]
BY_ID = {key: {'id': key, 'name': name, 'category': category, 'ratio': ratio}
         for key, name, category, ratio in CATALOG}
ROUND = {'circle-frame', 'double-circle', 'wreath', 'laurel', 'floral'}


@lru_cache(maxsize=240)
def ornament_sprite(identity, width, height, stroke_width=1.5):
    # w/h are the OUTSIDE extent, not a path's centre line. Inset keeps AA and stroke inside.
    density = 4
    w, h = max(1, round(width)), max(1, round(height))
    image = Image.new('RGBA', (w * density, h * density))
    draw = ImageDraw.Draw(image)
    # Reserve raster-filter support too: circular bounds use the outer contour,
    # so faint Lanczos/bicubic ringing must not escape the declared disk.
    clearance = 4 if identity in {'circle-frame', 'double-circle'} else 1
    pad = min(stroke_width / 2 + clearance, min(w,h) / 2 - .5) * density
    aw, ah = max(.1, w * density - pad * 2), max(.1, h * density - pad * 2)
    sw = max(1, round(stroke_width * density))
    def point(x, y): return (pad + x * aw, pad + y * ah)
    def line(points, closed=False):
        coords = [point(x, y) for x, y in points]
        if closed: coords.append(coords[0])
        draw.line(coords, fill='black', width=sw, joint='curve')
    def ellipse(x, y, rx, ry, fill=False):
        draw.ellipse((*point(x-rx, y-ry), *point(x+rx, y+ry)), fill='black' if fill else None, outline='black', width=sw)
    def leaf(cx, cy, angle, length=.085, breadth=.027):
        ca, sa = math.cos(angle), math.sin(angle)
        coords = []
        for i in range(25):
            t = i / 24 * math.tau
            u, v = math.cos(t) * length, math.sin(t) * breadth
            coords.append(point(cx + u*ca - v*sa, cy + u*sa + v*ca))
        draw.polygon(coords, fill='black')
    if identity in ('rect-frame', 'double-rect'):
        for inset in ([0, .06] if identity == 'double-rect' else [0]):
            line([(inset,inset),(1-inset,inset),(1-inset,1-inset),(inset,1-inset)], True)
    elif identity in ('circle-frame', 'double-circle'):
        ellipse(.5,.5,.5,.5)
        if identity == 'double-circle': ellipse(.5,.5,.43,.43)
    elif identity == 'line': line([(0,.5),(1,.5)])
    elif identity == 'diamond-divider':
        line([(0,.5),(.4,.5)]); line([(.6,.5),(1,.5)])
        line([(.43,.5),(.5,.05),(.57,.5),(.5,.95)], True)
    elif identity == 'corner-marks':
        for x,y,sx,sy in [(0,0,1,1),(1,0,-1,1),(0,1,1,-1),(1,1,-1,-1)]:
            line([(x,y+sy*.2),(x,y),(x+sx*.2,y)])
    elif identity == 'branch':
        line([(0,.85),(.2,.7),(.5,.48),(.8,.23),(1,.1)])
        for i in range(1,8):
            x=i/9; y=.85-.75*x
            line([(x,y),(x+.04,y-.22)]); line([(x,y),(x+.09,y+.2)])
            leaf(x+.035,y-.21,-.9,.055,.09); leaf(x+.09,y+.17,.9,.055,.09)
    elif identity in ('wreath','laurel','floral'):
        if identity == 'wreath':
            ellipse(.5,.5,.39,.39)
            for i in range(18):
                t=i/18*math.tau
                leaf(.5+.405*math.cos(t),.5+.405*math.sin(t),t+.6,.08,.024)
        elif identity == 'laurel':
            for side in (-1,1):
                pts=[]
                for i in range(61):
                    t=math.radians(20+i*2.25)
                    pts.append((.5+side*.36*math.sin(t),.48+.44*math.cos(t)))
                line(pts)
                for i in range(8):
                    t=math.radians(28+i*16)
                    x,y=.5+side*.36*math.sin(t),.48+.44*math.cos(t)
                    leaf(x+side*.025,y-.012,side*(-t+.5),.082,.025)
            line([(.40,.97),(.5,.91),(.6,.97)])
        else:
            ellipse(.5,.5,.38,.38)
            for t in [0,.9,2.2,3.1,4.2,5.35]:
                x,y=.5+.38*math.cos(t),.5+.38*math.sin(t)
                for n in range(5):
                    a=n/5*math.tau
                    ellipse(x+.035*math.cos(a),y+.035*math.sin(a),.029,.029)
                ellipse(x,y,.014,.014,True)
    elif identity == 'ribbon':
        line([(.12,.18),(.88,.18),(.88,.82),(.12,.82)],True)
        line([(.12,.3),(0,.3),(.045,.6),(0,.95),(.2,.95),(.12,.82)])
        line([(.88,.3),(1,.3),(.955,.6),(1,.95),(.8,.95),(.88,.82)])
    elif identity == 'heart':
        pts=[]
        for i in range(121):
            t=i/120*math.tau
            pts.append((.5+16*math.sin(t)**3/34,.49-(13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t))/36))
        line(pts,True)
    elif identity in ('star','sparkles'):
        for cx,cy,r in ([(.5,.5,.49)] if identity=='star' else [(.18,.58,.14),(.5,.4,.34),(.84,.67,.12)]):
            pts=[]
            for i in range(10):
                t=-math.pi/2+i*math.pi/5; radius=r if i%2==0 else r*.43
                pts.append((cx+radius*math.cos(t),cy+radius*math.sin(t)))
            line(pts,True)
    elif identity == 'mountains':
        line([(0,.95),(.25,.28),(.4,.65),(.61,.02),(1,.95),(0,.95)])
        line([(.50,.37),(.60,.45),(.68,.22)]); line([(.19,.45),(.25,.55),(.3,.4)])
    elif identity == 'forest':
        for x,y,s in [(.18,.35,.65),(.5,0,1),(.81,.28,.72)]:
            line([(x,y),(x-.14*s,y+.35*s),(x-.065*s,y+.35*s),(x-.2*s,y+.7*s),(x+.2*s,y+.7*s),(x+.065*s,y+.35*s),(x+.14*s,y+.35*s)],True)
            line([(x,y+.7*s),(x,y+.98*s)])
    elif identity == 'paw':
        ellipse(.5,.69,.25,.23)
        for x,y in [(.13,.4),(.36,.16),(.64,.16),(.87,.4)]: ellipse(x,y,.095,.13,True)
    image = image.resize((w,h), Image.Resampling.LANCZOS)
    out=io.BytesIO(); image.save(out,'PNG')
    return out.getvalue()
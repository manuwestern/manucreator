"""Strict static SVG subset and transparent PNG normalization. Never serve SVG inline."""
import io
import math
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from defusedxml.ElementTree import fromstring
from PIL import Image, ImageOps
from fastapi import HTTPException

TAGS={'svg','g','path','rect','circle','ellipse','line','polyline','polygon','title','desc'}
PAINT={'fill','stroke','stroke-width','stroke-linecap','stroke-linejoin','stroke-miterlimit','fill-rule','opacity','fill-opacity','stroke-opacity'}
ATTRS=PAINT|{'id','viewBox','width','height','x','y','x1','x2','y1','y2','cx','cy','r','rx','ry','points','d','transform','version','preserveAspectRatio'}

def invalid(message):raise HTTPException(422,message)

def static_svg(content):
    try:root=fromstring(content,forbid_dtd=True,forbid_entities=True,forbid_external=True)
    except Exception:invalid('SVG nicht lesbar. DTDs und XML-Entitäten sind nicht erlaubt.')
    nodes=list(root.iter())
    if len(nodes)>2000:invalid('SVG zu komplex: höchstens 2000 statische Formen.')
    for node in nodes:
        tag=node.tag.split('}')[-1]
        if tag not in TAGS:invalid(f'SVG enthält „{tag}“. Nur statische Formen/Pfade; Schrift bitte in Pfade umwandeln.')
        node.tag=tag
        if tag not in {'title','desc'} and node.text and node.text.strip():invalid('SVG-Schriftzüge bitte vor dem Upload in Pfade umwandeln.')
        attrs={}
        for key,value in node.attrib.items():
            if key=='style':
                for declaration in value.split(';'):
                    if not declaration.strip():continue
                    if ':' not in declaration:invalid('Ungültiger SVG-Stil.')
                    prop,val=declaration.split(':',1)
                    if prop.strip() not in PAINT:invalid('SVG enthält nicht unterstützte Stile oder Effekte.')
                    attrs[prop.strip()]=val.strip()
            elif key not in ATTRS:invalid(f'SVG-Eigenschaft „{key}“ nicht unterstützt. Keine Verweise, Bilder, Filter oder Animationen.')
            else:attrs[key]=value
        for key,value in attrs.items():
            if re.search(r'url\s*\(|https?:|data:|javascript:|var\s*\(|@|[<>\\]',value,re.I):invalid('SVG darf keine eingebetteten oder externen Inhalte enthalten.')
            if len(value)>300000:invalid('SVG-Pfad zu komplex. Bitte vereinfachen.')
            if key in {'fill','stroke'} and not re.fullmatch(r'(none|[a-zA-Z]+|#[0-9a-fA-F]{3,8}|rgba?\([0-9.,%\s]+\))',value):invalid('Nur einfache einfarbige SVG-Füllungen und Linien sind erlaubt.')
        node.attrib.clear();node.attrib.update(attrs)
    if root.tag!='svg':invalid('Eine SVG-Wurzel wird benötigt.')
    try:
        if 'viewBox' in root.attrib:
            x,y,w,h=map(float,re.split(r'[\s,]+',root.attrib['viewBox'].strip()))
        else:
            w=float(re.sub(r'px$','',root.attrib['width']));h=float(re.sub(r'px$','',root.attrib['height']));x=y=0
        if not all(math.isfinite(v) for v in (x,y,w,h)) or not .001<w<=100000 or not .001<h<=100000 or not .01<=w/h<=100:raise ValueError()
    except Exception:invalid('SVG benötigt eine gültige viewBox oder Breite/Höhe in Pixeln (Seitenverhältnis 1:100 bis 100:1).')
    root.set('viewBox',f'{x} {y} {w} {h}');root.set('width',str(max(1,round(1024*min(1,w/h)))));root.set('height',str(max(1,round(1024*min(1,h/w)))))
    root.set('xmlns','http://www.w3.org/2000/svg')
    return ET.tostring(root)

def normalize_decoration(content,filename):
    if len(content)>8*1024*1024:raise HTTPException(413,'Bitte höchstens 8 MB hochladen.')
    svg=filename.lower().endswith('.svg')
    if svg:
        clean=static_svg(content)
        try:
            # Separate bounded process: malicious geometry cannot hang the API event loop.
            result=subprocess.run([sys.executable,'-m','studio.svg_worker'],input=clean,capture_output=True,timeout=12)
            if result.returncode:raise ValueError()
            image=Image.open(io.BytesIO(result.stdout)).convert('RGBA')
        except Exception:invalid('Dieses SVG lässt sich nicht sicher rendern. Bitte Pfade vereinfachen und ohne Effekte exportieren.')
        mime='image/svg+xml'
    else:
        try:
            image=Image.open(io.BytesIO(content))
            if image.format!='PNG' or getattr(image,'n_frames',1)!=1:invalid('Bitte ein statisches PNG mit transparentem Hintergrund oder ein statisches SVG auswählen.')
            if image.width*image.height>20_000_000:invalid('PNG-Dateien sind auf 20 Megapixel begrenzt.')
            image=ImageOps.exif_transpose(image).convert('RGBA')
            if image.getchannel('A').getextrema()[0]==255:invalid('Das PNG hat keinen transparenten Bereich. Ein weißer Hintergrund wird nicht automatisch entfernt.')
        except HTTPException:raise
        except Exception:invalid('Die PNG-Datei konnte nicht gelesen werden.')
        mime='image/png'
    if not image.getchannel('A').getbbox():invalid('Das Motiv ist vollständig transparent.')
    image.thumbnail((1400,1400),Image.Resampling.LANCZOS)
    normalized=Image.new('RGBA',image.size,'black');normalized.putalpha(image.getchannel('A'))
    out=io.BytesIO();normalized.save(out,'PNG')
    return out.getvalue(),image.size,mime
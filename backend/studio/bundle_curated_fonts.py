"""Maintainer-only asset preparation; never invoked by a customer request."""
import asyncio
import hashlib
import io
import json
import os
from pathlib import Path
import httpx
from fontTools.ttLib import TTFont
from dotenv import load_dotenv

FAMILIES={
 'Klar & modern':['open-sans','montserrat','nunito','raleway'],
 'Klassisch':['merriweather','lora','playfair-display','cormorant-garamond','noto-serif'],
 'Markant & dekorativ':['oswald','bebas-neue','anton','cinzel'],
 'Geschwungen & festlich':['great-vibes','dancing-script','allura','pacifico','lobster'],
 'Handschriftlich':['caveat','kalam','permanent-marker','amatic-sc'],
 'Technisch & Schreibmaschine':['roboto-mono','space-mono','special-elite']}

async def main():
    load_dotenv(Path(__file__).parents[1]/'.env')
    backend=Path(__file__).parent/'assets'/'curated-fonts'
    frontend=Path(__file__).parents[2]/'frontend'/'public'/'fonts'/'curated'
    backend.mkdir(parents=True,exist_ok=True);frontend.mkdir(parents=True,exist_ok=True)
    semaphore=asyncio.Semaphore(6)
    async with httpx.AsyncClient(timeout=60,follow_redirects=False) as client:
        async def fetch(url):
            async with semaphore:
                result=await client.get(url);result.raise_for_status();return result
        async def family(identity,category):
            detail=(await fetch(os.environ['FONT_CATALOG_URL'].rstrip('/')+'/'+identity)).json()
            version=detail['npmVersion'];license=(await fetch(f"{os.environ['FONT_LICENSE_BASE']}/{identity}@{version}/LICENSE")).content
            (frontend/(identity+'-LICENSE.txt')).write_bytes(license)
            (backend/(identity+'-LICENSE.txt')).write_bytes(license)
            variants=[]
            # Ship all real styles/weights exposed by the pinned family metadata.
            for weight in detail['weights']:
                for style in detail['styles']:
                    choices=detail['variants'][str(weight)][style]
                    if 'latin' not in choices:raise RuntimeError(f'{identity} has no Latin face')
                    url=choices['latin']['url']['ttf'].replace('@latest/',f'@{version}/')
                    name=f'{identity}-{weight}-{style}';path=backend/(name+'.ttf')
                    raw=path.read_bytes() if path.exists() else (await fetch(url)).content
                    font=TTFont(io.BytesIO(raw));cmap=font.getBestCmap() or {}
                    missing=[c for c in 'ÄÖÜäöüß' if ord(c) not in cmap]
                    if missing:raise RuntimeError(f'{name}: missing German glyphs {missing}')
                    font.flavor=None;output=io.BytesIO();font.save(output);ttf=output.getvalue();path.write_bytes(ttf)
                    font.flavor='woff2';output=io.BytesIO();font.save(output);woff=output.getvalue();(frontend/(name+'.woff2')).write_bytes(woff)
                    variants.append({'weight':weight,'style':style,'key':f'curated:{identity}:{weight}:{style}','ttf':name+'.ttf','url':'/fonts/curated/'+name+'.woff2','sha256':hashlib.sha256(ttf).hexdigest(),'woff2_sha256':hashlib.sha256(woff).hexdigest()})
            print(identity,len(variants),'faces; German glyphs OK')
            return {'id':identity,'family':detail['family'],'category':category,'version':version,'license':detail['license'],'license_url':'/fonts/curated/'+identity+'-LICENSE.txt','variants':variants,'default':next((v['key'] for v in variants if v['weight']==400 and v['style']=='normal'),variants[0]['key'])}
        jobs=[family(identity,category) for category,ids in FAMILIES.items() for identity in ids]
        items=await asyncio.gather(*jobs)
    manifest={'version':'manucreator-curated-1','families':items}
    for path in [backend/'manifest.json',frontend/'manifest.json',Path(__file__).parents[2]/'frontend'/'src'/'data'/'curatedFonts.json']:
        path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    print('Bundled',len(items),'families and',sum(len(f['variants']) for f in items),'faces')

if __name__=='__main__':asyncio.run(main())
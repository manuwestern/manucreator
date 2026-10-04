import json
from pathlib import Path
from fastapi import HTTPException

DIRECTORY=Path(__file__).parent/'assets'/'curated-fonts'
MANIFEST=json.loads((DIRECTORY/'manifest.json').read_text())
FACES={v['key']:v for f in MANIFEST['families'] for v in f['variants']}
FAMILIES={f['id']:f for f in MANIFEST['families']}

def path_for(key):
    face=FACES.get(key)
    if not face:raise HTTPException(422,'Dieser Schriftschnitt gehört nicht zur bereitgestellten Auswahl.')
    path=DIRECTORY/face['ttf']
    if not path.is_file():raise HTTPException(503,'Die gewählte Schriftdatei fehlt. Es wird keine Ersatzschrift verwendet.')
    return path
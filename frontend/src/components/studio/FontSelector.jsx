import { ExternalLink } from 'lucide-react';
import { curatedFamilies,curatedFamily,curatedFace } from '@/lib/curatedFonts';
import { fonts } from '@/lib/studioLayersLegacy';
import { FontSizeControl } from './FontSizeControl';
import '@/styles/studio-controls-fixes.css';

export const FontSelector=({font,onChange,legacyFace,fontSize,onSizeChange})=>{
  const family=curatedFamily(font),face=curatedFace(font),categories=[...new Set(curatedFamilies.map(f=>f.category))];
  const legacyLabel=legacyFace?`${legacyFace.family} · ${legacyFace.weight}${legacyFace.style==='italic'?' Kursiv':''}`:fonts.find(([id])=>id===font)?.[1]||'Bisherige Entwurfschrift';
  const variants=family?.variants||[],weights=[...new Set(variants.map(v=>v.weight))],styles=[...new Set(variants.filter(v=>v.weight===face?.weight).map(v=>v.style))];
  return <><label htmlFor="layer-font">Schrift<select id="layer-font" value={family?.id||'legacy'} onChange={e=>onChange(curatedFamilies.find(f=>f.id===e.target.value).default)} data-testid="layer-font">{!family&&<optgroup label="Bestehende Entwurfschrift"><option value="legacy">{legacyLabel}</option></optgroup>}{categories.map(category=><optgroup key={category} label={category}>{curatedFamilies.filter(f=>f.category===category).map(f=><option key={f.id} value={f.id}>{f.family}</option>)}</optgroup>)}</select></label>
    <div className={`curated-variants ${family?'has-size':'legacy-size'}`} data-testid="font-style-size-row">
      {family&&<><div className="font-control-field"><label htmlFor="font-weight">Stärke</label><select id="font-weight" value={face.weight} disabled={weights.length<2} onChange={e=>onChange((variants.find(v=>v.weight===Number(e.target.value)&&v.style===face.style)||variants.find(v=>v.weight===Number(e.target.value))).key)} data-testid="font-weight">{weights.map(w=><option key={w} value={w}>{w}</option>)}</select></div><div className="font-control-field"><label htmlFor="font-style">Stil</label><select id="font-style" value={face.style} disabled={styles.length<2} onChange={e=>onChange(variants.find(v=>v.weight===face.weight&&v.style===e.target.value).key)} data-testid="font-style">{styles.map(style=><option key={style} value={style}>{style==='italic'?'Kursiv':'Normal'}</option>)}</select></div></>}
      <FontSizeControl value={fontSize} onChange={onSizeChange}/>
    </div>
    {family&&<a className="curated-license" href={family.license_url} target="_blank" rel="noreferrer" data-testid="font-license">Schriftlizenz · {family.license}<ExternalLink size={11}/></a>}
  </>;
};
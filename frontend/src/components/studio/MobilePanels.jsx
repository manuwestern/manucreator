import { useEffect,useRef,useState } from 'react';
import { X,Minus,Plus,ArrowUp,ArrowDown,ChevronsUp,ChevronsDown,Eye,EyeOff,LockKeyhole,LockKeyholeOpen,Camera,ImagePlus,FolderOpen } from 'lucide-react';
import { curatedFamilies,curatedFamily,curatedFace,curatedCssFamily,ensureFont } from '@/lib/curatedFonts';
import { getTextPreview,effectValues } from '@/lib/textPreview';
import { isValidElement } from '@/lib/transformGeometry';
import { mmPerPx } from '@/lib/snapGuides';
import { TextEffects } from './TextEffects';
import { ShapeProperties } from './ShapeProperties';
import { DecorationProperties } from './DecorationProperties';

export const Sheet=({title,onClose,children,testId})=>{
  const [expanded,setExpanded]=useState(false);
  return <section className="ms-sheet" data-expanded={expanded} role="dialog" aria-label={title} data-testid={testId}><button type="button" className="ms-sheet-handle" aria-label={expanded?'Panel zuziehen':'Panel vergrößern'} onClick={()=>setExpanded(v=>!v)} data-testid="ms-sheet-handle"/><div className="ms-sheet-head"><h2>{title}</h2><button type="button" onClick={onClose} data-testid="ms-sheet-done">Fertig</button></div><div className="ms-sheet-body">{children}</div></section>;
};

export const Tiles=({items,note})=><><div className="ms-tiles">{items.filter(Boolean).map(([Icon,label,onClick,opts={}])=><button type="button" key={label} onClick={onClick} disabled={opts.disabled} aria-pressed={opts.pressed} className={opts.danger?'is-danger':''} data-testid={`ms-tile-${label.toLowerCase().replace(/[^a-zäöü]/g,'')}`}><Icon size={22}/>{label}</button>)}</div>{note&&<p className="ms-tiles-note">{note}</p>}</>;

const sizes=[12,16,20,24,32,40,48,64];
// Debounced text authoring; latest requested value always wins over slower previews.
export const TextPanel=({element:e,product,update,onPending,disabled})=>{
  const [tab,setTab]=useState('text'),[values,setValues]=useState(e),[error,setError]=useState(''),[effects,setEffects]=useState(false);
  const ticket=useRef(0),timer=useRef(),valuesRef=useRef(values),updateRef=useRef(update),latest=useRef(e);updateRef.current=update;latest.current=e;valuesRef.current=values;
  useEffect(()=>{setValues(e);},[e]);
  useEffect(()=>()=>{ticket.current++;clearTimeout(timer.current);onPending(false);},[onPending]);
  const edit=changes=>{const base=valuesRef.current,next={...base,...changes,font_size:changes.font_size??(base.font_size||Math.max(4,Math.floor(latest.current.h*.76)))};valuesRef.current=next;setValues(next);setError('');onPending(true);const seq=++ticket.current;clearTimeout(timer.current);
    timer.current=setTimeout(async()=>{try{if(next.text.length>product.max_text)throw new Error(`Höchstens ${product.max_text} Zeichen.`);await ensureFont(next.font);const r=await getTextPreview(next);if(seq!==ticket.current)return;const old=latest.current,c={...old,text:next.text,font:next.font,font_size:next.font_size,curvature:next.curvature||0,...effectValues(next),w:r.width,h:r.height,x:old.x+(old.w-r.width)/2,y:old.y+(old.h-r.height)/2};if(!isValidElement(c))throw new Error('Diese Größe ist technisch nicht möglich (höchstens 800 px).');updateRef.current(Object.fromEntries(['text','font','font_size','curvature','text_mode','outline_width','shadow_enabled','shadow_distance','shadow_angle','x','y','w','h'].map(k=>[k,c[k]])));}catch(err){if(seq===ticket.current)setError(err.message);}finally{if(seq===ticket.current)onPending(false);}},160);};
  const size=values.font_size||Math.max(4,Math.round(e.h*.76)),family=curatedFamily(values.font),face=curatedFace(values.font),variants=family?.variants||[],mm=mmPerPx(product);
  const setSize=v=>{const n=Math.max(4,Math.min(200,Math.round(v*10)/10));if(!Number.isFinite(n))return;edit({font_size:n});};
  return <fieldset disabled={disabled||e.locked} style={{border:0,padding:0,margin:0}}><div className="ms-tabs" role="tablist">{[['text','Text'],['font','Schrift'],['position','Position']].map(([id,label])=><button type="button" role="tab" key={id} aria-selected={tab===id} onClick={()=>setTab(id)} data-testid={`ms-text-tab-${id}`}>{label}</button>)}</div>
    {tab==='text'&&<label className="ms-field ms-clear">Text · {values.text.length}/{product.max_text}<input type="text" value={values.text} maxLength={product.max_text} onChange={ev=>edit({text:ev.target.value})} data-testid="ms-text-input"/><button type="button" aria-label="Text löschen" onClick={()=>edit({text:''})} data-testid="ms-text-clear"><X size={16}/></button></label>}
    {tab==='font'&&<><div className="ms-fonts" role="listbox" aria-label="Schriftart">{curatedFamilies.map(f=><button type="button" role="option" key={f.id} aria-pressed={family?.id===f.id} aria-selected={family?.id===f.id} onClick={()=>{ensureFont(f.default);edit({font:f.default});}} data-testid={`ms-font-${f.id}`}><span style={{fontFamily:curatedCssFamily(f.default)}}>Aa</span><small>{f.family}</small></button>)}</div>
      {variants.length>1&&<div className="ms-row" role="group" aria-label="Schriftschnitt">{variants.map(v=><button type="button" key={v.key} aria-pressed={values.font===v.key} onClick={()=>{ensureFont(v.key);edit({font:v.key});}} data-testid={`ms-variant-${v.weight}-${v.style}`}>{v.weight}{v.style==='italic'?' Kursiv':''}</button>)}</div>}
      <div className="ms-field">Schriftgröße (px)<div className="ms-stepper"><button type="button" aria-label="Kleiner" onClick={()=>setSize(size-1)} data-testid="ms-size-minus"><Minus size={18}/></button><input type="number" inputMode="decimal" min="4" max="200" step="1" value={Math.round(size*10)/10} onChange={ev=>ev.target.value!==''&&setSize(Number(ev.target.value))} data-testid="ms-size-input"/><button type="button" aria-label="Größer" onClick={()=>setSize(size+1)} data-testid="ms-size-plus"><Plus size={18}/></button></div><div className="ms-presets">{sizes.map(s=><button type="button" key={s} aria-pressed={Math.round(size)===s} onClick={()=>setSize(s)} data-testid={`ms-size-preset-${s}`}>{s}</button>)}</div></div>
      {mm&&e.font_size>0&&<label className="ms-field">Breite · {(e.w*mm).toFixed(1)} mm (Gestaltungshilfe)<input type="range" min={Math.max(2,Math.round(e.w*mm*4/e.font_size))} max={Math.round(product.area.w*mm*1.3)} step="0.5" value={Math.round(e.w*mm*2)/2} onChange={ev=>setSize(e.font_size*Number(ev.target.value)/(e.w*mm))} data-testid="ms-width-mm"/></label>}
      {face&&<a className="curated-license" href={family.license_url} target="_blank" rel="noreferrer">Schriftlizenz · {family.license}</a>}</>}
    {tab==='position'&&<><div className="ms-row"><button type="button" onClick={()=>update({x:product.area.x+(product.area.w-e.w)/2})} data-testid="ms-center-x">Horizontal zentrieren</button><button type="button" onClick={()=>update({y:product.area.y+(product.area.h-e.h)/2})} data-testid="ms-center-y">Vertikal zentrieren</button></div><label className="ms-field">Drehung · {Math.round(e.rotation||0)}°<input type="range" min="-180" max="180" step="1" value={((e.rotation||0)+540)%360-180} onChange={ev=>update({rotation:Number(ev.target.value)})} data-testid="ms-rotation"/></label><button type="button" className="ms-row" style={{width:'100%'}} onClick={()=>update({rotation:0})} data-testid="ms-rotation-reset"><span style={{flex:1,minHeight:44,display:'flex',alignItems:'center',justifyContent:'center',border:'1px solid #dfe4d6',borderRadius:10}}>Drehung zurücksetzen</span></button></>}
    <button type="button" className="ms-row" style={{width:'100%'}} onClick={()=>setEffects(v=>!v)} aria-expanded={effects} data-testid="ms-more-options"><span style={{flex:1,minHeight:44,display:'flex',alignItems:'center',justifyContent:'center',border:'1px solid #dfe4d6',borderRadius:10}}>Weitere Optionen · Kontur & Schatten</span></button>
    {effects&&<TextEffects values={values} edit={edit}/>}
    {error&&<p className="property-error" role="alert" data-testid="ms-text-error">{error}</p>}</fieldset>;
};

export const CurvePanel=({element:e,update,product,onPending,disabled})=>{
  const set=v=>update({curvature:Math.max(-150,Math.min(150,v))});
  const value=e.curvature||0;
  return <fieldset disabled={disabled||e.locked} style={{border:0,padding:0,margin:0}}><div className="ms-row" role="group" aria-label="Wölbungsrichtung">{[['Nach unten',-60],['Gerade',0],['Nach oben',60]].map(([label,v])=><button type="button" key={label} aria-pressed={v===0?value===0:v<0?value<0:value>0} onClick={()=>set(v)} data-testid={`ms-curve-${v<0?'down':v?'up':'straight'}`}>{label}</button>)}</div>
    <div className="ms-field">Bogen · {value}°<div className="ms-stepper"><button type="button" aria-label="Weniger Bogen" onClick={()=>set(value-5)} data-testid="ms-curve-minus"><Minus size={18}/></button><input type="range" min="-150" max="150" step="5" value={value} onChange={ev=>set(Number(ev.target.value))} data-testid="ms-curve-slider" style={{border:0}}/><button type="button" aria-label="Mehr Bogen" onClick={()=>set(value+5)} data-testid="ms-curve-plus"><Plus size={18}/></button></div></div>
    <div className="ms-row"><button type="button" onClick={()=>set(0)} data-testid="ms-curve-reset">Wölbung zurücksetzen</button></div>
    <CurveSync element={e} product={product} update={update} onPending={onPending}/></fieldset>;
};
// Curvature changes the text sprite size: re-measure through the shared preview service.
const CurveSync=({element:e,update,onPending})=>{const key=`${e.curvature}|${e.text}|${e.font}|${e.font_size}`,last=useRef(key),updateRef=useRef(update);updateRef.current=update;
  useEffect(()=>{if(last.current===key||!e.font_size)return;last.current=key;let alive=true;onPending(true);getTextPreview(e).then(r=>{if(alive&&(Math.abs(r.width-e.w)>.5||Math.abs(r.height-e.h)>.5))updateRef.current({w:r.width,h:r.height,x:e.x+(e.w-r.width)/2,y:e.y+(e.h-r.height)/2});}).catch(()=>{}).finally(()=>{if(alive)onPending(false);});return()=>{alive=false;};},[key,e,onPending]);return null;};

export const LayersPanel=({elements,selected,onSelect,reorder,updateElement})=>{
  const list=[...elements].reverse(),index=elements.findIndex(x=>x.id===selected);
  const move=to=>{if(index<0)return;const copy=[...elements];const [item]=copy.splice(index,1);copy.splice(to,0,item);reorder(copy);};
  return <><p className="ms-tiles-note" style={{marginTop:0}}>Oben liegt vorne.</p><div className="ms-layers">{list.map(e=><div key={e.id} className="ms-layer" aria-pressed={e.id===selected} data-testid={`ms-layer-${e.id}`}><button type="button" onClick={()=>onSelect(e.id)} style={{flex:1,display:'flex',alignItems:'center',gap:10,height:'auto',width:'auto'}} data-testid={`ms-layer-select-${e.id}`}><i>{e.kind==='text'?'T':e.kind==='image'?'Bild':e.kind==='shape'?'Form':'Motiv'}</i><span>{e.kind==='text'?e.text||'Text':e.field_label||e.kind}</span></button><button type="button" aria-label={e.hidden?'Einblenden':'Ausblenden'} onClick={()=>updateElement(e.id,{hidden:!e.hidden})} data-testid={`ms-layer-visibility-${e.id}`}>{e.hidden?<EyeOff size={17}/>:<Eye size={17}/>}</button><button type="button" aria-label={e.locked?'Entsperren':'Sperren'} onClick={()=>updateElement(e.id,{locked:!e.locked})} data-testid={`ms-layer-lock-${e.id}`}>{e.locked?<LockKeyhole size={17}/>:<LockKeyholeOpen size={17}/>}</button></div>)}</div>
    {index>=0&&<div className="ms-row" style={{marginTop:12}}><button type="button" disabled={index>=elements.length-1} onClick={()=>move(index+1)} data-testid="ms-layer-forward"><ArrowUp size={16}/>Eine Ebene vor</button><button type="button" disabled={index>=elements.length-1} onClick={()=>move(elements.length-1)} data-testid="ms-layer-front"><ChevronsUp size={16}/>Ganz nach vorne</button><button type="button" disabled={index<=0} onClick={()=>move(index-1)} data-testid="ms-layer-back"><ArrowDown size={16}/>Eine Ebene zurück</button><button type="button" disabled={index<=0} onClick={()=>move(0)} data-testid="ms-layer-rear"><ChevronsDown size={16}/>Ganz nach hinten</button></div>}</>;
};

export const ImageAddPanel=({onFile,disabled})=>{
  const gallery=useRef(),camera=useRef(),files=useRef(),[rights,setRights]=useState(false);
  const pick=ev=>{const f=ev.target.files?.[0];ev.target.value='';if(f)onFile(f);};
  return <><label className="ms-field" style={{display:'flex',gap:10,alignItems:'flex-start'}}><input type="checkbox" checked={rights} onChange={ev=>setRights(ev.target.checked)} style={{width:18,height:18,marginTop:2}} data-testid="ms-image-rights"/><span>Ich darf dieses Bild und abgebildete Personen für meinen Entwurf verwenden.</span></label>
    <input ref={gallery} type="file" accept="image/jpeg,image/png,image/webp" className="sr-only" onChange={pick} data-testid="ms-image-input-gallery"/><input ref={camera} type="file" accept="image/*" capture="environment" className="sr-only" onChange={pick} data-testid="ms-image-input-camera"/><input ref={files} type="file" accept="image/jpeg,image/png,image/webp" className="sr-only" onChange={pick} data-testid="ms-image-input-file"/>
    <fieldset disabled={disabled||!rights} style={{border:0,padding:0}}><Tiles items={[[ImagePlus,'Foto auswählen',()=>gallery.current.click()],[Camera,'Kamera öffnen',()=>camera.current.click()],[FolderOpen,'Datei auswählen',()=>files.current.click()]]} note="JPG, PNG oder WebP · maximal 8 MB"/></fieldset></>;
};

export const ShapeFramePanel=({element:e,update,disabled})=>{
  const shapes=[['rect','Rechteck'],['circle','Kreis'],['ellipse','Oval'],['heart','Herz']];
  return <fieldset disabled={disabled||e.locked} style={{border:0,padding:0}}><div className="ms-row" role="group" aria-label="Bildform">{shapes.map(([id,label])=><button type="button" key={id} aria-pressed={(e.image_shape||'rect')===id} onClick={()=>update({image_shape:id})} data-testid={`ms-image-shape-${id}`}>{label}</button>)}</div>
    <div className="ms-row"><button type="button" onClick={()=>{const s=Math.min(e.w,e.h);update({w:s,h:s,x:e.x+(e.w-s)/2,y:e.y+(e.h-s)/2,crop:{x:0,y:0,w:1,h:1},image_ratio:0});}} data-testid="ms-image-fit-shape">Bild in Form ausrichten</button><button type="button" onClick={()=>update({image_shape:'rect'})} data-testid="ms-image-shape-reset">Form zurücksetzen</button></div><p className="ms-tiles-note">„Bild in Form ausrichten“ macht den Rahmen quadratisch; Rahmenform wirkt in Vorschau, Download und Bestellung gleich.</p></fieldset>;
};

export const MotifPanel=({element:e,product,update,disabled})=>e.kind==='shape'?<ShapeProperties element={e} product={product} update={update} disabled={disabled}/>:<DecorationProperties element={e} product={product} update={update} disabled={disabled}/>;

import { useCallback,useEffect,useRef,useState } from 'react';
import { RotateCcw,LoaderCircle } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { ensureFont } from '@/lib/curatedFonts';
import { existingFace } from '@/lib/fontCatalog';
import { getTextPreview,effectValues } from '@/lib/textPreview';
import { isValidElement } from '@/lib/transformGeometry';
import { FontSelector } from './FontSelector';
import { TextEffects } from './TextEffects';

export const TextProperties=({element,product,update,disabled,onPending})=>{
  const [values,setValues]=useState(element),[face,setFace]=useState(null),[error,setError]=useState(''),[pending,setPending]=useState(false);
  const latest=useRef(element),ticket=useRef(0),timer=useRef(),mounted=useRef(true);latest.current=element;
  useEffect(()=>{setValues(element);},[element]);
  useEffect(()=>{let alive=true;ensureFont(element.font).catch(e=>{if(alive)setError(e.message);});if(element.font.startsWith('fs:'))existingFace(element.font).then(value=>{if(alive)setFace(value);}).catch(e=>{if(alive)setError(e.message);});else setFace(null);return()=>{alive=false;};},[element.font]);
  const dispose=useCallback(()=>{mounted.current=false;ticket.current++;clearTimeout(timer.current);onPending(false);},[onPending]);
  useEffect(()=>{mounted.current=true;return dispose;},[dispose]);
  const edit=changes=>{
    const next={...values,...changes,font_size:changes.font_size??(values.font_size||Math.max(4,Math.floor(element.h*.76)))};
    setValues(next);setError('');setPending(true);onPending(true);const seq=++ticket.current;clearTimeout(timer.current);
    timer.current=setTimeout(async()=>{try{
      if(next.text.length>product.max_text)throw new Error(`Bitte auf höchstens ${product.max_text} Zeichen kürzen. Dein Entwurf bleibt unverändert.`);
      await ensureFont(next.font);const rendered=await getTextPreview(next);if(seq!==ticket.current||!mounted.current)return;
      const old=latest.current,candidate={...old,text:next.text,font:next.font,font_size:next.font_size,curvature:next.curvature||0,...effectValues(next),w:rendered.width,h:rendered.height,x:old.x+(old.w-rendered.width)/2,y:old.y+(old.h-rendered.height)/2};
      if(!isValidElement(candidate))throw new Error('Die technische Elementgröße beträgt höchstens 800 px. Bitte Schriftgröße oder Effekt verringern.');
      // Only text/geometry are authored here. Do not overwrite concurrently edited admin field permissions.
      const keys=['text','font','font_size','curvature','text_mode','outline_width','shadow_enabled','shadow_distance','shadow_angle','x','y','w','h'];
      update(Object.fromEntries(keys.map(key=>[key,candidate[key]])));
    }catch(e){if(seq===ticket.current&&mounted.current)setError(e.message);}finally{if(seq===ticket.current&&mounted.current){setPending(false);onPending(false);}}},180);
  };
  return <><fieldset disabled={disabled||element.locked} className="text-properties-controls">
    <label htmlFor="layer-text">Text<span data-testid="layer-text-count">{values.text.length}/{product.max_text}</span><Input id="layer-text" value={values.text} onChange={e=>edit({text:e.target.value})} data-testid="layer-text"/></label>
    <FontSelector font={values.font} onChange={font=>edit({font})} legacyFace={face} fontSize={values.font_size||Math.max(4,element.h*.76)} onSizeChange={font_size=>edit({font_size})}/>
    <div className="curve-heading"><label htmlFor="text-curvature">Bogen <span data-testid="text-curvature-value">{values.curvature||0}°</span></label><button title="Gerader Text" aria-label="Bogen zurücksetzen" onClick={()=>edit({curvature:0})} data-testid="text-reset-curvature"><RotateCcw size={14}/></button></div>
    <input id="text-curvature" type="range" min="-150" max="150" step="5" value={values.curvature||0} onChange={e=>edit({curvature:Number(e.target.value)})} data-testid="text-curvature"/>
    <div className="curve-labels"><span>Nach unten</span><span>Gerade</span><span>Nach oben</span></div>
    <TextEffects values={values} edit={edit}/>
  </fieldset>{pending&&<p className="property-status" data-testid="text-rendering"><LoaderCircle className="loading-spin" size={13}/>Text wird gesetzt …</p>}{error&&<p role="alert" className="property-error" data-testid="text-property-error">{error}</p>}</>;
};
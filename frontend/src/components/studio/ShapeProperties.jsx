import { useEffect,useState } from 'react';
import { LockKeyhole,LockKeyholeOpen,Square,ScanLine } from 'lucide-react';
import { isInside } from '@/lib/transformGeometry';
import { shapeNames,validShape } from '@/lib/studioShapes';

const NumberField=({label,testId,value,min=4,max=800,step=1,onChange})=>{
  const [draft,setDraft]=useState(String(Math.round(value*100)/100));
  useEffect(()=>setDraft(String(Math.round(value*100)/100)),[value]);
  return <label>{label}<input type="number" min={min} max={max} step={step} value={draft} onChange={e=>{setDraft(e.target.value);if(e.target.value!=='')onChange(Number(e.target.value));}} data-testid={testId}/></label>;
};

export const ShapeProperties=({element:e,product,update,disabled})=>{
  const [error,setError]=useState('');
  useEffect(()=>setError(''),[e]);
  const change=values=>{
    const next={...e,...values};
    if(values.w!==undefined||values.h!==undefined){
      if(e.shape_type==='line')next.h=e.stroke_width;
      else if(e.shape_type!=='rectangle'||e.shape_proportional){
        if(values.w!==undefined)next.h=e.h*next.w/e.w;else next.w=e.w*next.h/e.h;
      }
    }
    if(values.stroke_width!==undefined&&e.shape_type==='line')next.h=values.stroke_width;
    next.x=e.x+(e.w-next.w)/2;next.y=e.y+(e.h-next.h)/2;
    if(!validShape(next)){setError('Diese Größe oder Strichstärke passt nicht zur Form. Der bisherige Stand bleibt erhalten.');return;}
    if(!isInside(next,product.area,0)){setError('Die vollständige Form einschließlich Strichstärke muss innerhalb der Gravurfläche bleiben. Der bisherige Stand bleibt erhalten.');return;}
    setError('');update(next);
  };
  return <fieldset className="shape-properties" disabled={disabled||e.locked} data-testid="shape-properties"><p className="shape-kind" data-testid="shape-kind">{shapeNames[e.shape_type]}</p>
    {e.shape_type!=='line'&&<div className="effect-mode" role="group" aria-label="Formdarstellung">{[[Square,'filled','Gefüllt'],[ScanLine,'outline','Kontur']].map(([Icon,mode,label])=><button key={mode} type="button" aria-pressed={e.shape_mode===mode} onClick={()=>change({shape_mode:mode})} data-testid={`shape-mode-${mode}`}><Icon size={16}/>{label}</button>)}</div>}
    <div className="element-numbers shape-dimensions"><NumberField label={e.shape_type==='line'?'Länge (px)':e.shape_type==='circle'?'Durchmesser (px)':'Breite (px)'} testId={e.shape_type==='line'?'shape-length':e.shape_type==='circle'?'shape-diameter':'shape-width'} value={e.w} onChange={w=>change({w})}/>{e.shape_type==='rectangle'&&<NumberField label="Höhe (px)" testId="shape-height" value={e.h} onChange={h=>change({h})}/>}</div>
    {e.shape_type==='rectangle'&&<button className="shape-proportion-lock" type="button" aria-pressed={!!e.shape_proportional} onClick={()=>change({shape_proportional:!e.shape_proportional})} data-testid="shape-proportion-lock">{e.shape_proportional?<LockKeyhole size={15}/>:<LockKeyholeOpen size={15}/>}Proportionen {e.shape_proportional?'gesperrt':'frei'}</button>}
    {(e.shape_type==='line'||e.shape_mode==='outline')&&<NumberField label="Strichstärke (px)" testId="shape-stroke-width" value={e.stroke_width??2} min={.1} max={12} step={.1} onChange={stroke_width=>change({stroke_width})}/>}
    {error&&<p className="property-error" role="alert" data-testid="shape-property-error">{error}</p>}
  </fieldset>;
};
import { useState } from 'react';
import { AlignCenter,ArrowDown,ArrowLeft,ArrowRight,ArrowUp,RotateCcw } from 'lucide-react';
import { fitElement,isInside,isValidElement,imageFrame,scaleDetails } from '@/lib/transformGeometry';

export const ElementTools=({element:b,product,update,disabled,hideSize=false})=>{
  const [error,setError]=useState('');
  if(!b)return null;
  const wrongRatio=b.kind==='image'&&b.image_ratio>0&&Math.abs(b.w/b.h/(b.image_ratio*b.crop.w/b.crop.h)-1)>.012;
  const change=values=>{
    const e={...b,...values};
    if(values.w!==undefined){const scale=values.w/b.w;e.h=b.h*scale;Object.assign(e,scaleDetails(e,scale));}
    if(values.h!==undefined){const scale=values.h/b.h;e.w=b.w*scale;Object.assign(e,scaleDetails(e,scale));}
    if(values.w!==undefined||values.h!==undefined){e.x=b.x+(b.w-e.w)/2;e.y=b.y+(b.h-e.h)/2;}
    if(!isValidElement(e)){setError('Bitte gültige Maße, Formproportionen und Schriftgrößen verwenden (Elementgröße höchstens 800 px).');return;}
    setError('');update(e);
  };
  const repair=()=>{const fitted=wrongRatio?imageFrame(b,b.image_ratio*b.crop.w/b.crop.h,product.area):fitElement(b,product.area);update({...fitted,locked:false});setError('');};
  return <section className="element-tools" aria-label="Drehung, Größe und Position">
    {(!isInside(b,product.area)||wrongRatio)&&<button className="repair-element" disabled={disabled} onClick={repair} data-testid="element-fit-to-area">Dieses Element proportional einpassen</button>}
    <fieldset disabled={disabled||b.locked}><div className="rotation-control"><label htmlFor="element-rotation">Drehung<input id="element-rotation" type="number" min="-360" max="360" step="1" value={Math.round((b.rotation||0)*10)/10} onChange={e=>change({rotation:Math.max(-360,Math.min(360,Number(e.target.value)))})} data-testid="element-rotation"/></label><span>°</span><button title="Auf 0 Grad zurücksetzen" aria-label="Drehung zurücksetzen" onClick={()=>change({rotation:0})} data-testid="element-reset-rotation"><RotateCcw size={15}/></button></div>
    <input type="range" aria-label="Drehwinkel" min="-180" max="180" step="1" value={((b.rotation||0)+540)%360-180} onChange={e=>change({rotation:Number(e.target.value)})} data-testid="element-rotation-slider"/>
    {!hideSize&&<div className="element-numbers">{[['w','Breite'],['h','Höhe']].map(([key,label])=><label key={key}>{label} (px)<input type="number" min="1" max="800" step="1" value={Math.round(b[key]*10)/10} onChange={e=>change({[key]:Math.max(1,Number(e.target.value))})} data-testid={`element-${key}`}/></label>)}</div>}
    <div className="element-numbers">{[['x','Mitte X',b.w],['y','Mitte Y',b.h]].map(([key,label,dimension])=><label key={key}>{label}<input type="number" min={-800+dimension/2} max={800+dimension/2} step="any" value={Math.round((b[key]+dimension/2)*10)/10} onChange={e=>change({[key]:Number(e.target.value)-dimension/2})} data-testid={`element-${key}`}/></label>)}</div>
    <div className="element-move">{[[ArrowLeft,-5,0,'left','Nach links'],[ArrowUp,0,-5,'up','Nach oben'],[ArrowDown,0,5,'down','Nach unten'],[ArrowRight,5,0,'right','Nach rechts']].map(([Icon,dx,dy,id,label])=><button key={id} title={label} aria-label={label} onClick={()=>change({x:b.x+dx,y:b.y+dy})} data-testid={`element-move-${id}`}><Icon size={15}/></button>)}<button title="Horizontal zentrieren" aria-label="Zentrieren" onClick={()=>change({x:product.area.x+(product.area.w-b.w)/2})} data-testid="element-center"><AlignCenter size={15}/></button></div>
    </fieldset>{error&&<p className="property-error" role="alert" data-testid="element-boundary-error">{error}</p>}
  </section>;
};
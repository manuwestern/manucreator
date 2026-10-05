import { useEffect,useState } from 'react';
import { isInside } from '@/lib/transformGeometry';

export const DecorationProperties=({element:e,product,update,disabled})=>{
  const [error,setError]=useState('');
  useEffect(()=>setError(''),[e]);
  const stroke=value=>{
    const delta=value-(e.stroke_width??1.5),next={...e,stroke_width:value,x:e.x-delta/2,y:e.y-delta/2,w:e.w+delta,h:e.h+delta};
    if(!isInside(next,product.area,0)){setError('Diese Strichstärke passt nicht vollständig in die Gravurfläche. Die bisherige Einstellung bleibt erhalten.');return;}
    update(next);setError('');
  };
  return <fieldset className="decoration-properties" disabled={disabled||e.locked}><p data-testid="decoration-name">{e.field_label||'Dekoration'}</p><label htmlFor="decoration-stroke-width">Strichstärke <output data-testid="decoration-stroke-value">{Number(e.stroke_width??1.5).toFixed(1)} px</output><input id="decoration-stroke-width" type="range" min="0.3" max="8" step="0.1" value={Math.round((e.stroke_width??1.5)*10)/10} onChange={event=>stroke(Number(event.target.value))} data-testid="decoration-stroke-width"/></label>{e.locked&&<p className="property-status" data-testid="decoration-locked-note">Gesperrt</p>}{error&&<p className="property-error" role="alert" data-testid="decoration-boundary-error">{error}</p>}</fieldset>;
};
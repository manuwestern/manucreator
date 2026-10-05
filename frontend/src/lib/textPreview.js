import { studioApi } from './studioApi';
const cache=new Map();
export const effectValues=spec=>({text_mode:spec.text_mode||'filled',outline_width:spec.outline_width??1,shadow_enabled:spec.shadow_enabled||false,shadow_distance:spec.shadow_distance??3,shadow_angle:spec.shadow_angle??45});
export const visualKey=e=>e.kind==='image'?e.asset_id:JSON.stringify(e.kind==='decoration'?[e.ornament,e.w,e.h,e.stroke_width]:[e.text,e.font,e.font_size,e.curvature,effectValues(e)]);
export const getTextPreview = spec => {
  const normalized={text:spec.text || '',font:spec.font,font_size:Math.max(4,spec.font_size || Math.floor(spec.h*.76)),curvature:spec.curvature || 0,...effectValues(spec)};
  const key=JSON.stringify(normalized);
  if(!cache.has(key)) {
    if(cache.size>120)cache.delete(cache.keys().next().value);
    cache.set(key,studioApi('/text-preview',{method:'POST',body:normalized}).catch(e=>{cache.delete(key);throw e;}));
  }
  return cache.get(key);
};
export const getElementPreview=spec=>{
  if(spec.kind!=='decoration')return getTextPreview(spec);
  const body={ornament:spec.ornament,w:spec.w,h:spec.h,stroke_width:spec.stroke_width??1.5},key=JSON.stringify(body);
  if(!cache.has(key)){
    if(cache.size>180)cache.delete(cache.keys().next().value);
    cache.set(key,studioApi('/decoration-preview',{method:'POST',body}).catch(e=>{cache.delete(key);throw e;}));
  }
  return cache.get(key);
};
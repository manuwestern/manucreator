import { studioApi } from './studioApi';
import { adminApi } from './adminApi';
import { withPreviewRetry } from './previewRetry';
const cache=new Map();
export const effectValues=spec=>({text_mode:spec.text_mode||'filled',outline_width:spec.outline_width??1,shadow_enabled:spec.shadow_enabled||false,shadow_distance:spec.shadow_distance??3,shadow_angle:spec.shadow_angle??45});
export const visualKey=e=>e.kind==='image'?e.asset_id:JSON.stringify(e.kind==='shape'?[e.shape_type,e.shape_mode,e.w,e.h,e.stroke_width]:e.kind==='decoration'?[e.ornament,e.decoration_id,e.w,e.h,e.stroke_width]:[e.text,e.font,e.font_size,e.curvature,effectValues(e)]);
export const getTextPreview = spec => {
  const normalized={text:spec.text || '',font:spec.font,font_size:Math.max(4,spec.font_size || Math.floor(spec.h*.76)),curvature:spec.curvature || 0,...effectValues(spec)};
  const key=JSON.stringify(normalized);
  if(!cache.has(key)) {
    if(cache.size>120)cache.delete(cache.keys().next().value);
    cache.set(key,withPreviewRetry(()=>studioApi('/text-preview',{method:'POST',body:normalized})).catch(e=>{cache.delete(key);throw e;}));
  }
  return cache.get(key);
};
export const getElementPreview=(spec,adminMode=false)=>{
  if(spec.kind==='shape'){
    const body={shape_type:spec.shape_type,shape_mode:spec.shape_mode||'filled',w:spec.w,h:spec.h,stroke_width:spec.stroke_width??2},key=JSON.stringify(body);
    if(!cache.has(key)){if(cache.size>180)cache.delete(cache.keys().next().value);cache.set(key,withPreviewRetry(()=>studioApi('/shape-preview',{method:'POST',body})).catch(e=>{cache.delete(key);throw e;}));}
    return cache.get(key);
  }
  if(spec.kind!=='decoration')return getTextPreview(spec);
  if(spec.decoration_id){const key=`own:${adminMode}:${spec.decoration_id}`;if(!cache.has(key))cache.set(key,withPreviewRetry(()=>adminMode?adminApi(`/decorations/${spec.decoration_id}/sprite`):studioApi(`/decoration-assets/${spec.decoration_id}`)).catch(e=>{cache.delete(key);throw e;}));return cache.get(key);}
  const body={ornament:spec.ornament,w:spec.w,h:spec.h,stroke_width:spec.stroke_width??1.5},key=JSON.stringify(body);
  if(!cache.has(key)){
    if(cache.size>180)cache.delete(cache.keys().next().value);
    cache.set(key,withPreviewRetry(()=>studioApi('/decoration-preview',{method:'POST',body})).catch(e=>{cache.delete(key);throw e;}));
  }
  return cache.get(key);
};
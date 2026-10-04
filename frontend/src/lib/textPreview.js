import { studioApi } from './studioApi';
const cache=new Map();
export const getTextPreview = spec => {
  const normalized={text:spec.text || '',font:spec.font,font_size:Math.max(4,spec.font_size || Math.floor(spec.h*.76)),curvature:spec.curvature || 0};
  const key=JSON.stringify(normalized);
  if(!cache.has(key)) {
    if(cache.size>120)cache.delete(cache.keys().next().value);
    cache.set(key,studioApi('/text-preview',{method:'POST',body:normalized}).catch(e=>{cache.delete(key);throw e;}));
  }
  return cache.get(key);
};
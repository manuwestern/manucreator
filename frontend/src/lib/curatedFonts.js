import manifest from '@/data/curatedFonts.json';
import { existingFace } from './fontCatalog';
import { fonts } from './studioLayersLegacy';
const loaded=new Map();
export const curatedFamilies=manifest.families;
export const catalogVersion=manifest.version;
export const curatedFace=key=>curatedFamilies.flatMap(f=>f.variants).find(v=>v.key===key);
export const curatedFamily=key=>curatedFamilies.find(f=>f.variants.some(v=>v.key===key));
export const curatedCssFamily=key=>'Curated_'+key.replaceAll(/[^a-zA-Z0-9]/g,'_');
export const ensureFont=async key=>{
  if(key?.startsWith('fs:'))return existingFace(key);
  if(!key?.startsWith('curated:'))return document.fonts.load(`24px ${fonts.find(([id])=>id===key)?.[2]||'StudioSans'}`);
  const face=curatedFace(key);if(!face)throw new Error('Diese Schrift ist nicht in der bereitgestellten Auswahl.');
  if(!loaded.has(key))loaded.set(key,new FontFace(curatedCssFamily(key),`url(${face.url})`).load().then(font=>{document.fonts.add(font);return font;}).catch(e=>{loaded.delete(key);throw e;}));
  return loaded.get(key);
};
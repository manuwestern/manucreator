import { studioApi,productImage } from './studioApi';
const pending=new Map();
export const dynamicFamily = font => `StudioFace_${font.replace('fs:','')}`;
export const loadFace = async face => {
  const family=dynamicFamily(face.font);
  if(!pending.has(face.font)) {
    const promise=new FontFace(family,`url(${productImage(face.url)})`).load().then(f=>{document.fonts.add(f);return face;}).catch(error=>{pending.delete(face.font);throw error;});
    pending.set(face.font,promise);
  }
  await pending.get(face.font);return face;
};
export const existingFace = async font => loadFace(await studioApi(`/fonts/faces/${font.replace('fs:','')}`));
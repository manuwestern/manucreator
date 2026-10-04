import { defaultLayout } from './studioGeometry';
import { fitElement } from './transformGeometry';
import { dynamicFamily } from './fontCatalog';
import { curatedCssFamily } from './curatedFonts';
export { fonts } from './studioLayersLegacy';
import { fonts } from './studioLayersLegacy';
export const fullCrop = () => ({ x: 0, y: 0, w: 1, h: 1 });
export const familyFor = key => key?.startsWith('curated:')?curatedCssFamily(key):key?.startsWith('fs:') ? dynamicFamily(key) : fonts.find(([id]) => id === key)?.[2] || 'StudioSans';
export const newLayer = (kind, product, extra = {}) => {
  const a = product.area, box = fitElement({ x: a.x + a.w * .15, y: a.y + a.h * .35, w: a.w * .7, h: kind === 'text' ? Math.min(42, a.h * .2) : a.h * .5, rotation:0 }, a);
  return { id: crypto.randomUUID(), kind, text: kind === 'text' ? 'Dein Text'.slice(0, product.max_text) : '', font: 'curated:open-sans:400:normal', font_size:kind==='text'?Math.max(4,Math.min(24,box.h*.7)):0, curvature:0, rotation:0, image_ratio:0, asset_id: null, original_asset_id: null, crop: fullCrop(), locked: false, hidden: false, placeholder:false, image_type: product.templates.includes('photo') ? 'photo' : 'logo', ...box, ...extra };
};
export const migrateDesign = (design, product) => {
  if (design.elements) return {...design,elements:design.elements.map(e=>({rotation:0,curvature:0,font_size:0,image_ratio:0,...e}))};
  const layout = design.layout || defaultLayout(design, product), elements = [];
  if (design.template !== 'text' && design.asset_id) elements.push(newLayer('image', product, { id: 'legacy-image', asset_id: design.asset_id, ...layout.image, image_type: design.template }));
  if (design.text) elements.push(newLayer('text', product, { id: 'legacy-text', text: design.text, font: design.font, font_size:0, ...layout.text }));
  if (design.subtitle) elements.push(newLayer('text', product, { id: 'legacy-subtitle', text: design.subtitle, font: 'modern', font_size:0, ...layout.subtitle }));
  return { ...design, elements, layout: null, asset_id: null };
};
export const reframe = (design, product) => ({ ...design, product_id: product.id });
export const summarized = design => { const texts = design.elements.filter(e => e.kind === 'text' && !e.hidden).map(e => e.text); return { ...design, text: texts[0] || '', subtitle: (texts[1] || '').slice(0, 36), layout: null, asset_id: null }; };
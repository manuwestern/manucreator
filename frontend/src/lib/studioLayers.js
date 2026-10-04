import { constrain, defaultLayout } from './studioGeometry';
export const fullCrop = () => ({ x: 0, y: 0, w: 1, h: 1 });
export const fonts = [
  ['sans','Liberation Sans','StudioSans'], ['sans-bold','Liberation Sans · Fett','StudioSansBold'], ['sans-italic','Liberation Sans · Kursiv','StudioSansItalic'], ['serif','Liberation Serif','StudioSerif'], ['serif-italic','Liberation Serif · Kursiv','StudioSerifItalic'], ['mono','Liberation Mono','StudioMono'], ['narrow','Liberation Sans Narrow','StudioNarrow'], ['modern','Nimbus Sans','StudioModern'], ['classic','Nimbus Roman','StudioClassic'], ['bold','Nimbus Sans · Fett','StudioBold'],
];
export const familyFor = key => fonts.find(([id]) => id === key)?.[2] || 'StudioSans';
export const newLayer = (kind, product, extra = {}) => {
  const a = product.area, box = constrain({ x: a.x + a.w * .15, y: a.y + a.h * .35, w: a.w * .7, h: kind === 'text' ? Math.min(42, a.h * .2) : a.h * .5 }, a);
  return { id: crypto.randomUUID(), kind, text: kind === 'text' ? 'Dein Text'.slice(0, product.max_text) : '', font: 'sans', asset_id: null, original_asset_id: null, crop: fullCrop(), locked: false, hidden: false, image_type: product.templates.includes('photo') ? 'photo' : 'logo', ...box, ...extra };
};
export const migrateDesign = (design, product) => {
  if (design.elements) return design;
  const layout = design.layout || defaultLayout(design, product), elements = [];
  if (design.template !== 'text' && design.asset_id) elements.push(newLayer('image', product, { id: 'legacy-image', asset_id: design.asset_id, ...layout.image, image_type: design.template }));
  if (design.text) elements.push(newLayer('text', product, { id: 'legacy-text', text: design.text, font: design.font, ...layout.text }));
  if (design.subtitle) elements.push(newLayer('text', product, { id: 'legacy-subtitle', text: design.subtitle, font: 'modern', ...layout.subtitle }));
  return { ...design, elements, layout: null, asset_id: null };
};
export const reframe = (design, product) => ({ ...design, product_id: product.id, elements: design.elements.filter(e => e.kind === 'text' || product.templates.includes(e.image_type)).map(e => ({ ...e, text: e.text.slice(0, product.max_text), ...constrain(e, product.area) })) });
export const summarized = design => { const texts = design.elements.filter(e => e.kind === 'text' && !e.hidden).map(e => e.text); return { ...design, text: texts[0] || '', subtitle: (texts[1] || '').slice(0, 36), layout: null, asset_id: null }; };
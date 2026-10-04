export const constrain = (box, area) => {
  let { x, y, w, h } = box;
  const { x: ax, y: ay, w: aw, h: ah } = area;
  w = Math.max(10, Math.min(w, aw)); h = Math.max(10, Math.min(h, ah));
  if (area.shape === 'circle') {
    const scale = Math.min(1, .999 / Math.sqrt((w / aw) ** 2 + (h / ah) ** 2));
    w *= scale; h *= scale;
    if (h < 10) { h = 10; w = Math.min(w, aw * Math.sqrt(Math.max(0, .998001 - (h / ah) ** 2))); }
    if (w < 10) { w = 10; h = Math.min(h, ah * Math.sqrt(Math.max(0, .998001 - (w / aw) ** 2))); }
    const cx = ax + aw / 2, cy = ay + ah / 2, rx = aw / 2, ry = ah / 2;
    const dy = Math.max(0, ry * Math.sqrt(Math.max(0, 1 - (w / aw) ** 2)) - h / 2);
    const by = Math.max(cy - dy, Math.min(y + h / 2, cy + dy));
    const dx = Math.max(0, rx * Math.sqrt(Math.max(0, 1 - ((Math.abs(by - cy) + h / 2) / ry) ** 2)) - w / 2);
    const bx = Math.max(cx - dx, Math.min(x + w / 2, cx + dx));
    return { x: bx - w / 2, y: by - h / 2, w, h };
  }
  return { x: Math.max(ax, Math.min(x, ax + aw - w)), y: Math.max(ay, Math.min(y, ay + ah - h)), w, h };
};
export const defaultLayout = (design, product) => {
  const { x, y, w, h } = product.area, photo = design.template !== 'text';
  const size = { small: 32, medium: 42, large: 52 }[design.size];
  const shift = { top: -h * .15, center: 0, bottom: h * .15 }[design.position];
  const side = Math.min(w * .6, h * .48), textY = photo ? y + h * .68 : y + h * .42;
  const boxes = { text: { x: x + w * .08, y: textY + shift, w: w * .84, h: Math.min(size, h * .24) }, subtitle: { x: x + w * .08, y: textY + size + shift, w: w * .84, h: Math.min(25, h * .15) }, image: { x: x + (w - side) / 2, y: y + h * .08 + shift, w: side, h: side } };
  return Object.fromEntries(Object.entries(boxes).map(([key, b]) => [key, constrain(b, product.area)]));
};
export const layoutFor = (design, product) => design.layout || defaultLayout(design, product);
export const fontFamily = { classic: 'StudioClassic', modern: 'StudioModern', bold: 'StudioBold' };
export const fontSize = (text, font, box) => {
  const ctx = document.createElement('canvas').getContext('2d');
  let size = Math.max(6, Math.floor(box.h * .76));
  while (size > 6) { ctx.font = `${size}px ${font}`; if (ctx.measureText(text).width <= box.w - 4) break; size--; }
  return size;
};
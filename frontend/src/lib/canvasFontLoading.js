import { withPreviewRetry } from './previewRetry';

const pending = new Map();
const unquote = value => value.replace(/["']/g, '').trim();
const declaration = family => {
  for (const sheet of document.styleSheets) {
    let rules;
    try { rules = sheet.cssRules; } catch { continue; }
    for (const rule of rules) {
      if (rule.type !== 5 || unquote(rule.style.getPropertyValue('font-family')) !== family) continue;
      const source = rule.style.getPropertyValue('src').replace(/url\(["']?([^"')]+)["']?\)/g, (_, url) => `url("${new URL(url, sheet.href || document.baseURI).href}")`);
      return source;
    }
  }
  return null;
};

export const loadCanvasFont = family => {
  if (!pending.has(family)) pending.set(family, (async () => {
    try { return await document.fonts.load(`32px ${family}`); }
    catch (error) {
      // CSS FontFace failures are sticky. Load the identical declared file anew.
      const source = declaration(family);
      if (!source) throw error;
      return withPreviewRetry(async () => {
        const face = await new FontFace(family, source).load();
        document.fonts.add(face);
        return [face];
      });
    }
  })().catch(error => { pending.delete(family); throw error; }));
  return pending.get(family);
};
import { rotatedCorners } from './transformGeometry';

const bounds = e => { const c = rotatedCorners(e), xs = c.map(p => p.x), ys = c.map(p => p.y); return { left: Math.min(...xs), right: Math.max(...xs), top: Math.min(...ys), bottom: Math.max(...ys), cx: e.x + e.w / 2, cy: e.y + e.h / 2 }; };

// Targets: engraving-area centre plus edges/centres of other visible elements (locked allowed, hidden excluded).
export const snapCandidate = (candidate, others, area, threshold) => {
  const b = bounds(candidate), targetsX = [area.x + area.w / 2], targetsY = [area.y + area.h / 2];
  others.filter(o => !o.hidden && o.id !== candidate.id).forEach(o => { const t = bounds(o); targetsX.push(t.left, t.cx, t.right); targetsY.push(t.top, t.cy, t.bottom); });
  let dx = null, dy = null, gx = null, gy = null;
  for (const t of targetsX) for (const v of [b.left, b.cx, b.right]) { const d = t - v; if (Math.abs(d) <= threshold && (dx === null || Math.abs(d) < Math.abs(dx))) { dx = d; gx = t; } }
  for (const t of targetsY) for (const v of [b.top, b.cy, b.bottom]) { const d = t - v; if (Math.abs(d) <= threshold && (dy === null || Math.abs(d) < Math.abs(dy))) { dy = d; gy = t; } }
  return { x: candidate.x + (dx || 0), y: candidate.y + (dy || 0), guides: [gx !== null && { axis: 'x', pos: gx }, gy !== null && { axis: 'y', pos: gy }].filter(Boolean) };
};

export const mmPerPx = product => { const mm = parseFloat(String(product.area_mm || '').replace(',', '.').match(/\d+(?:\.\d+)?/)?.[0]); return mm > 0 ? mm / product.area.w : null; };

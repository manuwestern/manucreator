import { objectBounds } from './ObjectArtwork';

export const ENGRAVING_AREA = { cx: 300, cy: 300, radius: 250 };
export const GRID_STEP = 20;

function anchors(o) {
  const b = objectBounds(o), angle = (o.rotation || 0) * Math.PI / 180, scale = o.scale || 1;
  const points = [[b.x, b.y], [b.x + b.w, b.y], [b.x, b.y + b.h], [b.x + b.w, b.y + b.h]].map(([x, y]) => ({ x: o.x + (x * Math.cos(angle) - y * Math.sin(angle)) * scale, y: o.y + (x * Math.sin(angle) + y * Math.cos(angle)) * scale }));
  return { x: [Math.min(...points.map(p => p.x)), o.x, Math.max(...points.map(p => p.x))], y: [Math.min(...points.map(p => p.y)), o.y, Math.max(...points.map(p => p.y))] };
}

export function alignObject(object, objects, unitsPerPixel, snapEnabled, gridEnabled) {
  const active = anchors(object);
  const threshold = unitsPerPixel * (snapEnabled ? 7 : 2);
  const guides = [];
  const patch = { x: object.x, y: object.y };
  for (const axis of ['x', 'y']) {
    const targets = [];
    objects.filter(o => o.id !== object.id && o.visible).forEach(o => anchors(o)[axis].forEach(value => targets.push({ value, objectId: o.id })));
    // Explicit grid mode is authoritative: object anchors must never pull an axis off-grid.
    if (snapEnabled && gridEnabled) {
      patch[axis] = Math.round(object[axis] / GRID_STEP) * GRID_STEP;
      if (patch[axis] === 300) guides.push({ axis, value: 300, centre: true });
      else {
        const shifted = active[axis].map(value => value + patch[axis] - object[axis]);
        const match = targets.find(target => shifted.some(value => Math.abs(value - target.value) <= .5));
        if (match) guides.push({ axis, value: match.value, centre: false, objectId: match.objectId });
      }
      continue;
    }
    // In smart-guide mode, centre alignment takes precedence over nearby object edges.
    if (Math.abs(object[axis] - 300) <= threshold) {
      if (snapEnabled) patch[axis] = 300;
      guides.push({ axis, value: 300, centre: true });
      continue;
    }
    let nearest = null;
    active[axis].forEach(anchor => targets.forEach(target => {
      const delta = target.value - anchor;
      if (Math.abs(delta) <= threshold && (!nearest || Math.abs(delta) < Math.abs(nearest.delta))) nearest = { ...target, delta };
    }));
    if (nearest) {
      if (snapEnabled) patch[axis] += nearest.delta;
      guides.push({ axis, value: nearest.value, centre: !!nearest.centre, objectId: nearest.objectId });
    }
  }
  return { patch, guides };
}
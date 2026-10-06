import { objectBounds } from './ObjectArtwork';

export const SelectionHandles = ({ object: o, size, onStart }) => {
  if (!o || !o.visible || o.locked) return null;
  const raw = objectBounds(o), pixel = 600 / size / (o.scale || 1), touch = 44 * pixel;
  // Separate handles even on tiny objects, leaving their centre available for dragging.
  const w = Math.max(raw.w, 70 * pixel), h = o.type === 'line' ? raw.h : Math.max(raw.h, 56 * pixel);
  const b = { x: raw.x + (raw.w - w) / 2, y: raw.y + (raw.h - h) / 2, w, h };
  const rotationY = b.y - 34 * pixel;
  const handles = o.type === 'line' ? [[b.x, 0], [b.x + b.w, 0]] : [[b.x, b.y], [b.x + b.w, b.y], [b.x, b.y + b.h], [b.x + b.w, b.y + b.h]];
  return <g transform={`translate(${o.x} ${o.y}) rotate(${o.rotation || 0}) scale(${o.scale || 1})`} className="selection-outline" fill="white" stroke="#658058" strokeWidth={pixel} data-testid="object-selection">
    <rect x={b.x} y={b.y} width={b.w} height={b.h} fill="none" pointerEvents="none" /><path d={`M0 ${b.y} V${rotationY}`} pointerEvents="none" />
    <g onPointerDown={e => onStart(e, o, 'rotate')} className="rotate-handle" data-testid="object-rotate-handle"><circle cx="0" cy={rotationY} r={22 * pixel} fill="transparent" stroke="none" /><circle cx="0" cy={rotationY} r={10 * pixel} /><path d={`M${4 * pixel} ${rotationY - 3 * pixel} a${5 * pixel} ${5 * pixel} 0 1 0 0 ${7 * pixel} m0 ${-7 * pixel} v${4 * pixel} h${-4 * pixel}`} fill="none" /></g>
    {handles.map(([x, y], i) => <g key={i} onPointerDown={e => onStart(e, o, 'scale')} className="scale-handle" data-testid={`object-scale-handle-${i}`}><rect x={x - touch / 2} y={y - touch / 2} width={touch} height={touch} fill="transparent" stroke="none" /><rect x={x - 4 * pixel} y={y - 4 * pixel} width={8 * pixel} height={8 * pixel} rx={2 * pixel} /></g>)}
  </g>;
};
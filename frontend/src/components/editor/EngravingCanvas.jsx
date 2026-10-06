import { useEffect, useRef, useState } from 'react';

export const Branch = () => <g fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
  <path d="M-95 23 Q-30-12 94-17 M-62 9 Q-62-15-75-22 M-38 0 Q-31-25-17-37 M-7-7 Q4-35 25-45 M26-13 Q44-33 62-38 M50-16 Q68-8 79 6 M16-12 Q28 11 40 21 M-18-5 Q-13 19 4 29 M-48 5 Q-41 29-23 37" />
  <path d="M-75-22 Q-51-20-62 9 Q-78-2-75-22 M-17-37 Q-14-16-38 0 Q-38-23-17-37 M25-45 Q24-20-7-7 Q3-33 25-45 M62-38 Q56-17 26-13 Q43-35 62-38 M94-17 Q81-30 66-17 Q78-9 94-17 M79 6 Q59 8 50-16 Q75-10 79 6 M40 21 Q14 19 16-12 Q38 0 40 21 M4 29 Q-23 17-18-5 Q1 9 4 29 M-23 37 Q-45 36-48 5 Q-25 21-23 37" />
</g>;

const ObjectArtwork = ({ object: o }) => {
  if (o.type === 'heart') return <path d="M0 21 C-5 10-28-7-18-20 C-10-29-1-17 0-10 C4-27 17-29 21-18 C27-5 8 11 0 21Z" fill="none" stroke="currentColor" strokeWidth="3.4" strokeLinejoin="round" />;
  if (o.type === 'branch') return <Branch />;
  if (o.type === 'image') return <image href={o.src} x="-85" y="-85" width="170" height="170" preserveAspectRatio="xMidYMid meet" />;
  const width = Math.min(360, Math.max(100, (o.text || ' ').length * 26));
  return <>
    <defs><path id={`arc-${o.id}`} d={`M${-width / 2} 16 Q0 ${16 - (o.curve || 0) * .8} ${width / 2} 16`} /></defs>
    <text fontFamily={o.font || 'Cormorant Garamond'} fontSize={Math.min(57, width / Math.max(1, o.text.length) * 2.1)} fontWeight="600" fill="currentColor" textAnchor="middle" data-testid={`engraving-text-${o.id}`}>
      <textPath href={`#arc-${o.id}`} startOffset="50%">{o.text}</textPath>
    </text>
  </>;
};

function objectBounds(o) {
  if (o.type === 'text') { const width = Math.min(360, Math.max(100, (o.text || ' ').length * 26)); return { x: -width / 2 - 7, y: -43 - Math.max(0, o.curve || 0) * .4, w: width + 14, h: 66 + Math.abs(o.curve || 0) * .4 }; }
  if (o.type === 'heart') return { x: -29, y: -32, w: 58, h: 62 };
  if (o.type === 'image') return { x: -90, y: -90, w: 180, h: 180 };
  return { x: -103, y: -52, w: 206, h: 96 };
}

export const EngravingCanvas = ({ editor, preview = false, onSelect }) => {
  const host = useRef(null); const svg = useRef(null); const drag = useRef(null);
  const [size, setSize] = useState(300);
  useEffect(() => {
    const observer = new ResizeObserver(([entry]) => setSize(Math.max(70, Math.min(entry.contentRect.width - 24, entry.contentRect.height - 24, 660))));
    observer.observe(host.current); return () => observer.disconnect();
  }, []);
  const point = e => { const r = svg.current.getBoundingClientRect(); return { x: (e.clientX - r.left) * 600 / r.width, y: (e.clientY - r.top) * 600 / r.height }; };
  const start = (e, o, kind = 'move') => {
    if (preview || o.locked) return;
    e.stopPropagation(); e.preventDefault(); editor.select(o.id); if (onSelect) onSelect(o);
    editor.begin(); drag.current = { start: point(e), object: { ...o }, kind };
    e.currentTarget.setPointerCapture(e.pointerId);
  };
  const move = e => {
    if (!drag.current) return;
    const { start: p, object: o, kind } = drag.current; const next = point(e);
    let patch;
    if (kind === 'rotate') patch = { rotation: Math.round(Math.atan2(next.y - o.y, next.x - o.x) * 180 / Math.PI + 90) };
    else if (kind === 'scale') patch = { scale: Math.max(.4, Math.min(1.6, o.scale * Math.hypot(next.x - o.x, next.y - o.y) / Math.hypot(p.x - o.x, p.y - o.y))) };
    else patch = { x: Math.max(130, Math.min(470, o.x + next.x - p.x)), y: Math.max(130, Math.min(470, o.y + next.y - p.y)) };
    editor.patchObject(o.id, patch, false);
  };
  const end = () => { if (drag.current) { editor.end(); drag.current = null; } };
  return <div className="canvas-art" ref={host} data-testid={preview ? 'preview-art' : 'canvas-art'}>
    <svg ref={svg} width={size} height={size} viewBox="0 0 600 600" className={`engraving-canvas ${preview ? 'is-preview' : ''}`} data-testid={preview ? 'preview-canvas' : 'engraving-canvas'} aria-label="Deine Gestaltung auf der Holzscheibe" onPointerMove={move} onPointerUp={end} onPointerCancel={end}>
      <image href="/images/wood-slice.webp" width="600" height="600" className="wood-image" preserveAspectRatio="xMidYMid meet" data-testid={preview ? 'preview-wood' : 'wood-product'} />
      {editor.objects.filter(o => o.visible).map(o => {
        const selected = !preview && o.id === editor.selectedId; const b = objectBounds(o);
        return <g key={o.id} transform={`translate(${o.x} ${o.y}) rotate(${o.rotation || 0}) scale(${o.scale || 1})`} className={`engraved-object ${o.locked ? 'locked' : ''}`} style={{ color: '#603715' }} role={preview ? undefined : 'button'} tabIndex={preview ? undefined : 0} aria-label={`${o.name}${o.locked ? ', gesperrt' : ', auswählen und verschieben'}`} data-testid={`${preview ? 'preview-' : ''}object-${o.id}`} onPointerDown={e => start(e, o)} onKeyDown={e => {
          if (preview || o.locked) return;
          if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); editor.select(o.id); onSelect?.(o); }
          const dir = { ArrowLeft: [-2, 0], ArrowRight: [2, 0], ArrowUp: [0, -2], ArrowDown: [0, 2] }[e.key];
          if (dir) { e.preventDefault(); editor.patchObject(o.id, { x: Math.max(130, Math.min(470, o.x + dir[0])), y: Math.max(130, Math.min(470, o.y + dir[1])) }); }
        }}>
          {!preview && <rect x={b.x} y={b.y} width={b.w} height={b.h} fill="transparent" />}
          <ObjectArtwork object={o} />
          {selected && !o.locked && <g className="selection-outline" fill="white" stroke="#658058" strokeWidth="1.4" data-testid="object-selection">
            <rect x={b.x} y={b.y} width={b.w} height={b.h} fill="none" />
            <path d={`M0 ${b.y} V${b.y - 21}`} />
            <g onPointerDown={e => start(e, o, 'rotate')} className="rotate-handle" data-testid="object-rotate-handle"><circle cx="0" cy={b.y - 33} r="21" fill="transparent" stroke="none" /><circle cx="0" cy={b.y - 33} r="13" /><path d={`M5 ${b.y - 37} A6 6 0 1 0 5 ${b.y - 29} M5 ${b.y - 37} v5 h-5`} fill="none" /></g>
            {[[b.x, b.y], [b.x + b.w, b.y], [b.x, b.y + b.h], [b.x + b.w, b.y + b.h]].map(([x, y], i) => <g key={i} onPointerDown={e => start(e, o, 'scale')} className="scale-handle" data-testid={`object-scale-handle-${i}`}><rect x={x - 18} y={y - 18} width="36" height="36" fill="transparent" stroke="none" /><rect x={x - 6} y={y - 6} width="12" height="12" rx="3" /></g>)}
          </g>}
        </g>;
      })}
    </svg>
  </div>;
};
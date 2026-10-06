import { useEffect, useId, useRef, useState } from 'react';
import { ObjectArtwork, objectBounds } from './ObjectArtwork';
import { isShape, normalizeRotation } from './editorCatalog';
import { SelectionHandles } from './SelectionHandles';
import { alignObject, ENGRAVING_AREA, GRID_STEP } from './alignment';

export const EngravingCanvas = ({ editor, preview = false, onSelect, snapEnabled = true, gridEnabled = false }) => {
  const host = useRef(null), svg = useRef(null), drag = useRef(null);
  const [size, setSize] = useState(300), [guides, setGuides] = useState([]);
  const id = useId().replace(/[^a-zA-Z0-9]/g, '');
  const clipId = `engraving-clip-${id}`, gridId = `engraving-grid-${id}`;
  useEffect(() => {
    const observer = new ResizeObserver(([entry]) => setSize(Math.max(70, Math.min(entry.contentRect.width - 24, entry.contentRect.height - 24, 660))));
    observer.observe(host.current); return () => observer.disconnect();
  }, []);
  const point = e => { const r = svg.current.getBoundingClientRect(); return { x: (e.clientX - r.left) * 600 / r.width, y: (e.clientY - r.top) * 600 / r.height }; };
  const start = (e, o, kind = 'move') => {
    if (preview || drag.current || (e.pointerType === 'mouse' && e.button !== 0)) return;
    e.stopPropagation(); e.preventDefault(); editor.select(o.id); onSelect?.(o);
    if (o.locked) return;
    editor.begin(); drag.current = { start: point(e), clientX: e.clientX, clientY: e.clientY, object: { ...o }, kind, pointerId: e.pointerId };
    svg.current.setPointerCapture(e.pointerId);
  };
  const move = e => {
    if (!drag.current || drag.current.pointerId !== e.pointerId) return;
    const { start: p, object: o, kind, clientX, clientY } = drag.current;
    if (Math.hypot(e.clientX - clientX, e.clientY - clientY) < 3) return;
    const next = point(e); let patch;
    if (kind === 'rotate') patch = { rotation: normalizeRotation(Math.round(Math.atan2(next.y - o.y, next.x - o.x) * 180 / Math.PI + 90)) };
    else if (kind === 'scale') {
      const ratio = Math.hypot(next.x - o.x, next.y - o.y) / Math.max(1, Math.hypot(p.x - o.x, p.y - o.y));
      if (isShape(o)) {
        const dimensions = [o.widthMm, o.heightMm].filter(Boolean);
        const factor = Math.max(.5 / Math.min(...dimensions), ratio);
        patch = { widthMm: Number((o.widthMm * factor).toFixed(2)), heightMm: Number((o.heightMm * factor).toFixed(2)) };
      } else patch = { scale: Math.max(.01, o.scale * ratio) };
    } else {
      const units = 600 / svg.current.getBoundingClientRect().width;
      const desired = { ...o, x: o.x + (e.clientX - clientX) * units, y: o.y + (e.clientY - clientY) * units };
      const aligned = alignObject(desired, editor.objects, units, snapEnabled, gridEnabled);
      patch = aligned.patch; setGuides(aligned.guides);
    }
    editor.patchObject(o.id, patch, false);
  };
  const end = () => { if (drag.current) { editor.end(); drag.current = null; setGuides([]); } };
  return <div className="canvas-art" ref={host} data-testid={preview ? 'preview-art' : 'canvas-art'}>
    <svg ref={svg} width={size} height={size} viewBox="0 0 600 600" className={`engraving-canvas ${preview ? 'is-preview' : ''}`} data-testid={preview ? 'preview-canvas' : 'engraving-canvas'} aria-label="Deine Gestaltung auf der Holzscheibe" onPointerMove={move} onPointerUp={end} onPointerCancel={end} onLostPointerCapture={end}>
      <defs><clipPath id={clipId}><circle cx={ENGRAVING_AREA.cx} cy={ENGRAVING_AREA.cy} r={ENGRAVING_AREA.radius} /></clipPath><pattern id={gridId} width={GRID_STEP} height={GRID_STEP} patternUnits="userSpaceOnUse"><path d={`M${GRID_STEP} 0 H0 V${GRID_STEP}`} fill="none" stroke="#647c50" strokeOpacity=".23" strokeWidth=".7" /></pattern></defs>
      <image href="/images/wood-slice.webp" width="600" height="600" className="wood-image" preserveAspectRatio="xMidYMid meet" data-testid={preview ? 'preview-wood' : 'wood-product'} />
      {!preview && gridEnabled && <rect width="600" height="600" fill={`url(#${gridId})`} clipPath={`url(#${clipId})`} pointerEvents="none" data-testid="snap-grid" />}
      {!preview && <circle cx={ENGRAVING_AREA.cx} cy={ENGRAVING_AREA.cy} r={ENGRAVING_AREA.radius} fill="none" stroke="#677d4f" strokeOpacity=".5" strokeWidth="1" strokeDasharray="5 6" pointerEvents="none" data-testid="engraving-boundary" />}
      <g clipPath={`url(#${clipId})`} data-testid={preview ? 'preview-engraving-area' : 'engraving-area'}>
        {editor.objects.filter(o => o.visible).map(o => {
          const b = objectBounds(o), pixel = 600 / size / (o.scale || 1), touch = 44 * pixel;
          const hit = { w: Math.max(b.w, touch), h: Math.max(b.h, touch) };
          return <g key={o.id} transform={`translate(${o.x} ${o.y}) rotate(${o.rotation || 0}) scale(${o.scale || 1})`} className={`engraved-object ${o.locked ? 'locked' : ''}`} style={{ color: '#603715' }} role={preview ? undefined : 'button'} tabIndex={preview ? undefined : 0} aria-label={`${o.name}${o.locked ? ', gesperrt' : ', auswählen und verschieben'}`} data-testid={`${preview ? 'preview-' : ''}object-${o.id}`} onPointerDown={e => start(e, o)} onKeyDown={e => {
            if (preview) return;
            if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); editor.select(o.id); onSelect?.(o); }
            const dir = { ArrowLeft: [-2, 0], ArrowRight: [2, 0], ArrowUp: [0, -2], ArrowDown: [0, 2] }[e.key];
            if (dir && !o.locked) { e.preventDefault(); editor.patchObject(o.id, { x: o.x + dir[0], y: o.y + dir[1] }); }
          }}>
            {!preview && <rect x={b.x + (b.w - hit.w) / 2} y={b.y + (b.h - hit.h) / 2} width={hit.w} height={hit.h} fill="transparent" data-testid={`object-hitarea-${o.id}`} />}
            <ObjectArtwork object={o} preview={preview} />
          </g>;
        })}
      </g>
      {!preview && guides.map(guide => <g key={guide.axis} pointerEvents="none" data-testid={`alignment-guide-${guide.axis}`} data-kind={guide.centre ? 'centre' : 'object'}><line x1={guide.axis === 'x' ? guide.value : 25} x2={guide.axis === 'x' ? guide.value : 575} y1={guide.axis === 'y' ? guide.value : 25} y2={guide.axis === 'y' ? guide.value : 575} stroke="#537e36" strokeWidth={1.3 * 600 / size} strokeDasharray={guide.centre ? '5 4' : '2 3'} /></g>)}
      {!preview && <SelectionHandles object={editor.selected} size={size} onStart={start} />}
    </svg>
    {!preview && guides.length > 0 && <div className="alignment-status" data-testid="alignment-status" aria-live="polite">{guides.length === 2 && guides.every(g => g.centre) ? 'Mittig ausgerichtet' : guides.some(g => g.centre) ? 'An der Mitte ausgerichtet' : 'Am Objekt ausgerichtet'}</div>}
  </div>;
};
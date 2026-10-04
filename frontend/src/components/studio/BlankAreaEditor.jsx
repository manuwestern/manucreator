import { useEffect, useRef, useState } from 'react';
import { Stage, Layer, Image as KImage, Rect, Ellipse, Group, Transformer } from 'react-konva';
import { Circle, Scan, Square } from 'lucide-react';
import { useCanvasSize } from '@/hooks/useCanvasSize';
import { useCanvasAssets } from '@/hooks/useCanvasAssets';

export const normalizeArea = value => {
  let { x, y, w, h, shape } = value;
  w = Math.max(30, Math.min(800, w)); h = Math.max(30, Math.min(800, h));
  if (shape === 'circle') w = h = Math.min(w, h);
  return { x: Math.max(0, Math.min(x, 800 - w)), y: Math.max(0, Math.min(y, 800 - h)), w, h, shape };
};

export const BlankAreaEditor = ({ image, area, onChange }) => {
  const [wrap, size] = useCanvasSize(), { blank, error } = useCanvasAssets(image), group = useRef(), transformer = useRef(), stage = useRef();
  const [drawing, setDrawing] = useState(false), start = useRef(null), scale = size / 800;
  useEffect(() => { transformer.current?.nodes(group.current && !drawing ? [group.current] : []); }, [area, drawing]);
  const point = () => { const p = stage.current.getPointerPosition(); return { x: Math.max(0, Math.min(800, p.x / scale)), y: Math.max(0, Math.min(800, p.y / scale)) }; };
  const move = () => { if (!start.current) return; const p = point(), s = start.current; onChange(normalizeArea({ x: Math.min(s.x, p.x), y: Math.min(s.y, p.y), w: Math.abs(p.x - s.x), h: Math.abs(p.y - s.y), shape: area.shape })); };
  const end = () => { if (start.current) { move(); start.current = null; setDrawing(false); } };
  const commit = e => { const n = e.target; const a = normalizeArea({ x: n.x(), y: n.y(), w: n.width() * n.scaleX(), h: n.height() * n.scaleY(), shape: area.shape }); n.scale({ x: 1, y: 1 }); n.position(a); onChange(a); };
  return <section className="blank-area-editor"><div className="area-toolbar">{[['rect',Square,'Rechteck'],['circle',Circle,'Kreis']].map(([shape,Icon,label]) => <button type="button" key={shape} aria-pressed={shape === area.shape} onClick={() => onChange(normalizeArea({ ...area, shape }))} data-testid={`area-shape-${shape}`}><Icon size={15} />{label}</button>)}<button type="button" aria-pressed={drawing} onClick={() => setDrawing(v => !v)} data-testid="area-draw"><Scan size={16} />Fläche zeichnen</button></div>
    <div ref={wrap} className={`blank-board ${drawing ? 'is-drawing' : ''}`} data-testid="admin-area-canvas" data-area={JSON.stringify(area)}><Stage width={size} height={size} scaleX={scale} scaleY={scale} ref={stage} onMouseDown={() => { if (drawing) start.current = point(); }} onTouchStart={() => { if (drawing) start.current = point(); }} onMouseMove={move} onTouchMove={move} onMouseUp={end} onTouchEnd={end}>
      <Layer><KImage image={blank} width={800} height={800} listening={false} /><Group ref={group} x={area.x} y={area.y} width={area.w} height={area.h} draggable={!drawing} listening={!drawing} onDragEnd={commit} onTransformEnd={commit} dragBoundFunc={p => { const b = normalizeArea({ ...area, x: p.x / scale, y: p.y / scale }); return { x: b.x * scale, y: b.y * scale }; }}>{area.shape === 'circle' ? <Ellipse x={area.w / 2} y={area.h / 2} radiusX={area.w / 2} radiusY={area.h / 2} fill="#56794230" stroke="#567942" strokeWidth={2 / scale} /> : <Rect width={area.w} height={area.h} fill="#56794230" stroke="#567942" strokeWidth={2 / scale} />}</Group><Transformer ref={transformer} rotateEnabled={false} flipEnabled={false} keepRatio={area.shape === 'circle'} enabledAnchors={['top-left','top-right','bottom-left','bottom-right']} anchorSize={12} borderStroke="#567942" anchorStroke="#567942" boundBoxFunc={(old, next) => next.width < 30 * scale || next.height < 30 * scale ? old : next} /></Layer>
    </Stage>{error && <p className="studio-error" role="alert" data-testid="admin-photo-error">{error}</p>}</div>
    <div className="element-numbers">{[['x','Links'],['y','Oben'],['w','Breite'],['h','Höhe']].map(([key,label]) => <label key={key}>{label} (px)<input type="number" min="0" max="800" step="1" value={Math.round(area[key])} onChange={e => onChange(normalizeArea({ ...area, [key]: Number(e.target.value), ...(area.shape === 'circle' && ['w','h'].includes(key) ? { w: Number(e.target.value), h: Number(e.target.value) } : {}) }))} data-testid={`area-${key}`} /></label>)}</div>
  </section>;
};
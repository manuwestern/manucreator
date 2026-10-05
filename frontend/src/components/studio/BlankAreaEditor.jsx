import { useEffect, useRef, useState } from 'react';
import { Stage, Layer, Image as KImage, Transformer } from 'react-konva';
import { Circle, Scan, Square, Trash2 } from 'lucide-react';
import { useCanvasSize } from '@/hooks/useCanvasSize';
import { useCanvasAssets } from '@/hooks/useCanvasAssets';
import { MaskRegionNode } from './MaskRegionNode';
import '@/styles/studio-masks.css';

export const normalizeArea = (value, minimum = 30) => {
  let { x, y, w, h, shape } = value;
  w = Math.max(minimum, Math.min(800, w)); h = Math.max(minimum, Math.min(800, h));
  if (shape === 'circle') w = h = Math.min(w, h);
  return { ...value, x: Math.max(0, Math.min(x, 800-w)), y: Math.max(0, Math.min(y, 800-h)), w, h, shape };
};

export const BlankAreaEditor = ({ image, area, exclusions = [], onChange, onExclusionsChange }) => {
  const [wrap, size] = useCanvasSize(), { blank, error, retry } = useCanvasAssets(image);
  const nodes = useRef({}), transformer = useRef(), stage = useRef(), start = useRef(null);
  const [selected, setSelected] = useState('area'), [drawing, setDrawing] = useState(false);
  const active = exclusions.find(zone => zone.id === selected) || area;
  const hole = active !== area, scale = size/800, minimum = hole ? 2 : 30;
  const prefix = hole ? 'exclusion' : 'area';
  useEffect(() => { transformer.current?.nodes(!drawing && nodes.current[selected] ? [nodes.current[selected]] : []); }, [selected, drawing, area, exclusions]);
  const select = id => { setSelected(id); setDrawing(false); start.current = null; };
  const update = value => {
    const next = normalizeArea(value, minimum);
    if (hole) onExclusionsChange(exclusions.map(zone => zone.id === selected ? next : zone));
    else onChange(next);
  };
  const add = shape => {
    if (exclusions.length >= 24) return;
    const w = Math.max(8, Math.min(area.w, area.h)*.18), id = crypto.randomUUID();
    onExclusionsChange([...exclusions, { id, shape, x: area.x+(area.w-w)/2, y: area.y+(area.h-w)/2, w, h: w }]);
    select(id);
  };
  const point = () => { const p = stage.current.getPointerPosition(); return { x: Math.max(0, Math.min(800, p.x/scale)), y: Math.max(0, Math.min(800, p.y/scale)) }; };
  const move = () => {
    if (!start.current) return;
    const p = point(), s = start.current;
    let w = Math.abs(p.x-s.x), h = Math.abs(p.y-s.y);
    if (active.shape === 'circle') w = h = Math.min(w, h);
    update({ ...active, x: p.x < s.x ? s.x-w : s.x, y: p.y < s.y ? s.y-h : s.y, w, h });
  };
  const end = () => { if (start.current) { move(); start.current = null; setDrawing(false); } };
  return <section className="blank-area-editor" data-testid="admin-mask-editor">
    <div className="mask-regions" aria-label="Maskenbereiche">
      <button type="button" aria-pressed={!hole} onClick={() => select('area')} data-testid="mask-select-area"><Scan size={15}/>Gravurfläche</button>
      {exclusions.map((zone, index) => <button type="button" key={zone.id} aria-pressed={selected === zone.id} onClick={() => select(zone.id)} data-testid={`mask-select-exclusion-${zone.id}`}>{zone.shape === 'circle' ? <Circle size={15}/> : <Square size={15}/>}Aussparung {index+1}</button>)}
    </div>
    <div className="mask-add-toolbar"><span data-testid="mask-exclusion-count">Aussparungen · {exclusions.length}/24</span>{[['rect',Square,'Rechteck'],['circle',Circle,'Kreis']].map(([shape,Icon,label]) => <button type="button" key={shape} disabled={exclusions.length >= 24} onClick={() => add(shape)} data-testid={`exclusion-add-${shape}`}><Icon size={15}/>+ {label}</button>)}</div>
    <div className="area-toolbar">{[['rect',Square,'Rechteck'],['circle',Circle,'Kreis']].map(([shape,Icon,label]) => <button type="button" key={shape} aria-pressed={shape === active.shape} onClick={() => update({ ...active, shape })} data-testid={`${prefix}-shape-${shape}`}><Icon size={15}/>{label}</button>)}<button type="button" aria-pressed={drawing} onClick={() => { start.current = null; setDrawing(v => !v); }} data-testid="area-draw"><Scan size={16}/>{drawing ? 'Zeichnen abbrechen' : hole ? 'Aussparung zeichnen' : 'Fläche zeichnen'}</button>{hole && <button type="button" title="Aussparung löschen" aria-label="Aussparung löschen" onClick={() => { onExclusionsChange(exclusions.filter(zone => zone.id !== selected)); select('area'); }} data-testid="exclusion-delete"><Trash2 size={16}/></button>}</div>
    <div ref={wrap} className={`blank-board ${drawing ? 'is-drawing' : ''}`} data-testid="admin-area-canvas" data-area={JSON.stringify(area)} data-exclusions={JSON.stringify(exclusions)} data-selected-region={selected}>
      <Stage width={size} height={size} scaleX={scale} scaleY={scale} ref={stage} onMouseDown={() => { if (drawing) start.current = point(); }} onTouchStart={() => { if (drawing) start.current = point(); }} onMouseMove={move} onTouchMove={move} onMouseUp={end} onTouchEnd={end} onMouseLeave={end}>
        <Layer><KImage image={blank} width={800} height={800} listening={false}/>
          {[{ ...area, id: 'area' }, ...exclusions].map(zone => <MaskRegionNode key={zone.id} zone={zone} selected={zone.id === selected} drawing={drawing} scale={scale} nodeRef={node => { nodes.current[zone.id] = node; }} onSelect={() => select(zone.id)} onChange={value => zone.id === 'area' ? onChange(normalizeArea(value)) : onExclusionsChange(exclusions.map(old => old.id === zone.id ? normalizeArea(value, 2) : old))}/>) }
          <Transformer ref={transformer} rotateEnabled={false} flipEnabled={false} keepRatio={active.shape === 'circle'} enabledAnchors={['top-left','top-right','bottom-left','bottom-right']} anchorSize={12} borderStroke={hole ? '#b45b50' : '#567942'} anchorStroke={hole ? '#b45b50' : '#567942'} boundBoxFunc={(old, next) => next.width < minimum*scale || next.height < minimum*scale ? old : next}/>
        </Layer>
      </Stage>{error && <div className="studio-error" role="alert" data-testid="admin-photo-error">{error}<button type="button" className="canvas-retry" onClick={retry} data-testid="admin-photo-retry">Erneut laden</button></div>}
    </div>
    <p className="mask-active-label" data-testid="mask-active-region">{hole ? `Aussparung ${exclusions.indexOf(active)+1}` : 'Gravurfläche'} · {active.shape === 'circle' ? 'Kreis' : 'Rechteck'}</p>
    <div className="element-numbers">{(active.shape === 'circle' ? [['x','Links'],['y','Oben'],['w','Durchmesser']] : [['x','Links'],['y','Oben'],['w','Breite'],['h','Höhe']]).map(([key,label]) => <label key={key}>{label} (px)<input type="number" min={['w','h'].includes(key) ? minimum : 0} max="800" step="any" value={Math.round(active[key]*10)/10} onChange={e => update({ ...active, [key]: Number(e.target.value), ...(active.shape === 'circle' && ['w','h'].includes(key) ? { w: Number(e.target.value), h: Number(e.target.value) } : {}) })} data-testid={`${prefix}-${key}`}/></label>)}</div>
  </section>;
};